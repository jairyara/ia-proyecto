# Dashboard · Semana 07 — Representaciones del reconocimiento
"""Autómata finito determinista (AFD) del protocolo de entrega POD.

Modela el ciclo de vida de una entrega como una 5-tupla formal
``M = (Q, Σ, δ, q0, F)``:

- ``Q``: estados del protocolo (``q0`` en tránsito, ``q1`` en geocerca,
  ``q2`` validando bultos, ``q3`` entrega exitosa y ``q_fallo`` excepción).
- ``Σ``: alfabeto de eventos ``{A, V, F, C}`` (Arribo, Validación física,
  Firma digital POD y Cancelación).
- ``δ``: tabla de transiciones ``(estado, símbolo) -> estado``.
- ``q0``: estado inicial; ``F = {q3}``: único estado de aceptación.

El autómata no mide distancias ni evalúa reglas: reconoce si la **secuencia
cronológica** de eventos respeta el protocolo. Una firma sin validación
previa (``AF``) o una cancelación intermedia (``AVC``) terminan en
``q_fallo``, que es absorbente: una vez en excepción no hay retorno.
"""

from __future__ import annotations

ALFABETO_POD = {
    "A": "Arribo a la geocerca del cliente",
    "V": "Validación física de bultos",
    "F": "Firma digital de remisión (POD)",
    "C": "Cancelación o rechazo de la entrega",
}

ESTADOS_POD = {
    "q0": "En tránsito hacia el cliente",
    "q1": "Dentro de la geocerca del cliente",
    "q2": "Validando bultos en sitio",
    "q3": "Entrega exitosa auditada",
    "q_fallo": "Excepción: entrega fallida o protocolo violado",
}

ESTADO_INICIAL_POD = "q0"
ESTADOS_ACEPTACION_POD = frozenset({"q3"})

# δ: solo existen las transiciones legales del protocolo; cualquier otro par
# (estado, símbolo) cae en el estado sumidero q_fallo.
TRANSICIONES_POD = {
    ("q0", "A"): "q1",
    ("q1", "V"): "q2",
    ("q1", "C"): "q_fallo",
    ("q2", "F"): "q3",
    ("q2", "C"): "q_fallo",
    ("q_fallo", "A"): "q_fallo",
    ("q_fallo", "V"): "q_fallo",
    ("q_fallo", "F"): "q_fallo",
    ("q_fallo", "C"): "q_fallo",
}

# Secuencias de demostración: flujo canónico, cancelación, salto ilegal y
# entrega interrumpida antes de la firma.
SECUENCIAS_DEMOSTRACION = ("AVF", "AVC", "AF", "AV")

RESUMENES_POD = {
    True: "Secuencia aceptada: la entrega cumplió el protocolo completo A → V → F.",
    False: "Secuencia no aceptada: el protocolo quedó incompleto o violado.",
}


def validar_entrega(secuencia: str) -> dict:
    """Recorre el AFD símbolo a símbolo y devuelve la traza completa.

    Cada paso registra el estado de origen, el símbolo leído, el estado de
    destino y si la transición existe en la tabla legal; los símbolos fuera
    del alfabeto o las transiciones no declaradas conducen a ``q_fallo``.
    """
    estado = ESTADO_INICIAL_POD
    traza = []
    for paso, simbolo in enumerate(secuencia, start=1):
        transicion_legal = (estado, simbolo) in TRANSICIONES_POD
        destino = TRANSICIONES_POD.get((estado, simbolo), "q_fallo")
        traza.append(
            {
                "paso": paso,
                "simbolo": simbolo,
                "significado": ALFABETO_POD.get(simbolo, "Símbolo fuera del alfabeto"),
                "estado_origen": estado,
                "estado_destino": destino,
                "transicion_legal": transicion_legal,
            }
        )
        estado = destino
    aceptada = estado in ESTADOS_ACEPTACION_POD
    return {
        "secuencia": secuencia,
        "traza": traza,
        "estado_inicial": ESTADO_INICIAL_POD,
        "estado_final": estado,
        "estado_final_descripcion": ESTADOS_POD[estado],
        "aceptada": aceptada,
        "resumen": RESUMENES_POD[aceptada],
    }
