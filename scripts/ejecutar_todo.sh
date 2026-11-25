#!/usr/bin/env bash
# Ejecuta el pipeline completo del agente Ferrandes (EP2 + EP3).
# Uso: bash scripts/ejecutar_todo.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== 1) Pruebas unitarias (sin dependencias) =="
python3 tests/ejecutar_tests.py

echo
echo "== 2) Demo + evidencia de pruebas =="
python3 scripts/demo.py >/dev/null && echo "OK -> evidencia/evidencia_pruebas.txt, evidencia/logs_agente.jsonl"

echo
echo "== 3) Evaluacion de observabilidad (EP3, sin dependencias) =="
python3 scripts/evaluar_observabilidad.py

echo
echo "== 4) Dashboard, informe y PPT (requieren dependencias) =="
if python3 -c "import matplotlib" 2>/dev/null; then
  python3 scripts/generar_dashboard.py >/dev/null && echo "OK -> dashboard/capturas/"
else
  echo "SALTADO dashboard: pip install -r requirements.txt"
fi
if python3 -c "import docx" 2>/dev/null; then
  python3 scripts/generar_informe.py
  python3 scripts/generar_evaluacion.py
else
  echo "SALTADO informe/evaluacion: pip install -r requirements.txt"
fi
if python3 -c "import pptx" 2>/dev/null; then
  python3 presentacion/generar_ppt.py
else
  echo "SALTADO PPT: pip install -r requirements.txt"
fi

echo
echo "== 5) Smoke test del agente LangChain (opcional) =="
if python3 -c "import langchain" 2>/dev/null; then
  python3 scripts/smoke_langchain.py >/dev/null && echo "OK -> evidencia/evidencia_langchain.txt"
else
  echo "SALTADO (langchain no instalado): pip install -r requirements.txt"
fi

echo
echo "== 6) Verificación de artefactos =="
ls -1 evidencia/ dashboard/ informe/*.docx presentacion/*.pptx
echo "Todo listo. Recuerda generar los PDF con LibreOffice y abrir streamlit run dashboard/app.py"
