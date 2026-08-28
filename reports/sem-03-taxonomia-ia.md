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

`data/requerimientos_logistica.csv` contiene 20 requerimientos aplicados al
proyecto. Incluye clasificación manual de referencia, cubre las siete áreas y
contiene casos híbridos.

La ejecución utilizada fue:

```bash
python -m unittest discover -s tests -v
python -m src.clasificador_requerimientos --fail-on-mismatch
```

## 4. Resultados

- 20 requerimientos logísticos procesados.
- 20/20 categorías principales coinciden con la referencia manual (100%).
- El vocabulario por área es propio del dominio logístico y queda documentado
  en el reporte de clasificación.
- Las pruebas verifican normalización, coincidencia de palabras completas,
  clasificación multiárea, consistencia del dataset, validación del CSV y
  contenido básico del reporte.
- El detalle queda en `reports/sem-03-clasificacion-requerimientos.md`.

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
