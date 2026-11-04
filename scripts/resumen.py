"""Resume en Markdown la evidencia JSON exportada desde SonarQube."""
import json
import sys
from pathlib import Path

carpeta = Path(sys.argv[1])
cargar = lambda n: json.loads((carpeta / n).read_text(encoding="utf-8"))

qg = cargar("quality_gate.json")["projectStatus"]
print(f"## Quality Gate: **{qg['status']}**\n")
print("| Condición | Valor | Umbral | Estado |\n|---|---|---|---|")
for c in qg.get("conditions", []):
    print(f"| {c['metricKey']} | {c.get('actualValue', '-')} | {c.get('errorThreshold', '-')} | {c['status']} |")

print("\n## Métricas\n\n| Métrica | Valor |\n|---|---|")
for m in sorted(cargar("metricas.json")["component"]["measures"], key=lambda m: m["metric"]):
    print(f"| {m['metric']} | {m.get('value', '-')} |")

issues = cargar("issues.json")["issues"]
print(f"\n## Issues ({len(issues)})\n\n| Archivo:línea | Tipo | Severidad | Regla | Mensaje |\n|---|---|---|---|---|")
for i in issues:
    print(f"| {i['component'].split(':', 1)[1]}:{i.get('line', '-')} | {i['type']} | {i['severity']} | {i['rule']} | {i['message']} |")

hotspots = cargar("hotspots.json")["hotspots"]
print(f"\n## Security Hotspots ({len(hotspots)})\n\n| Archivo:línea | Categoría | Prob. | Estado | Mensaje |\n|---|---|---|---|---|")
for h in hotspots:
    print(f"| {h['component'].split(':', 1)[1]}:{h.get('line', '-')} | {h['securityCategory']} | {h['vulnerabilityProbability']} | {h['status']} | {h['message']} |")
