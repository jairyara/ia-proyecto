"""Catálogo seguro de código e informes para el espacio didáctico semanal.

Solo se exponen rutas declaradas en :data:`SEMANAS`. Las explicaciones se
calculan sobre el archivo real, combinando estructura AST, contexto de dominio
y descripciones específicas para las sentencias centrales de cada ejercicio.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent


def _workspace_editor() -> str:
    """Ruta del repositorio vista por el IDE que se ejecuta en el host.

    En desarrollo local coincide con ``ROOT``. Cuando la API corre dentro de
    Docker, Compose inyecta la ruta del host porque ``/app`` no existe para el
    IDE del usuario.
    """
    configurada = os.getenv("DASHBOARD_EDITOR_WORKSPACE", "").strip()
    return configurada.rstrip("/\\") or str(ROOT)


SEMANAS: dict[str, dict[str, Any]] = {
    "semana02": {
        "numero": 2,
        "titulo": "Aprendizaje supervisado",
        "ejercicios": [
            {
                "id": "riesgo-retraso",
                "titulo": "Baseline de riesgo de retraso",
                "descripcion": "Generación sintética, entrenamiento, evaluación e inferencia.",
                "archivos": [
                    ("datos-sinteticos", "Generador de pedidos", "src/datos/sintetico.py"),
                    ("modelo-riesgo", "Modelo supervisado", "src/modelado/riesgo_retraso.py"),
                ],
            },
            {
                "id": "datos-amazon",
                "titulo": "Datos Amazon Last Mile",
                "descripcion": "Descarga, limpieza y curaduría de rutas reales.",
                "archivos": [
                    ("datos-amazon", "Curaduría Amazon", "src/datos/amazon.py"),
                ],
            },
        ],
        "informes": [
            ("sem02-riesgo", "Riesgo de retraso", "reports/sem-02-riesgo-retraso.md"),
            ("sem02-amazon", "Datos Amazon Last Mile", "reports/sem-02-datos-amazon-last-mile.md"),
        ],
    },
    "semana03": {
        "numero": 3,
        "titulo": "Clasificación simbólica",
        "ejercicios": [
            {
                "id": "clasificacion-requerimientos",
                "titulo": "Clasificador de requerimientos",
                "descripcion": "Taxonomía, normalización y reglas explicables.",
                "archivos": [
                    ("reglas-requerimientos", "Motor de reglas", "src/clasificacion/requerimientos.py"),
                    ("acceso-clasificador", "Acceso compatible", "src/clasificador_requerimientos.py"),
                ],
            },
        ],
        "informes": [
            ("sem03-taxonomia", "Taxonomía de IA", "reports/sem-03-taxonomia-ia.md"),
            ("sem03-clasificacion", "Clasificación de requerimientos", "reports/sem-03-clasificacion-requerimientos.md"),
        ],
    },
    "semana04": {
        "numero": 4,
        "titulo": "Búsqueda y replanificación",
        "ejercicios": [
            {
                "id": "busqueda-rutas",
                "titulo": "A*, líneas base y replanificación",
                "descripcion": "Grafo, heurísticas, búsquedas y respuesta a vías cerradas.",
                "archivos": [
                    ("grafo-entregas", "Grafo de entregas", "src/busqueda/grafo.py"),
                    ("a-estrella", "Búsqueda A*", "src/busqueda/a_estrella.py"),
                    ("no-informada", "Dijkstra y BFS", "src/busqueda/no_informada.py"),
                    ("replanificacion", "Replanificación", "src/busqueda/replanificacion.py"),
                    ("experimento-rutas", "Experimento reproducible", "src/busqueda_rutas.py"),
                ],
            },
        ],
        "informes": [
            ("sem04-busqueda", "Búsqueda de rutas", "reports/sem-04-busqueda-rutas.md"),
        ],
    },
    "semana05": {
        "numero": 5,
        "titulo": "Sistema híbrido trazable",
        "ejercicios": [
            {
                "id": "sistema-hibrido",
                "titulo": "Reglas + TF-IDF + clasificación",
                "descripcion": "Triple señal auditada: reglas expertas, recuperación documental y clase predicha.",
                "archivos": [
                    ("motor-hibrido", "Motor híbrido", "src/hibrido/sistema.py"),
                    ("experimento-hibrido", "Experimento reproducible", "src/sistema_hibrido.py"),
                ],
            },
        ],
        "informes": [
            ("sem05-hibrido", "Sistema híbrido de trazabilidad", "reports/sem-05-sistema-hibrido.md"),
        ],
    },
}


FUNCTION_DESCRIPTIONS = {
    "generar_pedidos": "Crea pedidos sintéticos reproducibles y calcula su etiqueta de retraso.",
    "entrenar_y_evaluar": "Divide los datos, entrena los candidatos y compara sus métricas.",
    "construir_pipelines": "Define preprocesamiento y modelos dentro de pipelines sin fuga de datos.",
    "guardar_artefactos": "Serializa el modelo elegido y sus métricas reproducibles.",
    "classify_requirement": "Aplica todas las categorías y ordena la evidencia encontrada.",
    "normalize_text": "Normaliza el texto para que las reglas comparen vocabulario equivalente.",
    "contains_keyword": "Comprueba palabras o frases completas y evita falsos positivos parciales.",
    "a_estrella": "Encuentra una ruta mínima priorizando f(n) = g(n) + h(n).",
    "dijkstra": "Encuentra el costo mínimo usando únicamente el costo acumulado g(n).",
    "bfs": "Explora el grafo por niveles mediante una cola FIFO.",
    "replanificar_ruta": "Bloquea un tramo y calcula una ruta alternativa desde el estado actual.",
    "evaluar_reglas": "Evalúa las reglas expertas y reporta qué palabra de la consulta disparó cada una.",
    "recuperar_evidencia": "Recupera el protocolo operativo más afín con TF-IDF y similitud coseno.",
    "clasificar": "Predice la categoría operativa y su distribución de probabilidad.",
    "answer": "Responde la consulta combinando reglas, evidencia documental y clase predicha.",
    "load_documents": "Carga la base de conocimiento y siembra los protocolos por defecto si falta el archivo.",
    "responder_consulta": "Adapta la respuesta del motor híbrido al contrato de la API.",
    "obtener_contexto": "Expone reglas, clases y ejemplos para documentar la interfaz.",
    "desde_cuadricula": "Transforma una cuadrícula transitable en un grafo dirigido ponderado.",
    "desde_amazon_ruta": "Transforma una ruta curada de Amazon en nodos y aristas ponderadas.",
    "main": "Orquesta la ejecución reproducible desde la línea de comandos.",
}


DOMAIN_EXPLANATIONS: tuple[tuple[str, str], ...] = (
    ("heapq.heappop", "Extrae de la cola de prioridad el candidato con menor costo estimado."),
    ("heapq.heappush", "Inserta un candidato en la cola manteniendo el orden de prioridad."),
    ("nuevo_g =", "Calcula el costo real acumulado si se avanza hasta este vecino."),
    ("f_nxt =", "Combina costo real y heurística mediante f(n) = g(n) + h(n)."),
    ("came_from", "Registra predecesores para reconstruir después la ruta encontrada."),
    ("train_test_split", "Separa entrenamiento y evaluación con una partición independiente."),
    ("pipeline.fit", "Ajusta preprocesamiento y modelo usando únicamente el conjunto de entrenamiento."),
    ("predict_proba", "Obtiene la probabilidad estimada de pertenecer a cada clase."),
    ("predicciones = pipeline.predict", "Genera etiquetas binarias sobre datos que el modelo no usó para ajustarse."),
    ("accuracy_score", "Calcula la proporción total de predicciones correctas."),
    ("f1_score", "Calcula el equilibrio entre precisión y cobertura de la clase de retraso."),
    ("confusion_matrix", "Cuenta verdaderos y falsos positivos y negativos."),
    ("OneHotEncoder", "Convierte la prioridad categórica en columnas numéricas sin orden artificial."),
    ("StandardScaler", "Estandariza variables numéricas usando estadísticas del entrenamiento."),
    ("joblib.dump", "Guarda el pipeline entrenado para reutilizar exactamente sus transformaciones."),
    ("np.random.default_rng", "Crea un generador aleatorio local controlado por una semilla."),
    ("log_odds =", "Combina condiciones logísticas para construir la probabilidad sintética base."),
    ("flips =", "Introduce ruido controlado para que la etiqueta no sea una regla perfectamente trivial."),
    ("unicodedata.normalize", "Separa letras y tildes antes de retirar marcas diacríticas."),
    ("contains_keyword", "Exige coincidencias de palabras o frases completas."),
    ("matched_keywords", "Conserva las palabras que justifican cada clasificación."),
    ("ranked = sorted", "Ordena áreas por puntaje y usa el orden del catálogo para desempatar."),
    ("haversine", "Calcula una estimación geodésica en línea recta entre dos coordenadas."),
    ("grafo.bloquear_arista", "Marca el tramo como no transitable para la siguiente planificación."),
    ("GrafoEntregas.desde", "Construye la representación de estados que consumen los algoritmos."),
    ("registrar_explicacion", "Activa evidencia adicional sin cambiar la solución calculada."),
    ("TfidfVectorizer", "Convierte texto en vectores ponderados: más peso a términos informativos y menos a los comunes."),
    ("fit_transform", "Aprende el vocabulario de la base documental y construye su matriz TF-IDF."),
    ("cosine_similarity", "Mide el parecido angular entre la consulta y cada protocolo de la base."),
    ("similarities.argmax", "Selecciona la posición del documento con mayor similitud coseno."),
    ("make_pipeline", "Encadena vectorización y clasificador en un único flujo sin fuga de datos."),
    ("LogisticRegression", "Modelo supervisado que aprende a separar las categorías operativas del dominio."),
    ("predict_proba", "Obtiene la probabilidad estimada de pertenecer a cada clase."),
    ("detonantes =", "Registra las palabras exactas de la consulta que activaron la regla experta."),
    ("classifier.fit", "Entrena el clasificador con los ejemplos etiquetados del dominio logístico."),
    ("unicodedata.category", "Filtra las marcas diacríticas para normalizar el texto de entrada."),
)


@dataclass(frozen=True)
class Bloque:
    nombre: str
    tipo: str
    inicio: int
    fin: int
    descripcion: str


def _ruta_segura(relativa: str) -> Path:
    ruta = (ROOT / relativa).resolve()
    try:
        ruta.relative_to(ROOT)
    except ValueError as error:
        raise ValueError("La ruta solicitada sale del repositorio") from error
    if not ruta.is_file():
        raise FileNotFoundError(f"No existe el contenido registrado: {relativa}")
    return ruta


def _indice_catalogo() -> tuple[dict[str, dict], dict[str, dict]]:
    archivos: dict[str, dict] = {}
    informes: dict[str, dict] = {}
    for semana_id, semana in SEMANAS.items():
        for ejercicio in semana["ejercicios"]:
            for archivo_id, titulo, ruta in ejercicio["archivos"]:
                archivos[archivo_id] = {
                    "id": archivo_id,
                    "titulo": titulo,
                    "ruta": ruta,
                    "ejercicio_id": ejercicio["id"],
                    "semana_id": semana_id,
                }
        for informe_id, titulo, ruta in semana["informes"]:
            informes[informe_id] = {
                "id": informe_id,
                "titulo": titulo,
                "ruta": ruta,
                "semana_id": semana_id,
            }
    return archivos, informes


def catalogo_semanas() -> dict[str, list[dict[str, Any]]]:
    semanas = []
    for semana_id, semana in sorted(SEMANAS.items(), key=lambda item: item[1]["numero"]):
        semanas.append(
            {
                "id": semana_id,
                "numero": semana["numero"],
                "titulo": semana["titulo"],
                "ejercicios": [
                    {
                        "id": ejercicio["id"],
                        "titulo": ejercicio["titulo"],
                        "descripcion": ejercicio["descripcion"],
                        "archivos": [
                            {"id": item[0], "titulo": item[1], "ruta": item[2]}
                            for item in ejercicio["archivos"]
                        ],
                    }
                    for ejercicio in semana["ejercicios"]
                ],
                "informes": [
                    {"id": item[0], "titulo": item[1], "ruta": item[2]}
                    for item in semana["informes"]
                ],
            }
        )
    return {"semanas": semanas}


def _bloques_python(source: str) -> list[Bloque]:
    tree = ast.parse(source)
    bloques: list[Bloque] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            tipo = "clase" if isinstance(node, ast.ClassDef) else "función"
            descripcion = FUNCTION_DESCRIPTIONS.get(
                node.name,
                f"Define la {tipo} `{node.name}` y agrupa su comportamiento.",
            )
            bloques.append(
                Bloque(
                    nombre=node.name,
                    tipo=tipo,
                    inicio=node.lineno,
                    fin=node.end_lineno or node.lineno,
                    descripcion=descripcion,
                )
            )
    return sorted(bloques, key=lambda item: (item.inicio, -(item.fin - item.inicio)))


def _bloque_linea(bloques: list[Bloque], numero: int) -> Bloque | None:
    candidatos = [item for item in bloques if item.inicio <= numero <= item.fin]
    return min(candidatos, key=lambda item: item.fin - item.inicio) if candidatos else None


def _explicar_linea(texto: str, numero: int, bloque: Bloque | None) -> tuple[str, str]:
    limpio = texto.strip()
    contexto = f" Dentro de `{bloque.nombre}`: {bloque.descripcion}" if bloque else ""
    if not limpio:
        return "espacio", "Separa visualmente bloques para mejorar la lectura del archivo."
    if limpio.startswith("#"):
        return "comentario", f"Documenta la intención del bloque: {limpio.lstrip('#').strip()}"
    for fragmento, explicacion in DOMAIN_EXPLANATIONS:
        if fragmento in limpio:
            return "dominio", explicacion + contexto
    if limpio.startswith(('"""', "'''")):
        return "documentación", "Inicia o termina documentación legible para personas y herramientas."
    if limpio.startswith("from ") or limpio.startswith("import "):
        return "importación", "Importa nombres necesarios sin ejecutar el ejercicio principal todavía."
    if limpio.startswith("@"):
        return "decorador", "Aplica comportamiento adicional a la definición que aparece a continuación."
    if limpio.startswith("class "):
        return "clase", f"Declara una estructura que agrupa datos y comportamiento.{contexto}"
    if limpio.startswith(("def ", "async def ")):
        return "función", f"Declara una unidad reutilizable con entradas y salida definidas.{contexto}"
    if limpio.startswith(("if ", "elif ")):
        return "condición", f"Evalúa una condición y ejecuta el bloque solo cuando se cumple.{contexto}"
    if limpio == "else:":
        return "condición", f"Define el camino alternativo cuando las condiciones previas no se cumplen.{contexto}"
    if limpio.startswith(("for ", "while ")):
        return "iteración", f"Repite el bloque sobre elementos o mientras se mantenga una condición.{contexto}"
    if limpio.startswith("return"):
        return "retorno", f"Finaliza la función y entrega este resultado al código llamador.{contexto}"
    if limpio.startswith("raise "):
        return "validación", f"Detiene la operación con un error explícito ante una entrada inválida.{contexto}"
    if limpio.startswith(("try:", "except ", "finally:")):
        return "control de errores", f"Controla fallos esperables y garantiza una respuesta predecible.{contexto}"
    if limpio.startswith("with "):
        return "recurso", f"Abre un recurso y garantiza su cierre al terminar el bloque.{contexto}"
    if limpio in {"break", "continue", "pass"}:
        return "flujo", f"Modifica explícitamente el avance del bloque actual.{contexto}"
    if re.match(r"^[A-Za-z_][\w.\[\], ]*\s*[+:]?=", limpio):
        destino = limpio.split("=", 1)[0].strip().rstrip(":")
        return "asignación", f"Calcula y guarda un valor en `{destino}` para reutilizarlo después.{contexto}"
    if limpio[0] in ")]}":
        return "continuación", f"Cierra una expresión o colección iniciada en líneas anteriores.{contexto}"
    if limpio.endswith(("(", "[", "{")) or limpio.endswith(","):
        return "continuación", f"Continúa una llamada o estructura distribuida en varias líneas.{contexto}"
    return "sentencia", f"Ejecuta esta instrucción como parte del flujo del ejercicio.{contexto}"


def obtener_codigo(archivo_id: str) -> dict[str, Any]:
    archivos, _ = _indice_catalogo()
    if archivo_id not in archivos:
        raise KeyError(f"Archivo no registrado: {archivo_id}")
    metadata = archivos[archivo_id]
    ruta = _ruta_segura(metadata["ruta"])
    source = ruta.read_text(encoding="utf-8")
    bloques = _bloques_python(source)
    lineas = []
    for numero, texto in enumerate(source.splitlines(), start=1):
        bloque = _bloque_linea(bloques, numero)
        tipo, explicacion = _explicar_linea(texto, numero, bloque)
        lineas.append(
            {
                "numero": numero,
                "codigo": texto,
                "tipo": tipo,
                "explicacion": explicacion,
                "bloque": bloque.nombre if bloque else None,
                "resumen_bloque": bloque.descripcion if bloque else None,
            }
        )
    return {
        **metadata,
        "workspace_editor": _workspace_editor(),
        "lenguaje": "python",
        "hash": hashlib.sha256(source.encode("utf-8")).hexdigest()[:16],
        "total_lineas": len(lineas),
        "lineas": lineas,
        "outline": [
            {
                "nombre": bloque.nombre,
                "tipo": bloque.tipo,
                "linea": bloque.inicio,
                "fin": bloque.fin,
                "descripcion": bloque.descripcion,
            }
            for bloque in bloques
        ],
    }


def obtener_informe(informe_id: str) -> dict[str, Any]:
    _, informes = _indice_catalogo()
    if informe_id not in informes:
        raise KeyError(f"Informe no registrado: {informe_id}")
    metadata = informes[informe_id]
    ruta = _ruta_segura(metadata["ruta"])
    contenido = ruta.read_text(encoding="utf-8")
    encabezados = []
    for numero, linea in enumerate(contenido.splitlines(), start=1):
        coincidencia = re.match(r"^(#{1,6})\s+(.+?)\s*$", linea)
        if coincidencia:
            encabezados.append(
                {
                    "nivel": len(coincidencia.group(1)),
                    "titulo": coincidencia.group(2),
                    "linea": numero,
                }
            )
    return {
        **metadata,
        "contenido": contenido,
        "encabezados": encabezados,
        "palabras": len(re.findall(r"\b\w+\b", contenido, flags=re.UNICODE)),
        "hash": hashlib.sha256(contenido.encode("utf-8")).hexdigest()[:16],
    }


TRACE_FILES = {
    "a_estrella": (
        "a-estrella",
        "a_estrella.py",
        "a_estrella",
        {
            "init": "frontier: list[tuple[float, int, str]] =",
            "pop": "f_curr, _, current = heapq.heappop(frontier)",
            "goal": "if current == meta:",
            "neighbors": "for nxt, costo_paso in grafo.vecinos(current):",
            "score": "nuevo_g = g_curr + costo_paso",
            "update": "if nxt not in g_score or nuevo_g < g_score[nxt]:",
            "push": "heapq.heappush(frontier, (f_nxt, contador, nxt))",
            "path": "while cur is not None:",
        },
    ),
    "dijkstra": (
        "no-informada",
        "no_informada.py · Dijkstra",
        "dijkstra",
        {
            "init": "frontier: list[tuple[float, int, str]] = [(0.0, contador, inicio)]",
            "pop": "g_curr, _, current = heapq.heappop(frontier)",
            "goal": "if current == meta:",
            "neighbors": "for nxt, costo_paso in grafo.vecinos(current):",
            "score": "nuevo_g = g_curr + costo_paso",
            "update": "if nxt not in g_score or nuevo_g < g_score[nxt]:",
            "push": "heapq.heappush(frontier, (nuevo_g, contador, nxt))",
            "path": "while cur is not None:",
        },
    ),
    "bfs": (
        "no-informada",
        "no_informada.py · BFS",
        "bfs",
        {
            "init": "queue: deque[str] = deque([inicio])",
            "pop": "current = queue.popleft()",
            "goal": "if current == meta:",
            "neighbors": "for nxt, _ in grafo.vecinos(current):",
            "score": "if nxt not in visitados:",
            "update": "came_from[nxt] = current",
            "push": "queue.append(nxt)",
            "path": "while cur is not None:",
        },
    ),
}


def fragmento_traza(algoritmo: str) -> tuple[str, list[dict[str, Any]]]:
    """Retorna líneas reales de ``src`` para sincronizarlas con la simulación."""

    archivo_id, etiqueta, bloque_nombre, anchors = TRACE_FILES[algoritmo]
    documento = obtener_codigo(archivo_id)
    bloque = next(
        (item for item in documento["outline"] if item["nombre"] == bloque_nombre),
        None,
    )
    if bloque is None:
        raise RuntimeError(f"No se encontró el bloque de traza {bloque_nombre!r}")
    lineas_bloque = [
        item
        for item in documento["lineas"]
        if bloque["linea"] <= item["numero"] <= bloque["fin"]
    ]
    resultado = []
    for evento, anchor in anchors.items():
        linea = next((item for item in lineas_bloque if anchor in item["codigo"]), None)
        if linea is None:
            raise RuntimeError(f"No se encontró el ancla de traza {evento!r}: {anchor}")
        resultado.append(
            {
                "id": evento,
                "linea": linea["numero"],
                "codigo": linea["codigo"].strip(),
                "explicacion": linea["explicacion"],
            }
        )
    return etiqueta, resultado
