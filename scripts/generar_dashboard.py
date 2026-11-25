#!/usr/bin/env python3
"""Genera las visualizaciones del dashboard y su version HTML autocontenida.

Entrada: evidencia generada por scripts/evaluar_observabilidad.py.
Salida: dashboard/capturas/*.png, dashboard/assets/*.png, dashboard/dashboard.html.

Uso: python scripts/generar_dashboard.py   (requiere matplotlib)
"""
from __future__ import annotations

import base64
import json
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parent.parent
EVIDENCIA = RAIZ / "evidencia"
DASH = RAIZ / "dashboard"
CAPTURAS = DASH / "capturas"
ASSETS = DASH / "assets"

AZUL = "#1F4E79"
CELESTE = "#2E86DE"
NARANJA = "#E67E22"
ROJO = "#C0392B"
VERDE = "#27AE60"
GRIS = "#5D6D7E"


def cargar(nombre: str) -> dict:
    return json.loads((EVIDENCIA / nombre).read_text(encoding="utf-8"))


def _guardar(fig, nombre: str) -> None:
    CAPTURAS.mkdir(parents=True, exist_ok=True)
    fig.savefig(CAPTURAS / nombre, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _estilo():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.edgecolor": "#CBD5E1", "axes.labelcolor": GRIS,
        "axes.titleweight": "bold", "axes.titlecolor": AZUL,
        "xtick.color": GRIS, "ytick.color": GRIS,
        "figure.facecolor": "white", "axes.facecolor": "#F8FAFC",
    })


def grafico_latencia(detalle: list[dict], metricas: dict):
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ids = [d["escenario"] for d in detalle]
    valores = [d["latencia_ms"] for d in detalle]
    colores = [ROJO if v > metricas["umbral_latencia_ms"] else CELESTE for v in valores]
    ax.bar(ids, valores, color=colores, width=0.65)
    ax.axhline(metricas["umbral_latencia_ms"], color=NARANJA, ls="--", lw=1.5,
               label=f"Umbral {metricas['umbral_latencia_ms']} ms")
    ax.axhline(metricas["latencia_p95_ms"], color=VERDE, ls=":", lw=2,
               label=f"p95 {metricas['latencia_p95_ms']} ms")
    ax.set_title("Latencia por escenario (mediana de 3 repeticiones)")
    ax.set_ylabel("ms")
    ax.legend(frameon=False, fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    _guardar(fig, "02_latencia_escenarios.png")


def grafico_precision(detalle: list[dict], metricas: dict):
    fig, ax = plt.subplots(figsize=(9, 4.2))
    por_intencion = metricas["por_intencion"]
    nombres = list(por_intencion)
    precisiones = [por_intencion[k]["precision"] for k in nombres]
    consistencias = [por_intencion[k]["consistencia"] for k in nombres]
    x = range(len(nombres))
    ax.bar([i - 0.19 for i in x], precisiones, width=0.38, label="Precisión", color=CELESTE)
    ax.bar([i + 0.19 for i in x], consistencias, width=0.38, label="Consistencia", color=VERDE)
    ax.set_xticks(list(x))
    ax.set_xticklabels(nombres, rotation=25, ha="right", fontsize=8)
    ax.set_ylim(0, 1.08)
    ax.set_title("Precisión y consistencia por intención")
    ax.legend(frameon=False, fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    _guardar(fig, "03_precision_por_intencion.png")


def grafico_hallazgos(analisis: dict):
    fig, ax = plt.subplots(figsize=(10, 4.5))
    hallazgos = sorted(analisis["hallazgos"], key=lambda h: h["cantidad"])
    colores = {"alta": ROJO, "media": NARANJA, "informativa": GRIS}
    ax.barh([f"{h['id']} {h['titulo'][:38]}" for h in hallazgos],
            [h["cantidad"] for h in hallazgos],
            color=[colores.get(h["severidad"], GRIS) for h in hallazgos])
    ax.set_title("Patrones detectados en registros de ejecución")
    ax.set_xlabel("Ocurrencias")
    ax.grid(axis="x", alpha=0.3)
    ax.tick_params(axis="y", labelsize=8)
    _guardar(fig, "04_hallazgos_trazas.png")


def grafico_recursos(detalle: list[dict], seguridad: dict):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8))
    ax1.bar([d["escenario"] for d in detalle], [d["cpu_promedio_pct"] for d in detalle],
            color=NARANJA, width=0.65)
    ax1.set_title("CPU por escenario (%)")
    ax1.set_ylim(0, max(110, max(d["cpu_promedio_pct"] for d in detalle) * 1.15))
    ax1.tick_params(axis="x", rotation=45, labelsize=7)
    ax1.grid(axis="y", alpha=0.3)

    checks = seguridad["checks"]
    nombres = list(checks)
    ax2.barh(nombres, [1 if checks[k] else 0 for k in nombres],
             color=[VERDE if checks[k] else ROJO for k in nombres])
    ax2.set_title("Controles de seguridad activos")
    ax2.set_xlim(0, 1.15)
    ax2.set_xticks([])
    ax2.tick_params(axis="y", labelsize=8)
    for i, nombre in enumerate(nombres):
        ax2.text(1.05, i, "OK" if checks[nombre] else "PENDIENTE", va="center",
                 fontsize=8, color=VERDE if checks[nombre] else ROJO)
    fig.tight_layout()
    _guardar(fig, "05_recursos_seguridad.png")


def dashboard_general(metricas: dict, detalle: list[dict], analisis: dict):
    fig = plt.figure(figsize=(14, 8.4))
    fig.patch.set_facecolor("#F1F5F9")
    fig.text(0.035, 0.945, "OBSERVABILIDAD · AGENTE FERRANDES (EP3)",
             fontsize=20, fontweight="bold", color=AZUL)
    fig.text(0.035, 0.905,
             f"Encargo con presentación · ISY0101 · {metricas['n_ejecuciones']} ejecuciones · "
             f"{metricas['n_escenarios']} escenarios · generado {metricas['generado']}",
             fontsize=10, color=GRIS)

    kpis = [
        ("PRECISIÓN MEDIA", f"{metricas['precision_media']:.0%}", CELESTE),
        ("LATENCIA p95", f"{metricas['latencia_p95_ms']} ms", NARANJA),
        ("CONSISTENCIA", f"{metricas['consistencia_media']:.0%}", VERDE),
        ("ERRORES", str(metricas["errores_inesperados"]), ROJO),
        ("RAM MÁX.", f"{metricas['rss_max_mb']} MB", GRIS),
    ]
    for i, (titulo, valor, color) in enumerate(kpis):
        x = 0.035 + i * 0.194
        fig.add_artist(plt.Rectangle((x, 0.77), 0.175, 0.105, transform=fig.transFigure,
                                     facecolor="white", edgecolor="#CBD5E1"))
        fig.text(x + 0.009, 0.848, titulo, fontsize=8, color=GRIS)
        fig.text(x + 0.009, 0.792, valor, fontsize=18, fontweight="bold", color=color)

    gs = fig.add_gridspec(2, 2, left=0.06, right=0.97, bottom=0.08, top=0.73, hspace=0.42, wspace=0.22)

    ax1 = fig.add_subplot(gs[0, 0])
    ax1.bar([d["escenario"] for d in detalle], [d["latencia_ms"] for d in detalle],
            color=CELESTE, width=0.7)
    ax1.axhline(metricas["umbral_latencia_ms"], color=NARANJA, ls="--", lw=1.2)
    ax1.set_title("Latencia por escenario (ms)", loc="left", fontsize=11)
    ax1.tick_params(axis="x", rotation=45, labelsize=7)
    ax1.grid(axis="y", alpha=0.3)

    ax2 = fig.add_subplot(gs[0, 1])
    por = metricas["por_intencion"]
    ax2.barh(list(por), [por[k]["precision"] for k in por], color=VERDE)
    ax2.set_xlim(0, 1.05)
    ax2.set_title("Precisión por intención", loc="left", fontsize=11)
    ax2.tick_params(axis="y", labelsize=7)
    ax2.grid(axis="x", alpha=0.3)

    ax3 = fig.add_subplot(gs[1, 0])
    colores = {"alta": ROJO, "media": NARANJA, "informativa": GRIS}
    hallazgos = sorted(analisis["hallazgos"], key=lambda h: h["cantidad"])
    ax3.barh([h["id"] for h in hallazgos], [h["cantidad"] for h in hallazgos],
             color=[colores.get(h["severidad"], GRIS) for h in hallazgos])
    ax3.set_title("Hallazgos en logs (ocurrencias)", loc="left", fontsize=11)
    ax3.grid(axis="x", alpha=0.3)

    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis("off")
    resumen_txt = (
        f"Falsos negativos de catálogo\n  EP2: {analisis['falsos_negativos_historicos']}   "
        f"→ EP3: {analisis['falsos_negativos_ep3']}\n\n"
        f"Consistencia mínima: {metricas['consistencia_min']:.0%}\n"
        f"Errores esperados: {metricas['errores_esperados']}\n"
        f"Ejecuciones sobre umbral: {metricas['ejecuciones_sobre_umbral']}\n\n"
        "Controles de seguridad:\n"
        "  • PII redactada en trazas\n"
        "  • Consentimiento por cliente\n"
        "  • Auditoría de escrituras\n"
        "  • Guardrail normativo"
    )
    ax4.text(0.02, 0.95, resumen_txt, va="top", fontsize=10, color=GRIS,
             family="DejaVu Sans", linespacing=1.5)
    ax4.set_title("Lectura del dashboard", loc="left", fontsize=11)

    fig.text(0.035, 0.03, "Fuente: evidencia/metricas.json · evidencia/analisis_trazas.json · "
             "dashboard/app.py (Streamlit)", fontsize=8, color=GRIS)
    CAPTURAS.mkdir(parents=True, exist_ok=True)
    fig.savefig(CAPTURAS / "01_dashboard_general.png", dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def diagrama_observabilidad() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    dot = ASSETS / "diagrama_observabilidad.dot"
    dot.write_text("""digraph observabilidad {
  rankdir=LR;
  node [shape=box, style="rounded,filled", fillcolor="#EAF2F8", fontname="Helvetica", fontsize=10];
  A [label="Agente Ferrandes\\n(45 ejecuciones)"];
  B [label="Instrumentación\\nspans + trace_id"];
  C [label="Trazas redactadas\\ntrazas_ep3.jsonl"];
  D [label="Métricas\\nprecisión / latencia /\\nconsistencia / errores / recursos"];
  E [label="Dashboard\\nStreamlit + PNG"];
  F [label="Análisis\\nhallazgos + causa raíz"];
  G [label="Recomendaciones\\nIE7 / IE8"];
  A -> B -> C -> D -> E;
  C -> F -> G;
  D -> F;
  G -> A [label="mejora continua", style=dashed];
}
""", encoding="utf-8")
    try:
        subprocess.run(["dot", "-Tpng", str(dot), "-o",
                        str(ASSETS / "diagrama_observabilidad.png")], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass


def html_dashboard(metricas: dict, analisis: dict, seguridad: dict) -> None:
    def img(nombre: str) -> str:
        datos = base64.b64encode((CAPTURAS / nombre).read_bytes()).decode("ascii")
        return f'<img class="shot" src="data:image/png;base64,{datos}" alt="{nombre}">'

    filas = "".join(
        f"<tr><td>{h['id']}</td><td>{h['titulo']}</td><td>{h['severidad']}</td>"
        f"<td>{h['cantidad']}</td><td>{h['estado']}</td><td>{h['indicador']}</td></tr>"
        for h in analisis["hallazgos"]
    )
    checks = "".join(f"<li><b>{k}</b>: {'sí' if v else 'NO'}</li>"
                     for k, v in seguridad["checks"].items())
    contenido = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>Dashboard EP3 · Agente Ferrandes</title>
<style>
body {{ font-family: DejaVu Sans, Arial, sans-serif; background:#F1F5F9; color:#1F2937; margin:0; }}
header {{ background:#1F4E79; color:white; padding:24px 40px; }}
h1 {{ margin:0; font-size:26px; }} header p {{ margin:6px 0 0; color:#BFD7EA; }}
main {{ max-width:1200px; margin:auto; padding:28px 30px; }}
.kpis {{ display:flex; gap:14px; flex-wrap:wrap; }}
.kpi {{ background:white; border:1px solid #CBD5E1; border-radius:10px; padding:16px 20px; min-width:170px; }}
.kpi span {{ display:block; font-size:11px; color:#5D6D7E; text-transform:uppercase; }}
.kpi strong {{ display:block; font-size:26px; color:#1F4E79; }}
.shot {{ width:100%; border:1px solid #CBD5E1; border-radius:10px; background:white; margin:16px 0; }}
table {{ border-collapse:collapse; width:100%; background:white; font-size:13px; }}
th,td {{ border:1px solid #CBD5E1; padding:8px 10px; text-align:left; }}
th {{ background:#EAF2F8; color:#1F4E79; }}
h2 {{ color:#1F4E79; margin-top:36px; }}
</style></head><body>
<header><h1>Observabilidad del Agente Ferrandes · EP3</h1>
<p>{metricas['n_ejecuciones']} ejecuciones · {metricas['n_escenarios']} escenarios · generado {metricas['generado']}</p></header>
<main>
<div class="kpis">
<div class="kpi"><span>Precisión media</span><strong>{metricas['precision_media']:.0%}</strong></div>
<div class="kpi"><span>Latencia p95</span><strong>{metricas['latencia_p95_ms']} ms</strong></div>
<div class="kpi"><span>Consistencia</span><strong>{metricas['consistencia_media']:.0%}</strong></div>
<div class="kpi"><span>Errores inesperados</span><strong>{metricas['errores_inesperados']}</strong></div>
<div class="kpi"><span>RAM máxima</span><strong>{metricas['rss_max_mb']} MB</strong></div>
</div>
<h2>Vista general</h2>{img('01_dashboard_general.png')}
<h2>Latencia y precisión</h2>{img('02_latencia_escenarios.png')}{img('03_precision_por_intencion.png')}
<h2>Análisis de trazas</h2>{img('04_hallazgos_trazas.png')}
<table><tr><th>ID</th><th>Hallazgo</th><th>Severidad</th><th>N</th><th>Estado</th><th>IE</th></tr>{filas}</table>
<h2>Recursos y seguridad</h2>{img('05_recursos_seguridad.png')}
<ul>{checks}</ul>
<p><small>Versión interactiva: <code>streamlit run dashboard/app.py</code></small></p>
</main></body></html>"""
    (DASH / "dashboard.html").write_text(contenido, encoding="utf-8")


def main() -> None:
    _estilo()
    metricas = cargar("metricas.json")
    detalle = json.loads((EVIDENCIA / "mediciones_detalle.json").read_text(encoding="utf-8"))
    analisis = cargar("analisis_trazas.json")
    seguridad = cargar("verificacion_seguridad.json")

    dashboard_general(metricas, detalle, analisis)
    grafico_latencia(detalle, metricas)
    grafico_precision(detalle, metricas)
    grafico_hallazgos(analisis)
    grafico_recursos(detalle, seguridad)
    diagrama_observabilidad()
    html_dashboard(metricas, analisis, seguridad)
    print("Dashboard generado:", DASH / "dashboard.html")
    print("Capturas:", sorted(p.name for p in CAPTURAS.glob("*.png")))


if __name__ == "__main__":
    main()
