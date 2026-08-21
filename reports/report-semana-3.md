# Reporte — Semana 3

**Fecha:** 2026-08-20  
**Sesión:** 2  
**Tema:** taxonomía y áreas de inteligencia artificial aplicadas al proyecto.

## 1. Objetivo

Nivelar el proyecto de logística con los contenidos confirmados hasta la semana
3: definir el papel de las áreas de IA, construir una línea base simbólica para
clasificar requerimientos y dejar evidencia reproducible de su funcionamiento.

## 2. Método

La taxonomía relaciona siete áreas de IA con componentes del sistema. El núcleo
es **Búsqueda y optimización**; aprendizaje predictivo, sistemas expertos y
visión por computador resuelven capacidades específicas. Sistemas autónomos,
recomendación y PLN cubren la replanificación, la interacción con el operador y
las explicaciones.

`src/semana03_taxonomia.py` normaliza los textos y busca palabras o frases
completas para evitar falsos positivos. Cada coincidencia suma evidencia a un
área. La salida conserva todas las áreas detectadas, elige como principal la de
mayor puntuación y resuelve empates según el orden explícito de la taxonomía.

## 3. Datos y validación

`data/requerimientos_logistica.csv` contiene 12 casos iniciales con una
clasificación manual de referencia. El conjunto cubre las siete áreas y un caso
híbrido de planificación más reglas.

La ejecución utilizada fue:

```bash
python3 -m unittest discover -s tests -v
python3 -m src.semana03_taxonomia --fail-on-mismatch
```

## 4. Resultados

- 12 requerimientos procesados.
- 12/12 categorías principales coinciden con la referencia manual (100%).
- Las pruebas verifican normalización, coincidencia de palabras completas,
  clasificación multiárea, consistencia del dataset, validación del CSV y
  contenido básico del reporte.
- El detalle de reglas activadas queda en `reports/semana03.md`.

## 5. Conclusiones y limitaciones

La línea base ofrece trazabilidad y un comportamiento determinista apropiado
para validar la taxonomía, pero no comprende contexto ni sinónimos no
declarados. La coincidencia del 100% solo describe el pequeño conjunto actual y
no demuestra generalización. Los empates requieren revisión porque dependen de
una prioridad declarada.

El siguiente bloque funcional debe definir primero el grafo, las variables del
dataset y la tarea predictiva. Después se podrán comparar A* con una búsqueda no
informada y entrenar el baseline supervisado del corte 1 sin introducir
supuestos no acordados.
