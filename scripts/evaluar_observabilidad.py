#!/usr/bin/env python3
"""Bateria de observabilidad EP3: ejecuta el agente real y genera evidencia.

Salidas (en evidencia/):
- logs_agente_EP2_historico.jsonl  copia de los logs originales (comparacion)
- logs_agente.jsonl                logs del agente durante la bateria
- trazas_ep3.jsonl                 trazas instrumentadas y redactadas
- metricas.json / metricas.csv     mediciones agregadas y por escenario
- analisis_trazas.json             hallazgos del analisis de logs
- Analisis_Logs_EP3.md             informe legible de hallazgos

Uso: python scripts/evaluar_observabilidad.py
"""
from __future__ import annotations

import csv
import json
import os
import shutil
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

# Parcheo de seguridad ANTES de importar el agente: así los modulos que importan
# las herramientas de escritura reciben las versiones auditadas.
from src.herramientas import escritura as escritura_mod  # noqa: E402
from src.observabilidad.seguridad import GuardiaSeguridad, detectar_pii, redactar  # noqa: E402

GUARDIA = GuardiaSeguridad()
for cliente in ("CL-001", "CL-002", "CL-003", "CL-004"):
    GUARDIA.registrar_consentimiento(cliente)


# `servicios` ya se consume como primer parametro del wrapper: el cliente
# queda en args[0] cuando la herramienta lo recibe de forma posicional.
INDICE_CLIENTE = {"crear_cotizacion": 0, "crear_ticket_escalamiento": 0}


def _auditar(nombre: str, original):
    def envuelto(servicios, *args, **kwargs):
        indice = INDICE_CLIENTE.get(nombre)
        cliente = kwargs.get("cliente_id") or (args[indice] if indice is not None and len(args) > indice else None)
        if cliente:
            permitido, motivo = GUARDIA.puede_escribir(str(cliente))
            GUARDIA.registrar_evento(f"ESCRITURA_{nombre.upper()}", str(cliente),
                                     {"motivo": motivo}, permitido)
            if not permitido:
                raise PermissionError(motivo)
        else:
            GUARDIA.registrar_evento(f"ESCRITURA_{nombre.upper()}", None,
                                     {"motivo": "operacion_interna_sin_cliente_directo"}, True)
        return original(servicios, *args, **kwargs)
    envuelto.__name__ = nombre
    envuelto.__doc__ = original.__doc__
    return envuelto


for _nombre in ("crear_cotizacion", "confirmar_pedido", "generar_orden_reposicion",
                "crear_ticket_escalamiento"):
    if hasattr(escritura_mod, _nombre):
        setattr(escritura_mod, _nombre, _auditar(_nombre, getattr(escritura_mod, _nombre)))

import src.agente as agente_mod  # noqa: E402
from src.agente import AgenteFerrandes  # noqa: E402
from src.config import EVIDENCIA_DIR, LOG_PATH  # noqa: E402
from src.datos import cargar_datos  # noqa: E402
from src.observabilidad.metricas import (  # noqa: E402
    Medicion, calcular_precision, capturar_recursos, normalizar, resumen, a_dict,
)
from src.observabilidad.trazas import analizar_trazas  # noqa: E402
from src.servicios import Servicios  # noqa: E402

UMBRAL_LATENCIA_MS = 50.0
REPETICIONES = 3
HZ = os.sysconf(os.sysconf_names["SC_CLK_TCK"])

ESCENARIOS = [
    dict(id="S01", consulta="tienes stock del taladro HER-001?", cliente=None,
         intencion="stock", herramientas={"consultar_stock"}, keyword="her-001",
         variabilidad="regresion", error_esperado=False),
    dict(id="S02", consulta="tienes stock del producto TOR-002?", cliente=None,
         intencion="stock", herramientas={"consultar_stock"}, keyword="bajo",
         variabilidad="stock_critico", error_esperado=False),
    dict(id="S03", consulta="tienes stock del producto TOR-999?", cliente=None,
         intencion="stock", herramientas={"consultar_stock"}, keyword="no existe",
         variabilidad="dato_inexistente", error_esperado=True),
    dict(id="S04", consulta="precio de ELE-001", cliente=None,
         intencion="precio", herramientas={"consultar_precio"}, keyword="ele-001",
         variabilidad="regresion", error_esperado=False),
    dict(id="S05", consulta="precio de ELE-002", cliente=None,
         intencion="precio", herramientas={"consultar_precio"}, keyword="ele-002",
         variabilidad="nominal", error_esperado=False),
    dict(id="S06", consulta="cotizar CL-001 TOR-001:50, EPP-001:20", cliente="CL-001",
         intencion="cotizacion",
         herramientas={"analizar_solicitud", "consultar_stock", "crear_cotizacion",
                       "evaluar_riesgo_credito", "confirmar_pedido"},
         keyword="flujo de pedido", variabilidad="nominal", error_esperado=False),
    dict(id="S07", consulta="cotizar CL-001 TOR-001:10, XXX-999:5", cliente="CL-001",
         intencion="cotizacion",
         herramientas={"analizar_solicitud", "consultar_stock", "crear_cotizacion",
                       "evaluar_riesgo_credito", "confirmar_pedido"},
         keyword="decision replanificacion", variabilidad="dato_invalido", error_esperado=False),
    dict(id="S08", consulta="cotizar CL-002 TOR-001:9000", cliente="CL-002",
         intencion="cotizacion",
         herramientas={"analizar_solicitud", "consultar_stock", "decidir_reposicion",
                       "generar_orden_reposicion", "crear_cotizacion",
                       "evaluar_riesgo_credito", "crear_ticket_escalamiento"},
         keyword="en_aprobacion", variabilidad="monto_alto", error_esperado=False),
    dict(id="S09", consulta="consultar credito de CL-003", cliente="CL-003",
         intencion="credito", herramientas={"evaluar_riesgo_credito"}, keyword="decision",
         variabilidad="cliente_sin_credito", error_esperado=False),
    dict(id="S10", consulta="que EPP exige la norma para trabajo en altura?", cliente=None,
         intencion="normativa", herramientas={"crear_ticket_escalamiento"}, keyword="especialista",
         variabilidad="consulta_normativa", error_esperado=False),
    dict(id="S11", consulta="quiero devolver un producto CL-001", cliente="CL-001",
         intencion="soporte", herramientas={"crear_ticket_escalamiento"}, keyword="ticket",
         variabilidad="soporte", error_esperado=False),
    dict(id="S12", consulta="catalogo de taladros", cliente=None,
         intencion="catalogo", herramientas={"buscar_catalogo"}, keyword="her-001",
         variabilidad="nominal", error_esperado=False),
    dict(id="S13", consulta="estado de mi pedido PAT-000001", cliente=None,
         intencion="estado_pedido", herramientas={"consultar_pedido"}, keyword="pedido",
         variabilidad="dato_inexistente", error_esperado=True),
    dict(id="S14", consulta="hola", cliente=None,
         intencion=None, herramientas=set(), keyword="puedo ayudarte",
         variabilidad="consulta_general", error_esperado=False),
    dict(id="S15", consulta="mi RUT 12.345.678-5 y mi mail juan.perez@example.cl; stock de TOR-001",
         cliente=None, intencion="stock", herramientas={"consultar_stock"}, keyword="tor-001",
         variabilidad="pii_en_consulta", error_esperado=False),
]

SPAN: dict[str, float] = {}


def _redactar_estructura(valor):
    """Aplica minimizacion de datos a listas/diccionarios de la traza."""
    if isinstance(valor, str):
        return redactar(valor)
    if isinstance(valor, list):
        return [_redactar_estructura(v) for v in valor]
    if isinstance(valor, dict):
        return {k: _redactar_estructura(v) for k, v in valor.items()}
    return valor


def _cronometrar(modulo, nombre: str):
    original = getattr(modulo, nombre)

    def envuelto(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = original(*args, **kwargs)
        SPAN[nombre] = round((time.perf_counter() - inicio) * 1000, 4)
        return resultado
    envuelto.__name__ = nombre
    setattr(modulo, nombre, envuelto)


_cronometrar(agente_mod, "clasificar_intencion")
_cronometrar(agente_mod, "recuperar_contexto")


def _preparar_directorios() -> None:
    EVIDENCIA_DIR.mkdir(parents=True, exist_ok=True)
    historico = EVIDENCIA_DIR / "logs_agente_EP2_historico.jsonl"
    if LOG_PATH.exists() and not historico.exists():
        shutil.copy2(LOG_PATH, historico)
    LOG_PATH.write_text("", encoding="utf-8")


def _ejecutar_escenario(escenario: dict) -> tuple[Medicion, list[dict]]:
    consulta = escenario["consulta"]
    trazas: list[dict] = []
    precisiones: list[float] = []
    latencias: list[float] = []
    cpus: list[float] = []
    rss_inicial = 0.0
    rss_final = 0.0
    respuestas_normalizadas: list[str] = []
    herramientas_observadas: set[str] = set()
    intencion_observada = None
    errores = 0
    pii_total: dict[str, int] = {}

    for repeticion in range(REPETICIONES):
        SPAN.clear()
        servicios = Servicios()
        agente = AgenteFerrandes(servicios, sesion_id=f"ses-ep3-{escenario['id'].lower()}-{repeticion}")
        capturado: dict = {}

        def capturar_log(*args):
            nonlocal capturado
            capturado = {
                "consulta": args[0], "intencion": args[1],
                "herramientas_usadas": list(args[2]), "pasos": list(args[4]),
                "fuentes_rag": list(args[3]), "respuesta": args[5],
                "cliente_id": args[6],
            }
        agente._escribir_log = capturar_log

        rss_antes, cpu_inicial = capturar_recursos()
        inicio = time.perf_counter()
        try:
            respuesta = agente.responder(consulta, escenario["cliente"])
            estado = "ok"
        except Exception as exc:  # la excepcion tambien es una observacion
            respuesta = f"ERROR DE EJECUCION: {type(exc).__name__}: {exc}"
            estado = "error"
            errores += 1
        duracion_ms = round((time.perf_counter() - inicio) * 1000, 3)
        rss_despues, cpu_final = capturar_recursos()
        cpu_pct = round(((cpu_final - cpu_inicial) / HZ / max(duracion_ms / 1000, 1e-6)) * 100, 2)
        rss_inicial = rss_inicial or rss_antes
        rss_final = max(rss_final, rss_despues)

        intencion_observada = capturado.get("intencion")
        herramientas_observadas = set(capturado.get("herramientas_usadas", []))
        precisiones.append(calcular_precision(
            escenario["intencion"], intencion_observada,
            escenario["herramientas"], herramientas_observadas,
            escenario["keyword"], respuesta,
        ))
        latencias.append(duracion_ms)
        cpus.append(cpu_pct)
        norm = normalizar(respuesta)
        respuestas_normalizadas.append(norm)

        detectado = any(marca in respuesta.lower() for marca in
                        ("no existe", "no se encontraron", "error", "no registrado"))
        es_error = detectado and not escenario["error_esperado"]
        if es_error:
            errores += 1
        pii = detectar_pii(consulta)
        for clave, valor in pii.items():
            pii_total[clave] = pii_total.get(clave, 0) + valor

        trazas.append({
            "trace_id": f"tr-{escenario['id']}-{repeticion}",
            "sesion_id": f"ses-ep3-{escenario['id'].lower()}-{repeticion}",
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "escenario": escenario["id"],
            "variabilidad": escenario["variabilidad"],
            "intencion": intencion_observada,
            "consulta": redactar(consulta),
            "respuesta": redactar(respuesta),
            "consulta_original_pii": pii,
            "cliente_id": escenario["cliente"],
            "herramientas_usadas": sorted(herramientas_observadas),
            "pasos": _redactar_estructura(capturado.get("pasos", [])),
            "fuentes_rag": _redactar_estructura(capturado.get("fuentes_rag", [])),
            "pii_detectada": bool(pii),
            "estado": ("error_esperado" if (detectado and escenario["error_esperado"])
                       else ("error" if es_error else estado)),
            "duracion_ms": duracion_ms,
            "spans_ms": {
                "clasificacion": SPAN.get("clasificar_intencion", 0.0),
                "rag": SPAN.get("recuperar_contexto", 0.0),
                "ejecucion": round(max(duracion_ms - SPAN.get("clasificar_intencion", 0.0)
                                       - SPAN.get("recuperar_contexto", 0.0), 0.0), 4),
                "registro": 0.0,
            },
            "precision": precisiones[-1],
            "rss_mb": rss_final,
            "cpu_pct": cpu_pct,
        })

    conteo = Counter(respuestas_normalizadas)
    consistencia = round(conteo.most_common(1)[0][1] / REPETICIONES, 4)
    latencias_ordenadas = sorted(latencias)
    latencia_mediana = round(latencias_ordenadas[len(latencias_ordenadas) // 2], 3)

    medicion = Medicion(
        escenario=escenario["id"],
        consulta=redactar(consulta),
        variabilidad=escenario["variabilidad"],
        intencion_esperada=escenario["intencion"],
        intencion_observada=intencion_observada,
        precision=round(sum(precisiones) / len(precisiones), 4),
        latencia_ms=latencia_mediana,
        consistencia=consistencia,
        error_inesperado=errores > 0,
        error_esperado=bool(escenario["error_esperado"]),
        respuesta_normalizada=respuestas_normalizadas[0][:280],
        repeticiones=REPETICIONES,
        herramientas_esperadas=sorted(escenario["herramientas"]),
        herramientas_observadas=sorted(herramientas_observadas),
        rss_inicial_mb=round(rss_inicial, 2),
        rss_final_mb=round(rss_final, 2),
        cpu_promedio_pct=round(sum(cpus) / len(cpus), 2),
        clasificacion_ms=round(sum(t["spans_ms"]["clasificacion"] for t in trazas) / REPETICIONES, 4),
        rag_ms=round(sum(t["spans_ms"]["rag"] for t in trazas) / REPETICIONES, 4),
        ejecucion_ms=round(sum(t["spans_ms"]["ejecucion"] for t in trazas) / REPETICIONES, 4),
        timestamp=datetime.now().isoformat(timespec="seconds"),
    )
    return medicion, trazas


def main() -> None:
    _preparar_directorios()
    mediciones: list[Medicion] = []
    trazas: list[dict] = []
    for escenario in ESCENARIOS:
        medicion, nuevas = _ejecutar_escenario(escenario)
        mediciones.append(medicion)
        trazas.extend(nuevas)
        print(f"{escenario['id']} {escenario['variabilidad']:<20} "
              f"precision={medicion.precision:.2f} latencia={medicion.latencia_ms:>7.3f} ms "
              f"consistencia={medicion.consistencia:.2f}")

    res = resumen(mediciones, UMBRAL_LATENCIA_MS)
    for traza in trazas:
        traza["consistencia"] = next(
            m.consistencia for m in mediciones if m.escenario == traza["escenario"]
        )

    for nombre, datos in (("metricas.json", res), ("analisis_trazas.json", None)):
        if datos is not None:
            (EVIDENCIA_DIR / nombre).write_text(
                json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8"
            )

    (EVIDENCIA_DIR / "mediciones_detalle.json").write_text(
        json.dumps([a_dict(m) for m in mediciones], ensure_ascii=False, indent=2), encoding="utf-8"
    )

    with (EVIDENCIA_DIR / "metricas.csv").open("w", newline="", encoding="utf-8") as archivo:
        campos = list(a_dict(mediciones[0]).keys())
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        for medicion in mediciones:
            escritor.writerow(a_dict(medicion))

    with (EVIDENCIA_DIR / "trazas_ep3.jsonl").open("w", encoding="utf-8") as archivo:
        for traza in trazas:
            archivo.write(json.dumps(traza, ensure_ascii=False) + "\n")

    catalogo_ids = {p["id"] for p in cargar_datos()["productos"]}
    historico_path = EVIDENCIA_DIR / "logs_agente_EP2_historico.jsonl"
    historico = [json.loads(l) for l in historico_path.read_text(encoding="utf-8").splitlines()
                 if l.strip()]
    analisis = analizar_trazas(trazas, res, historico, catalogo_ids)
    (EVIDENCIA_DIR / "analisis_trazas.json").write_text(
        json.dumps(analisis, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    verificacion = GUARDIA.verificar_trazas(EVIDENCIA_DIR / "trazas_ep3.jsonl")
    (EVIDENCIA_DIR / "verificacion_seguridad.json").write_text(
        json.dumps(verificacion, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lineas = [
        "# Analisis de registros de ejecucion — EP3 Agente Ferrandes",
        "",
        f"Generado: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## 1. Alcance del analisis",
        "",
        f"- {res['n_ejecuciones']} ejecuciones instrumentadas ({res['n_escenarios']} escenarios "
        f"x {REPETICIONES} repeticiones) sobre el agente real.",
        f"- {len(historico)} registros historicos de la EP2 examinados para detectar recurrencias.",
        f"- Umbral de latencia: {UMBRAL_LATENCIA_MS} ms. p95 observado: {res['latencia_p95_ms']} ms.",
        "",
        "## 2. Metricas globales",
        "",
        "| Metrica | Valor |",
        "| :-- | --: |",
        f"| Precision media | {res['precision_media']:.0%} |",
        f"| Latencia p50 / p95 / max | {res['latencia_p50_ms']} / {res['latencia_p95_ms']} / {res['latencia_max_ms']} ms |",
        f"| Consistencia media (min) | {res['consistencia_media']:.0%} ({res['consistencia_min']:.0%}) |",
        f"| Errores inesperados | {res['errores_inesperados']} |",
        f"| Errores esperados (datos inexistentes) | {res['errores_esperados']} |",
        f"| RSS max / CPU media | {res['rss_max_mb']} MB / {res['cpu_promedio_pct']}% |",
        "",
        "## 3. Patrones y anomalias detectadas",
        "",
        "| ID | Hallazgo | Severidad | Ocurrencias | Estado | IE |",
        "| :-- | :-- | :-- | --: | :-- | :-- |",
    ]
    for h in analisis["hallazgos"]:
        lineas.append(f"| {h['id']} | {h['titulo']} | {h['severidad']} | {h['cantidad']} "
                      f"| {h['estado']} | {h['indicador']} |")
    lineas += ["", "## 4. Causa raiz y correcciones", ""]
    for h in analisis["hallazgos"]:
        lineas += [
            f"### {h['id']} — {h['titulo']}",
            "",
            f"- **Evidencia:** {h['cantidad']} ocurrencias. Ejemplo: {h['ejemplo']}",
            f"- **Causa raiz:** {h['causa_raiz']}",
            f"- **Correccion / accion:** {h['correccion']}",
            f"- **Estado:** {h['estado']} · **Indicador:** {h['indicador']}",
            "",
        ]
    lineas += [
        "## 5. Verificacion de seguridad",
        "",
        json.dumps(verificacion, ensure_ascii=False, indent=2),
        "",
    ]
    (EVIDENCIA_DIR / "Analisis_Logs_EP3.md").write_text("\n".join(lineas), encoding="utf-8")

    print("\nRESUMEN:", json.dumps({k: res[k] for k in (
        "precision_media", "latencia_p95_ms", "consistencia_media",
        "tasa_error_inesperado", "rss_max_mb", "cpu_promedio_pct")}, ensure_ascii=False))
    print("SEGURIDAD:", json.dumps(verificacion["checks"], ensure_ascii=False))
    print("HALLAZGOS:", json.dumps(
        [{"id": h["id"], "n": h["cantidad"], "estado": h["estado"]}
         for h in analisis["hallazgos"]], ensure_ascii=False))


if __name__ == "__main__":
    main()
