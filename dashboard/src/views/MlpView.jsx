import { useEffect, useState } from 'react'
import { PageHeader, DataState, useResumen } from './ResumenView.jsx'
import { api } from '../services/api.js'

const percentage = (value) => Number.isFinite(Number(value))
  ? `${(Number(value) * 100).toFixed(1)} %` : '—'

export default function MlpView({ onNavigate }) {
  const { data, error } = useResumen()
  const [modelo, setModelo] = useState(null)
  const [predicciones, setPredicciones] = useState(null)
  const [selectedId, setSelectedId] = useState(null)
  const [ontologia, setOntologia] = useState(null)
  const [modelError, setModelError] = useState('')
  const [ontologyError, setOntologyError] = useState('')

  useEffect(() => {
    let active = true
    Promise.all([api.resumenModeloVisual(), api.prediccionesModeloVisual({ limite: 50 })])
      .then(([resumen, pagina]) => {
        if (active) {
          setModelo(resumen)
          setPredicciones(pagina)
          setSelectedId(pagina.items[0]?.imagen_id ?? null)
        }
      })
      .catch((requestError) => { if (active) setModelError(requestError.message) })
    return () => { active = false }
  }, [])

  useEffect(() => {
    if (selectedId === null) return
    let active = true
    api.ontologiaModeloVisual(selectedId)
      .then((grafo) => { if (active) { setOntologia(grafo); setOntologyError('') } })
      .catch((requestError) => { if (active) setOntologyError(requestError.message) })
    return () => { active = false }
  }, [selectedId])

  const entrenado = modelo?.estado === 'evaluado'
  const total = (modelo?.total_train ?? 0) + (modelo?.total_test ?? 0)
  const ejemplo = predicciones?.items?.find((item) => item.imagen_id === selectedId)
  const relacionesCaso = ontologia?.ejemplo_imagen_id === selectedId
    ? ontologia.relaciones.filter(({ origen }) => origen.startsWith('imagen:') || origen.startsWith('prediccion:'))
    : []
  const matriz = modelo?.matriz_confusion

  return <div className="view-shell data-view">
    <PageHeader eyebrow="CORTE 2 · SEMANA 08" title="Reconocer, registrar e interpretar" description="Un MLP clasifica el estado visible de empaques sintéticos; PostgreSQL conserva la evidencia y una ontología expresa el significado de cada predicción reservada." />
    <DataState data={data} error={error} />
    {modelError && <div className="alert alert--error" role="alert">No se pudo consultar el experimento: {modelError}</div>}
    {!modelo && !modelError && <div role="status" className="learning-loading"><span className="spinner" />Consultando el modelo…</div>}
    {data && modelo?.estado === 'no_entrenado' && <div className="data-warning"><strong>Modelo no registrado.</strong> Las imágenes de demostración existen, pero aún no hay evaluación ni predicciones persistidas. No se inventan resultados.</div>}
    {data && entrenado && <div className="data-warning"><strong>Experimento didáctico · {modelo.version}.</strong> {modelo.aviso} {modelo.accuracy <= modelo.accuracy_baseline && 'El MLP no supera la línea base: no debe usarse para decisiones operativas.'}</div>}
    {data && <div className="data-grid">
      <section className="panel data-section"><span className="eyebrow">01 · ORIGEN</span><h2>Imágenes de demostración</h2>
        <p>{data.visual ? `${data.visual.imagenes} imágenes · ${data.visual.clases.intacto ?? 0} intactas · ${data.visual.clases.danado ?? 0} dañadas · ${data.visual.grupos} grupos de origen.` : 'Las imágenes aún no están importadas.'} Son empaques sintéticos, no fotografías de envíos Amazon.</p>
        <p><strong>Dos usos distintos:</strong> el conjunto visual permite entrenar y probar el MLP; su asociación aleatoria con 200 paradas Amazon solo ilustra la inspección de datos. Ni las paradas ni esa asociación son entradas del MLP.</p>
        <button className="secondary-button" onClick={() => onNavigate?.('visual')}>Inspeccionar imágenes y asociación simulada</button></section>
      <section className="panel data-section"><span className="eyebrow">02 · MÉTODO</span><h2>Separación 75 % / 25 %</h2>
        <div className="flow-strip"><span>Imagen</span><span>Gris 16×16</span><span>256 píxeles</span><span>MLP</span><span>Clase</span></div>
        {entrenado ? <><div className="mlp-split"><p><strong>75 % · {modelo.total_train} imágenes</strong><br />Entrenamiento: el modelo ajusta sus pesos aquí.</p><p><strong>25 % · {modelo.total_test} imágenes</strong><br />Prueba reservada: mide el resultado con imágenes no usadas para aprender.</p></div><p>Partición por grupo de origen: ningún grupo cruza los conjuntos. Total: {total} imágenes.</p></>
          : <p>El protocolo fija 75 % para entrenamiento y 25 % para prueba reservada por grupo. Los conteos reales aparecerán cuando exista un modelo registrado.</p>}</section>
      <section className="panel data-section"><span className="eyebrow">03 · EVALUACIÓN</span><h2>{entrenado ? 'Resultado en prueba reservada' : 'Evaluación no disponible'}</h2>
        {entrenado ? <><p><strong>Accuracy MLP: {percentage(modelo.accuracy)}</strong> · línea base: {percentage(modelo.accuracy_baseline)}. {modelo.convergencia_advertida && 'El entrenamiento alcanzó el límite de iteraciones.'}</p>
          <table className="mlp-matrix"><caption>Matriz de confusión · filas reales, columnas predichas</caption><thead><tr><th></th><th>Dañado</th><th>Intacto</th></tr></thead><tbody><tr><th>Dañado</th><td>{matriz?.[0]?.[0]}</td><td>{matriz?.[0]?.[1]}</td></tr><tr><th>Intacto</th><td>{matriz?.[1]?.[0]}</td><td>{matriz?.[1]?.[1]}</td></tr></tbody></table>
          <p>F1 dañado: {percentage(modelo.por_clase?.danado?.['f1-score'])} · F1 intacto: {percentage(modelo.por_clase?.intacto?.['f1-score'])}.</p></>
          : <p>{modelError ? 'No se muestran métricas porque falló la consulta.' : 'Las métricas aparecerán cuando la evaluación esté registrada.'}</p>}</section>
      <section className="panel data-section"><span className="eyebrow">04 · EVIDENCIA Y SIGNIFICADO</span><h2>{ejemplo ? 'Predicción de prueba rastreable' : 'Sin predicción disponible'}</h2>
        {entrenado && predicciones?.items?.length > 0 && <label className="data-select">Imagen reservada para prueba
          <select value={selectedId ?? ''} onChange={(event) => { setSelectedId(Number(event.target.value)); setOntologia(null); setOntologyError('') }}>
            {predicciones.items.map((item) => <option key={item.imagen_id} value={item.imagen_id}>{item.id_origen}</option>)}
          </select></label>}
        {ejemplo ? <><img className="mlp-example-image" src={ejemplo.archivo_url} alt={`Empaque sintético ${ejemplo.id_origen}`} />
          <p>Imagen {ejemplo.id_origen} · conjunto de <strong>prueba (25 %)</strong> · etiqueta de origen: <strong>{ejemplo.etiqueta_real}</strong> · predicción de {modelo.version}: <strong>{ejemplo.clase_predicha}</strong> ({percentage(ejemplo.probabilidad_predicha)} de probabilidad asignada por el modelo; no certeza de daño real).</p>
          {ontologyError && <div className="alert alert--error" role="alert">No se pudo consultar la ontología: {ontologyError}</div>}
          {!ontologia && !ontologyError && <p role="status">Consultando relaciones semánticas…</p>}
          {ontologia && <><p><strong>Imagen → predicción → concepto:</strong> relaciones del caso en la ontología {ontologia.version}. La revisión humana sigue siendo necesaria.</p>
            <ul className="mlp-relations">{relacionesCaso.map(({ origen, relacion, destino }) => <li key={`${origen}-${relacion}-${destino}`}>{origen} <strong>→ {relacion} →</strong> {destino}</li>)}</ul></>}</>
          : <p>{modelError ? 'No se muestran predicciones porque falló la consulta.' : 'Las predicciones del conjunto reservado aparecerán cuando exista un modelo registrado.'}</p>}</section>
    </div>}
  </div>
}
