## Quality Gate: **ERROR**

| Condición | Valor | Umbral | Estado |
|---|---|---|---|
| new_coverage | 0.0 | 80 | ERROR |
| new_duplicated_lines_density | 0.0 | 3 | OK |
| new_security_hotspots_reviewed | 0.0 | 100 | ERROR |
| new_violations | 2 | 0 | ERROR |

## Métricas

| Métrica | Valor |
|---|---|
| bugs | 0 |
| code_smells | 2 |
| coverage | 64.7 |
| duplicated_lines_density | 0.0 |
| ncloc | 37 |
| reliability_rating | 1.0 |
| security_hotspots | 2 |
| security_rating | 1.0 |
| sqale_rating | 1.0 |
| vulnerabilities | 0 |

## Issues (2)

| Archivo:línea | Tipo | Severidad | Regla | Mensaje |
|---|---|---|---|---|
| etl/reportes.py:12 | CODE_SMELL | MAJOR | python:S1172 | Remove the unused function parameter "fila". |
| etl/reportes.py:19 | CODE_SMELL | CRITICAL | python:S5754 | Specify an exception class to catch or reraise the exception |

## Security Hotspots (2)

| Archivo:línea | Categoría | Prob. | Estado | Mensaje |
|---|---|---|---|---|
| etl/reportes.py:4 | auth | HIGH | TO_REVIEW | "password" detected here, review this potentially hard-coded credential. |
| etl/reportes.py:13 | rce | MEDIUM | TO_REVIEW | Make sure that this dynamic injection or execution of code is safe. |
