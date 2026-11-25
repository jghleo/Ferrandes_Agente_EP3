# Guion de presentación EP3 — Agente Ferrandes

**Evaluación Parcial N°3 · ISY0101 · 20 minutos (10 de exposición + 10 de preguntas)**

> **Integrante A:** Leandro Marin · **Integrante B:** ⬅ completar antes de la entrega.
> Las reflexiones personales finales **no se redactan con IA**.

## Reglas de la defensa

- Usar rigor técnico pero de forma comprensible: definir cada métrica antes de dar el número.
- Cada afirmación debe apoyarse en una ruta concreta: `evidencia/metricas.json`, `evidencia/analisis_trazas.json`, `dashboard/capturas/`, `informe/Informe_Tecnico_EP3_Ferrandes.pdf`.
- Si una pregunta no puede responderse con evidencia, decir explícitamente el límite (por ejemplo: "el LLM real no fue ejecutado").
- Reparto equitativo: **A** abre y cierra los bloques de métricas, dashboard y ética; **B** lidera trazabilidad, mejoras y defensa con datos. El cierre es compartido.

---

## 1. Exposición (10:00)

| Tiempo | Diapositiva / apartado | Habla | Contenido clave | Evidencia que se muestra |
|---|---|---|---|---|
| 0:00–0:40 | 1. Portada | **A** | Presentación del equipo y continuidad: EP2 construyó el agente; EP3 lo mide, lo hace trazable y lo defiende con datos. | `Presentacion_EP3_Ferrandes.pptx` |
| 0:40–1:40 | 2. De agente funcional a sistema observable | **A** | IL3.1–IL3.4 y los cinco IE del encargo. Explicitar que el foco ya no es "responder", sino "medir y mejorar". | `README.md` |
| 1:40–2:30 | 3. Mapa IE → evidencia | **B** | Recorrer IE1–IE9 y decir qué archivo respalda cada uno. Frase puente: "Nada de lo que veremos es simulado: sale de 45 ejecuciones reales". | Tabla de la diapositiva 3 |
| 2:30–3:20 | 4. Pipeline de observabilidad | **B** | `evaluar_observabilidad.py` → métricas + trazas + consentimiento/auditoría → dashboard → informe. Distinguir errores esperados (dato inexistente) de errores inesperados. | `scripts/evaluar_observabilidad.py`, `evidencia/` |
| 3:20–4:20 | 5. Métricas (IE1, IE2) | **A** | Definir precisión (0,4 intención + 0,4 Jaccard(tools) + 0,2 keyword), latencia p50/p95/máx, consistencia tras normalizar IDs, errores y recursos. Resultados: 100 %, 2,644 / 27,669 / 28,154 ms, 100 %, 0 errores, 33,06 MB / 86,85 %. | `evidencia/metricas.json` |
| 4:20–5:10 | 6. Dashboard (IE4) | **A** | Abrir la app Streamlit o la réplica HTML. Mostrar filtros por escenario, precisión por intención, consistencia por variabilidad, hallazgos y controles. | `dashboard/app.py`, `dashboard/dashboard.html`, captura 01 |
| 5:10–6:00 | 7. Análisis crítico (IE6) | **B** | Patrones: P01 (2 falsos negativos EP2 → 0 EP3), P03 (3 replanificaciones), P04 (3 retenciones por crédito), P05 (3 derivaciones normativas), P08 (0 trazas incompletas). Conectar cada patrón con una mejora. | Captura 04, `evidencia/Analisis_Logs_EP3.md` |
| 6:00–6:40 | 8. Antes / después | **B** | Cinco correcciones con verificación: extracción genérica de códigos, prioridad de intenciones, ítems inválidos al planificador, spans con `trace_id`, redacción de PII. | Captura 03, `tests/test_observabilidad.py` |
| 6:40–7:30 | 9. Ética y cumplimiento (IE8) | **A** | Minimización, consentimiento (15/15), auditoría, guardrail normativo. Marco: Ley 19.628, Ley 21.719, NIST AI RMF 1.0 y OWASP LLM. Límite: agente local determinista; con LLM real aumentaría la variabilidad. | `evidencia/verificacion_seguridad.json`, captura 05 |
| 7:30–8:20 | 10. Mejoras y escalabilidad (IE7) | **B** | Cada mejora nace de una métrica: caché/paralelismo por la cola p95, alertas por variabilidad, PostgreSQL + vector store, gobernanza de trazas. | Captura 02, informe §6 |
| 8:20–8:55 | 11. Evidencia y resultados | **A + B** | A dice las cifras globales; B cierra con "45 pruebas unitarias OK y 13 diapositivas con notas". | `tests/ejecutar_tests.py`, `evidencia/evidencia_pruebas.txt` |
| 9:00–9:40 | 12. Comunicación especializada (IE9) | **B** | Responder dos preguntas del público usando el formato "afirmación → número → archivo → límite". | Diapositiva 12 |
| 9:40–10:00 | 13. Cierre | **A + B** | A: "La EP3 convierte un agente funcional en un sistema observable, seguro y defendible". B: anuncia preguntas. | Diapositiva 13 |

### Guion literal sugerido (fragmentos de apertura)

**A (0:00):** "Somos el equipo Ferrandes. En la EP2 construimos un agente B2B que cotiza, confirma pedidos, emite reposiciones y escala. En la EP3 respondimos otra pregunta: ¿cómo sabemos que funciona bien? Instrumentamos 15 escenarios con 3 repeticiones y convertimos cada ejecución en una métrica, una traza y una decisión de mejora."

**B (1:40):** "El mapa es directo: IE1 y IE2 son las métricas, IE3 son los registros, IE4 es el dashboard, IE5 es el informe; IE6 a IE9 son esta defensa. Cada uno tiene un archivo en el repositorio, y los cuatro hallazgos críticos ya están corregidos o monitorizados."

**A (3:20):** "Antes de mostrar el resultado, definimos la regla. Precisión no es 'me gustó la respuesta': es 0,4 de acierto de intención, 0,4 de coincidencia de herramientas y 0,2 de palabra clave. Consistencia compara la respuesta modal después de normalizar los IDs dinámicos, para que un OC-000001 no cuente como otro pedido distinto."

---

## 2. Preguntas y respuestas preparadas (10:00)

| # | Pregunta probable | Respuesta con evidencia (y límite cuando corresponda) |
|---|---|---|
| 1 | ¿Cómo se mide la precisión? | "Fórmula ponderada sobre 15 escenarios etiquetados; 100 % observado en `evidencia/metricas.json`. Límite: la etiqueta es local, construida por el equipo." |
| 2 | ¿Por qué p95 y no la media? | "p95 captura la variabilidad de los flujos de pedido con reposición: p50 = 2,644 ms pero p95 = 27,669 ms. La media ocultaría esa cola." |
| 3 | ¿Los IDs dinámicos no rompen la consistencia? | "Se normalizan antes de comparar; consistencia 100 % incluso en el mínimo. Ver `src/observabilidad/metricas.py`." |
| 4 | ¿Los errores esperados cuentan como fallos? | "No. Un dato inexistente se informa correctamente (2 casos); los errores inesperados son 0. Están separados en el dashboard y en `metricas.json`." |
| 5 | ¿Qué cambió respecto de la EP2? | "2 falsos negativos de catálogo en los logs históricos → 0 en EP3, gracias a la extracción genérica `[A-Z]{3}-\d{3}`. Además, 45/45 trazas tienen `trace_id` y spans." |
| 6 | ¿Qué pasa con datos personales? | "`redactar()` elimina RUT, email, teléfono, tarjeta y IP antes de persistir; 0 PII en `trazas_ep3.jsonl`, 15/15 consentimientos y auditoría activa." |
| 7 | ¿Es ético usar un agente así en producción? | "Con controles sí, pero con límites: derivación normativa a especialista, sin inventiva legal y revisión de consentimientos. No afirmamos cumplimiento legal absoluto, sino alineación con Ley 19.628, Ley 21.719, NIST AI RMF y OWASP LLM." |
| 8 | ¿Es escalable? | "Las herramientas están desacopladas, por lo que SQLite→PostgreSQL y TF-IDF→vector store no cambian la interfaz. Es una ruta propuesta, no una migración ejecutada; el límite es explícito." |
| 9 | ¿Por qué se replanifica ante ítems inválidos en vez de abortar? | "Porque el flujo B2B debe continuar con lo válido; 3 eventos P03 quedan registrados con su corrección y prueba de regresión." |
| 10 | ¿Usaron IA para hacer todo esto? | "Sí como apoyo de redacción, código y gráficos, declarado en el informe. Las decisiones de diseño, el análisis de causas y estas reflexiones son propias; no usamos IA para las conclusiones individuales." |

### Cómo responder si no hay evidencia

1. Repetir la pregunta con precisión.
2. Dar el dato que sí existe y su ruta.
3. Decir el límite: "No ejecutamos LLM real / no publicamos el repo / la exposición no está grabada".
4. Ofrecer la siguiente medición: "La prueba de regresión sería …".

---

## 3. Cierre individual (redactar sin IA)

⬅ **REDACTAR SIN APOYO DE IA — Integrante A:** aprendizaje, aporte concreto y qué cambiaría.

⬅ **REDACTAR SIN APOYO DE IA — Integrante B:** aprendizaje, aporte concreto y qué cambiaría.

> Recordatorio: completar el nombre del integrante B en la portada, ensayar con cronómetro y verificar que cada integrante hable cerca de 5 minutos.
