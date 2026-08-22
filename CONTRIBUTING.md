# Guía de contribución

Convenciones de trabajo para mantener evidencia clara, cambios revisables y
ejecuciones reproducibles durante el semestre.

El entorno de referencia del curso es Python 3.13.x. Después de activar
`.venv`, todos los comandos se ejecutan mediante `python` para asegurar que no
se use por accidente el intérprete global.

## Flujo recomendado

1. Crear una rama corta a partir de `main`.
2. Implementar un único cambio coherente.
3. Ejecutar el script o notebook afectado y las pruebas.
4. Actualizar el reporte del tema y `CHANGELOG.md` cuando corresponda.
5. Solicitar revisión antes de integrar a `main`.

No se deben versionar entornos virtuales, credenciales, cachés, datasets con
información sensible ni artefactos binarios reproducibles.

## Convención de commits

Formato inspirado en Conventional Commits, con el scope nombrando el módulo o
tema afectado:

```text
<tipo>(<módulo>): <descripción corta en imperativo>

<instrucciones, contexto y resultados relevantes>
```

Scopes habituales: `clasificador`, `datos`, `reportes`, `docs`. Para las
entregas de corte se usa `corte<N>` y para cambios transversales, `repo`.

### Reglas

- título de máximo 72 caracteres y escrito en imperativo;
- un commit por tarea o cambio coherente;
- cuerpo con la tarea y la evidencia obtenida (métricas, salidas o pruebas);
- no mezclar refactorizaciones con cambios funcionales sin justificación.

### Tipos

| Tipo | Uso |
|---|---|
| `feat` | Nueva funcionalidad, modelo o módulo |
| `fix` | Corrección de un error |
| `docs` | README, reportes o documentación |
| `chore` | Entorno, dependencias o estructura |
| `test` | Pruebas nuevas o corregidas |
| `refactor` | Reestructura sin cambio de comportamiento |
| `update` | Actualización de contenido o datos existentes |
| `entrega` | Entrega formal de un corte |

Ejemplo:

```text
feat(corte1): implementa búsqueda A* sobre el grafo

Tarea: comparar A* con una búsqueda no informada sobre el mismo escenario.

- Registra costo total y nodos expandidos.
- Conserva el mismo criterio de desempate en ambos algoritmos.
- Pruebas: python -m unittest discover -s tests -v
```

## Entregas y versiones

Los tres cortes se etiquetan con SemVer:

| Corte | Semana | Tag |
|---:|---:|---|
| 1 | 6 | `v1.0.0` |
| 2 | 12 | `v2.0.0` |
| 3 | 18 | `v3.0.0` |

El commit de entrega usa `entrega(corte<N>): <nombre>`, seguido de un tag
anotado. El resto de los cambios se acumula en `[En curso]` dentro de
`CHANGELOG.md`.

## Criterios de calidad

Antes de integrar un cambio debe comprobarse:

```bash
python -m unittest discover -s tests -v
python -m src.clasificador_requerimientos --fail-on-mismatch
```

- **Realizado:** existen el código, los datos y el informe requeridos.
- **Funciona:** la ejecución termina sin errores y es reproducible.
- **Coincide:** el resultado corresponde con la actividad y se justifica.

## Reportes

Cada práctica o componente deja un reporte en `reports/` nombrado por tema
(`<tema>.md`, por ejemplo `taxonomia-ia.md` o
`clasificacion-requerimientos-logistica.md`) con:

1. objetivo y alcance;
2. cambios o commits analizados;
3. datos, configuración y método;
4. resultados y métricas;
5. conclusiones, limitaciones y siguientes pasos.

El reporte de cada corte consolida el avance arquitectónico, las métricas
comparables y las decisiones que afecten al sistema completo.
