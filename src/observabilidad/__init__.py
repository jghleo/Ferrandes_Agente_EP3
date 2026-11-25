"""Paquete de observabilidad, trazabilidad y seguridad de la EP3.

Expone:
- metricas: precision, latencia, consistencia, errores y recursos.
- trazas: analisis de logs y deteccion de patrones/anomalias.
- seguridad: redaccion de PII, consentimiento, auditoria y verificacion.
"""

from .metricas import Medicion, capturar_recursos, normalizar, resumen
from .seguridad import GuardiaSeguridad, redactar
from .trazas import analizar_trazas

__all__ = [
    "Medicion",
    "capturar_recursos",
    "normalizar",
    "resumen",
    "GuardiaSeguridad",
    "redactar",
    "analizar_trazas",
]
