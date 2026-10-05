import { useEffect, useState } from 'react'
import Icon from '../components/Icon.jsx'
import { DataState, useResumen } from './ResumenView.jsx'
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
  const aciertos = matriz ? (matriz[0]?.[0] ?? 0) + (matriz[1]?.[1] ?? 0) : null
  const totalPrueba = matriz ? matriz.flat().reduce((sum, value) => sum + value, 0) : null

  return <div className="view-shell mlp-view">
    <header className="view-header view-header--compact">
      <div>
        <div className="week-kicker"><span>SEMANA 08</span><i /> RECONOCIMIENTO DE IMÁGENES</div>
        <h1>De la imagen a una<br /><em>predicción que se pueda explicar.</em></h1>
        <p>Sigue un empaque de prueba desde la entrada y sus 256 valores hasta la evaluación y el significado logístico. Cada etapa muestra qué sabemos y qué aún no.</p>
      </div>
      <div className="model-badge model-badge--mint"><Icon name="activity" size={24} /><span><small>EXPERIMENTO DIDÁCTICO</small><strong>Imagen · MLP · Ontología</strong></span></div>
    </header>
    <DataState data={data} error={error} />
    {modelError && <div className="alert alert--error" role="alert">No se pudo consultar el experimento: {modelError}</div>}
    {!modelo && !modelError && <div role="status" className="learning-loading"><span className="spinner" />Consultando el modelo…</div>}
    {data && modelo?.estado === 'no_entrenado' && <div className="data-warning"><strong>Modelo no registrado.</strong> Las imágenes de demostración existen, pero aún no hay evaluación ni predicciones persistidas. No se inventan resultados.</div>}
    {data && entrenado && <div className="data-warning"><strong>Experimento didáctico · {modelo.version}.</strong> {modelo.aviso} {modelo.accuracy <= modelo.accuracy_baseline && 'El MLP no supera la línea base: no debe usarse para decisiones operativas.'}</div>}
    {data && <>
    <section className="provenance-banner mlp-provenance">
      <div><strong>{data.visual?.imagenes ?? '—'}</strong><small>imágenes sintéticas</small></div>
      <div><strong>{entrenado ? modelo.total_train : '—'}</strong><small>entrenamiento · 75 %</small></div>
      <div><strong>{entrenado ? modelo.total_test : '—'}</strong><small>prueba reservada · 25 %</small></div>
      <p><Icon name="check" /><span><b>Origen:</b> empaques de demostración, no fotografías de envíos Amazon. La asociación con paradas es simulada y no alimenta el MLP.</span></p>
    </section>
    <section className="panel mlp-process-map" aria-labelledby="mlp-process-title">
      <div className="panel-heading"><div><span className="eyebrow">MAPA DE LA SEMANA 08</span><h2 id="mlp-process-title">De la imagen a la interpretación</h2></div><span className="count-pill">Entrenar ≠ probar</span></div>
      <div className="mlp-process-map__body">
        <div className="mlp-process-map__chain" aria-label="Preparación común">
          <div><small>01 · ORIGEN</small><strong>{data.visual?.imagenes ?? '—'} imágenes</strong><span>Piloto de demostración</span></div>
          <b aria-hidden="true">→</b>
          <div><small>02 · PREPARACIÓN</small><strong>Gris 16×16</strong><span>Vector de 256 valores</span></div>
          <b aria-hidden="true">→</b>
          <div><small>03 · PARTICIÓN</small><strong>Por grupo</strong><span>75 % / 25 %</span></div>
        </div>
        <div className="mlp-process-map__lanes">
          <div><small>RUTA DE ENTRENAMIENTO</small><strong>{entrenado ? modelo.total_train : '75 %'} imágenes → MLP</strong><span>Ajustan los pesos; no calculan la evaluación final.</span></div>
          <div><small>RUTA DE PRUEBA</small><strong>{ejemplo?.id_origen ?? (entrenado ? `${modelo.total_test} imágenes` : '25 % reservado')}</strong><span>La imagen elegida no participa en el ajuste.</span></div>
        </div>
        <div className="mlp-process-map__join"><span aria-hidden="true">↓</span><strong>MLP entrenado + imagen de prueba → predicción</strong><span>{ejemplo ? `${ejemplo.clase_predicha} · ${percentage(ejemplo.probabilidad_predicha)} asignado a esa clase` : 'La salida real aparecerá con un modelo registrado.'}</span></div>
        <div className="mlp-process-map__outcomes">
          <div><small>04 · EVALUACIÓN</small><strong>Predicción frente a etiqueta</strong><span>{entrenado ? `${percentage(modelo.accuracy)} frente a ${percentage(modelo.accuracy_baseline)} de línea base` : 'Métricas de prueba aún no disponibles'}</span></div>
          <div><small>05 · SIGNIFICADO</small><strong>Imagen → predicción → concepto</strong><span>Ontología y revisión humana; no despacho automático.</span></div>
        </div>
        <p>Las dos salidas cumplen funciones distintas: la evaluación mide el modelo sobre la prueba reservada; la ontología relaciona una predicción concreta con conceptos logísticos. PostgreSQL conserva la evidencia cuando el experimento se registra.</p>
      </div>
    </section>
    <div className="learning-sequence">
      <section className="panel data-section mlp-lab-card"><span className="eyebrow">01 · CASO DE ESTUDIO</span><h2>Imágenes de demostración</h2>
        {entrenado && predicciones?.items?.length > 0 && <label className="data-select">Imagen reservada para prueba
          <select value={selectedId ?? ''} onChange={(event) => { setSelectedId(Number(event.target.value)); setOntologia(null); setOntologyError('') }}>
            {predicciones.items.map((item) => <option key={item.imagen_id} value={item.imagen_id}>{item.id_origen}</option>)}
          </select></label>}
        {ejemplo && <div className="learning-case"><img className="mlp-example-image" src={ejemplo.archivo_url} alt={`Empaque sintético ${ejemplo.id_origen}`} /><p><strong>Caso: {ejemplo.id_origen}</strong><br />Etiqueta de origen: {ejemplo.etiqueta_real}. El modelo todavía no ha intervenido en este primer paso.</p></div>}
        <p>{data.visual ? `${data.visual.imagenes} imágenes · ${data.visual.clases.intacto ?? 0} intactas · ${data.visual.clases.danado ?? 0} dañadas · ${data.visual.grupos} grupos de origen.` : 'Las imágenes aún no están importadas.'} Son empaques sintéticos, no fotografías de envíos Amazon.</p>
        <p><strong>Dos usos distintos:</strong> el conjunto visual permite entrenar y probar el MLP; su asociación aleatoria con 200 paradas Amazon solo ilustra la inspección de datos. Ni las paradas ni esa asociación son entradas del MLP.</p>
        <button className="secondary-button" onClick={() => onNavigate?.('visual')}>Inspeccionar imágenes y asociación simulada</button></section>
      <section className="panel data-section mlp-lab-card"><span className="eyebrow">02 · PREPROCESAMIENTO Y PROTOCOLO</span><h2>Separación 75 % / 25 %</h2>
        <p><strong>Matemática de la entrada:</strong> cada imagen se convierte a gris, se reduce a 16×16 con Lanczos y se aplana. Para cada uno de los 256 píxeles, <code>xᵢ = pᵢ / 255</code>, así <code>x ∈ [0,1]²⁵⁶</code>. La API no publica los valores individuales del caso; no los inventamos.</p>
        {entrenado ? <><div className="mlp-split"><p><strong>75 % · {modelo.total_train} imágenes</strong><br />Entrenamiento: el modelo ajusta sus pesos aquí.</p><p><strong>25 % · {modelo.total_test} imágenes</strong><br />Prueba reservada: mide el resultado con imágenes no usadas para aprender.</p></div><p>Partición por grupo de origen: ningún grupo cruza los conjuntos. Total: {total} imágenes.</p></>
          : <p>El protocolo fija 75 % para entrenamiento y 25 % para prueba reservada por grupo. Los conteos reales aparecerán cuando exista un modelo registrado.</p>}</section>
      <section className="panel data-section mlp-lab-card"><span className="eyebrow">03 · RED NEURONAL Y PREDICCIÓN</span><h2>Del vector a la clase</h2>
        <div className="mlp-network"><span>256 entradas</span><b>→</b><span>64 neuronas ReLU</span><b>→</b><span>1 salida logística</span></div>
        <p><code>h = ReLU(xW₁ + b₁)</code> y <code>p = 1 / (1 + e<sup>−(hW₂+b₂)</sup>)</code>. Los pesos se ajustan solo con entrenamiento. La única salida logística estima la probabilidad de una clase; la otra es su complemento.</p>
        {ejemplo ? <p>Para <strong>{ejemplo.id_origen}</strong>, {modelo.version} predijo <strong>{ejemplo.clase_predicha}</strong> y asignó a esa clase <strong>{percentage(ejemplo.probabilidad_predicha)}</strong>. Esa probabilidad no es certeza de daño real.</p> : <p>La predicción del caso aparecerá cuando exista un modelo registrado.</p>}
        <p className="method-note">Las activaciones internas por imagen no se guardan en la API; no presentamos una atribución por píxel que no se haya calculado.</p>
      </section>
      <section className="panel data-section mlp-lab-card"><span className="eyebrow">04 · EVALUACIÓN</span><h2>{entrenado ? 'Resultado en prueba reservada' : 'Evaluación no disponible'}</h2>
        {entrenado ? <><p><strong>Accuracy MLP: {percentage(modelo.accuracy)}</strong> · línea base: {percentage(modelo.accuracy_baseline)}. {modelo.convergencia_advertida && 'El entrenamiento alcanzó el límite de iteraciones.'}</p>
          {totalPrueba > 0 && <p className="learning-equation"><code>accuracy = aciertos / total = {aciertos} / {totalPrueba} = {percentage(modelo.accuracy)}</code></p>}
          <table className="mlp-matrix"><caption>Matriz de confusión · filas reales, columnas predichas</caption><thead><tr><th></th><th>Dañado</th><th>Intacto</th></tr></thead><tbody><tr><th>Dañado</th><td>{matriz?.[0]?.[0]}</td><td>{matriz?.[0]?.[1]}</td></tr><tr><th>Intacto</th><td>{matriz?.[1]?.[0]}</td><td>{matriz?.[1]?.[1]}</td></tr></tbody></table>
          <p>F1 dañado: {percentage(modelo.por_clase?.danado?.['f1-score'])} · F1 intacto: {percentage(modelo.por_clase?.intacto?.['f1-score'])}. Las <strong>{matriz?.[0]?.[1]}</strong> imágenes dañadas predichas intactas son el error más preocupante para una posible inspección.</p></>
          : <p>{modelError ? 'No se muestran métricas porque falló la consulta.' : 'Las métricas aparecerán cuando la evaluación esté registrada.'}</p>}</section>
      <section className="panel data-section mlp-lab-card"><span className="eyebrow">05 · SIGNIFICADO Y LÍMITE OPERATIVO</span><h2>{ejemplo ? 'Predicción de prueba rastreable' : 'Sin predicción disponible'}</h2>
        {ejemplo ? <>
          <p>Imagen {ejemplo.id_origen} · conjunto de <strong>prueba (25 %)</strong> · etiqueta de origen: <strong>{ejemplo.etiqueta_real}</strong> · predicción de {modelo.version}: <strong>{ejemplo.clase_predicha}</strong> ({percentage(ejemplo.probabilidad_predicha)} de probabilidad asignada por el modelo; no certeza de daño real).</p>
          {ontologyError && <div className="alert alert--error" role="alert">No se pudo consultar la ontología: {ontologyError}</div>}
          {!ontologia && !ontologyError && <p role="status">Consultando relaciones semánticas…</p>}
          {ontologia && <><p><strong>Imagen → predicción → concepto:</strong> relaciones del caso en la ontología {ontologia.version}. La revisión humana sigue siendo necesaria.</p>
            <ul className="mlp-relations">{relacionesCaso.map(({ origen, relacion, destino }) => <li key={`${origen}-${relacion}-${destino}`}>{origen} <strong>→ {relacion} →</strong> {destino}</li>)}</ul></>}</>
          : <p>{modelError ? 'No se muestran predicciones porque falló la consulta.' : 'Las predicciones del conjunto reservado aparecerán cuando exista un modelo registrado.'}</p>}
        <div className="learning-conclusion"><Icon name="alert" /><p><strong>Conclusión de esta semana:</strong> {entrenado && modelo.accuracy <= modelo.accuracy_baseline ? 'el resultado no mejora la referencia simple. ' : 'el piloto aún no autoriza decisiones automáticas. '}La revisión humana sigue siendo necesaria. Mejorar datos, representación o modelo pertenece a iteraciones futuras, no a maquillar esta evaluación.</p></div>
      </section>
    </div>
    <section className="explainability-strip explainability-strip--mint">
      <div><Icon name="search" /><span><strong>Origen separado</strong><small>Las paradas Amazon no entran al modelo.</small></span></div>
      <div><Icon name="activity" /><span><strong>Prueba reservada</strong><small>Las métricas no proceden del entrenamiento.</small></span></div>
      <div><Icon name="rules" /><span><strong>Predicción trazable</strong><small>Imagen, clase y relación semántica.</small></span></div>
    </section>
    </>}
  </div>
}
