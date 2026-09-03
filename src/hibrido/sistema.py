"""Sistema híbrido de soporte logístico (Semana 5).

Combina tres técnicas del marco tecnológico de la IA sobre la misma consulta
en lenguaje natural:

1. **Reglas expertas** (simbólico): cada regla declara sus palabras clave y la
   acción operativa que dispara. La decisión es determinista y auditable.
2. **Recuperación de información** (TF-IDF + similitud coseno): localiza el
   protocolo operativo (SOP) más afín dentro de ``data/base_conocimiento.txt``.
3. **Clasificación supervisada** (regresión logística): predice la categoría
   operativa del incidente para ruteo y métricas.

La respuesta conserva trazabilidad completa: regla disparada con la palabra
que la activó, evidencia documental con su similitud y clase predicha con la
distribución de probabilidad por categoría.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import unicodedata

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"
KB_PATH = DATA_DIR / "base_conocimiento.txt"
MIN_DOCUMENTOS = 8

DEFAULT_DOCS = [
    "Protocolo 1: Control de temperatura y cadena de frio en transporte de perecederos y farmaceuticos; si la temperatura supera los limites o falla el termografo, se debe activar refrigeracion de emergencia o derivar a centro de acopio cercano.",
    "Protocolo 2: Gestion de congestion y bloqueos viales; ante cierres viales, obras o accidentes de transito que excedan 20 minutos de espera, el sistema debe replanificar la ruta con vias alternas evitando cuellos de botella.",
    "Protocolo 3: Control de capacidad volumetrica y peso maximo de la flota; ante exceso de kilos o sobrecupo vehicular, se debe reasignar la carga a vehiculos de mayor tonelaje o programar un segundo viaje.",
    "Protocolo 4: Cumplimiento de ventanas horarias de entrega; si el retraso en ruta supera el margen de tolerancia del cliente comercial, el despachador debe notificar y renegociar la ventana de recepcion.",
    "Protocolo 5: Gestion de envios prioritarios y pedidos urgentes; los paquetes clasificados como express o de alta prioridad tienen preferencia en la asignacion de flota directa y orden de despacho.",
    "Protocolo 6: Novedad por destinatario ausente o direccion inaccesible; se activa protocolo de reintento de entrega al final de la jornada y custodia temporal en bodega satelite.",
    "Protocolo 7: Transporte de mercancias fragiles y manejo delicado; embalaje especial con sujecion reforzada, velocidad restringida y restriccion de estiba maxima para evitar averias.",
    "Protocolo 8: Restricciones de circulacion urbana y pico y placa ambiental; asignacion inteligente de vehiculos electricos o hibridos para zonas centricas de bajas emisiones y horarios restringidos.",
    "Protocolo 9: Gestion de fallas mecanicas en ruta; reporte telematico inmediato para envio de grua de auxilio y transferencia de pedidos a un movil de respaldo en el sector.",
    "Protocolo 10: Validacion documental y recepcion de mercancia; verificacion digital de remision, firma electronica y captura de comprobante de entrega en dispositivo movil.",
]

CONSULTAS_EJEMPLO = [
    "El furgón refrigerado perdió temperatura y la carga láctea corre riesgo",
    "Accidente grave y congestión vial con cierre en la autopista de reparto",
    "El vehículo superó la capacidad máxima de peso y kilos permitida",
]


@dataclass(frozen=True)
class Regla:
    """Regla experta declarativa: palabras clave -> acción operativa."""

    accion: str
    palabras: tuple[str, ...]
    descripcion: str


# 5 reglas expertas adaptadas al dominio logístico (Proyecto 8).
# A diferencia del script de clase (lambdas anónimas), aquí las reglas son
# datos: el motor evalúa las condiciones y además reporta qué palabra de la
# consulta disparó cada regla, evidencia útil para la sustentación.
RULES: tuple[Regla, ...] = (
    Regla(
        accion="activar_protocolo_cadena_frio",
        palabras=("frio", "temperatura", "refrigerad", "congelad"),
        descripcion="Variación térmica en perecederos o fármacos: activa refrigeración de emergencia o derivación a punto frío.",
    ),
    Regla(
        accion="replanificar_ruta_alterna",
        palabras=("bloqueo", "cierre", "trafico", "congestion", "accidente"),
        descripcion="Contingencia vial: recalcula la ruta con el módulo A* excluyendo la vía afectada.",
    ),
    Regla(
        accion="reasignar_vehiculo_mayor_capacidad",
        palabras=("peso", "capacidad", "sobrecupo", "kilos", "tonelaje", "sobrecarga"),
        descripcion="Restricción de carga: divide la orden o reasigna un vehículo de mayor tonelaje.",
    ),
    Regla(
        accion="renegociar_ventana_entrega",
        palabras=("ventana", "horario", "retraso", "tarde", "plazo"),
        descripcion="Riesgo de incumplimiento de ventana horaria: notifica y actualiza el cronograma de entrega.",
    ),
    Regla(
        accion="escalar_despacho_prioritario",
        palabras=("urgente", "prioritario", "emergencia", "express"),
        descripcion="Envío de alta prioridad: asigna flota directa y lo antepone en la cola de despacho.",
    ),
)

# 16 ejemplos etiquetados del dominio logístico, balanceados en 4 clases.
TRAIN_X = [
    "el furgon de lacteos perdio temperatura en ruta",
    "falla en el sistema de refrigeracion del vehiculo",
    "la carne congelada subio a temperatura critica",
    "alerta termica en transporte de medicamentos biologicos",
    "autopista bloqueada por accidente multiple",
    "cierre total de via por obras de reparacion",
    "congestion severa que retrasa la llegada a zona norte",
    "embotellamiento grave por derrumbe en la carretera",
    "el camion supero la capacidad maxima de peso permitida",
    "exceso de kilos en el despacho de mercancia pesada",
    "sobrecupo volumetrico no caben mas paquetes en la van",
    "carga excede el tonelaje autorizado para este vehiculo",
    "el cliente no se encuentra en el domicilio registrado",
    "entrega tardia fuera de la ventana horaria pactada",
    "paquete express urgente requiere despacho inmediato",
    "destinatario rechaza la entrega por demora en el horario",
]

TRAIN_Y = [
    "cadena_frio",
    "cadena_frio",
    "cadena_frio",
    "cadena_frio",
    "rutas_trafico",
    "rutas_trafico",
    "rutas_trafico",
    "rutas_trafico",
    "capacidad_flota",
    "capacidad_flota",
    "capacidad_flota",
    "capacidad_flota",
    "entregas_clientes",
    "entregas_clientes",
    "entregas_clientes",
    "entregas_clientes",
]

CLASE_DESCRIPCIONES = {
    "cadena_frio": "Incidencias térmicas y conservación de productos sensibles.",
    "rutas_trafico": "Novedades de movilidad: congestión, cierres e incidentes viales.",
    "capacidad_flota": "Restricciones físicas de peso, volumen y capacidad vehicular.",
    "entregas_clientes": "Acuerdos de servicio: ventanas horarias, prioridad y recepción.",
}


def _normalizar(texto: str) -> str:
    """Minúsculas sin tildes para comparar vocabulario de forma estable."""

    base = unicodedata.normalize("NFD", texto.lower())
    return "".join(char for char in base if unicodedata.category(char) != "Mn")


def load_documents() -> list[str]:
    """Carga la base de conocimiento; si no existe, siembra los SOP por defecto."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not KB_PATH.exists():
        KB_PATH.write_text("\n".join(DEFAULT_DOCS), encoding="utf-8")
    docs = [
        line.strip()
        for line in KB_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(docs) < MIN_DOCUMENTOS:
        raise ValueError(
            f"data/base_conocimiento.txt debe contener al menos {MIN_DOCUMENTOS} entradas."
        )
    return docs


DOCS = load_documents()
vectorizer = TfidfVectorizer()
doc_matrix = vectorizer.fit_transform(DOCS)

classifier = make_pipeline(
    TfidfVectorizer(),
    LogisticRegression(max_iter=1000, random_state=42),
)
classifier.fit(TRAIN_X, TRAIN_Y)


def evaluar_reglas(query: str) -> list[dict]:
    """Evalúa las reglas expertas y reporta qué palabra disparó cada una."""

    q = _normalizar(query)
    activadas = []
    for regla in RULES:
        detonantes = [palabra for palabra in regla.palabras if palabra in q]
        if detonantes:
            activadas.append(
                {
                    "accion": regla.accion,
                    "descripcion": regla.descripcion,
                    "detonantes": detonantes,
                }
            )
    return activadas


def recuperar_evidencia(query: str) -> dict:
    """Recupera el protocolo más afín con TF-IDF + similitud coseno."""

    q = _normalizar(query)
    similarities = cosine_similarity(vectorizer.transform([q]), doc_matrix)[0]
    best_index = int(similarities.argmax())
    return {
        "indice": best_index,
        "documento": DOCS[best_index],
        "similitud": float(similarities[best_index]),
    }


def clasificar(query: str) -> dict:
    """Predice la categoría operativa y su distribución de probabilidad."""

    q = _normalizar(query)
    label = str(classifier.predict([q])[0])
    probabilidades = classifier.predict_proba([q])[0]
    clases = classifier.classes_
    return {
        "clase": label,
        "descripcion": CLASE_DESCRIPCIONES.get(label, ""),
        "probabilidades": [
            {"clase": str(clase), "probabilidad": float(probabilidad)}
            for clase, probabilidad in sorted(
                zip(clases, probabilidades), key=lambda item: item[1], reverse=True
            )
        ],
    }


def answer(query: str) -> dict:
    """Responde una consulta con trazabilidad de las tres técnicas."""

    reglas = evaluar_reglas(query)
    evidencia = recuperar_evidencia(query)
    prediccion = clasificar(query)
    return {
        "consulta": query,
        "reglas": [item["accion"] for item in reglas],
        "reglas_detalle": reglas,
        "evidencia": evidencia["documento"],
        "similitud": evidencia["similitud"],
        "clase": prediccion["clase"],
        "clases": prediccion["probabilidades"],
    }
