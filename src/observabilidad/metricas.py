"""Metricas de observabilidad de la EP3 (IL3.1 / IE1, IE2).

Operacionalizacion:

==================  ============================================================
Metrica             Definicion operativa
==================  ============================================================
Precision           (0.4 * acierto de intencion + 0.4 * Jaccard de herramientas
                    + 0.2 * presencia de palabra clave esperada en la respuesta)
Latencia            milisegundos de pared del ciclo responder(); se reportan
                    p50, p95 y maximo (el p95 es el umbral de alerta).
Consistencia        frecuencia de la respuesta normalizada modal entre R
                    repeticiones de la misma consulta (-id dinamicos).
Tasa de errores     respuestas erroneas NO esperadas / ejecuciones.
Uso de recursos     RSS del proceso (MB) y CPU [%] durante la ejecucion.
==================  ============================================================

Las mediciones se obtienen ejecutando el agente real, no se estiman.
"""
from __future__ import annotations

import re
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Callable

# Identificadores generados por la base de datos: no deben contar como
# inconsistencia, pero si se registran como ruido de la superficie de respuesta.
DINAMICOS = re.compile(
    r"\b(?:COT|PAT|TKT|OC)-\d{6,8}\b|\bses-[0-9a-f]{8}\b|"
    r"\b\d{4}-\d{2}-\d{2}T[\d:.+-]+\b"
)


def normalizar(texto: str | None) -> str:
    """Normaliza una respuesta para comparar consistencia semantica."""
    if not texto:
        return ""
    resultado = DINAMICOS.sub("<ID>", str(texto))
    resultado = re.sub(r"[\s]+", " ", resultado).lower()
    return resultado.strip()


def jaccard(esperado: set[str], observado: set[str]) -> float:
    if not esperado and not observado:
        return 1.0
    union = esperado | observado
    return len(esperado & observado) / len(union) if union else 0.0


def calcular_precision(intencion_esperada: str | None, intencion_observada: str | None,
                       herramientas_esperadas: set[str], herramientas_observadas: set[str],
                       palabra_clave: str | None, respuesta: str) -> float:
    acierto_intencion = 1.0 if (intencion_esperada or None) == (intencion_observada or None) else 0.0
    coincidencia_tools = jaccard(herramientas_esperadas, herramientas_observadas)
    palabra_clave = (palabra_clave or "").lower()
    acierto_respuesta = 1.0 if (not palabra_clave or palabra_clave in respuesta.lower()) else 0.0
    return round(0.4 * acierto_intencion + 0.4 * coincidencia_tools + 0.2 * acierto_respuesta, 4)


def _leer_proc() -> tuple[float, int]:
    """Devuelve (RSS en MB, jiffies de CPU) del proceso actual."""
    try:
        with open("/proc/self/statm", encoding="ascii") as archivo:
            paginas = int(archivo.read().split()[1])
        rss_mb = paginas * 4096 / (1024 * 1024)
        with open("/proc/self/stat", encoding="ascii") as archivo:
            campos = archivo.read().split()
        jiffies = int(campos[13]) + int(campos[14])
        return round(rss_mb, 3), jiffies
    except (OSError, ValueError, IndexError):
        import resource
        return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 3), 0


def capturar_recursos() -> tuple[float, int]:
    return _leer_proc()


def _hz() -> int:
    try:
        return int(__import__("os").sysconf(__import__("os").SC_CLK_TCK))
    except (AttributeError, OSError, ValueError):
        return 100


@dataclass
class Medicion:
    escenario: str
    consulta: str                      # ya redactada
    variabilidad: str
    intencion_esperada: str | None
    intencion_observada: str | None
    precision: float
    latencia_ms: float
    consistencia: float
    error_inesperado: bool
    error_esperado: bool
    respuesta_normalizada: str
    repeticiones: int
    herramientas_esperadas: list[str]
    herramientas_observadas: list[str]
    rss_inicial_mb: float
    rss_final_mb: float
    cpu_promedio_pct: float
    clasificacion_ms: float
    rag_ms: float
    ejecucion_ms: float
    timestamp: str


def _percentil(valores: list[float], p: float) -> float:
    if not valores:
        return 0.0
    ordenados = sorted(valores)
    if len(ordenados) == 1:
        return round(ordenados[0], 3)
    posicion = (len(ordenados) - 1) * p
    inferior = int(posicion)
    superior = min(inferior + 1, len(ordenados) - 1)
    fraccion = posicion - inferior
    return round(ordenados[inferior] * (1 - fraccion) + ordenados[superior] * fraccion, 3)


def resumen(mediciones: list[Medicion], umbral_latencia_ms: float = 50.0) -> dict:
    """Agrega mediciones globales y por corte (intencion / variabilidad)."""
    if not mediciones:
        return {}
    latencias = [m.latencia_ms for m in mediciones]
    precisiones = [m.precision for m in mediciones]
    consistencias = [m.consistencia for m in mediciones]

    def corte(clave: Callable[[Medicion], str]) -> dict:
        grupos: dict[str, list[Medicion]] = {}
        for m in mediciones:
            grupos.setdefault(clave(m), []).append(m)
        return {
            nombre: {
                "n": len(grupo),
                "precision": round(statistics.mean(m.precision for m in grupo), 4),
                "latencia_p95_ms": _percentil([m.latencia_ms for m in grupo], 0.95),
                "consistencia": round(statistics.mean(m.consistencia for m in grupo), 4),
                "errores_inesperados": sum(m.error_inesperado for m in grupo),
            }
            for nombre, grupo in sorted(grupos.items())
        }

    return {
        "generado": datetime.now().isoformat(timespec="seconds"),
        "umbral_latencia_ms": umbral_latencia_ms,
        "n_escenarios": len(mediciones),
        "n_ejecuciones": sum(m.repeticiones for m in mediciones),
        "precision_media": round(statistics.mean(precisiones), 4),
        "precision_min": round(min(precisiones), 4),
        "latencia_p50_ms": _percentil(latencias, 0.50),
        "latencia_p95_ms": _percentil(latencias, 0.95),
        "latencia_max_ms": round(max(latencias), 3),
        "consistencia_media": round(statistics.mean(consistencias), 4),
        "consistencia_min": round(min(consistencias), 4),
        "tasa_error_inesperado": round(sum(m.error_inesperado for m in mediciones) / len(mediciones), 4),
        "errores_inesperados": sum(m.error_inesperado for m in mediciones),
        "errores_esperados": sum(m.error_esperado for m in mediciones),
        "rss_max_mb": round(max(m.rss_final_mb for m in mediciones), 2),
        "cpu_promedio_pct": round(statistics.mean(m.cpu_promedio_pct for m in mediciones), 2),
        "ejecuciones_sobre_umbral": sum(1 for m in mediciones if m.latencia_ms > umbral_latencia_ms),
        "por_intencion": corte(lambda m: m.intencion_observada or "sin_intencion"),
        "por_variabilidad": corte(lambda m: m.variabilidad),
    }


def a_dict(medicion: Medicion) -> dict:
    return asdict(medicion)
