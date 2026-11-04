import importlib
import sqlite3

import pytest

from etl import reportes
from etl.reportes import buscar_cliente, evaluar_regla, total


@pytest.fixture
def conexion_con_clientes():
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE clientes (id INTEGER PRIMARY KEY, email TEXT)")
    con.executemany("INSERT INTO clientes VALUES (?, ?)",
                    [(1, "ana@mail.com"), (2, "luis@mail.com")])
    yield con
    con.close()


# ---------- buscar_cliente: inyección SQL ----------

def test_buscar_cliente_encuentra_por_email(conexion_con_clientes):
    assert buscar_cliente(conexion_con_clientes, "ana@mail.com") == [(1, "ana@mail.com")]


def test_buscar_cliente_inexistente(conexion_con_clientes):
    assert buscar_cliente(conexion_con_clientes, "nadie@mail.com") == []


@pytest.mark.parametrize("ataque", [
    "' OR '1'='1",
    "' OR 1=1 --",
    "ana@mail.com' --",
    "x'; DROP TABLE clientes; --",
])
def test_buscar_cliente_resiste_inyeccion_sql(conexion_con_clientes, ataque):
    assert buscar_cliente(conexion_con_clientes, ataque) == []
    # La tabla sigue intacta después del intento.
    assert conexion_con_clientes.execute(
        "SELECT COUNT(*) FROM clientes").fetchone()[0] == 2


# ---------- evaluar_regla: sin eval ----------

@pytest.mark.parametrize("regla, esperado", [
    ((0, ">", 10), True),
    ((0, "<=", 10), False),
    ((0, "==", 15), True),
    ((0, "!=", 15), False),
    ((0, ">=", 15), True),
    ((1, "==", "ana@mail.com"), True),
    ((1, "<", "b"), True),
])
def test_evaluar_regla(regla, esperado):
    assert evaluar_regla(regla, (15, "ana@mail.com")) is esperado


@pytest.mark.parametrize("simbolo", ["and", "__import__('os')", "**", ""])
def test_evaluar_regla_rechaza_operador_no_permitido(simbolo):
    with pytest.raises(ValueError, match="operador no permitido"):
        evaluar_regla((0, simbolo, 1), (15,))


def test_evaluar_regla_no_ejecuta_codigo():
    # Con eval esto habría ejecutado código; ahora es solo un valor a comparar.
    assert evaluar_regla((0, "==", "__import__('os').system('echo x')"), (15,)) is False


# ---------- total: excepción específica ----------

@pytest.mark.parametrize("filas, esperado", [
    ([(1, 10), (2, 20.5)], 30.5),
    ([], 0),
])
def test_total(filas, esperado):
    assert total(filas) == esperado


@pytest.mark.parametrize("filas", [
    [(1,)],              # IndexError: falta la columna
    [(1, "diez")],       # TypeError: valor no numérico
    None,                # TypeError: no iterable
])
def test_total_falla_explicitamente(filas):
    with pytest.raises(ValueError, match="formato inválido"):
        total(filas)


# ---------- credencial desde el entorno ----------

def test_db_password_se_lee_del_entorno(monkeypatch):
    monkeypatch.setenv("DB_PASSWORD", "desde-entorno")
    assert importlib.reload(reportes).DB_PASSWORD == "desde-entorno"
    monkeypatch.delenv("DB_PASSWORD")
    assert importlib.reload(reportes).DB_PASSWORD is None
