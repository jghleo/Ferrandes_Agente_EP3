"""Analisis de registros de ejecucion y deteccion de anomalias (IL3.2 / IE3, IE6).

`analizar_trazas()` cruza las trazas instrumentadas de la EP3 con:
- los logs historicos de la EP2 (para demonstrar correcciones),
- el resumen de metricas (para vincular hallazgos con datos observados),
- el catalogo de productos (para distinguir errores reales de respuestas correctas).
"""
from __future__ import annotations

import re
import statistics
from collections import Counter
from typing import Iterable

from .metricas import _percentil

CODIGO = re.compile(r"\b(?:TOR|HER|EPP|ELE|FIJ|SOL)-\d{3}\b", re.IGNORECASE)


def _respuestas(log: dict) -> str:
    return str(log.get("respuesta", ""))


def _es_falso_negativo(respuesta: str, ids_catalogo: set[str]) -> bool:
    """El agente dice 'no existe' pero el codigo mencionado si existe (o es su prefijo)."""
    if "no existe el producto" not in respuesta.lower():
        return False
    mencion = re.search(r"no existe el producto\s+([^\s.]+)", respuesta, re.IGNORECASE)
    if not mencion:
        return False
    codigo = mencion.group(1).upper().rstrip(".")
    if codigo in ids_catalogo:
        return True
    return any(pid.upper().startswith(codigo + "-") for pid in ids_catalogo)


def _patron(hallazgo_id: str, titulo: str, severidad: str, cantidad: int,
            ejemplo: str, causa: str, correccion: str, estado: str, ie: str) -> dict:
    return {
        "id": hallazgo_id,
        "titulo": titulo,
        "severidad": severidad,
        "cantidad": cantidad,
        "ejemplo": ejemplo[:220],
        "causa_raiz": causa,
        "correccion": correccion,
        "estado": estado,
        "indicador": ie,
    }


def analizar_trazas(trazas: Iterable[dict], metricas: dict | None = None,
                    historico: Iterable[dict] | None = None,
                    ids_catalogo: set[str] | None = None) -> dict:
    trazas = list(trazas)
    historico = list(historico or [])
    ids_catalogo = set(ids_catalogo or [])
    metricas = metricas or {}

    duraciones = [float(t.get("duracion_ms", 0)) for t in trazas]
    p95 = _percentil(duraciones, 0.95)
    umbral = float(metricas.get("umbral_latencia_ms", 50.0))
    hallazgos: list[dict] = []

    # --- 1. Falsos negativos historicos vs. EP3 -----------------------------
    falsos_historicos = [h for h in historico if _es_falso_negativo(_respuestas(h), ids_catalogo)]
    falsos_ep3 = [t for t in trazas if _es_falso_negativo(_respuestas(t), ids_catalogo)]
    if falsos_historicos or falsos_ep3:
        hallazgos.append(_patron(
            "P01", "Falso negativo por codigo de producto incompleto", "alta",
            len(falsos_historicos) + len(falsos_ep3),
            falsos_historicos[0].get("consulta", "") if falsos_historicos else (falsos_ep3[0].get("consulta", "") if falsos_ep3 else ""),
            "La version preliminar extraia el prefijo del codigo (HER, ELE) en lugar del ID completo.",
            "Regex de extraccion con sufijo -\\d{3} en extraer_producto() y validacion contra el catalogo antes de responder; "
            "se anade caso de prueba de regresion.",
            "corregido" if not falsos_ep3 else "abierto", "IE3 / IE6",
        ))

    # --- 2. Errores legitimos por dato inexistente --------------------------
    no_existe = [t for t in trazas if "no existe" in _respuestas(t).lower()]
    if no_existe:
        hallazgos.append(_patron(
            "P02", "Dato inexistente correctamente informado", "informativa", len(no_existe),
            no_existe[0].get("consulta", ""),
            "El usuario consulta referencias fuera del catalogo (variabilidad de datos).",
            "Mantener el mensaje explicito y registrar error_esperado=True para no penalizar la precision.",
            "monitoreado", "IE1 / IE3",
        ))

    # --- 3. Replanificacion -------------------------------------------------
    replan = [t for t in trazas if (
        any("REPLANIF" in str(p.get("etapa", "")).upper() for p in t.get("pasos", []))
        or "REPLANIFICACION" in _respuestas(t).upper()
    )]
    if replan:
        hallazgos.append(_patron(
            "P03", "Replanificacion ante items invalidos", "media", len(replan),
            replan[0].get("consulta", ""),
            "Entrada con referencias inexistentes en una solicitud multi-item.",
            "El planificador descarta items invalidos, informa el motivo y continua con los validos.",
            "corregido", "IE6 / IE7",
        ))

    # --- 4. Escalamiento por credito ---------------------------------------
    escalados = [t for t in trazas if "EN_APROBACION" in _respuestas(t).upper()]
    if escalados:
        hallazgos.append(_patron(
            "P04", "Pedido retenido por politica de credito", "media", len(escalados),
            escalados[0].get("consulta", ""),
            "Monto sobre umbral o cupo insuficiente.",
            "Bloqueo EN_APROBACION + ticket al vendedor; no se confirma pedido sin autorizacion.",
            "monitoreado", "IE3 / IE8",
        ))

    # --- 5. Guardrail normativo --------------------------------------------
    normativos = [t for t in trazas if any("DERIVACION_NORMATIVA" in str(p.get("etapa", "")).upper()
                                          for p in t.get("pasos", []))]
    if normativos:
        hallazgos.append(_patron(
            "P05", "Derivacion de consulta normativa a especialista", "media", len(normativos),
            normativos[0].get("consulta", ""),
            "Riesgo de inventar criterio legal/tecnico sobre EPP y seguridad laboral.",
            "Guardrail: derivar a especialista via ticket y responder solo con informacion verificable.",
            "corregido", "IE8",
        ))

    # --- 6. Latencia atipica ------------------------------------------------
    lentos = [t for t in trazas if float(t.get("duracion_ms", 0)) > umbral]
    hallazgos.append(_patron(
        "P06", "Latencia por encima del umbral de alerta", "alta" if lentos else "informativa",
        len(lentos), lentos[0].get("consulta", "") if lentos else "Sin ejecuciones sobre el umbral.",
        f"p95 observado = {p95} ms; umbral = {umbral} ms.",
        "Ruta de escalabilidad: cache de recuperacion y ejecucion concurrente de herramientas independientes.",
        "abierto" if lentos else "monitoreado", "IE2 / IE7",
    ))

    # --- 7. Consistencia ----------------------------------------------------
    consistencia_min = float(metricas.get("consistencia_min", 1.0))
    bajos = [t for t in trazas if float(t.get("consistencia", 1.0)) < 0.9]
    hallazgos.append(_patron(
        "P07", "Respuestas no consistentes entre repeticiones", "alta" if consistencia_min < 0.9 else "informativa",
        len(bajos), bajos[0].get("consulta", "") if bajos else "Sin divergencias tras normalizar IDs dinamicos.",
        f"Consistencia minima = {consistencia_min:.2f}.",
        "Normalizar IDs secuenciales antes de comparar; fijar semilla del generador en pruebas.",
        "abierto" if consistencia_min < 0.9 else "corregido", "IE1 / IE3",
    ))

    # --- 8. Trazabilidad incompleta -----------------------------------------
    sin_trace = [t for t in trazas if not t.get("trace_id")
                 or not (t.get("spans") or t.get("spans_ms"))]
    hallazgos.append(_patron(
        "P08", "Trazas sin identificador o sin spans", "alta" if sin_trace else "informativa",
        len(sin_trace), "Sin trazas incompletas." if not sin_trace else str(sin_trace[0].get("trace_id")),
        "Version EP2 registraba solo intencion y respuesta, sin unidades de trabajo temporales.",
        "Cada ejecucion emite trace_id, spans (clasificacion, RAG, ejecucion, log) y estado del resultado.",
        "corregido" if not sin_trace else "abierto", "IE3 / IE6",
    ))

    # --- 9. Sin herramientas con intencion detectada ------------------------
    sin_tools = [t for t in trazas if t.get("intencion") and not t.get("herramientas_usadas")]
    if sin_tools:
        hallazgos.append(_patron(
            "P09", "Intencion detectada sin invocacion de herramienta", "media", len(sin_tools),
            sin_tools[0].get("consulta", ""),
            "La clasificacion no logra extraer parametros y responde con una pregunta de aclaracion.",
            "Anadir validacion temprana de parametros y mensaje guiado (ya cubierto por la politica local).",
            "monitoreado", "IE3",
        ))

    con_pii = [t for t in trazas if t.get("pii_detectada")]
    if con_pii:
        hallazgos.append(_patron(
            "P10", "PII redactada antes de persistir la traza", "media", len(con_pii),
            con_pii[0].get("consulta", ""),
            "Algunas consultas de prueba incluyen RUT/email explicitos.",
            "redactar() sustituye PII por etiquetas; verificar_trazas() confirma 0 PII en el archivo.",
            "corregido", "IE8",
        ))

    conteo_intenciones = Counter(t.get("intencion") or "sin_intencion" for t in trazas)
    conteo_errores = Counter(h["id"] for h in hallazgos if h["severidad"] == "alta")

    return {
        "generado": metricas.get("generado"),
        "n_trazas_ep3": len(trazas),
        "n_logs_historicos": len(historico),
        "latencia_p95_ms": p95,
        "umbral_latencia_ms": umbral,
        "falsos_negativos_historicos": len(falsos_historicos),
        "falsos_negativos_ep3": len(falsos_ep3),
        "distribucion_intenciones": dict(conteo_intenciones),
        "hallazgos": hallazgos,
        "puntos_criticos": [h for h in hallazgos if h["severidad"] == "alta"],
        "resumen": (f"Se analizaron {len(trazas)} trazas EP3 y {len(historico)} registros historicos. "
                    f"Hallazgos criticos: {sum(conteo_errores.values())}. "
                    f"Falsos negativos de catalogo: {len(falsos_historicos)} en EP2 -> "
                    f"{len(falsos_ep3)} en EP3."),
    }
