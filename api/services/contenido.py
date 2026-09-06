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
    ("heapq.heappop", "Extrae de la cola de prioridad (min-heap) el nodo con menor costo proyectado f(n) (en A*) o menor g(n) (en Dijkstra) en tiempo O(log N)."),
    ("heapq.heappush", "Inserta un candidato en la cola de prioridad manteniendo el orden del min-heap en tiempo O(log N)."),
    ("nuevo_g =", "Calcula el costo real acumulado si se avanza hasta este vecino: g(vecino) = g(actual) + c(actual, vecino)."),
    ("f_nxt =", "Aplica la función de evaluación A*: f(n) = g(n) + h(n), sumando tiempo recorrido g(n) y tiempo estimado a la meta h(n)."),
    ("came_from", "Registra predecesores para reconstruir el camino óptimo hacia atrás al alcanzar la meta."),
    ("train_test_split", "Divide los pedidos en 75% entrenamiento y 25% evaluación con partición estratificada para preservar la proporción de retrasos."),
    ("pipeline.fit", "Ajusta preprocesamiento (StandardScaler, OneHotEncoder) y clasificador únicamente con datos de entrenamiento (sin fuga de datos)."),
    ("predict_proba", "Obtiene la probabilidad estimada de pertenecer a cada clase evaluando la función logística sigmoide."),
    ("predicciones = pipeline.predict", "Genera etiquetas binarias sobre el conjunto de evaluación independiente (X_test) que el modelo no vio al entrenar."),
    ("accuracy_score", "Calcula la proporción total de predicciones correctas: (VP + VN) / Total."),
    ("f1_score", "Calcula el F1-score: 2·(Prec·Rec)/(Prec+Rec), media armónica que balancea falsas alarmas y retrasos no detectados."),
    ("confusion_matrix", "Cuenta verdaderos positivos, falsos positivos, verdaderos negativos y falsos negativos."),
    ("OneHotEncoder", "Convierte la prioridad categórica en columnas binarias (one-hot) sin imponer un orden numérico artificial."),
    ("StandardScaler", "Estandariza variables numéricas mediante z-score: z = (x - μ) / σ usando la media y desviación estándar del entrenamiento."),
    ("joblib.dump", "Guarda el pipeline entrenado para reutilizar exactamente sus transformaciones en inferencias futuras."),
    ("np.random.default_rng", "Crea un generador pseudoaleatorio local controlado por una semilla fija para asegurar reproducibilidad total."),
    ("log_odds =", "Combina linealmente las condiciones logísticas (tráfico, pico, distancia, ventana) para construir el log-odds base z = β0 + Σ βi·xi."),
    ("probabilidad = 1.0 / (1.0 + np.exp(-log_odds))", "Aplica la función logística sigmoide σ(z) = 1 / (1 + e^-z) para acotar el riesgo de retraso en [0.0, 1.0]."),
    ("retrasado = (probabilidad >= 0.5)", "Aplica la regla de decisión con umbral 0.5: clasifica como retrasado (1) si la probabilidad es ≥ 50%."),
    ("flips =", "Introduce un 10% de ruido aleatorio para que la etiqueta simule imprevistos reales y no sea trivialmente separable."),
    ("unicodedata.normalize", "Separa letras y tildes (forma NFD) antes de retirar marcas diacríticas para normalizar texto."),
    ("contains_keyword", "Exige coincidencias de palabras o frases completas con límites de palabra para evitar falsos positivos."),
    ("matched_keywords", "Conserva las palabras clave exactas que justifican cada clasificación con evidencia auditable."),
    ("ranked = sorted", "Ordena áreas por puntaje de evidencia léxica y usa el orden del catálogo para desempatar."),
    ("haversine", "Calcula la distancia geodésica en línea recta sobre la esfera terrestre entre dos coordenadas geográficas."),
    ("grafo.bloquear_arista", "Marca el tramo vial como no transitable en el grafo para que los algoritmos busquen rutas alternas."),
    ("grafo.desbloquear_arista", "Restaura la transitabilidad de una vía previamente bloqueada en el grafo."),
    ("replanificar_ruta", "Simula el hallazgo de una vía cerrada durante la entrega y recalcula la ruta óptima con A* desde la posición actual."),
    ("GrafoEntregas.desde", "Construye la red vial (espacio de estados) con nodos de paradas y aristas ponderadas que consumen los algoritmos."),
    ("registrar_explicacion", "Activa el registro paso a paso de estados y costos para trazabilidad y visualización sin cambiar la solución calculada."),
    ("TfidfVectorizer", "Convierte textos de protocolos en vectores ponderados: da más peso a términos logísticos raros y menos a los comunes."),
    ("fit_transform", "Aprende el vocabulario de la base documental y construye su matriz de pesos TF-IDF."),
    ("cosine_similarity", "Mide la afinidad angular cos(θ) = (u·v)/(||u||·||v||) entre la consulta del operador y cada protocolo logístico."),
    ("similarities.argmax", "Selecciona el índice del protocolo operativo con mayor similitud coseno respecto a la consulta."),
    ("make_pipeline", "Encadena vectorización y clasificador en un único flujo garantizando ausencia total de data leakage."),
    ("LogisticRegression", "Modelo lineal probabilístico que aprende a predecir la probabilidad de cada categoría operativa."),
    ("RandomForestClassifier", "Ensamble no lineal de 200 árboles de decisión con muestreo aleatorio para contrastar con el modelo lineal."),
    ("detonantes =", "Registra las palabras exactas de la consulta que activaron la regla experta para auditoría."),
    ("queue.popleft", "Extrae de la cola FIFO en tiempo constante O(1) el nodo más antiguo para expandir el siguiente nivel en BFS."),
    ("queue.append", "Agrega un nodo al final de la cola FIFO para ser explorado en el siguiente nivel de profundidad de BFS."),
    ("while cur is not None", "Recorre hacia atrás el diccionario came_from desde el destino hasta el origen para reconstruir el camino óptimo."),
    ("for nxt, costo_paso in grafo.vecinos", "Itera sobre los vecinos accesibles y no bloqueados del nodo actual junto con su costo de desplazamiento."),
    ("if current == meta", "Test de meta: evalúa si el nodo extraído es el destino final. En A* y Dijkstra garantiza costo mínimo."),
)

IMPORT_EXPLANATIONS: dict[str, str] = {
    "pandas": "Importa la librería pandas (alias 'pd') para cargar, transformar y analizar tablas de pedidos logísticos (DataFrames).",
    "numpy": "Importa la librería numpy (alias 'np') para cálculo numérico vectorial, operaciones de matrices y funciones matemáticas/probabilísticas.",
    "heapq": "Importa el módulo heapq de colas de prioridad (min-heap binario) para extraer en tiempo O(log N) el nodo con menor f(n) o g(n).",
    "math": "Importa el módulo math de la biblioteca estándar (sin, cos, atan2, sqrt, radians) para calcular la distancia de Haversine.",
    "time": "Importa el módulo time para cronometrar con alta resolución (time.perf_counter) el tiempo real de cómputo en milisegundos.",
    "deque": "Importa deque (cola de doble extremo) para implementar la cola FIFO de BFS con inserciones y extracciones eficientes en O(1).",
    "dataclass": "Importa el decorador @dataclass para crear estructuras de datos inmutables y tipadas (nodos, resultados de búsqueda y métricas).",
    "field": "Importa field para configurar valores predeterminados mutables (como listas y diccionarios) en clases decoradas con @dataclass.",
    "Path": "Importa Path de pathlib para gestionar rutas de archivos de manera robusta y compatible entre sistemas operativos (Linux/Windows).",
    "re": "Importa el módulo re para búsqueda, coincidencia y limpieza de texto mediante expresiones regulares.",
    "json": "Importa el módulo json para leer y exportar métricas, grafos y configuraciones en formato estructurado JSON.",
    "unicodedata": "Importa unicodedata para normalizar cadenas de texto (descomposición NFD) y remover tildes/acentos diacríticos de forma uniforme.",
    "joblib": "Importa joblib para guardar y cargar en disco los modelos entrenados y sus transformaciones de preprocesamiento.",
    "argparse": "Importa argparse para gestionar argumentos y opciones desde la línea de comandos de manera estándar.",
    "StandardScaler": "Importa StandardScaler de scikit-learn para estandarizar variables numéricas continuas mediante z-score: z = (x - μ) / σ.",
    "OneHotEncoder": "Importa OneHotEncoder de scikit-learn para transformar variables categóricas (prioridad alta/media/baja) en columnas binarias (one-hot).",
    "ColumnTransformer": "Importa ColumnTransformer de scikit-learn para aplicar transformaciones distintas a columnas numéricas y categóricas en un solo paso.",
    "Pipeline": "Importa Pipeline de scikit-learn para encadenar preprocesamiento y clasificador, garantizando ausencia de fuga de datos (data leakage).",
    "make_pipeline": "Importa make_pipeline para encadenar vectorización TF-IDF y clasificador en un único flujo sin data leakage.",
    "LogisticRegression": "Importa Regresión Logística (modelo supervisado interpretable) para predecir probabilidades de retraso mediante la función sigmoide.",
    "RandomForestClassifier": "Importa Random Forest (ensamble de 200 árboles de decisión con bagging) para comparar el rendimiento contra la regresión logística.",
    "train_test_split": "Importa train_test_split para dividir los pedidos en 75% entrenamiento y 25% evaluación independiente de forma estratificada.",
    "accuracy_score": "Importa accuracy_score para medir la exactitud global (porcentaje de predicciones correctas sobre el total).",
    "f1_score": "Importa f1_score para calcular la media armónica entre precisión y exhaustividad (recall), métrica reina ante clases desbalanceadas.",
    "confusion_matrix": "Importa confusion_matrix para desglosar aciertos y errores en Verdaderos Positivos, Falsos Positivos, Verdaderos Negativos y Falsos Negativos.",
    "TfidfVectorizer": "Importa TfidfVectorizer para convertir textos de protocolos operativos en vectores numéricos ponderados por frecuencia TF-IDF.",
    "cosine_similarity": "Importa cosine_similarity para medir la afinidad angular cos(θ) entre el vector de la consulta y los protocolos logísticos.",
    "a_estrella": "Importa el algoritmo de búsqueda informada A* que encuentra la ruta óptima minimizando la función de costo f(n) = g(n) + h(n).",
    "ResultadoBusqueda": "Importa la estructura ResultadoBusqueda con la ruta óptima, costo acumulado, nodos explorados y tiempo de cómputo.",
    "dijkstra": "Importa el algoritmo de Dijkstra (búsqueda de costo uniforme con heurística h(n)=0) como línea base de comparación para A*.",
    "bfs": "Importa búsqueda en anchura (BFS) que encuentra el camino con menor número de saltos mediante una cola FIFO.",
    "replanificar_ruta": "Importa la función de replanificación que simula vías bloqueadas y recalcula la ruta óptima con A* desde el punto actual.",
    "GrafoEntregas": "Importa la clase GrafoEntregas que modela la red de transporte (nodos de depósito/clientes y aristas ponderadas con lista de adyacencia).",
    "Parada": "Importa la clase Parada que modela cada punto de entrega o depósito (coordenadas GPS, tipo de parada y demanda de paquetes).",
    "haversine_km": "Importa la función de distancia geodésica de Haversine para calcular la heurística admisible en línea recta entre coordenadas GPS.",
    "SistemaHibridoLogistica": "Importa el motor híbrido trazable que combina reglas expertas simbólicas, similitud documental TF-IDF y clasificación supervisada.",
}

VARIABLE_SEMANTICS: dict[str, str] = {
    "distancia_km": "Variable numérica continua que guarda la distancia del trayecto de entrega en kilómetros (km).",
    "volumen_m3": "Variable numérica continua que guarda el volumen del paquete o carga a entregar en metros cúbicos (m³).",
    "ventana_min": "Variable numérica discreta que guarda el tamaño de la ventana horaria pactada con el cliente en minutos (min).",
    "trafico_index": "Variable numérica continua que guarda el nivel de congestión vehicular normalizado entre 0.0 (fluido) y 1.0 (trancón total).",
    "cadena_frio": "Variable indicadora binaria: 1 si el pedido requiere refrigeración estricta, 0 en caso contrario.",
    "hora_pico": "Variable indicadora binaria: 1 si la entrega ocurre en horas de alto tráfico vehicular, 0 en horario valle.",
    "zona_rural": "Variable indicadora binaria: 1 si el destino se encuentra en área rural o de difícil acceso, 0 en zona urbana.",
    "prioridad": "Variable categórica ('alta', 'media', 'baja') que guarda el nivel de urgencia o servicio pactado para la entrega.",
    "retrasado": "Variable objetivo binaria (etiqueta supervisada): 1 si el pedido sufrió retraso, 0 si se entregó puntualmente.",
    "probabilidad": "Guarda la probabilidad estimada de retraso en el intervalo [0.0, 1.0] calculada mediante la función sigmoide logística.",
    "log_odds": "Guarda el valor de la combinación lineal z = β0 + Σ βi·xi que representa el logaritmo de la razón de momios de retraso.",
    "flips": "Guarda una máscara booleana de ruido aleatorio del 10% para simular contingencias reales y evitar separabilidad artificial.",
    "frontier": "Cola de prioridad (min-heap) que contiene los nodos candidatos ordenados por costo f(n) = g(n) + h(n) o g(n).",
    "g_score": "Diccionario que asocia cada nodo con su costo real acumulado mínimo g(n) desde el depósito de origen.",
    "f_score": "Diccionario que asocia cada nodo con su costo proyectado total f(n) = g(n) + h(n) hacia el destino.",
    "came_from": "Diccionario de punteros que guarda el nodo predecesor de cada parada para reconstruir el camino óptimo.",
    "queue": "Cola FIFO (First-In, First-Out) que almacena los nodos a explorar por niveles en la búsqueda BFS.",
    "visitados": "Conjunto (set) de nodos ya alcanzados para prevenir ciclos infinitos y exploraciones redundantes.",
    "current": "Identificador del nodo o parada actual que se está expandiendo en la presente iteración del algoritmo.",
    "nuevo_g": "Costo acumulado calculado si se transita por el nodo actual hacia el vecino: g(actual) + c(actual, vecino).",
    "f_nxt": "Función de evaluación de A* para el vecino: f(vecino) = nuevo_g + h(vecino).",
    "costo_paso": "Peso o costo directo de desplazamiento entre el nodo actual y el vecino inmediato.",
    "costo_total": "Costo acumulado total del camino óptimo en segundos de viaje o distancia en kilómetros.",
    "nodos_expandidos": "Contador de nodos extraídos de la frontera, métrica central del esfuerzo computacional.",
    "nodos_visitados": "Contador de nodos únicos insertados en la frontera o descubiertos durante la exploración.",
    "tiempo_ms": "Tiempo de cómputo real transcurrido medido en milisegundos.",
    "ruta": "Lista ordenada de identificadores de paradas [nodo_1, nodo_2, ...] que forman el camino óptimo.",
    "explicacion": "Lista con el registro paso a paso de estados, costos y decisiones para auditoría y sustentación.",
    "aristas_bloqueadas": "Conjunto de aristas dirigidas (origen, destino) cerradas por obras o congestión vehicular.",
    "X_train": "Matriz de características de entrenamiento (75% de los pedidos) usada para ajustar el modelo.",
    "X_test": "Matriz de características de evaluación independiente (25% de los pedidos) para evaluar sin sesgos.",
    "y_train": "Vector de etiquetas de retraso correspondientes al conjunto de entrenamiento.",
    "y_test": "Vector de etiquetas de retraso reales de prueba para medir exactitud y F1-score sin trampa.",
    "predicciones": "Vector de predicciones binarias generadas por el modelo sobre los datos de prueba.",
}


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


def _explicar_import(limpio: str) -> str:
    """Explica pedagógicamente la razón e impacto del paquete o símbolo importado."""
    for clave, explicacion in IMPORT_EXPLANATIONS.items():
        if re.search(rf"\b{re.escape(clave)}\b", limpio):
            return explicacion
    if limpio.startswith("import "):
        modulo = limpio[7:].split()[0].split(".")[0].strip(",")
        return f"Importa la librería o módulo `{modulo}` para disponer de sus herramientas en este componente logístico."
    if limpio.startswith("from "):
        partes = limpio.split()
        if len(partes) >= 2:
            modulo = partes[1].split(".")[0]
            return f"Importa funciones o clases del módulo `{modulo}` para modularizar y reutilizar la lógica de entrega."
    return "Importa nombres y utilidades necesarios para estructurar y ejecutar el ejercicio del dominio logístico."


def _buscar_semantica_variable(destino: str) -> str | None:
    """Identifica el significado y unidades que guarda la variable asignada."""
    nombre_var = re.split(r"[:\[\].\s]", destino)[0].strip()
    if nombre_var in VARIABLE_SEMANTICS:
        return VARIABLE_SEMANTICS[nombre_var]
    for clave, semantica in VARIABLE_SEMANTICS.items():
        if clave in destino:
            return semantica
    return None


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
        return "importación", _explicar_import(limpio)
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
        semantica = _buscar_semantica_variable(destino)
        if semantica:
            return "asignación", f"Asigna `{destino}`: {semantica}{contexto}"
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
