# etl/reportes.py — versión corregida tras el análisis de SonarQube
import operator
import os

# Corrección 1: la credencial se lee del entorno, no se escribe en el código.
DB_PASSWORD = os.environ.get("DB_PASSWORD")

# Corrección 3: reglas declarativas con operadores permitidos, sin eval.
OPERADORES = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}


def buscar_cliente(con, email):
    # Corrección 2: consulta parametrizada con "?"; el valor nunca se interpola.
    consulta = "SELECT * FROM clientes WHERE email = ?"
    return con.execute(consulta, (email,)).fetchall()


def evaluar_regla(regla, fila):
    """Evalúa una regla (columna, operador, valor) sobre una fila.

    Ejemplo: evaluar_regla((0, ">", 10), (15, "ana@mail.com")) -> True
    """
    columna, simbolo, valor = regla
    if simbolo not in OPERADORES:
        raise ValueError(f"operador no permitido: {simbolo}")
    return OPERADORES[simbolo](fila[columna], valor)


def total(filas):
    # Corrección 4: excepción específica y propagada, no se oculta la falla.
    try:
        return sum(f[1] for f in filas)
    except (TypeError, IndexError) as error:
        raise ValueError("filas con formato inválido") from error
