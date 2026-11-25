#!/usr/bin/env python3
"""Genera la presentacion de defensa EP3 (PPT) con evidencia del dashboard.

Uso: python presentacion/generar_ppt.py   (requiere python-pptx)
"""
from __future__ import annotations

import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

RAIZ = Path(__file__).resolve().parent.parent
EVIDENCIA = RAIZ / "evidencia"
CAPTURAS = RAIZ / "dashboard" / "capturas"
ASSETS = RAIZ / "dashboard" / "assets"
SALIDA = Path(__file__).resolve().parent / "Presentacion_EP3_Ferrandes.pptx"

AZUL = RGBColor(0x1F, 0x4E, 0x79)
CELESTE = RGBColor(0x2E, 0x86, 0xDE)
BLANCO = RGBColor(0xFF, 0xFF, 0xFF)
GRIS = RGBColor(0x45, 0x55, 0x65)
NARANJA = RGBColor(0xE6, 0x7E, 0x22)
VERDE = RGBColor(0x1E, 0x84, 0x49)
ROJO = RGBColor(0xC0, 0x39, 0x2B)


def cargar(nombre: str) -> dict:
    return json.loads((EVIDENCIA / nombre).read_text(encoding="utf-8"))


def nueva() -> Presentation:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def fondo(prs, titulo: str, notas: str = ""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    banda = slide.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(0.92))
    banda.fill.solid()
    banda.fill.fore_color.rgb = AZUL
    banda.line.fill.background()
    banda.shadow.inherit = False
    caja = slide.shapes.add_textbox(Inches(0.45), Inches(0.18), Inches(12.4), Inches(0.6))
    p = caja.text_frame.paragraphs[0]
    p.text = titulo
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = BLANCO
    if notas:
        slide.notes_slide.notes_text_frame.text = notas
    return slide


def texto(slide, items, left=0.6, top=1.2, width=12.1, height=5.6,
          tam=16, color=GRIS, salto=8):
    caja = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = caja.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item
        p.font.size = Pt(tam)
        p.font.color.rgb = color
        p.space_after = Pt(salto)
    return caja


def tabla(slide, cabeceras, filas, left=0.6, top=1.25, width=12.1, height=4.9,
          tam=12, anchos=None):
    shape = slide.shapes.add_table(len(filas) + 1, len(cabeceras), Inches(left), Inches(top),
                                   Inches(width), Inches(height))
    tab = shape.table
    if anchos:
        for i, ancho in enumerate(anchos):
            tab.columns[i].width = Inches(ancho)
    for i, cabecera in enumerate(cabeceras):
        celda = tab.cell(0, i)
        celda.text = cabecera
        celda.fill.solid()
        celda.fill.fore_color.rgb = AZUL
        for p in celda.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(tam)
                r.font.bold = True
                r.font.color.rgb = BLANCO
    for fila_i, fila in enumerate(filas, start=1):
        for col_i, valor in enumerate(fila):
            celda = tab.cell(fila_i, col_i)
            celda.text = str(valor)
            celda.fill.solid()
            celda.fill.fore_color.rgb = RGBColor(0xF2, 0xF6, 0xFA) if fila_i % 2 else BLANCO
            for p in celda.text_frame.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(tam)
                    r.font.color.rgb = GRIS
    return tab


def imagen(slide, ruta: Path, left=0.7, top=1.15, ancho=11.9):
    if ruta.exists():
        slide.shapes.add_picture(str(ruta), Inches(left), Inches(top), width=Inches(ancho))


def portada(prs, m: dict):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    franja = slide.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
    franja.fill.solid()
    franja.fill.fore_color.rgb = AZUL
    franja.line.fill.background()
    franja.shadow.inherit = False
    caja = slide.shapes.add_textbox(Inches(0.9), Inches(1.5), Inches(11.6), Inches(4.6))
    tf = caja.text_frame
    tf.word_wrap = True
    datos = [
        (54, True, BLANCO, "Agente Ferrandes: Observabilidad EP3"),
        (22, False, CELESTE, "Métricas, trazabilidad, dashboard y uso responsable"),
        (17, False, BLANCO, "Ferretería Industrial Andes SpA · ISY0101 · Ingeniería de Soluciones con IA"),
        (16, False, CELESTE, f"Evidencia: {m['n_ejecuciones']} ejecuciones · "
                             f"precisión {m['precision_media']:.0%} · p95 {m['latencia_p95_ms']} ms"),
        (15, False, BLANCO, "Integrantes: Leandro Marin (A) · ⬅ completar (B)  |  Docente: Juan Burgueño  |  Semana 17"),
    ]
    for i, (tam, negrita, color, valor) in enumerate(datos):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = valor
        p.font.size = Pt(tam)
        p.font.bold = negrita
        p.font.color.rgb = color
        p.space_after = Pt(14)
    slide.notes_slide.notes_text_frame.text = (
        "0:00-0:40 · Integrante A. Presentación del equipo y continuidad con la EP2."
    )


def main() -> None:
    m = cargar("metricas.json")
    a = cargar("analisis_trazas.json")
    seg = cargar("verificacion_seguridad.json")
    detalle = cargar("mediciones_detalle.json")
    prs = nueva()

    portada(prs, m)

    s = fondo(prs, "De la EP2 a la EP3: qué cambia",
              "0:40-1:40 · Integrante A. La EP2 construyó el agente; la EP3 lo mide y lo hace confiable.")
    texto(s, [
        "EP2: agente funcional con 13 herramientas, memoria, planificación y LangChain.",
        "EP3: instrumentación para medir y mejorar ese mismo agente en producción.",
        "Variabilidad de datos: stock crítico, producto inexistente, ítem inválido, monto alto, PII y normativa.",
        f"Guardrails corregidos: falsos negativos de catálogo {a['falsos_negativos_historicos']} → "
        f"{a['falsos_negativos_ep3']}; ítems inválidos ahora se replanifican.",
        "Entrega: informe ≤5 páginas + repositorio + dashboard + esta presentación (20 min: 10 + 10).",
    ], tam=17)

    s = fondo(prs, "Lo que exige la pauta EP3",
              "1:40-2:30 · Integrante B. Relacionar cada IE con la evidencia del repositorio.")
    tabla(s, ["Indicador", "Evidencia en el proyecto", "Pond."], [
        ["IE1 / IE2 · observabilidad (IL3.1)", f"{len(detalle)} escenarios, 5 métricas, spans", "25%"],
        ["IE3 · trazabilidad (IL3.2)", f"{a['n_trazas_ep3']} trazas + {a['n_logs_historicos']} logs EP2", "15%"],
        ["IE4 / IE5 · dashboard e informe", "Streamlit + capturas + informe 2 páginas", "20%"],
        ["IE6 / IE7 · presentación (IL3.4)", "hallazgos y recomendaciones con datos", "20%"],
        ["IE8 / IE9 · ética y comunicación", "redacción PII, consentimiento, APA, defensa", "20%"],
    ], tam=13, anchos=[4.6, 6.3, 1.2])

    s = fondo(prs, "Arquitectura de observabilidad",
              "2:30-3:20 · Integrante B. El pipeline convierte ejecuciones en decisiones.")
    imagen(s, ASSETS / "diagrama_observabilidad.png", 2.0, 1.35, 9.3)
    texto(s, [
        "Instrumentación → trazas redactadas → métricas → dashboard → análisis → recomendaciones.",
        "Cada ejecución: trace_id + spans (clasificación, RAG, ejecución, registro) + estado.",
    ], 0.8, 6.2, 12, 1.0, tam=12, color=NARANJA, salto=2)

    s = fondo(prs, "Métricas implementadas (IE1, IE2)",
              "3:20-4:20 · Integrante A. Definir cada métrica antes de mostrar resultados.")
    tabla(s, ["Métrica", "Definición operativa", "Resultado"], [
        ["Precisión", "0,4 intención + 0,4 Jaccard(tools) + 0,2 keyword", f"{m['precision_media']:.0%}"],
        ["Latencia", "milisegundos de pared; p50 / p95 / máx",
         f"{m['latencia_p50_ms']} / {m['latencia_p95_ms']} / {m['latencia_max_ms']} ms"],
        ["Consistencia", "respuesta modal tras normalizar IDs dinámicos",
         f"{m['consistencia_media']:.0%} (mín. {m['consistencia_min']:.0%})"],
        ["Tasa de errores", "errores inesperados / escenarios",
         f"{m['tasa_error_inesperado']:.0%} ({m['errores_inesperados']})"],
        ["Recursos", "RSS máxima y CPU media", f"{m['rss_max_mb']} MB / {m['cpu_promedio_pct']}%"],
    ], tam=13, anchos=[2.6, 6.5, 3.0])

    s = fondo(prs, "Dashboard de monitoreo (IE4)",
              "4:20-5:10 · Integrante A. Mostrar la misma fuente de datos de la app Streamlit.")
    imagen(s, CAPTURAS / "01_dashboard_general.png", 0.55, 1.1, 12.2)
    texto(s, ["streamlit run dashboard/app.py  ·  réplica estática: dashboard/dashboard.html"],
          0.7, 6.65, 12, 0.5, tam=11, color=NARANJA, salto=0)

    s = fondo(prs, "Análisis crítico de ejecución (IE6)",
              "5:10-6:00 · Integrante B. Explicar patrones y justificar correcciones.")
    imagen(s, CAPTURAS / "04_hallazgos_trazas.png", 0.5, 1.1, 8.1)
    texto(s, [
        f"P01 · falsos negativos de catálogo: {a['falsos_negativos_historicos']} en EP2 → "
        f"{a['falsos_negativos_ep3']} en EP3.",
        "P03 · ítems inválidos: 3 replanificaciones verificadas.",
        "P05 · 3 consultas normativas derivadas a especialista.",
        "P08 · 0 trazas sin trace_id o sin spans.",
        f"p95 {m['latencia_p95_ms']} ms < umbral {m['umbral_latencia_ms']} ms.",
    ], 8.9, 1.35, 3.9, 5.3, tam=13, color=NARANJA, salto=9)

    s = fondo(prs, "Correcciones realizadas: antes / después",
              "6:00-6:40 · Integrante B. Cada corrección tiene evidencia de regresión.")
    tabla(s, ["Problema observado", "Acción en EP3", "Verificación"], [
        ["HER-001 / ELE-001 respondidos como 'no existe'",
         "Extracción genérica [A-Z]{3}-\\d{3} + validación", "2 → 0 falsos negativos"],
        ["Ítems desconocidos ignorados", "Llegan al planificador y se descartan", "3 replanificaciones"],
        ["Colisión 'producto' vs. 'devolver'", "Prioridad de intenciones específicas", "S11 precisión 100%"],
        ["Logs sin unidades temporales", "trace_id + spans + estado", "45/45 trazas completas"],
        ["Consultas con RUT/email", "redactar() antes de persistir", "0 PII en trazas"],
    ], tam=12, anchos=[4.6, 4.5, 3.0])

    s = fondo(prs, "Defensa de criterios éticos (IE8)",
              "6:40-7:30 · Integrante A. Normativa, controles y límites.")
    tabla(s, ["Control", "Implementación", "Evidencia"], [
        ["Minimización", "RUT, email, teléfono, tarjeta e IP redactados", "0 PII"],
        ["Consentimiento", "Registro por cliente y finalidad",
         f"{seg['consentimiento_cubierto']}/{seg['registros_con_cliente']}"],
        ["Auditoría", "Cada escritura sensible queda registrada", "activa"],
        ["Uso responsable", "Derivación normativa; sin inventiva legal", "3 tickets"],
        ["Marco", "Ley 19.628, Ley 21.719, NIST AI RMF, OWASP LLM", "APA en informe"],
    ], tam=13, anchos=[3.0, 6.0, 3.1])
    texto(s, ["Límite declarado: agente local determinista; con LLM real la latencia y la variabilidad aumentan."],
          0.7, 6.35, 12, 0.6, tam=12, color=ROJO, salto=0)

    s = fondo(prs, "Propuesta de mejora y escalabilidad (IE7)",
              "7:30-8:20 · Integrante B. Todas las mejoras salen del dashboard.")
    texto(s, [
        f"1. Caché del índice y paralelismo: p95 {m['latencia_p95_ms']} ms vs. p50 "
        f"{m['latencia_p50_ms']} ms en flujos de pedido.",
        "2. Alertas por variabilidad: p95 y tasa de error por intención en el dashboard.",
        "3. Escalabilidad: PostgreSQL + embeddings/vector store sin cambiar la interfaz de herramientas.",
        "4. Gobernanza: revisión de consentimientos, rotación de claves y purga de trazas.",
        "5. Sostenibilidad: mismas herramientas probadas en 45 ejecuciones y 45 tests unitarios.",
    ], tam=17, salto=14)

    s = fondo(prs, "Evidencia y resultados",
              "8:20-8:55 · Ambos. Cifras verificables en evidencia/.")
    texto(s, [
        f"{m['n_ejecuciones']} ejecuciones · {m['n_escenarios']} escenarios · 3 repeticiones cada uno.",
        f"Precisión media {m['precision_media']:.0%} · consistencia {m['consistencia_media']:.0%} · "
        f"0 errores inesperados.",
        f"45 pruebas unitarias OK (python tests/ejecutar_tests.py).",
        f"{a['n_logs_historicos']} logs históricos EP2 analizados; informe técnico de 2 páginas.",
        "Repositorio: código + README + diagramas + evidencia + dashboard + esta defensa.",
    ], tam=17, salto=14)

    s = fondo(prs, "Comunicación especializada: defensa con datos (IE9)",
              "9:00-9:40 · Integrante B. Responder con evidencia, no con opinión.")
    tabla(s, ["Pregunta", "Respuesta respaldada"], [
        ["¿Cómo se mide la precisión?", "Fórmula ponderada; 15 escenarios etiquetados; 100% observado."],
        ["¿Por qué p95 y no la media?", "p95 captura la variabilidad de pedidos con reposición."],
        ["¿Los IDs dinámicos no rompen la consistencia?", "Se normalizan antes de comparar; 100% tras normalizar."],
        ["¿Qué pasa con datos personales?", "Redacción + consentimiento + auditoría; 0 PII en trazas."],
        ["¿Es escalable?", "Herramientas desacopladas; ruta PostgreSQL + vector store."],
    ], tam=12, anchos=[4.8, 7.3])

    s = fondo(prs, "Cierre y responsabilidades",
              "9:40-10:00 · Ambos. Cerrar y anunciar preguntas.")
    texto(s, [
        "La EP3 convierte un agente funcional en un sistema observable, seguro y defendible con datos.",
        "⬅ REDACTAR SIN IA — reflexión individual del Integrante A (aprendizaje y aporte).",
        "⬅ REDACTAR SIN IA — reflexión individual del Integrante B (aprendizaje y aporte).",
        "Pendiente para la entrega: completar nombres de integrantes y ensayar la defensa con cronómetro.",
        "¡Gracias! Preguntas →",
    ], tam=17, salto=16)

    prs.save(SALIDA)
    print("📊 Presentación generada:", SALIDA, f"({len(prs.slides)} diapositivas)")


if __name__ == "__main__":
    main()
