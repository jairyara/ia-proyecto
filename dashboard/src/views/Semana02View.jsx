import { useEffect, useState } from 'react'
import Icon from '../components/Icon.jsx'
import { api } from '../services/api.js'

const initialOrder = {
  distancia_km: 12,
  volumen_m3: 0.12,
  prioridad: 'media',
  ventana_min: 120,
  cadena_frio: 0,
  hora_pico: 1,
  zona_rural: 0,
  trafico_index: 0.55,
}

function Slider({ label, value, min, max, step, unit, onChange }) {
  const progress = ((value - min) / (max - min)) * 100
  return (
    <label className="slider-field">
      <span><strong>{label}</strong><output>{Number(value).toFixed(step < 0.1 ? 2 : step < 1 ? 1 : 0)} {unit}</output></span>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(event) => onChange(Number(event.target.value))} style={{ '--progress': `${progress}%` }} />
      <small><span>{min}</span><span>{max} {unit}</span></small>
    </label>
  )
}

export default function Semana02View() {
  const [order, setOrder] = useState(initialOrder)
  const [prediction, setPrediction] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.metricas().then(setMetrics).catch((requestError) => setError(requestError.message))
  }, [])

  useEffect(() => {
    const timeout = window.setTimeout(async () => {
      setLoading(true)
      setError('')
      try {
        setPrediction(await api.predecirRiesgo(order))
      } catch (requestError) {
        setError(requestError.message)
      } finally {
        setLoading(false)
      }
    }, 280)
    return () => window.clearTimeout(timeout)
  }, [order])

  const update = (key, value) => setOrder((current) => ({ ...current, [key]: value }))
  const probability = prediction ? prediction.probabilidad * 100 : 0
  const results = metrics?.resultados || {}
  const selected = metrics?.modelo_elegido
  const matrix = selected ? results[selected]?.matriz_confusion : null

  return (
    <div className="view-shell">
      <header className="view-header view-header--compact">
        <div>
          <div className="week-kicker"><span>SEMANA 02</span><i /> APRENDIZAJE SUPERVISADO</div>
          <h1>Anticipar el retraso<br /><em>antes de despachar.</em></h1>
          <p>Ajusta las condiciones operativas. El modelo entrenado responde en tiempo real y expone qué variables empujan su decisión.</p>
        </div>
        <div className="model-badge"><Icon name="brain" size={24} /><span><small>MODELO ACTIVO</small><strong>{selected?.replace('_', ' ') || 'Cargando baseline'}</strong></span></div>
      </header>

      {error && <div className="alert alert--error" role="alert"><Icon name="alert" /><span><strong>No se pudo consultar el modelo.</strong>{error}</span></div>}

      <div className="ml-grid">
        <section className="panel form-panel">
          <div className="panel-heading"><div><span className="eyebrow">NUEVO PEDIDO</span><h2>Condiciones de la entrega</h2></div><button className="text-button" onClick={() => setOrder(initialOrder)}>Restablecer</button></div>
          <div className="sliders-grid">
            <Slider label="Distancia" value={order.distancia_km} min={1} max={30} step={0.5} unit="km" onChange={(value) => update('distancia_km', value)} />
            <Slider label="Volumen" value={order.volumen_m3} min={0.01} max={0.6} step={0.01} unit="m³" onChange={(value) => update('volumen_m3', value)} />
            <Slider label="Ventana disponible" value={order.ventana_min} min={30} max={240} step={5} unit="min" onChange={(value) => update('ventana_min', value)} />
            <Slider label="Índice de tráfico" value={order.trafico_index} min={0} max={1} step={0.01} unit="" onChange={(value) => update('trafico_index', value)} />
          </div>
          <div className="choice-section">
            <span className="field-caption">PRIORIDAD DEL PEDIDO</span>
            <div className="choice-group">
              {['baja', 'media', 'alta'].map((priority) => <button key={priority} className={order.prioridad === priority ? 'active' : ''} onClick={() => update('prioridad', priority)}>{priority}</button>)}
            </div>
          </div>
          <div className="toggles-grid">
            {[
              ['cadena_frio', 'Cadena de frío', 'Control térmico requerido'],
              ['hora_pico', 'Hora pico', 'Demanda vial elevada'],
              ['zona_rural', 'Zona rural', 'Cobertura fuera del núcleo urbano'],
            ].map(([key, title, subtitle]) => (
              <label className="toggle-row" key={key}>
                <span><strong>{title}</strong><small>{subtitle}</small></span>
                <input type="checkbox" checked={Boolean(order[key])} onChange={(event) => update(key, event.target.checked ? 1 : 0)} />
                <i />
              </label>
            ))}
          </div>
        </section>

        <section className={`panel prediction-panel ${prediction?.etiqueta ? 'prediction-panel--risk' : ''}`} aria-live="polite">
          <div className="prediction-top"><span className="eyebrow">PREDICCIÓN EN VIVO</span><span className={`live-pill ${loading ? 'live-pill--loading' : ''}`}><i />{loading ? 'Calculando' : 'Actualizada'}</span></div>
          <div className="risk-score">
            <div className="risk-ring" style={{ '--risk': `${probability * 3.6}deg` }}><span><strong>{probability.toFixed(1)}%</strong><small>probabilidad</small></span></div>
            <div><small>CLASIFICACIÓN</small><h2>{prediction?.etiqueta ? 'Riesgo alto' : 'Riesgo bajo'}</h2><p>Umbral de decisión: 50%</p></div>
          </div>
          <div className="risk-scale"><span style={{ width: `${probability}%` }} /><i style={{ left: '50%' }} /></div>
          <div className="scale-labels"><span>0% · estable</span><span>50% · umbral</span><span>100% · crítico</span></div>
          <div className="factors">
            <div className="section-title"><span>FACTORES CON MAYOR IMPACTO</span><small>aporte local</small></div>
            {(prediction?.factores || []).map((factor) => (
              <div className="factor-row" key={factor.variable}>
                <span className={`factor-arrow ${factor.impacto === 'reduce' ? 'factor-arrow--down' : ''}`}>{factor.impacto === 'reduce' ? '↓' : '↑'}</span>
                <strong>{factor.variable}</strong>
                <span>{factor.impacto} el riesgo</span>
                <code>{factor.aporte > 0 ? '+' : ''}{factor.aporte}</code>
              </div>
            ))}
          </div>
          <p className="model-note"><Icon name="activity" /> La predicción proviene del pipeline serializado; no de una regla escrita para el dashboard.</p>
        </section>
      </div>

      <section className="panel comparison-panel">
        <div className="panel-heading"><div><span className="eyebrow">VALIDACIÓN DEL BASELINE</span><h2>Comparación de modelos</h2></div><span className="count-pill">partición test · n=200</span></div>
        <div className="model-comparison">
          {Object.entries(results).map(([name, values]) => (
            <article className={`model-card ${name === selected ? 'model-card--selected' : ''}`} key={name}>
              <div><span className="model-icon"><Icon name={name.includes('forest') ? 'rules' : 'activity'} /></span><span><small>{name === selected ? 'MODELO ELEGIDO' : 'MODELO COMPARADO'}</small><strong>{name.replace('_', ' ')}</strong></span>{name === selected && <i className="selected-check"><Icon name="check" size={14} /></i>}</div>
              {[['Accuracy', values.accuracy], ['F1-Score', values.f1]].map(([label, value]) => <div className="metric-bar" key={label}><span><small>{label}</small><strong>{(value * 100).toFixed(1)}%</strong></span><i><b style={{ width: `${value * 100}%` }} /></i></div>)}
            </article>
          ))}
          <article className="confusion-card">
            <span className="field-caption">MATRIZ DE CONFUSIÓN · ELEGIDO</span>
            {matrix && <div className="confusion-layout"><span /><small>Pred. 0</small><small>Pred. 1</small><small>Real 0</small><strong className="tn">{matrix[0][0]}</strong><strong>{matrix[0][1]}</strong><small>Real 1</small><strong>{matrix[1][0]}</strong><strong className="tp">{matrix[1][1]}</strong></div>}
          </article>
        </div>
      </section>
    </div>
  )
}
