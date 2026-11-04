#!/usr/bin/env bash
# Uso: SONAR_TOKEN=... scripts/analizar.sh <carpeta-evidencia>
# Ejecuta pruebas + cobertura, corre sonar-scanner y guarda la evidencia vía API.
set -euo pipefail
: "${SONAR_TOKEN:?Define SONAR_TOKEN}"
SALIDA="${1:?Indica la carpeta de evidencia, p. ej. evidencias/antes}"
HOST="http://localhost:9000"
KEY="taller-calidad"
mkdir -p "$SALIDA"

pytest --cov=etl --cov-report=term-missing --cov-report=xml | tee "$SALIDA/pytest_cobertura.txt"
# coverage.xml guarda la ruta absoluta del host; dentro del contenedor el proyecto está en /usr/src.
sed -i.bak "s#<source>$(pwd)#<source>/usr/src#" coverage.xml && rm -f coverage.xml.bak

# En macOS --network host no expone el host: se usa host.docker.internal.
docker run --rm -e SONAR_HOST_URL="http://host.docker.internal:9000" \
  -e SONAR_TOKEN="$SONAR_TOKEN" -v "$(pwd):/usr/src" sonarsource/sonar-scanner-cli \
  -Dsonar.qualitygate.wait=false > "$SALIDA/sonar_scanner.log" 2>&1 || true
tail -5 "$SALIDA/sonar_scanner.log"

# Esperar a que el Compute Engine procese el análisis.
TAREA=$(sed -n 's/.*api\/ce\/task?id=\([A-Za-z0-9_-]*\).*/\1/p' "$SALIDA/sonar_scanner.log")
for _ in $(seq 1 60); do
  estado=$(curl -s -u "$SONAR_TOKEN:" "$HOST/api/ce/task?id=$TAREA" \
    | python3 -c "import sys,json;print(json.load(sys.stdin)['task']['status'])")
  if [ "$estado" = "SUCCESS" ] || [ "$estado" = "FAILED" ]; then break; fi
  sleep 3
done
echo "Compute Engine: $estado"

curl -s -u "$SONAR_TOKEN:" "$HOST/api/qualitygates/project_status?projectKey=$KEY" > "$SALIDA/quality_gate.json"
curl -s -u "$SONAR_TOKEN:" "$HOST/api/issues/search?componentKeys=$KEY&ps=500&resolved=false" > "$SALIDA/issues.json"
curl -s -u "$SONAR_TOKEN:" "$HOST/api/hotspots/search?project=$KEY&ps=500" > "$SALIDA/hotspots.json"
curl -s -u "$SONAR_TOKEN:" "$HOST/api/measures/component?component=$KEY&metricKeys=bugs,vulnerabilities,security_hotspots,code_smells,coverage,duplicated_lines_density,ncloc,security_rating,reliability_rating,sqale_rating" > "$SALIDA/metricas.json"
python3 scripts/resumen.py "$SALIDA" | tee "$SALIDA/RESUMEN.md"
