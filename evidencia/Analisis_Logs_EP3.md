# Analisis de registros de ejecucion — EP3 Agente Ferrandes

Generado: 2026-11-24T21:31:06

## 1. Alcance del analisis

- 45 ejecuciones instrumentadas (15 escenarios x 3 repeticiones) sobre el agente real.
- 166 registros historicos de la EP2 examinados para detectar recurrencias.
- Umbral de latencia: 50.0 ms. p95 observado: 27.669 ms.

## 2. Metricas globales

| Metrica | Valor |
| :-- | --: |
| Precision media | 100% |
| Latencia p50 / p95 / max | 2.644 / 27.669 / 28.154 ms |
| Consistencia media (min) | 100% (100%) |
| Errores inesperados | 0 |
| Errores esperados (datos inexistentes) | 2 |
| RSS max / CPU media | 33.06 MB / 86.85% |

## 3. Patrones y anomalias detectadas

| ID | Hallazgo | Severidad | Ocurrencias | Estado | IE |
| :-- | :-- | :-- | --: | :-- | :-- |
| P01 | Falso negativo por codigo de producto incompleto | alta | 2 | corregido | IE3 / IE6 |
| P02 | Dato inexistente correctamente informado | informativa | 3 | monitoreado | IE1 / IE3 |
| P03 | Replanificacion ante items invalidos | media | 3 | corregido | IE6 / IE7 |
| P04 | Pedido retenido por politica de credito | media | 3 | monitoreado | IE3 / IE8 |
| P05 | Derivacion de consulta normativa a especialista | media | 3 | corregido | IE8 |
| P06 | Latencia por encima del umbral de alerta | informativa | 0 | monitoreado | IE2 / IE7 |
| P07 | Respuestas no consistentes entre repeticiones | informativa | 0 | corregido | IE1 / IE3 |
| P08 | Trazas sin identificador o sin spans | informativa | 0 | corregido | IE3 / IE6 |
| P10 | PII redactada antes de persistir la traza | media | 3 | corregido | IE8 |

## 4. Causa raiz y correcciones

### P01 — Falso negativo por codigo de producto incompleto

- **Evidencia:** 2 ocurrencias. Ejemplo: tienes stock del taladro HER-001?
- **Causa raiz:** La version preliminar extraia el prefijo del codigo (HER, ELE) en lugar del ID completo.
- **Correccion / accion:** Regex de extraccion con sufijo -\d{3} en extraer_producto() y validacion contra el catalogo antes de responder; se anade caso de prueba de regresion.
- **Estado:** corregido · **Indicador:** IE3 / IE6

### P02 — Dato inexistente correctamente informado

- **Evidencia:** 3 ocurrencias. Ejemplo: tienes stock del producto TOR-999?
- **Causa raiz:** El usuario consulta referencias fuera del catalogo (variabilidad de datos).
- **Correccion / accion:** Mantener el mensaje explicito y registrar error_esperado=True para no penalizar la precision.
- **Estado:** monitoreado · **Indicador:** IE1 / IE3

### P03 — Replanificacion ante items invalidos

- **Evidencia:** 3 ocurrencias. Ejemplo: cotizar CL-001 TOR-001:10, XXX-999:5
- **Causa raiz:** Entrada con referencias inexistentes en una solicitud multi-item.
- **Correccion / accion:** El planificador descarta items invalidos, informa el motivo y continua con los validos.
- **Estado:** corregido · **Indicador:** IE6 / IE7

### P04 — Pedido retenido por politica de credito

- **Evidencia:** 3 ocurrencias. Ejemplo: cotizar CL-002 TOR-001:9000
- **Causa raiz:** Monto sobre umbral o cupo insuficiente.
- **Correccion / accion:** Bloqueo EN_APROBACION + ticket al vendedor; no se confirma pedido sin autorizacion.
- **Estado:** monitoreado · **Indicador:** IE3 / IE8

### P05 — Derivacion de consulta normativa a especialista

- **Evidencia:** 3 ocurrencias. Ejemplo: que EPP exige la norma para trabajo en altura?
- **Causa raiz:** Riesgo de inventar criterio legal/tecnico sobre EPP y seguridad laboral.
- **Correccion / accion:** Guardrail: derivar a especialista via ticket y responder solo con informacion verificable.
- **Estado:** corregido · **Indicador:** IE8

### P06 — Latencia por encima del umbral de alerta

- **Evidencia:** 0 ocurrencias. Ejemplo: Sin ejecuciones sobre el umbral.
- **Causa raiz:** p95 observado = 28.147 ms; umbral = 50.0 ms.
- **Correccion / accion:** Ruta de escalabilidad: cache de recuperacion y ejecucion concurrente de herramientas independientes.
- **Estado:** monitoreado · **Indicador:** IE2 / IE7

### P07 — Respuestas no consistentes entre repeticiones

- **Evidencia:** 0 ocurrencias. Ejemplo: Sin divergencias tras normalizar IDs dinamicos.
- **Causa raiz:** Consistencia minima = 1.00.
- **Correccion / accion:** Normalizar IDs secuenciales antes de comparar; fijar semilla del generador en pruebas.
- **Estado:** corregido · **Indicador:** IE1 / IE3

### P08 — Trazas sin identificador o sin spans

- **Evidencia:** 0 ocurrencias. Ejemplo: Sin trazas incompletas.
- **Causa raiz:** Version EP2 registraba solo intencion y respuesta, sin unidades de trabajo temporales.
- **Correccion / accion:** Cada ejecucion emite trace_id, spans (clasificacion, RAG, ejecucion, log) y estado del resultado.
- **Estado:** corregido · **Indicador:** IE3 / IE6

### P10 — PII redactada antes de persistir la traza

- **Evidencia:** 3 ocurrencias. Ejemplo: mi RUT [RUT] y mi mail [EMAIL]; stock de TOR-001
- **Causa raiz:** Algunas consultas de prueba incluyen RUT/email explicitos.
- **Correccion / accion:** redactar() sustituye PII por etiquetas; verificar_trazas() confirma 0 PII en el archivo.
- **Estado:** corregido · **Indicador:** IE8

## 5. Verificacion de seguridad

{
  "registros": 45,
  "pii_detectada": {},
  "registros_con_cliente": 15,
  "consentimiento_cubierto": 15,
  "registros_sin_trace_id": 0,
  "checks": {
    "sin_pii_en_trazas": true,
    "trazabilidad_completa": true,
    "consentimiento_completo": true,
    "auditoria_activa": true
  }
}
