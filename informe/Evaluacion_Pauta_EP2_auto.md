# Evaluación automática del proyecto vs. pauta EP2 (ISY0101)

> Generado con `anthropic/claude-sonnet-5.5` vía OpenRouter a partir del README, el
> informe (docx/md), el guion, la evidencia de pruebas y una verificación de estructura.
> **Uso interno del equipo** (no forma parte de la entrega). Segunda medición, tras las mejoras.

## Resumen ejecutivo

Proyecto técnicamente sólido y bien documentado. Tiene 13 herramientas en tres familias, LangChain create_agent, memoria corta y larga (SQLite), retriever TF-IDF con métricas, planificador con replanificación, 38 tests y evidencia trazable. Brechas: el modelo de LangChain es simulado y no hay prueba de autonomía con un LLM real. La recuperación es léxica (TF-IDF), no densa. Faltan las reflexiones individuales y los nombres de los integrantes. El límite de 5 páginas, el repositorio público, la presentación y la demo en vivo no se pueden verificar. IE10 se evalúa solo desde el guion. Nota estimada 5,8 (logro global 0,80).

## Nota estimada

| Dimensión | Ponderación | Nota |
|---|---|---|
| Encargo (IE1–IE6) | 60% | **6.0** |
| Presentación (IE7–IE10) | 40% | **5.5** |
| **Final** | 100% | **5.8** |

> Medición anterior (antes de las mejoras): Encargo 5,6 · Presentación 5,8 · Final **5,68**.

## Indicadores de evaluación (antes → después)

| IE | Indicador | Puntaje | Δ |
|---|---|---|---|
| IE1 | Configuración de herramientas con autonomía | 80% → **80%** | +0 |
| IE2 | Integración de frameworks | 80% → **80%** | +0 |
| IE3 | Memoria de contenido | 80% → **80%** | +0 |
| IE4 | Recuperación de contexto semántico | 60% → **80%** | +20 |
| IE5 | Planificación de tareas | 80% → **100%** | +20 |
| IE6 | Informe técnico con diagramas y flujos | 80% → **80%** | +0 |
| IE7 | Ejemplos de toma de decisiones | 80% → **80%** | +0 |
| IE8 | Diagrama de orquestación y README | 100% → **80%** | -20 |
| IE9 | Justificación de componentes | 80% → **80%** | +0 |
| IE10 | Lenguaje técnico y argumentación en presentación | 60% → **60%** | +0 |

### IE1. Configuración de herramientas con autonomía — Buen desempeno (80%)

Hay 13 herramientas separadas en consulta, escritura y razonamiento, expuestas como StructuredTool. En la demo el agente encadena stock, reposición, cotización, crédito y ticket sin intervención. Pero en LangChain el modelo simulado solo invoca planificar_pedido, que concentra la lógica, por lo que la autonomía con LLM real no está demostrada.

**Fortalezas:**
- 13 herramientas por familia, con esquema de argumentos tipado
- Cadena autónoma de acciones con efectos persistentes (OC, cotización, ticket)

**Brechas:**
- Autonomía del LLM real no evidenciada; el modelo simulado es determinista
- Lógica concentrada en planificar_pedido, no en decisión del modelo

**Recomendación:** Ejecutar y registrar al menos una traza con ChatAnthropic real eligiendo herramientas.

### IE2. Integración de frameworks — Buen desempeno (80%)

Usa LangChain create_agent con grafo start→model→tools→model→end y permite cambiar el modelo (Claude o simulado). Las herramientas se reutilizan entre el agente local y el de LangChain. La escalabilidad se afirma (migrar a PostgreSQL o vector DB) pero no se prueba, y no hay evidencia de ejecución con API real.

**Fortalezas:**
- Grafo del framework evidenciado en el smoke test
- Herramientas compartidas entre agente local y LangChain

**Brechas:**
- Escalabilidad y compatibilidad afirmadas, no probadas
- Sin evidencia con modelo real

**Recomendación:** Documentar una prueba con Claude real y versiones exactas en requirements.txt.

### IE3. Memoria de contenido — Buen desempeno (80%)

Hay buffer de sesión con resumen comprimido y memoria persistente en SQLite (clientes, cotizaciones, pedidos con historial, tickets, OC). El escenario F consulta un pedido previo y existe un test de persistencia entre sesiones. Sin embargo, no se evidencia la memoria dentro del grafo LangChain (checkpointer), y el test solo se cita sin mostrar su salida.

**Fortalezas:**
- Dos niveles de memoria con persistencia real en SQLite
- Test de continuidad entre sesiones A y B

**Brechas:**
- Memoria no evidenciada en el grafo LangChain
- Resumen comprimido sin evidencia de su efecto en flujos largos

**Recomendación:** Mostrar una traza de conversación larga con el resumen activo y retomada en otra sesión.

### IE4. Recuperación de contexto semántico — Buen desempeno (80%)

Hay un retriever con similitud coseno TF-IDF y normalización morfológica sobre catálogo, políticas y FAQs. Se mide con hit-rate@3=100% y MRR=1,00 sobre 8 consultas. TF-IDF es léxico, no semántico; los embeddings densos son opcionales y no evidenciados. El conjunto de evaluación es pequeño y la integración del RAG en el flujo del agente no es visible en la evidencia.

**Fortalezas:**
- Métricas de calidad de recuperación (hit-rate, MRR)
- Interfaz preparada para embeddings densos

**Brechas:**
- TF-IDF es léxico y el conjunto etiquetado es solo de 8 consultas
- Uso del RAG dentro del flujo del agente poco evidenciado

**Recomendación:** Activar y evaluar embeddings densos con más consultas, mostrando fuentes recuperadas en la respuesta.

### IE5. Planificación de tareas — Muy buen desempeno (100%)

Hay un plan de 6 etapas con prioridad y criticidad, y priorizar() ordena por criticidad. Se inyectan pasos adaptativos (reposición, escalamiento, pago contra entrega, guardrail) y se replanifica ante ítems inválidos. El flujo está diagramado y demostrado en los escenarios B, C, D y H con decisiones justificadas.

**Fortalezas:**
- Priorización por criticidad más inyección adaptativa de pasos
- Replanificación ante entradas inválidas, con trazabilidad

**Brechas:**
- Priorización entre múltiples solicitudes concurrentes no evidenciada
- Plan base fijo de 6 etapas

**Recomendación:** Demostrar la priorización con varias tareas simultáneas de distinta criticidad.

### IE6. Informe técnico con diagramas y flujos — Buen desempeno (80%)

El informe .docx incluye diagramas, tablas de herramientas, escenarios y decisiones, y referencias APA. Está incompleto: nombres de integrantes y reflexiones individuales como placeholders. El máximo de 5 páginas no es verificable. Las justificaciones de diseño son breves y no incluyen alternativas consideradas, que solo aparecen en el guion.

**Fortalezas:**
- Diagramas de arquitectura y flujo, con tablas de escenarios
- Declaración de IA y referencias APA incluidas

**Brechas:**
- Reflexiones individuales y conclusiones por integrante pendientes
- Largo ≤5 páginas no verificable; justificaciones escuetas

**Recomendación:** Completar reflexiones sin IA, verificar el límite de 5 páginas e incluir alternativas descartadas.

### IE7. Ejemplos de toma de decisiones — Buen desempeno (80%)

La evidencia muestra decisiones en distintas condiciones: faltante de stock con OC, monto sobre umbral y cupo con ticket, cliente nuevo con pago contra entrega, guardrail normativo e ítems inválidos. Cada decisión lleva su justificación y log. La demo en vivo no es verificable. La evidencia entregada está truncada (escenario D) y el modelo es simulado.

**Fortalezas:**
- Decisiones con justificación explícita y log jsonl
- Variedad de condiciones del entorno cubiertas

**Brechas:**
- Demo en vivo no verificable
- Evidencia generada con decisiones deterministas/simuladas

**Recomendación:** Ensayar la demo y mostrar al menos un caso con LLM real.

### IE8. Diagrama de orquestación y README — Buen desempeno (80%)

El README es completo: estructura, instalación, ejecución, arquitectura por capas, diagramas Mermaid y PNG, y declaración de IA. Hay inconsistencias: se menciona scripts/ejecutar_todo.py y colab/ que no aparecen en el árbol, integrantes sin completar y URL del repositorio no verificable.

**Fortalezas:**
- Instrucciones de ejecución claras, sin dependencias para el agente local
- Diagrama de arquitectura con tabla de capas

**Brechas:**
- Archivos citados ausentes en el árbol (ejecutar_todo.py, colab/)
- Repositorio remoto y nombres de integrantes no verificables

**Recomendación:** Alinear el árbol del README con el repo real, completar integrantes y publicar el enlace.

### IE9. Justificación de componentes — Buen desempeno (80%)

La tabla de decisiones vincula LangChain, herramientas por familia, SQLite, TF-IDF y el planificador con razones técnicas. El guion compara con Haystack y AutoGen, pero de forma superficial y con una caracterización dudosa de Haystack. La alineación con requerimientos medibles (latencia, volumen) es escasa.

**Fortalezas:**
- Tabla decisión-justificación clara
- Alternativas de framework consideradas en el guion

**Brechas:**
- Alternativas ausentes del informe y comparación superficial
- Sin criterios cuantitativos de requerimientos

**Recomendación:** Incluir en el informe una matriz comparativa de alternativas contra requisitos del flujo.

### IE10. Lenguaje técnico y argumentación en presentación — Desempeno aceptable (60%)

No hay registro de la exposición; solo guion y PPT citado. El guion usa vocabulario técnico y respuestas con evidencia (38 tests, hit-rate, logs), y reparte el tiempo entre dos integrantes. No se puede verificar la ejecución, la equidad ni la defensa de preguntas, por lo que se asigna un nivel conservador.

**Fortalezas:**
- Guion con terminología técnica y respaldo en métricas
- Reparto de tiempos equitativo y respuestas preparadas

**Brechas:**
- Exposición real no verificable
- Respuestas sugeridas con matices débiles (p. ej. Haystack)

**Recomendación:** Ensayar con cronómetro y preparar respuestas con evidencia concreta por cada decisión.

## Requisitos formales

| Requisito | Estado | Observación |
|---|---|---|
| Informe máximo 5 páginas (Word/PDF) | no verificable | Existe el .docx, pero el número de páginas no se puede confirmar; la sección 9 está incompleta. |
| Repositorio con código, documentación, bocetos y evidencia de pruebas | parcial | La estructura y la evidencia existen localmente; la URL pública no se verifica y faltan archivos citados (ejecutar_todo.py, colab/). |
| README con instrucciones de ejecución | cumple | Instrucciones claras para tests, demo y LangChain. |
| Referencias en formato APA | cumple | Referencias APA presentes; las fuentes son pocas y genéricas. |
| Declaración de uso de IA | cumple | Presente en README e informe. |
| Reflexiones individuales sin IA en conclusiones | no cumple | Quedan como placeholders en el informe. |
| Presentación 20 min con participación equitativa | no verificable | Solo hay guion con distribución de tiempos. |
| Apoyo visual y demo en vivo | parcial | Existe PPT y script de demo; la ejecución en vivo no es verificable. |
| Nombres de integrantes | no cumple | Placeholders en README e informe. |

## Acciones prioritarias

1. Redactar reflexiones individuales sin IA y completar nombres de integrantes en informe, README y PPT.
2. Verificar que el informe no supere 5 páginas y publicar el repositorio con enlace verificable.
3. Ejecutar y registrar una traza con LLM real (ChatAnthropic) para demostrar autonomía e IE1/IE2.
4. Evaluar embeddings densos con más consultas y mostrar fuentes RAG en el flujo del agente.
5. Agregar al informe una matriz de alternativas vs requisitos y ensayar la demo y las preguntas con cronómetro.
6. Cálculo: encargo (80+80+80+80+100+80)/6=83,3% → 6,0; presentación (80+80+80+60)/4=75% → 5,5; final 0,6×6,0+0,4×5,5=5,8 (logro global 80%).
