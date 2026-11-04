import sqlite3

import pytest

from etl.pipeline import ejecutar_pipeline


@pytest.fixture
def conexion():
    con = sqlite3.connect(":memory:")
    yield con
    con.close()


@pytest.fixture
def csv_valido(tmp_path):
    csv = tmp_path / "clientes.csv"
    csv.write_text("id,email\n1, Ana@Mail.com\n2,luis@mail.com\n", encoding="utf-8")
    return csv


def contar_clientes(con):
    return con.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]


def test_pipeline_carga_clientes(conexion, tmp_path):
    csv = tmp_path / "clientes.csv"
    csv.write_text("id,email\n1, Ana@Mail.com\n2,luis@mail.com\n")
    ejecutar_pipeline(csv, conexion)
    filas = conexion.execute(
        "SELECT email FROM clientes ORDER BY id").fetchall()
    assert filas == [("ana@mail.com",), ("luis@mail.com",)]


def test_pipeline_retorna_filas_cargadas(conexion, csv_valido):
    assert ejecutar_pipeline(csv_valido, conexion) == 2


def test_pipeline_es_idempotente(conexion, csv_valido):
    ejecutar_pipeline(csv_valido, conexion)
    ejecutar_pipeline(csv_valido, conexion)
    assert contar_clientes(conexion) == 2  # 2 filas, no 4


def test_pipeline_actualiza_registro_existente(conexion, tmp_path):
    csv = tmp_path / "clientes.csv"
    csv.write_text("id,email\n1,ana@mail.com\n", encoding="utf-8")
    ejecutar_pipeline(csv, conexion)
    csv.write_text("id,email\n1,ANA.NUEVA@mail.com\n", encoding="utf-8")
    ejecutar_pipeline(csv, conexion)
    assert conexion.execute("SELECT id, email FROM clientes").fetchall() == [
        (1, "ana.nueva@mail.com")]


def test_pipeline_email_invalido_no_carga_nada(conexion, tmp_path):
    """Decisión: falla rápido. Si una fila es inválida se lanza ValueError
    y no se carga ninguna fila (el lote es todo o nada)."""
    csv = tmp_path / "clientes.csv"
    csv.write_text("id,email\n1,ana@mail.com\n2,correo-malo\n3,luis@mail.com\n",
                   encoding="utf-8")
    with pytest.raises(ValueError, match="correo-malo"):
        ejecutar_pipeline(csv, conexion)
    assert contar_clientes(conexion) == 0


def test_pipeline_csv_vacio(conexion, tmp_path):
    csv = tmp_path / "clientes.csv"
    csv.write_text("id,email\n", encoding="utf-8")
    assert ejecutar_pipeline(csv, conexion) == 0
    assert contar_clientes(conexion) == 0
