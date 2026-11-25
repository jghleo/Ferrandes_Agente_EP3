"""Dashboard de observabilidad del Agente Ferrandes — EP3.

Ejecutar:
    pip install -r requirements.txt
    streamlit run dashboard/app.py

El dashboard lee la evidencia real generada por
`python scripts/evaluar_observabilidad.py`; no muestra datos simulados.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent
EVIDENCIA = RAIZ / "evidencia"


def cargar(nombre: str) -> dict:
    ruta = EVIDENCIA / nombre
    if not ruta.exists():
        st.error(f"No existe {ruta}. Ejecuta primero scripts/evaluar_observabilidad.py")
        st.stop()
    return json.loads(ruta.read_text(encoding="utf-8"))


st.set_page_config(page_title="Observabilidad · Agente Ferrandes EP3", layout="wide")
metricas = cargar("metricas.json")
analisis = cargar("analisis_trazas.json")
seguridad = cargar("verificacion_seguridad.json")

st.title("Observabilidad del Agente Ferrandes")
st.caption(f"EP3 · ISY0101 · medición generada el {metricas['generado']} · "
           f"{metricas['n_ejecuciones']} ejecuciones / {metricas['n_escenarios']} escenarios")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Precisión media", f"{metricas['precision_media']:.0%}")
c2.metric("Latencia p95", f"{metricas['latencia_p95_ms']} ms")
c3.metric("Consistencia", f"{metricas['consistencia_media']:.0%}")
c4.metric("Errores inesperados", metricas["errores_inesperados"])
c5.metric("RSS máxima", f"{metricas['rss_max_mb']} MB")

st.markdown("---")
col_izq, col_der = st.columns([3, 2])

with col_izq:
    st.subheader("Comportamiento por escenario")
    detalle = json.loads((EVIDENCIA / "mediciones_detalle.json").read_text(encoding="utf-8")) \
        if (EVIDENCIA / "mediciones_detalle.json").exists() else []
    if detalle:
        corte = st.selectbox("Corte", ["Todos", "Nominal", "Variabilidad"],
                             key="corte_escenario")
        if corte == "Nominal":
            detalle = [d for d in detalle if d["variabilidad"] == "nominal"]
        st.line_chart(
            {f"{d['escenario']}": d["latencia_ms"] for d in detalle},
            height=260,
        )
        st.caption(f"Umbral de alerta: {metricas['umbral_latencia_ms']} ms · "
                   f"p95: {metricas['latencia_p95_ms']} ms · "
                   f"máximo: {metricas['latencia_max_ms']} ms")
    else:
        st.info("Falta evidencia/mediciones_detalle.json")

with col_der:
    st.subheader("Precisión por intención")
    st.bar_chart({k: v["precision"] for k, v in metricas["por_intencion"].items()}, height=260)
    st.caption("Precisión = 0,4 intención + 0,4 herramientas (Jaccard) + 0,2 palabra clave")

st.markdown("---")
c_izq, c_der = st.columns(2)
with c_izq:
    st.subheader("Análisis de registros / trazabilidad")
    st.dataframe(
        [{"ID": h["id"], "Hallazgo": h["titulo"], "Severidad": h["severidad"],
          "N": h["cantidad"], "Estado": h["estado"], "IE": h["indicador"]}
         for h in analisis["hallazgos"]],
        use_container_width=True, hide_index=True,
    )
with c_der:
    st.subheader("Consistencia y errores por variabilidad")
    st.bar_chart({k: v["consistencia"] for k, v in metricas["por_variabilidad"].items()}, height=220)
    st.write(f"Falsos negativos de catálogo: **{analisis['falsos_negativos_historicos']} en EP2 → "
             f"{analisis['falsos_negativos_ep3']} en EP3**")

st.markdown("---")
st.subheader("Seguridad y uso responsable")
st.json(seguridad)
if all(seguridad["checks"].values()):
    st.success("Controles activos: sin PII en trazas, trazabilidad completa, consentimiento y auditoría.")
else:
    st.warning("Hay controles de seguridad pendientes; revisar verificación.")

with st.expander("Cómo regenerar esta evidencia"):
    st.code("python scripts/evaluar_observabilidad.py\nstreamlit run dashboard/app.py",
            language="bash")
