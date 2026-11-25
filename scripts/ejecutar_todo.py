"""Ejecuta el pipeline completo del agente Ferrandes (EP2 + EP3).

Uso:
    python scripts/ejecutar_todo.py

Los scripts que requieren dependencias (dashboard, informe y PPT) se saltan
si las librerías no están instaladas. Instala con: pip install -r requirements.txt
"""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def correr(comando: list[str]) -> bool:
    print(f"\n== {Path(comando[0]).name} {' '.join(comando[1:])} ==")
    try:
        subprocess.run([sys.executable, *comando], cwd=RAIZ, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def correr_si(modulo: str, comando: list[str]) -> bool:
    try:
        __import__(modulo)
    except ImportError:
        print(f"SALTADO: falta '{modulo}'. Instala con: pip install -r requirements.txt")
        return True
    return correr(comando)


def main() -> None:
    ok = True
    ok &= correr(["tests/ejecutar_tests.py"])
    ok &= correr(["scripts/demo.py"])

    # EP3: medicion real, dashboard y entregables derivados.
    ok &= correr(["scripts/evaluar_observabilidad.py"])
    ok &= correr_si("matplotlib", ["scripts/generar_dashboard.py"])
    ok &= correr_si("docx", ["scripts/generar_informe.py"])
    ok &= correr_si("docx", ["scripts/generar_evaluacion.py"])
    ok &= correr_si("pptx", ["presentacion/generar_ppt.py"])

    # EP2: framework de agentes (opcional).
    ok &= correr_si("langchain", ["scripts/smoke_langchain.py"])

    print("\n== Verificación de artefactos ==")
    for ruta in ["evidencia/", "dashboard/", "informe/", "presentacion/"]:
        print(f"  {ruta}")
    print("\nPara el PDF del informe:")
    print("  libreoffice -env:UserInstallation=file:///tmp/opencode/lo_profile "
          "--headless --convert-to pdf --outdir informe informe/Informe_Tecnico_EP3_Ferrandes.docx")
    print("  libreoffice -env:UserInstallation=file:///tmp/opencode/lo_profile "
          "--headless --convert-to pdf --outdir informe informe/Evaluacion_Pauta_EP3_Ferrandes.docx")
    print("\nPara el dashboard interactivo:")
    print("  streamlit run dashboard/app.py")
    print("\nResultado:", "TODO OK ✅" if ok else "Hubo errores revisa arriba ⚠️")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
