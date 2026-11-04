# Informe · Taller: calidad en un mini-pipeline ETL

**Curso:** Arquitectura de datos · Pruebas de software y garantía de calidad
**Autores (parejas):** Nicolás Cuervo · [pareja] · **Fecha:** 3 de noviembre de 2026
**Herramientas:** Python 3.11.16 · pytest 9.2.0 · pytest-cov 7.1.0 · SonarQube 10.7 Community (Docker) · sonar-scanner-cli

## 1. Resultados

| Criterio | Evidencia | Resultado |
|---|---|---|
| Pruebas unitarias | `tests/test_transform.py`: 10 funciones y 31 casos con `parametrize` y `pytest.raises` | ✅ 31/31 en verde |
| Integración | `tests/test_integracion.py`: carga CSV → SQLite, idempotencia, email inválido, CSV vacío, actualización | ✅ 6/6 |
| Seguridad (Paso 5) | `tests/test_reportes.py`: inyección SQL, reglas sin `eval`, excepciones, credencial | ✅ 24/24 |
| Cobertura | `reportes/cobertura.txt`: **100 %** del paquete `etl` (39/39 sentencias) | ✅ ≥ 80 % |
| SonarQube | `evidencias/antes/` (Quality Gate **ERROR**) → `evidencias/despues/` (Quality Gate **OK**) | ✅ Aprobado |

En total hay **61 pruebas, todas en verde**. El diseño previo de los casos de prueba (3 válidos y 3 inválidos por función, con casos límite) está en `docs/casos_de_prueba.md`.

### Decisión: CSV con un email inválido
Elegí **fallar rápido y no cargar nada**. `ejecutar_pipeline` normaliza todas las filas antes del `INSERT`, así que un solo email inválido lanza `ValueError` y la tabla queda vacía: el lote es "todo o nada". En un pipeline de datos es preferible detener la carga y avisar que cargar datos parciales sin que nadie se entere. La prueba `test_pipeline_email_invalido_no_carga_nada` verifica la excepción y que `COUNT(*) == 0`. Si se quisiera tolerar errores, la alternativa sería enviar las filas inválidas a una tabla de rechazos.

La **idempotencia** se cumple gracias a `INSERT OR REPLACE` sobre la clave primaria: si se ejecuta dos veces, quedan 2 filas y no 4.

## 2. Hallazgos de SonarQube en `reportes.py`

Quality Gate **Sonar way** antes de corregir: **ERROR**, con `new_violations = 2`, `new_security_hotspots_reviewed = 0 %` y `new_coverage = 0 %`.

| # | Defecto | Línea | Regla | Tipo en SonarQube | Riesgo (OWASP) |
|---|---|---|---|---|---|
| 1 | `DB_PASSWORD = "admin123"` | 4 | S2068 | **Security Hotspot** (auth, prob. ALTA) | A07 · credenciales en el código |
| 2 | `eval(expresion)` | 13 | S1523 | **Security Hotspot** (rce, prob. MEDIA) | A03 · inyección de código |
| 3 | `except: pass` | 19 | S5754 | **Code smell** (CRÍTICO) | Oculta fallas (fiabilidad) |
| 4 | parámetro `fila` sin usar | 12 | S1172 | **Code smell** (MAYOR) | Mantenibilidad |
| 5 | SQL armado con f-string | 8 | S2077 / S3649 | **No detectado** (ver nota) | A03 · inyección SQL |

**Nota sobre la herramienta:**
- **Versión.** El PDF usa la imagen `sonarqube:community`, que hoy descarga la versión 26.10. En esa versión no hay reglas de Security Hotspot para Python (la API devuelve 0) y los defectos de seguridad no se reportan, así que usé `sonarqube:10.7-community`.
- **Perfil.** S1523 (`eval`) existe pero no viene activa en "Sonar way". Creé el perfil **"Taller calidad"**, que hereda de Sonar way y activa S1523.
- **Inyección SQL.** SonarQube Community no la detectó. La regla de *taint analysis* (S3649) solo existe en las ediciones comerciales, y el hotspot S2077 no reconoce `con.execute` porque `con` no tiene tipo. Por eso este defecto se demuestra con una prueba.
- **Lección.** Un SAST no reemplaza a las pruebas: hay que combinar herramientas (SAST, pruebas, revisión).

## 3. Correcciones

| Defecto | Antes | Después | Prueba que lo demuestra |
|---|---|---|---|
| Credencial | `DB_PASSWORD = "admin123"` | `os.environ.get("DB_PASSWORD")` | `test_db_password_se_lee_del_entorno` |
| Inyección SQL | `f"... WHERE email = '{email}'"` | `"... WHERE email = ?"` con `(email,)` | `test_buscar_cliente_resiste_inyeccion_sql` (`' OR '1'='1`, `DROP TABLE`, …): devuelve `[]` y la tabla sigue intacta |
| `eval` | `eval(expresion)` | regla `(columna, operador, valor)` con un diccionario de `operator.*` permitido | `test_evaluar_regla*`, `test_evaluar_regla_no_ejecuta_codigo` |
| `except:` | `except: pass` devolvía `None` en silencio | `except (TypeError, IndexError)` y se relanza como `ValueError` | `test_total_falla_explicitamente` |

`evaluar_regla` cambió de firma: ya no recibe código Python como texto, sino una regla declarativa. Eso elimina la ejecución de código arbitrario y, de paso, usa `fila`, lo que corrige S1172.

Quality Gate después de corregir: **OK**, con `new_violations = 0`, `new_coverage = 100 %`, `new_duplicated_lines_density = 0 %` y 0 hotspots abiertos. Los issues S5754 y S1172 quedaron `CLOSED / FIXED`.

## 4. Reflexión

- **La cobertura no es calidad.** Antes de agregar `reportes.py` teníamos un 100 % de cobertura, y aun así la inyección SQL habría pasado inadvertida si no hubiéramos escrito una prueba con una entrada maliciosa. La cobertura mide qué líneas se ejecutan, no si las aserciones son buenas.
- **Escribir los casos antes que el código de prueba** obligó a pensar en los límites (descuento 0 y 1, cantidad 0, espacios y mayúsculas) y en errores de redondeo como `0.1 × 3`.
- **El Quality Gate evalúa el código nuevo.** Al principio el análisis no marcaba nada, porque las líneas de `reportes.py` tenían una fecha de commit anterior a la línea base. La calidad depende del proceso (commit → análisis), no solo de la herramienta.
- **Las herramientas cambian.** La versión más reciente de SonarQube Community dejó de reportar estos riesgos. Conviene fijar versiones (`10.7-community`, `requirements.txt`) para que el pipeline sea reproducible.
- Como siguiente paso, llevaría `scripts/analizar.sh` a un pipeline de CI (GitHub Actions) para que el Quality Gate bloquee automáticamente el *merge*.
