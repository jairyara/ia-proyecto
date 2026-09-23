# Guía técnica — arquitectura, datos y operación

Documenta el sistema actual, no la secuencia de implementación. Para alcance
académico, dashboard actual y propuesta MLP, consultar [proyecto y dashboard](proyecto.md).

## Arquitectura y estado actual

Un único proyecto Compose `ia-proyecto` contiene dos servicios: `dashboard`
(React compilado + FastAPI) y `db` (PostgreSQL). No hay contenedor Node en runtime.
Python 3.14; dependencias fijadas en `requirements.txt` y `dashboard/pnpm-lock.yaml`.

- Semanas 2–7 conservan CSV/JSON, algoritmos, contratos y reportes originales.
- La persistencia nueva usa SQLAlchemy y migraciones Alembic administrativas;
  nunca `create_all`, migraciones o seeds automáticos al iniciar HTTP.
- La BD contiene 14.411 paradas, 100 rutas y 17 estaciones Amazon; además,
  200 imágenes y 200 asociaciones simuladas a paradas distintas.
- La API de lectura y el dashboard permiten inspeccionar paradas e imágenes del
  piloto. No hay MLP visual entrenado ni particiones/preprocesamiento
  definitivos; se espera la guía.
- El funcionamiento histórico no depende de que la BD nueva esté disponible.

## Arranque y configuración

Desde la raíz, sin sobrescribir una configuración existente:

```bash
test -f .env || cp .env.example .env
# Definir POSTGRES_PASSWORD en .env antes de arrancar.
docker compose up -d --build --wait
docker compose ps
# Web: http://localhost:8000; health: /api/health; OpenAPI: /docs.
docker compose exec dashboard python -m alembic upgrade head
docker compose exec dashboard python -m alembic current
docker compose exec dashboard python -m alembic check
```

La revisión vigente es `0003_piloto_visual`. Las revisiones anteriores se
conservan para reproducir instalaciones; no se editan migraciones ya aplicadas.

| Configuración | Uso |
|---|---|
| `APP_PORT` | Puerto local web, 8000 por defecto |
| `COMPOSE_PROFILES=persistencia` | Inicia app + BD con un comando; incluido en `.env.example` |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | BD y credenciales; contraseña sin valor predeterminado |
| `DB_HOST`, `DB_PORT` | Host: `127.0.0.1:5433`; Compose inyecta `db:5432` |
| `DB_CONNECT_TIMEOUT` | 3 segundos por defecto, entre 1 y 60 |
| `DATABASE_URL` | Override para Python, driver `postgresql+psycopg`; no reconfigura el servidor Compose |
| `VISUAL_STORAGE_ROOT` | Host: `data/visual/almacen`; Docker: `/var/lib/ia/visual` |

Las variables del proceso prevalecen sobre `.env`; Python no interpola valores
del archivo. Usar comillas simples para contraseñas con `$` o `#`; una URL
explícita necesita escapar caracteres reservados. No imprimir credenciales.
Cambiar `.env` no cambia la contraseña de un usuario dentro de un volumen existente.

Es un entorno local: puertos enlazados a `127.0.0.1`. Antes de exponerlo, definir
roles de mínimos privilegios, autenticación, TLS y gestión de secretos.
Sin persistencia: `COMPOSE_PROFILES= docker compose up -d dashboard`; esto no
detiene una BD que ya esté activa.

## Datos y vocabulario

**Parada Amazon:** fila identificada por `pedido_id`, con datos agregados de
paquetes; no equivale a un paquete físico individual. Un **pedido de demostración**
es una parada seleccionada para ilustrar la inspección.

**Imagen sintética:** render de empaque, no fotografía de una entrega Amazon.
**Asociación simulada:** vínculo ilustrativo sin procedencia física compartida.
**Etiqueta visual:** anotación de origen, distinta de una predicción y del riesgo
de retraso. **Grupo visual:** objeto de origen cuyas vistas/variantes no deben
repartirse entre entrenamiento y evaluación.

`amazon_pedidos.csv` se importa sin cambiar sus valores. Se conservan `Decimal`
y unidades originales (km, m³, segundos, minutos), UTC y `zone_id` textual,
incluido el literal `nan`. `retrasado_estimado` es heurístico, no retraso observado
ni daño visual. `pedidos.csv` y `amazon_rutas_muestra.json` son fuentes distintas
usadas por módulos anteriores; no fusionarlas ni borrarlas como duplicados.

### Modelo persistido

| Tablas | Responsabilidad |
|---|---|
| `datasets`, `importaciones` | Fuente/version/hash, procedencia y auditoría de intentos |
| `estaciones`, `rutas`, `paradas` | Logística versionada, IDs de origen, valores y unidades |
| `imagenes` | Fuente, clave relativa, SHA-256, MIME, bytes, dimensiones, grupo y etiquetas |
| `pilotos_visuales` | Datasets, versión, algoritmo, semillas, JSON del mapa y su hash |
| `asociaciones_visuales` | Piloto, parada e imagen; tipo obligatorio `simulada` |

Unicidad de IDs por dataset y de cada imagen/parada por piloto; FK compuestas
impiden cruces entre datasets. Sin borrados en cascada. Los conteos logísticos de
un dataset visual son cero; las imágenes se cuentan en su propia tabla.
Una sesión SQLAlchemy por operación, transacciones explícitas, no compartir
sesiones entre hilos. Al añadir modelos, registrarlos en `migrations/env.py` y
revisar nombres/orden de constraints generados por Alembic.

## Importación Amazon

```bash
docker compose exec dashboard python -m src.datos.seed --dry-run
docker compose exec dashboard python -m src.datos.seed
# Repetir: sin_cambios, cero filas nuevas; se registra otro intento de auditoría.
```

El manifiesto `data/manifests/amazon-v1.json` fija hash y conteos. Se valida el
CSV completo: cabecera, tipos, rangos, fechas, duplicados y coherencia de rutas;
no se descartan filas inválidas. Bloqueo PostgreSQL y transacción completa evitan
cargas parciales y duplicados concurrentes. Otra fuente requiere otro manifiesto
revisado y versión, mediante `--csv` y `--manifiesto`; no sobrescribir la anterior.

## Piloto visual: fuente y límites

**Industrial Quality Control of Packages**, Christian Vorhemus, versión 2:
200 vistas laterales, 100 `intact`/100 `damaged`, una por serial; PNG RGB 960×540,
126.285.817 bytes. La fuente contiene 400 imágenes con dos vistas por objeto.
La licencia declarada del dataset es **GPL 2**, distinta de MIT del generador.
[Ficha del autor](https://www.kaggle.com/datasets/christianvorhemus/industrial-quality-control-of-packages).

La evidencia de autor/licencia, inventario, hashes, selección y revisión se
conserva en `data/manifests/paquetes-v2-*.json` y `piloto-visual-v1*.json`.
Se verifican contenido decodificable, tamaño máximo de 2 MiB/2 millones de
píxeles, dimensiones, etiquetas, grupos y duplicados por bytes/píxeles.

Son empaques farmacéuticos del mismo diseño/escenario: 200 grupos no implican
200 escenarios independientes. Hay desenfoque, encuadres parciales y deformaciones
leves incluso en `intact`. La revisión no demuestra ausencia de variables de
confusión ni generalización a fotografías reales. No cambiar etiquetas en silencio,
crear aumentos para completar 200 ni redistribuir imágenes sin revisar condiciones.

### Adquirir, auditar e importar

En host con Python 3.14 y dependencias instaladas:

```bash
python -m src.vision.adquisicion --dry-run  # sin red ni escrituras
python -m src.vision.adquisicion            # solo 200 originales, reanudable
python -m src.vision.auditoria              # auditoría offline
```

Los originales y hojas de revisión están en `data/visual/`, excluido de Git y
de la imagen Docker. Con Amazon ya importado:

```bash
docker compose run --rm --no-deps \
  -v "$PWD/data/visual/paquetes-v2:/originales:ro" \
  dashboard python -m src.vision.seed --originales /originales --dry-run

docker compose run --rm --no-deps \
  -v "$PWD/data/visual/paquetes-v2:/originales:ro" \
  dashboard python -m src.vision.seed --originales /originales
```

El modo seco no conecta a BD ni escribe; tampoco certifica el estado de la BD.
Repetir la importación conserva el mapa y devuelve `sin_cambios`.

`asociaciones-v1.json` fija el mapa: IDs canónicos, muestra sin reemplazo con
`random.Random(20260922).sample` y barajado independiente de imágenes con
`random.Random(20260923).shuffle`; algoritmo `python314-random-sample-shuffle-v1`.
Se persiste en BD y volumen, no se recalcula al consultar. Su SHA-256 es
`d645bac9ea84ad279843a50b8ad9d0549a7a77c39fd71b7204d4a174d15332d5`.
`--version v2` crea otro piloto, no modifica el anterior; selección visual
identificada como `2-side-<version>`. La CLI solo admite la fuente aprobada.

14.211 paradas quedan sin imagen deliberadamente. La pantalla de inspección
muestra: **Imagen sintética asociada aleatoriamente para demostración; no
corresponde al envío original de Amazon.** No usar variables Amazon, nombres de
archivo o IDs como características visuales. Particiones por grupo, aumentos
solo en entrenamiento y transformaciones aprendidas solo con entrenamiento;
proporciones y modelo definitivos pendientes de la guía.

## Almacenamiento y recuperación

`postgres_data` conserva la BD; `visual_data` conserva
`<hash-mapa>/mapa.json` y `<hash-mapa>/<sha256-imagen>.png`, fuera de la SPA.
Las claves en BD son relativas. La API entrega archivos por ID desde el
almacenamiento privado, no acepta rutas del cliente ni expone un directorio
estático público.

## API de inspección y documentación

FastAPI publica el esquema OpenAPI y la interfaz Swagger en `/docs` (`/openapi.json`
para herramientas). Es la documentación de la API vigente; no se añade
Docusaurus por ahora. El router de lectura `/api/datos` ofrece:

| Ruta | Uso |
|---|---|
| `/resumen` | Conteos actuales de Amazon y piloto, y estado del modelo visual |
| `/paradas` | Paradas paginadas; filtros opcionales `ruta` y `estacion` |
| `/imagenes` | Imágenes paginadas; filtro opcional `etiqueta` |
| `/imagenes/{id}` | Metadatos, etiqueta de origen y asociación simulada |
| `/imagenes/{id}/archivo` | PNG original servido por ID desde el volumen privado |

Los conteos provienen de la BD, no de constantes del frontend. Si PostgreSQL no
está disponible, estos endpoints responden 503; las semanas históricas siguen
operativas. El modelo visual continúa sin entrenamiento ni predicciones.

Usar siempre el mismo almacenamiento asociado a la BD: en el entorno Docker
actual no reimportar desde host con otra raíz vacía. La CLI permite
`--almacenamiento` en instalaciones host independientes.

BD y filesystem no forman una transacción distribuida. Se registra el intento,
valida, copia a staging propio y publica el lote por renombrado antes del commit.
Fallos de copia revierten metadatos y limpian solo staging propio. Ante commit
incierto se conserva el lote y un reintento lo verifica/reutiliza. Un proceso
interrumpido puede dejar `en_curso` o staging; no bloquea reintentos. Corrupción
se rechaza sin sobrescribir ni reasignar; no hay GC ni reparación automáticos.

- Reiniciar/detener: `docker compose restart` / `docker compose stop`.
- **No usar `down -v` ni prune global para limpiar o reiniciar.**
- Respaldar BD, volumen visual y manifiestos con importaciones detenidas;
  restaurarlos conjuntamente. Respaldar solo BD no recupera imágenes.
- Eliminar residuos solo tras verificar que no están referenciados y que no hay
  importaciones activas. No se garantiza recuperación de fallos físicos de disco.
- `downgrade` es destructivo; solo en BD desechable. No sirve como reintento ni
  recuperación de pilotos publicados: conserva catálogo/archivos pero elimina tablas.

## Pruebas y desarrollo

```bash
python -m unittest discover -s tests -v
python -m src.clasificador_requerimientos --fail-on-mismatch
python -m pip check
pnpm --dir dashboard test
pnpm --dir dashboard build
```

Para integración, proporcionar `TEST_DATABASE_URL` a una BD desechable cuyo
nombre termine en `_test`, nunca a `ia_logistica`. Las pruebas crean/eliminan
schemas propios. Sin esa variable se omiten explícitamente los casos de BD.
Las fixtures visuales son PNG propios: la suite no descarga datasets externos.

Referencia de validación: 160 pruebas backend con PostgreSQL, local y Docker;
135 aprobadas/25 omitidas sin BD; 17 frontend. Se cubren migraciones,
idempotencia, corrupción, concurrencia, fallos de copia/commit y compatibilidad
histórica. Los conteos cambiarán al añadir pruebas; ejecutar los comandos, no
usar este registro como garantía de cambios posteriores.
