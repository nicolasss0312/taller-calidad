import pytest

from etl.transform import normalizar_email, calcular_total


# ---------- normalizar_email ----------

@pytest.mark.parametrize("entrada, esperado", [
    (" Ana@Mail.COM ", "ana@mail.com"),
    ("luis.p+datos@uni.edu.co", "luis.p+datos@uni.edu.co"),
    ("\tMARIA_G@Empresa.org\n", "maria_g@empresa.org"),
])
def test_normalizar_email_valido(entrada, esperado):
    assert normalizar_email(entrada) == esperado


@pytest.mark.parametrize("entrada", ["", " ", "sin-arroba", None])
def test_normalizar_email_invalido(entrada):
    with pytest.raises(ValueError):
        normalizar_email(entrada)


@pytest.mark.parametrize("entrada", ["ana@", "@mail.com", "ana@mail", 123])
def test_normalizar_email_formato_incorrecto(entrada):
    with pytest.raises(ValueError):
        normalizar_email(entrada)


def test_normalizar_email_mensaje_incluye_valor_original():
    with pytest.raises(ValueError, match="email inválido: Ana@"):
        normalizar_email("Ana@")


# ---------- calcular_total ----------

@pytest.mark.parametrize("precio, cantidad, descuento, esperado", [
    (100, 2, 0.1, 180.0),   # descuento normal
    (100, 2, 0.5, 100.0),
    (50, 3, 0.25, 112.5),
])
def test_calcular_total_con_descuento(precio, cantidad, descuento, esperado):
    assert calcular_total(precio, cantidad, descuento) == esperado


@pytest.mark.parametrize("precio, cantidad, descuento, esperado", [
    (100, 2, 0, 200.0),     # descuento límite inferior
    (100, 2, 1, 0.0),       # descuento límite superior
    (100, 0, 0.3, 0.0),     # cantidad 0
    (0, 5, 0.2, 0.0),       # precio 0
])
def test_calcular_total_casos_limite(precio, cantidad, descuento, esperado):
    assert calcular_total(precio, cantidad, descuento) == esperado


def test_calcular_total_descuento_por_defecto():
    assert calcular_total(10, 3) == 30.0


@pytest.mark.parametrize("precio, cantidad", [(-1, 2), (10, -1), (-5, -5)])
def test_calcular_total_negativos(precio, cantidad):
    with pytest.raises(ValueError, match="fuera de rango"):
        calcular_total(precio, cantidad)


@pytest.mark.parametrize("descuento", [1.01, 2, -0.01, -1])
def test_calcular_total_descuento_fuera_de_rango(descuento):
    with pytest.raises(ValueError):
        calcular_total(100, 1, descuento)


@pytest.mark.parametrize("precio, cantidad, descuento, esperado", [
    (19.99, 3, 0.15, 50.97),   # 50.9745 -> 50.97
    (10.555, 1, 0, 10.55),     # representación binaria de 10.555
    (0.1, 3, 0, 0.3),          # 0.30000000000000004 -> 0.3
    (33.33, 3, 0.333, 66.69),  # 66.69333 -> 66.69
])
def test_calcular_total_redondeo(precio, cantidad, descuento, esperado):
    assert calcular_total(precio, cantidad, descuento) == esperado
