# Taxonomía de IA y línea base simbólica

**Fecha:** 2026-08-20  
**Tema:** taxonomía y áreas de inteligencia artificial aplicadas al proyecto.

## 1. Objetivo

Definir el papel de las áreas de IA en el sistema de logística, construir una
línea base simbólica para clasificar requerimientos y dejar evidencia
reproducible de su funcionamiento.

## 2. Método

La taxonomía relaciona siete áreas de IA con componentes del sistema. El núcleo
es **Búsqueda y optimización**; aprendizaje predictivo, sistemas expertos y
visión por computador resuelven capacidades específicas. Sistemas autónomos,
recomendación y PLN cubren la replanificación, la interacción con el operador y
las explicaciones.

`src/clasificador_requerimientos.py` normaliza los textos y busca palabras o
frases completas para evitar falsos positivos. Cada coincidencia suma evidencia
a un área. La salida conserva todas las áreas detectadas, elige como principal
la de mayor puntuación y resuelve empates según el orden explícito de la
taxonomía.

## 3. Datos y validación

`data/casos_ia.csv` conserva los 20 casos exigidos por la guía y
`data/requerimientos_logistica.csv` contiene 20 casos aplicados al proyecto.
Ambos incluyen clasificación manual de referencia, cubren las siete áreas y
contienen casos híbridos.

La ejecución utilizada fue:

```bash
python -m unittest discover -s tests -v
python -m src.clasificador_requerimientos --fail-on-mismatch
python -m src.clasificador_requerimientos \
  --input data/requerimientos_logistica.csv \
  --output reports/clasificacion-requerimientos-logistica.md \
  --fail-on-mismatch
```

## 4. Resultados

- 20 casos generales y 20 requerimientos logísticos procesados.
- 20/20 categorías principales coinciden con cada referencia manual (100% en
  ambos conjuntos).
- Cinco grupos de reglas propias del dominio se mantienen separados de las
  reglas generales para que su procedencia sea auditable.
- Las pruebas verifican normalización, coincidencia de palabras completas,
  clasificación multiárea, consistencia del dataset, validación del CSV y
  contenido básico del reporte.
- El detalle queda en `reports/clasificacion-casos-base.md` y
  `reports/clasificacion-requerimientos-logistica.md`.

## 5. Conclusiones y limitaciones

La línea base ofrece trazabilidad y un comportamiento determinista apropiado
para validar la taxonomía, pero no comprende contexto ni sinónimos no
declarados. La coincidencia del 100% solo describe los conjuntos controlados
actuales y no demuestra generalización. Los empates requieren revisión porque
dependen de una prioridad declarada.

El siguiente bloque funcional debe definir primero el grafo, las variables del
dataset y la tarea predictiva. Después se podrán comparar A* con una búsqueda no
informada y entrenar el baseline supervisado del corte 1 sin introducir
supuestos no acordados.
