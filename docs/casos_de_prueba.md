# Diseño de casos de prueba (antes de escribir las pruebas)

## `normalizar_email(email)`

| # | Tipo | Entrada | Resultado esperado |
|---|------|---------|--------------------|
| 1 | Válido | `" Ana@Mail.COM "` (espacios + mayúsculas) | `"ana@mail.com"` |
| 2 | Válido | `"luis.p+datos@uni.edu.co"` (punto, `+`, subdominios) | igual, sin cambios |
| 3 | Válido | `"\tMARIA_G@Empresa.org\n"` (tab/salto de línea, `_`) | `"maria_g@empresa.org"` |
| 4 | Inválido | `""` / `" "` (vacío o solo espacios) | `ValueError("email vacío")` |
| 5 | Inválido | `None` / `123` (no es texto) | `ValueError` |
| 6 | Inválido | `"sin-arroba"`, `"ana@"`, `"@mail.com"`, `"ana@mail"` | `ValueError("email inválido: ...")` |

## `calcular_total(precio, cantidad, descuento=0.0)`

| # | Tipo | Entrada (precio, cantidad, descuento) | Resultado esperado |
|---|------|---------------------------------------|--------------------|
| 1 | Válido | `(100, 2, 0.1)` | `180.0` |
| 2 | Válido · límite | `(100, 2, 0)` y `(100, 2, 1)` (descuento 0 y 1) | `200.0` y `0.0` |
| 3 | Válido · límite | `(100, 0, 0.3)` (cantidad 0) | `0.0` |
| 4 | Válido · redondeo | `(19.99, 3, 0.15)` → 50.9745 | `50.97` |
| 5 | Inválido | `(-1, 2)` / `(10, -1)` (negativos) | `ValueError` |
| 6 | Inválido | descuento `1.01` o `-0.01` (fuera de [0, 1]) | `ValueError` |
