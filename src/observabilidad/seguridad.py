"""Protocolos de seguridad, privacidad y uso responsable (IL3.3 / IE8).

El modulo implementa controles verificables, no solo declaraciones:

1. Minimizacion de datos: `redactar()` elimina PII antes de escribir trazas.
2. Consentimiento: `GuardiaSeguridad.registrar_consentimiento()` y
   `puede_escribir()` condicionan las acciones con efectos persistentes.
3. Auditoria: ` registrar_evento()` deja constancia de cada escritura sensible.
4. Verificacion: `verificar_trazas()` comprueba que ningun log exponga PII.

Marco normativo citado en el informe (APA): Ley 19.628 (Chile), Ley 21.719
(Chile, 2024), NIST AI RMF 1.0 (2023), OWASP Top 10 for LLM Applications (2025).
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from ..config import RAIZ

EVIDENCIA_DIR = RAIZ / "evidencia"
CONSENTIMIENTOS_PATH = EVIDENCIA_DIR / "consentimientos.json"
AUDITORIA_PATH = EVIDENCIA_DIR / "auditoria_seguridad.jsonl"

PATRONES_PII = [
    ("RUT", re.compile(r"\b\d{1,2}\.?\d{3}\.?\d{3}-?[\dKk]\b")),
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    ("TELEFONO", re.compile(r"(?:\+?56[\s-]?)?9[\s-]?\d{4}[\s-]?\d{4}\b")),
    ("TARJETA", re.compile(r"\b(?:\d[ -]?){13,19}\b")),
    ("IP", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
]

# Motivos por los que se bloquea una escritura sensible.
MOTIVOS_BLOQUEO = {
    "sin_cliente": "No se identifica el cliente responsable de la operacion.",
    "sin_consentimiento": "El cliente no cuenta con consentimiento registrado para tratamiento de datos.",
    "finalidad_no_autorizada": "La finalidad declarada no esta autorizada para este cliente.",
}

FINALIDADES_PERMITIDAS = {"cotizacion_pedidos", "soporte", "auditoria_interna"}


def redactar(texto: str | None) -> str:
    """Sustituye PII por etiquetas, conservando el valor analitico del log."""
    if not texto:
        return ""
    resultado = str(texto)
    for etiqueta, patron in PATRONES_PII:
        resultado = patron.sub(f"[{etiqueta}]", resultado)
    return resultado


def detectar_pii(texto: str | None) -> dict[str, int]:
    """Devuelve el conteo de PII detectada por categoria (sin exponer el valor)."""
    if not texto:
        return {}
    return {etiqueta: len(patron.findall(str(texto))) for etiqueta, patron in PATRONES_PII
            if patron.search(str(texto))}


class GuardiaSeguridad:
    """guardarrail de privacidad para operaciones con efectos persistentes."""

    def __init__(self, ruta: Path | None = None):
        self.ruta = Path(ruta) if ruta else CONSENTIMIENTOS_PATH
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        self.consentimientos: dict[str, dict] = {}
        if self.ruta.exists():
            try:
                self.consentimientos = json.loads(self.ruta.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self.consentimientos = {}

    def registrar_consentimiento(self, cliente_id: str,
                                 finalidades=("cotizacion_pedidos",),
                                 responsable="equipo-ep3") -> dict:
        registro = {
            "cliente_id": cliente_id,
            "finalidades": sorted(set(finalidades) & FINALIDADES_PERMITIDAS),
            "responsable": responsable,
            "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "version_politica": "2026.10-EP3",
        }
        self.consentimientos[cliente_id] = registro
        self.ruta.write_text(
            json.dumps(self.consentimientos, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        self.registrar_evento("CONSENTIMIENTO_REGISTRADO", cliente_id, {"finalidades": registro["finalidades"]})
        return registro

    def puede_escribir(self, cliente_id: str | None, finalidad: str = "cotizacion_pedidos") -> tuple[bool, str]:
        if not cliente_id:
            return False, MOTIVOS_BLOQUEO["sin_cliente"]
        registro = self.consentimientos.get(cliente_id)
        if not registro:
            return False, MOTIVOS_BLOQUEO["sin_consentimiento"]
        if finalidad not in registro["finalidades"]:
            return False, MOTIVOS_BLOQUEO["finalidad_no_autorizada"]
        return True, "autorizado"

    def registrar_evento(self, evento: str, cliente_id: str | None = None,
                         datos: dict | None = None, permitido: bool | None = None) -> dict:
        registro = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "evento": evento,
            "cliente_id": cliente_id or "ANONIMO",
            "permitido": permitido,
            "datos": {k: redactar(str(v)) for k, v in (datos or {}).items()},
        }
        AUDITORIA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with AUDITORIA_PATH.open("a", encoding="utf-8") as archivo:
            archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
        return registro

    def verificar_trazas(self, ruta_trazas: Path) -> dict:
        """Verifica Minimizacion de datos, trazabilidad y consentimiento en logs."""
        ruta = Path(ruta_trazas)
        registros = []
        if ruta.exists():
            for linea in ruta.read_text(encoding="utf-8").splitlines():
                try:
                    registros.append(json.loads(linea))
                except json.JSONDecodeError:
                    continue
        texto = json.dumps(registros, ensure_ascii=False)
        pii = detectar_pii(texto)
        con_id = [r for r in registros if r.get("cliente_id")]
        sin_trace = [r for r in registros if not r.get("trace_id")]
        return {
            "registros": len(registros),
            "pii_detectada": pii,
            "registros_con_cliente": len(con_id),
            "consentimiento_cubierto": sum(1 for r in con_id
                                           if r["cliente_id"] in self.consentimientos),
            "registros_sin_trace_id": len(sin_trace),
            "checks": {
                "sin_pii_en_trazas": not pii,
                "trazabilidad_completa": not sin_trace,
                "consentimiento_completo": all(r["cliente_id"] in self.consentimientos for r in con_id),
                "auditoria_activa": AUDITORIA_PATH.exists(),
            },
        }
