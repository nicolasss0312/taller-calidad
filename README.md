# taller-calidad

Mini-pipeline ETL (CSV → limpieza → SQLite) con pruebas unitarias y de integración (pytest), cobertura (pytest-cov) y análisis estático con SonarQube.

## Ejecutar las pruebas

```bash
uv venv --python 3.11 .venv   # o: python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
pytest --cov=etl --cov-report=term-missing
```

## Analizar con SonarQube

```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube:10.7-community
# En http://localhost:9000: admin/admin → cambiar clave → My Account › Security → token
export SONAR_TOKEN=<token>
scripts/analizar.sh evidencias/<carpeta>
```

`scripts/analizar.sh` genera `coverage.xml`, ajusta las rutas para el contenedor, ejecuta `sonar-scanner-cli` y guarda el Quality Gate, los issues, los hotspots y las métricas (JSON + `RESUMEN.md`).

## Estructura

| Ruta | Contenido |
|---|---|
| `etl/` | `transform.py`, `pipeline.py`, `reportes.py` (corregido) |
| `tests/` | unitarias, integración y seguridad: 61 pruebas |
| `docs/casos_de_prueba.md` | diseño de los casos antes de escribir las pruebas |
| `evidencias/paso4_linea_base/` | primer análisis (sin `reportes.py`) |
| `evidencias/antes/` | análisis con los defectos: Quality Gate **ERROR** |
| `evidencias/despues/` | análisis corregido: Quality Gate **OK** |
| `reportes/cobertura.txt` | salida de `pytest --cov` (100 %) |
| `INFORME.md` | hallazgos, correcciones y reflexión |
