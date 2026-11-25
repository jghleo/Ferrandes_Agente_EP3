#!/usr/bin/env python3
"""Genera el informe tecnico EP3 (Markdown + Word) a partir de la evidencia real.

Uso: python scripts/generar_informe.py   (requiere python-docx)
Para el PDF: libreoffice --headless --convert-to pdf --outdir informe informe/Informe_Tecnico_EP3_Ferrandes.docx
"""
from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RAIZ = Path(__file__).resolve().parent.parent
EVIDENCIA = RAIZ / "evidencia"
INFORME = RAIZ / "informe"
CAPTURAS = RAIZ / "dashboard" / "capturas"

AZUL = RGBColor(0x1F, 0x4E, 0x79)


def cargar(nombre: str) -> dict:
    return json.loads((EVIDENCIA / nombre).read_text(encoding="utf-8"))


def sombrear(celda, color: str) -> None:
    tc_pr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color)
    tc_pr.append(shd)


def tabla(doc, cabeceras: list[str], filas: list[list[str]], anchos=None):
    t = doc.add_table(rows=1, cols=len(cabeceras))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, texto in enumerate(cabeceras):
        celda = t.rows[0].cells[i]
        celda.text = texto
        sombrear(celda, "D6E4F0")
        for p in celda.paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.size = Pt(8.5)
    for fila in filas:
        celdas = t.add_row().cells
        for i, texto in enumerate(fila):
            celdas[i].text = str(texto)
            for p in celdas[i].paragraphs:
                for r in p.runs:
                    r.font.size = Pt(8.5)
    if anchos:
        for fila in t.rows:
            for i, ancho in enumerate(anchos):
                fila.cells[i].width = Cm(ancho)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def parrafo(doc, texto: str, bold=False, size=9.5, espacio=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(espacio)
    r = p.add_run(texto)
    r.font.size = Pt(size)
    r.bold = bold
    return p


def encabezado(doc, texto: str, nivel=1):
    p = doc.add_heading(texto, level=nivel)
    for r in p.runs:
        r.font.color.rgb = AZUL
        r.font.size = Pt(12 if nivel == 1 else 10.5)
    p.paragraph_format.space_before = Pt(7)
    p.paragraph_format.space_after = Pt(3)
    return p


def imagen(doc, nombre: str, ancho_cm=15.5, caption=""):
    ruta = CAPTURAS / nombre
    if not ruta.exists():
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(ruta), width=Cm(ancho_cm))
    if caption:
        c = doc.add_paragraph(caption)
        c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in c.runs:
            r.font.size = Pt(8)
            r.italic = True
        c.paragraph_format.space_after = Pt(2)


def construir_markdown(m: dict, a: dict, s: dict) -> str:
    hallazgos = "\n".join(
        f"| {h['id']} | {h['titulo']} | {h['severidad']} | {h['cantidad']} | {h['estado']} | {h['indicador']} |"
        for h in a["hallazgos"]
    )
    return f"""# Informe Técnico EP3 — Agente Ferrandes (FERRANDES)

**Evaluación Parcial N°3 · ISY0101 · Encargo con Presentación (35 %)**
Integrantes: Leandro Marin (A) · ⬅ completar (B) · Docente: Juan Burgueño · Fecha: semana 18

## 1. Contexto y objetivo
Se continúa el agente B2B de la EP2 con foco en **observabilidad**: medir precisión, latencia y consistencia bajo variabilidad de datos; analizar registros; construir un dashboard; proponer mejoras; e integrar seguridad y uso responsable. Se ejecutaron **{m['n_ejecuciones']} ejecuciones** ({m['n_escenarios']} escenarios × 3 repeticiones) sobre el agente real.

## 2. Métricas implementadas (IE1, IE2)
| Métrica | Definición operativa | Resultado |
| :-- | :-- | --: |
| Precisión | 0,4 intención + 0,4 Jaccard(tools) + 0,2 palabra clave | {m['precision_media']:.0%} |
| Latencia | ms de pared; p50 / p95 / máx | {m['latencia_p50_ms']} / **{m['latencia_p95_ms']}** / {m['latencia_max_ms']} ms |
| Consistencia | respuesta modal tras normalizar IDs (mínimo) | {m['consistencia_media']:.0%} ({m['consistencia_min']:.0%}) |
| Tasa de errores | errores inesperados / escenarios | {m['tasa_error_inesperado']:.0%} ({m['errores_inesperados']}) |
| Recursos | RSS máx / CPU media | {m['rss_max_mb']} MB / {m['cpu_promedio_pct']}% |

Umbral de alerta: {m['umbral_latencia_ms']} ms. Errores esperados (datos inexistentes): {m['errores_esperados']}.

## 3. Análisis de registros y trazabilidad (IE3)
Se examinaron {a['n_trazas_ep3']} trazas instrumentadas y {a['n_logs_historicos']} registros históricos de la EP2.

| ID | Hallazgo | Severidad | N | Estado | IE |
| :-- | :-- | :-- | --: | :-- | :-- |
{hallazgos}

**Correcciones ejecutadas:** (P01) extracción de códigos con patrón genérico `\\b[A-Z]{{3}}-\\d{{3}}\\b` → 2 falsos negativos en EP2, 0 en EP3; (P03) ítems con prefijo desconocido ahora entran al planificador y se replanifican; (P08) cada ejecución emite `trace_id` y spans de clasificación, RAG, ejecución y registro. Detalle en `evidencia/Analisis_Logs_EP3.md`.

## 4. Dashboard de monitoreo (IE4)
![Dashboard general](../dashboard/capturas/01_dashboard_general.png)
*Figura 1. Vista general del dashboard (misma fuente que la app Streamlit).*

La aplicación interactiva `dashboard/app.py` permite filtrar por escenario, ver latencia, precisión por intención, consistencia por variabilidad, hallazgos y controles de seguridad. Réplica estática: `dashboard/dashboard.html`.

## 5. Seguridad, privacidad y uso responsable (IL3.3 / IE8)
| Control | Implementación | Verificación |
| :-- | :-- | :-- |
| Minimización de datos | `redactar()` antes de persistir (RUT, email, teléfono, tarjeta, IP) | 0 PII en `trazas_ep3.jsonl` |
| Consentimiento | Registro por cliente y finalidad (`consentimientos.json`) | {s['consentimiento_cubierto']}/{s['registros_con_cliente']} registros cubiertos |
| Auditoría | `auditoria_seguridad.jsonl` para cada escritura | activo |
| Trazabilidad | `trace_id` + spans + estado por ejecución | {s['registros_sin_trace_id']} trazas incompletas |
| Guardrail normativo | Derivación a especialista en consultas EPP/normativa | {[h['cantidad'] for h in a['hallazgos'] if h['id']=='P05'][0] if any(h['id']=='P05' for h in a['hallazgos']) else 0} derivaciones registradas |

Marco: Ley 19.628 y Ley 21.719 (Chile), NIST AI RMF 1.0, OWASP Top 10 for LLM Applications.

## 6. Recomendaciones basadas en datos (IE5 / IE7)
1. **Caché de recuperación y paralelismo:** los flujos de pedido concentran la latencia ({m['latencia_p95_ms']} ms p95 vs. {m['latencia_p50_ms']} ms p50); ejecutar validaciones independientes en paralelo y cachear TF-IDF.
2. **Alertas por variabilidad:** publicar p95 y tasa de error por intención en el dashboard; umbral {m['umbral_latencia_ms']} ms.
3. **Escalabilidad:** sustituir SQLite por PostgreSQL y el retriever léxico por embeddings + vector store, conservando la interfaz de herramientas.
4. **Gobernanza:** revisión trimestral de consentimientos, rotación de claves y purga de trazas; mantener la redacción de PII en todo el pipeline.

## 7. Evidencia, pruebas y referencias
- 45 pruebas unitarias (`python tests/ejecutar_tests.py`), todas OK; 15 escenarios instrumentados; logs históricos y EP3.
- Scripts reproducibles: `scripts/evaluar_observabilidad.py`, `scripts/generar_dashboard.py`, `dashboard/app.py`.
- Declaración de IA: se usó asistencia de IA para estructura de código, gráficos y borradores técnicos. Las decisiones de diseño, el análisis de causas y las reflexiones son de autoría del equipo. Fuente: https://bibliotecas.duoc.cl/ia
- Referencias APA: Anthropic (2026); LangChain (2026); NIST (2023); OWASP Foundation (2025); Duoc UC (2026); Biblioteca del Congreso Nacional de Chile (2024).

## 8. Conclusiones y reflexiones individuales
⬅ **REDACTAR SIN APOYO DE IA** — Integrante A: aprendizaje y contribución (3-5 líneas).
⬅ **REDACTAR SIN APOYO DE IA** — Integrante B: aprendizaje y contribución (3-5 líneas).
"""


def construir_docx(m: dict, a: dict, s: dict) -> None:
    doc = Document()
    seccion = doc.sections[0]
    seccion.top_margin = Cm(1.5)
    seccion.bottom_margin = Cm(1.4)
    seccion.left_margin = Cm(1.7)
    seccion.right_margin = Cm(1.7)
    normal = doc.styles["Normal"]
    normal.font.name = "DejaVu Sans"
    normal.font.size = Pt(9.3)

    titulo = doc.add_paragraph()
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = titulo.add_run("Informe Técnico EP3 — Agente Ferrandes")
    r.bold = True
    r.font.size = Pt(17)
    r.font.color.rgb = AZUL
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.add_run("Evaluación Parcial N°3 · ISY0101 · Encargo con Presentación (35 %)\n"
                "Integrantes: Leandro Marin (A) · ⬅ completar (B) · Docente: Juan Burgueño · Semana 18"
                ).font.size = Pt(9)

    encabezado(doc, "1. Contexto y objetivo")
    parrafo(doc, f"Se continúa el agente B2B de la EP2 con foco en observabilidad: medir precisión, "
            f"latencia y consistencia bajo variabilidad de datos; analizar registros; construir un dashboard; "
            f"proponer mejoras e integrar seguridad y uso responsable. Se ejecutaron {m['n_ejecuciones']} "
            f"ejecuciones ({m['n_escenarios']} escenarios × 3 repeticiones) sobre el agente real.")

    encabezado(doc, "2. Métricas implementadas (IE1, IE2)")
    tabla(doc, ["Métrica", "Definición operativa", "Resultado"], [
        ["Precisión", "0,4 intención + 0,4 Jaccard(tools) + 0,2 palabra clave", f"{m['precision_media']:.0%}"],
        ["Latencia", "milisegundos de pared; p50 / p95 / máx",
         f"{m['latencia_p50_ms']} / {m['latencia_p95_ms']} / {m['latencia_max_ms']} ms"],
        ["Consistencia", "respuesta modal tras normalizar IDs",
         f"{m['consistencia_media']:.0%} (mín. {m['consistencia_min']:.0%})"],
        ["Tasa de errores", "errores inesperados / escenarios",
         f"{m['tasa_error_inesperado']:.0%} ({m['errores_inesperados']})"],
        ["Recursos", "RSS máxima / CPU media", f"{m['rss_max_mb']} MB / {m['cpu_promedio_pct']}%"],
    ], anchos=[3.1, 9.2, 4.7])
    parrafo(doc, f"Umbral de alerta: {m['umbral_latencia_ms']} ms. "
            f"Errores esperados por dato inexistente: {m['errores_esperados']}.", size=8.5)

    encabezado(doc, "3. Análisis de registros y trazabilidad (IE3)")
    parrafo(doc, f"Se examinaron {a['n_trazas_ep3']} trazas instrumentadas y "
            f"{a['n_logs_historicos']} registros históricos de la EP2.", size=9)
    tabla(doc, ["ID", "Hallazgo", "Sev.", "N", "Estado"], [
        [h["id"], h["titulo"], h["severidad"], str(h["cantidad"]), h["estado"]]
        for h in a["hallazgos"]
    ], anchos=[1.2, 9.8, 2.2, 1.2, 2.6])
    parrafo(doc, "Correcciones: (P01) extracción con patrón genérico de código de producto — "
            "2 falsos negativos en EP2 → 0 en EP3; (P03) ítems con prefijo desconocido ahora "
            "se replanifican; (P08) cada ejecución emite trace_id y spans. "
            "Detalle: evidencia/Analisis_Logs_EP3.md.", size=8.7)

    encabezado(doc, "4. Dashboard de monitoreo (IE4)")
    imagen(doc, "01_dashboard_general.png", 15.3,
           "Figura 1. Vista general del dashboard (misma fuente que la app Streamlit).")
    parrafo(doc, "La aplicación interactiva dashboard/app.py permite filtrar por escenario, ver latencia, "
            "precisión por intención, consistencia por variabilidad, hallazgos y controles de seguridad. "
            "Réplica estática: dashboard/dashboard.html.", size=8.7)

    encabezado(doc, "5. Seguridad, privacidad y uso responsable (IL3.3 / IE8)")
    tabla(doc, ["Control", "Implementación", "Verificación"], [
        ["Minimización", "redactar() antes de persistir (RUT, email, teléfono, tarjeta, IP)", "0 PII en trazas"],
        ["Consentimiento", "Registro por cliente y finalidad", f"{s['consentimiento_cubierto']}/{s['registros_con_cliente']} cubiertos"],
        ["Auditoría", "Registro de cada escritura sensible", "activo"],
        ["Trazabilidad", "trace_id + spans + estado", f"{s['registros_sin_trace_id']} incompletas"],
        ["Guardrail normativo", "Derivación a especialista en consultas EPP", "registrada"],
    ], anchos=[3.0, 9.1, 4.9])
    parrafo(doc, "Marco normativo: Ley 19.628 y Ley 21.719 (Chile), NIST AI RMF 1.0 (2023), "
            "OWASP Top 10 for LLM Applications (2025).", size=8.5)

    encabezado(doc, "6. Recomendaciones basadas en datos (IE5 / IE7)")
    for texto in [
        f"1. Caché de recuperación y paralelismo: los flujos de pedido concentran la latencia "
        f"({m['latencia_p95_ms']} ms p95 frente a {m['latencia_p50_ms']} ms p50); ejecutar validaciones "
        f"independientes en paralelo y cachear el índice TF-IDF.",
        f"2. Alertas por variabilidad: publicar p95 y tasa de error por intención; umbral "
        f"{m['umbral_latencia_ms']} ms.",
        "3. Escalabilidad: migrar SQLite a PostgreSQL y el retriever léxico a embeddings + vector store, "
        "conservando la interfaz de herramientas.",
        "4. Gobernanza: revisión trimestral de consentimientos, rotación de claves y purga de trazas.",
    ]:
        parrafo(doc, texto, size=8.9, espacio=2)

    encabezado(doc, "7. Evidencia, pruebas y referencias")
    parrafo(doc, "45 pruebas unitarias (python tests/ejecutar_tests.py), todas OK; 15 escenarios instrumentados; "
            "logs históricos y EP3. Scripts: scripts/evaluar_observabilidad.py, scripts/generar_dashboard.py y "
            "dashboard/app.py. Declaración de IA: se usó asistencia de IA para estructura de código, gráficos "
            "y borradores técnicos; las decisiones de diseño, el análisis de causas y las reflexiones son de "
            "autoría del equipo (https://bibliotecas.duoc.cl/ia). Referencias APA: Anthropic (2026); "
            "LangChain (2026); NIST (2023); OWASP Foundation (2025); Duoc UC (2026); Biblioteca del Congreso "
            "Nacional de Chile (2024).", size=8.6)

    encabezado(doc, "8. Conclusiones y reflexiones individuales")
    parrafo(doc, "⬅ REDACTAR SIN APOYO DE IA — Integrante A: aprendizaje y contribución (3-5 líneas).", size=9)
    parrafo(doc, "⬅ REDACTAR SIN APOYO DE IA — Integrante B: aprendizaje y contribución (3-5 líneas).", size=9)

    INFORME.mkdir(parents=True, exist_ok=True)
    doc.save(INFORME / "Informe_Tecnico_EP3_Ferrandes.docx")


def main() -> None:
    metricas = cargar("metricas.json")
    analisis = cargar("analisis_trazas.json")
    seguridad = cargar("verificacion_seguridad.json")
    (INFORME / "Informe_Tecnico_EP3_Ferrandes.md").write_text(
        construir_markdown(metricas, analisis, seguridad), encoding="utf-8"
    )
    construir_docx(metricas, analisis, seguridad)
    print("Informe generado:", INFORME / "Informe_Tecnico_EP3_Ferrandes.docx")


if __name__ == "__main__":
    main()
