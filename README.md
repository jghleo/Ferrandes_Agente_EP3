# Agente Ferrandes — Observabilidad y defensa (EP3 · ISY0101)

**Repositorio público:** https://github.com/jghleo/Ferrandes_Agente_EP3

**Evaluación Parcial N°3** de *Ingeniería de Soluciones con IA*. Se continúa el agente B2B de la EP2 (Ferretería Industrial Andes SpA, FERRANDES) y se transforma en un **sistema observable, trazable, seguro y defendible con datos**: métricas reales, análisis de logs, dashboard, informe técnico y presentación de 20 minutos.

> Resultado actual: **45 ejecuciones** (15 escenarios × 3 repeticiones) · precisión 100 % · p95 27,669 ms · consistencia 100 % · 0 errores inesperados · 45/45 trazas completas · 0 PII en trazas · 45 pruebas unitarias OK.

---

## 📁 Estructura del repositorio

```text
Ferrandes_Agente_EP3/
├── README.md                       ← este documento
├── requirements.txt                ← dependencias del pipeline EP3 y del agente LangChain
├── src/
│   ├── agente.py, decisiones.py, planificador.py, servicios.py, ...   ← agente EP2
│   ├── herramientas/               ← consulta / escritura / razonamiento
│   ├── memoria/                    ← corto y largo plazo (SQLite)
│   └── observabilidad/             ← NUEVO EP3
│       ├── metricas.py             ← precisión, latencia, consistencia, errores, recursos
│       ├── trazas.py               ← trace_id, spans, análisis de logs
│       └── seguridad.py            ← redacción de PII, consentimiento y auditoría
├── scripts/
│   ├── evaluar_observabilidad.py   ← NUEVO: ejecuta 45 escenarios y genera evidencia
│   ├── generar_dashboard.py        ← NUEVO: gráficos y dashboard.html
│   ├── generar_informe.py          ← NUEVO: informe técnico MD + DOCX
│   ├── generar_evaluacion.py       ← NUEVO: evaluación según pauta MD + DOCX
│   ├── ejecutar_todo.py / .sh      ← pipeline completo
│   ├── demo.py, smoke_langchain.py ← heredados de EP2
├── dashboard/
│   ├── app.py                      ← dashboard interactivo Streamlit
│   ├── dashboard.html              ← réplica estática, autocontenida
│   ├── capturas/                   ← 5 PNG usadas en informe y PPT
│   └── assets/                     ← diagrama de observabilidad (PNG + DOT)
├── evidencia/
│   ├── metricas.json / .csv        ← métricas agregadas
│   ├── mediciones_detalle.json     ← 45 mediciones individuales
│   ├── trazas_ep3.jsonl            ← trazas con spans y PII redactada
│   ├── analisis_trazas.json        ← hallazgos P01–P10
│   ├── verificacion_seguridad.json ← chequeos de privacidad
│   ├── consentimientos.json        ← consentimiento por cliente y finalidad
│   ├── auditoria_seguridad.jsonl   ← escrituras sensibles
│   ├── Analisis_Logs_EP3.md        ← informe de hallazgos
│   ├── logs_agente_EP2_historico.jsonl ← 166 logs previos analizados
│   └── evidencia_*.txt, logs_agente.jsonl ← herencia EP2
├── informe/
│   ├── Informe_Tecnico_EP3_Ferrandes.md / .docx / .pdf   ← 2 páginas (≤ 5)
│   └── Evaluacion_Pauta_EP3_Ferrandes.md / .docx / .pdf  ← nota estimada 6,3
├── presentacion/
│   ├── Guion_Presentacion_EP3.md   ← 10 min exposición + 10 min preguntas
│   ├── Presentacion_EP3_Ferrandes.pptx ← 13 diapositivas con notas
│   └── generar_ppt.py              ← generador del PPT
├── assets/                         ← diagramas de arquitectura y flujo (EP2)
├── tests/                          ← 45 pruebas unitarias (incluye EP3)
├── colab/                          ← notebook heredado de EP2
└── datos_ferrandes.db              ← memoria persistente SQLite
```

---

## 🚀 Instalación

- **Python 3.9+** (probado con 3.14).
- El agente local, los tests y `scripts/evaluar_observabilidad.py` **no requieren dependencias**.
- Para dashboard, informe, PPT y agente LangChain:

```sh
python -m pip install -r requirements.txt
```

Variables opcionales (ver `.env.example`): `ANTHROPIC_API_KEY`, `FERRANDES_MODEL`, `FERRANDES_RETRIEVER_MODE`.

---

## ▶️ Cómo ejecutar

### Pipeline completo

```sh
python scripts/ejecutar_todo.py      # o: bash scripts/ejecutar_todo.sh
```

Ejecuta pruebas, demo, evaluación EP3 y los generadores disponibles. Los pasos con dependencias se omiten si faltan librerías.

### 1) Pruebas unitarias (45)

```sh
python tests/ejecutar_tests.py
```

### 2) Medición real de observabilidad

```sh
python scripts/evaluar_observabilidad.py
```

Genera en `evidencia/`: `metricas.json`, `metricas.csv`, `mediciones_detalle.json`, `trazas_ep3.jsonl`, `analisis_trazas.json`, `verificacion_seguridad.json`, `consentimientos.json` y `auditoria_seguridad.jsonl`.

### 3) Dashboard

```sh
python scripts/generar_dashboard.py      # capturas y dashboard.html
streamlit run dashboard/app.py           # versión interactiva (puerto 8501)
```

El dashboard lee **la misma evidencia** que produce el paso 2; no muestra datos simulados. Si no puedes levantar Streamlit, abre `dashboard/dashboard.html`.

### 4) Informe y evaluación

```sh
python scripts/generar_informe.py
python scripts/generar_evaluacion.py
libreoffice --headless --convert-to pdf --outdir informe informe/Informe_Tecnico_EP3_Ferrandes.docx
libreoffice --headless --convert-to pdf --outdir informe informe/Evaluacion_Pauta_EP3_Ferrandes.docx
```

### 5) Presentación

```sh
python presentacion/generar_ppt.py
```

Abre `presentacion/Presentacion_EP3_Ferrandes.pptx` y sigue `presentacion/Guion_Presentacion_EP3.md` (incluye notas del expositor y 10 preguntas preparadas).

### 6) Agente LangChain (opcional, heredado de EP2)

```sh
python scripts/smoke_langchain.py
```

---

## 📊 Métricas y resultados

| Métrica | Definición operativa | Resultado |
| :-- | :-- | --: |
| Precisión | 0,4 intención + 0,4 Jaccard(tools) + 0,2 palabra clave | 100 % |
| Latencia | ms de pared; p50 / p95 / máx | 2,644 / 27,669 / 28,154 ms |
| Consistencia | respuesta modal tras normalizar IDs dinámicos | 100 % (mín. 100 %) |
| Errores | inesperados / escenarios (esperados separados) | 0 % (2 esperados) |
| Recursos | RSS máxima / CPU media | 33,06 MB / 86,85 % |

Umbral de alerta: 50 ms. Desglose por intención y por variabilidad en `evidencia/metricas.json`.

### Hallazgos de trazabilidad

| ID | Hallazgo | N | Estado |
| :-- | :-- | --: | :-- |
| P01 | Falso negativo por código de producto incompleto (EP2) | 2 → 0 | corregido |
| P03 | Ítems inválidos → replanificación | 3 | corregido |
| P04 | Pedido retenido por política de crédito | 3 | monitorizado |
| P05 | Consulta normativa derivada a especialista | 3 | corregido |
| P08 | Trazas sin `trace_id` o sin spans | 0 | corregido |
| P10 | PII redactada antes de persistir | 3 | corregido |

Detalle completo en `evidencia/Analisis_Logs_EP3.md` y en el informe §3.

---

## 🔒 Seguridad y uso responsable

- **Minimización:** `redactar()` elimina RUT, email, teléfono, tarjeta y IP antes de escribir la traza → 0 PII en `trazas_ep3.jsonl`.
- **Consentimiento:** registro por cliente y finalidad → 15/15 cubiertos.
- **Auditoría:** cada escritura sensible queda en `auditoria_seguridad.jsonl`.
- **Trazabilidad:** `trace_id` + spans + estado en las 45 ejecuciones.
- **Guardrail normativo:** las consultas EPP/normativa se derivan a especialista; sin inventiva legal.
- **Marco:** Ley 19.628 y Ley 21.719 (Chile), NIST AI RMF 1.0, OWASP Top 10 for LLM Applications.

Límite declarado: el agente es local y determinista; con un LLM real aumentarían la latencia y la variabilidad.

---

## 🧪 Evidencia de pruebas y entrega

- 45 pruebas unitarias, todas OK (`python tests/ejecutar_tests.py`).
- Informe técnico: **2 páginas**, Word y PDF, con capturas del dashboard y referencias APA.
- Evaluación según pauta: nota estimada **6,3 / 7,0** (logro 0,88), con desglose IE1–IE9.
- Presentación: **13 diapositivas** con notas, guion de 20 minutos y apoyo visual del dashboard.

> ⬅ **Pendiente antes de la entrega:** nombre del integrante B y las dos reflexiones individuales, que deben redactarse **sin apoyo de IA**.

---

## 🤖 Declaración de uso de IA

Se usó asistencia de IA como apoyo para estructurar código, generar gráficos y preparar borradores técnicos. Las decisiones de diseño, el análisis de causas, las justificaciones y las reflexiones individuales son de autoría del equipo. Todo uso de IA debe citarse según [bibliotecas.duoc.cl/ia](https://bibliotecas.duoc.cl/ia).

---

## 👥 Integrantes y docente

| Rol | Nombre |
| :-- | :-- |
| Integrante A | Leandro Marin |
| Integrante B | ⬅ completar |
| Docente | Juan Burgueño |
| Asignatura | ISY0101 · Ingeniería de Soluciones con IA |
| Evaluación | EP3 · Encargo (60 %) + Presentación (40 %) |

---

## 📚 Referencias (APA)

- Anthropic. (2026). *Anthropic API documentation*. https://docs.anthropic.com
- Biblioteca del Congreso Nacional de Chile. (2024). *Ley 21.719 sobre protección de datos personales*. https://www.bcn.cl
- Duoc UC. (2026). *Bibliotecas: citas y referencias APA*. https://bibliotecas.duoc.cl
- LangChain. (2026). *LangChain documentation: Agents*. https://docs.langchain.com
- NIST. (2023). *AI Risk Management Framework 1.0* (DOI: 10.6028/NIST.AI.100-1). https://nvlpubs.nist.gov
- OWASP Foundation. (2025). *OWASP Top 10 for LLM Applications*. https://owasp.org/www-project-top-10-for-large-language-model-applications/
