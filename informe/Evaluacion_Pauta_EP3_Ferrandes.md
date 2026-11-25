# Evaluación según pauta EP3 — Agente Ferrandes

**Evaluación Parcial N°3 · ISY0101 · Encargo con Presentación**

> **Aclaración:** este documento es una **autoevaluación estimada** construida a partir de los entregables disponibles (código, evidencia, informe, PPT y guion). La **nota oficial** la determina el docente. La exposición en vivo no es verificable desde los archivos, por lo que IE6–IE9 se calibran de forma conservadora con lo que efectivamente se puede revisar.

## 1. Resumen ejecutivo

El proyecto cumple el núcleo técnico de la EP3: cinco métricas aplicadas a 45 ejecuciones reales, 45 trazas instrumentadas, 166 registros históricos analizados, dashboard Streamlit con réplica HTML, correcciones con prueba de regresión, controles de privacidad y un informe de 2 páginas con evidencia visual. Las brechas que bajan la estimación son de forma y de verificación: falta la reflexión personal sin IA y la defensa oral solo existe como guion/PPT. El repositorio ya está publicado en https://github.com/jghleo/Ferrandes_Agente_EP3. La entrega se declara en modalidad individual, aunque la pauta original habla de parejas.

**Nota estimada: 6,3 / 7,0** (logro global 0,88).

| Dimensión | Ponderación | Logro de dimensión | Nota de dimensión |
|---|---:|---:|---:|
| Encargo (IE1–IE5) | 60 % | 96,7 % | **6,8** |
| Presentación (IE6–IE9) | 40 % | 75,0 % | **5,5** |
| **Final** | **100 %** | **88,0 %** | **6,3** |

Cálculo: `nota = 1 + 6 × logro`. Final: `0,6 × 6,8 + 0,4 × 5,5 = 6,28 → 6,3`. Equivalente a `1 + 6 × 0,88 = 6,28`.

## 2. Resultado por indicador

Los niveles siguen la escala de la pauta: 100 % (muy buen), 80 % (buen), 60 % (aceptable), 30 % (incipiente) y 0 % (no logrado).

| IE | Indicador | Peso | Logro | Aporte al logro |
|---|---|---:|---:|---:|
| IE1 | Métricas de precisión, consistencia y errores | 15 % | 100 % | 0,150 |
| IE2 | Latencia y uso de recursos | 10 % | 100 % | 0,100 |
| IE3 | Análisis de logs y trazabilidad | 15 % | 100 % | 0,150 |
| IE4 | Dashboard visual | 10 % | 100 % | 0,100 |
| IE5 | Informe técnico con evidencia visual | 10 % | 80 % | 0,080 |
| IE6 | Análisis crítico y patrones | 10 % | 80 % | 0,080 |
| IE7 | Mejoras y escalabilidad | 10 % | 80 % | 0,080 |
| IE8 | Seguridad, ética y privacidad | 10 % | 80 % | 0,080 |
| IE9 | Comunicación especializada | 10 % | 60 % | 0,060 |
| | **Total** | **100 %** | **88 %** | **0,880** |

## 3. Justificación por indicador

### IE1 — Métricas de precisión, consistencia y errores — 100 %

**Fortalezas.** Precisión con definición operativa explícita (0,4 intención + 0,4 Jaccard de herramientas + 0,2 palabra clave), consistencia calculada sobre respuesta modal y con normalización de IDs dinámicos, y separación entre errores esperados (2 datos inexistentes) e inesperados (0). Se aplica a 15 escenarios con 3 repeticiones cada uno, incluyendo variabilidad de datos.

**Brechas.** La etiqueta de referencia es construida por el estudiante, no externa.

**Recomendación.** Ampliar el conjunto etiquetado y publicar la definición de "correcto" en el README para replicación externa.

### IE2 — Latencia y uso de recursos — 100 %

**Fortalezas.** p50 = 2,644 ms, p95 = 27,669 ms, máximo = 28,154 ms, RSS máxima = 33,06 MB y CPU media = 86,85 %. Hay desglose por intención y por tipo de variabilidad, umbral de alerta de 50 ms y 0 ejecuciones sobre el umbral.

**Brechas.** La medición de recursos se hace en el proceso local; no hay perfilado en un entorno desplegado.

**Recomendación.** Exportar las series temporales a Prometheus/Grafana cuando el agente pase a producción.

### IE3 — Análisis de registros y trazabilidad — 100 %

**Fortalezas.** Se examinaron 166 logs históricos de EP2 y 45 trazas EP3 con `trace_id` y spans. Se documentaron P01–P10 con severidad, frecuencia, estado e IE asociado. P01 pasó de 2 falsos negativos a 0; P08 de trazas incompletas a 45/45 completas.

**Brechas.** El análisis es retrospectivo sobre ejecuciones locales; no hay correlación con usuarios reales.

**Recomendación.** Añadir correlación por `session_id` y alertas automáticas sobre patrones P01/P03/P08.

### IE4 — Dashboard visual — 100 %

**Fortalezas.** `dashboard/app.py` (Streamlit) lee la misma evidencia JSON que generan los scripts; incluye KPIs, serie por escenario con filtro, precisión por intención, consistencia por variabilidad, tabla de hallazgos y controles de seguridad. Existe réplica autocontenida `dashboard/dashboard.html` y 5 capturas usadas en informe y PPT.

**Brechas.** La app interactiva requiere Streamlit; la versión HTML es estática.

**Recomendación.** Publicar el dashboard con autenticación y actualización periódica desde el pipeline de ejecución.

### IE5 — Informe técnico — 80 %

**Fortalezas.** Documento Word y PDF de 2 páginas (límite: 5), con tabla de métricas, tabla de hallazgos, captura del dashboard, controles de seguridad, recomendaciones numeradas, declaración de IA y referencias APA.

**Brechas.** La reflexión personal sigue como placeholder, por exigencia de redacción sin IA. El repositorio ya está publicado y es público.

**Recomendación.** Redactar la reflexión sin apoyo de IA y verificar el enlace público del repositorio antes de la entrega.

### IE6 — Análisis crítico de ejecución — 80 %

**Fortalezas.** La diapositiva 7 y el guion vinculan patrones concretos con mejoras: P01 → extracción genérica, P03 → replanificación, P05 → derivación normativa, P08 → spans. Cada corrección tiene prueba de regresión en `tests/test_observabilidad.py`.

**Brechas.** No hay registro de la exposición real; solo guion y PPT con notas del expositor.

**Recomendación.** Ensayar con cronómetro y, si es posible, grabar una sesión de práctica para verificar la argumentación oral.

### IE7 — Propuesta de mejora y escalabilidad — 80 %

**Fortalezas.** Las cuatro recomendaciones salen de datos observados: caché/paralelismo por la diferencia p50–p95, alertas por variabilidad, migración SQLite→PostgreSQL y TF-IDF→vector store, y gobernanza de consentimientos/trazas.

**Brechas.** La migración y el paralelismo son propuestas, no implementaciones medidas.

**Recomendación.** Implementar la caché y medir el delta de p95 como prueba de la hipótesis.

### IE8 — Defensa de criterios éticos — 80 %

**Fortalezas.** Redacción de PII antes de persistir, consentimiento por cliente y finalidad (15/15), auditoría de escrituras, guardrail normativo con 3 derivaciones y marco normativo citado (Ley 19.628, Ley 21.719, NIST AI RMF 1.0, OWASP LLM).

**Brechas.** La solución es local y determinista; no se demuestra operación en producción ni revisión legal formal.

**Recomendación.** Documentar un plan de retención/purga y una revisión de consentimientos antes de cualquier despliegue real.

### IE9 — Comunicación especializada — 60 %

**Fortalezas.** El guion usa vocabulario técnico preciso (Jaccard, p95, normalización, spans, redacción) y prepara 10 respuestas con formato "afirmación → número → archivo → límite". El PPT tiene notas del expositor y el guion cubre los 10 minutos con un solo expositor.

**Brechas.** La exposición y las preguntas reales no son verificables; solo existe el material escrito. Por eso se mantiene el nivel "desempeño aceptable", coherente con la calibración usada en la EP2.

**Recomendación.** Ensayar las 10 preguntas con evidencia abierta en pantalla y grabar el ensayo para autocheck.

## 4. Requisitos formales

| Requisito de la pauta | Estado | Observación |
|---|---|---|
| Informe escrito máximo 5 páginas (Word/PDF) | **Cumple** | `Informe_Tecnico_EP3_Ferrandes.docx/.pdf`, 2 páginas. |
| Repositorio con código, documentación, bocetos y evidencia | **Cumple** | Público: https://github.com/jghleo/Ferrandes_Agente_EP3 |
| README con instrucciones precisas | Cumple | Ver `README.md` actualizado a EP3. |
| Capturas, gráficos y visualizaciones del dashboard | Cumple | 5 capturas en `dashboard/capturas/`; figuras insertadas en el informe y PPT. |
| Citas APA | Cumple | Apartado 7 del informe con referencias APA. |
| Declaración de uso de IA | Cumple | Informe §7 y README. |
| Reflexión personal sin IA | **Pendiente** | Placeholder deliberado en informe, PPT y guion. |
| Identificación del integrante | **Cumple** | Leandro Marin; modalidad individual declarada. |
| Presentación 20 min con participación equitativa | No verificable / no aplica | Guion de 10 + 10 min con expositor único; sin grabación. |
| Apoyo visual (PPT o dashboard) | Cumple | PPT de 13 diapositivas + dashboard interactivo y estático. |

## 5. Acciones que pueden cambiar la nota

1. Redactar sin IA la reflexión personal: afecta IE5 e IE8.
2. Verificar el enlace público del repositorio: ya cumple el requisito formal.
3. Ensayar y grabar la defensa de 10 + 10 minutos: puede elevar IE6 e IE9 de 80 %/60 % a 100 %/80 %.
4. Ejecutar una medición de la caché propuesta: puede fortalecer IE7.

> Para referencia: si IE6 e IE9 subieran a 100 % y IE5 a 100 %, el logro global sería 0,96 y la nota estimada 6,8. La nota oficial depende de la evaluación docente.
