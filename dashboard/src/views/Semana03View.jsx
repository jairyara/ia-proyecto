import { useEffect, useState } from 'react'
import Icon from '../components/Icon.jsx'
import { api } from '../services/api.js'

const initialText = 'Calcular una ruta A* y validar restricciones de ventana horaria para entregas con cadena de frío.'

export default function Semana03View() {
  const [description, setDescription] = useState(initialText)
  const [examples, setExamples] = useState([])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const classify = async (text = description) => {
    if (text.trim().length < 3) return
    setLoading(true)
    setError('')
    try {
      setResult(await api.clasificar(text))
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    api.ejemplos().then(({ ejemplos }) => setExamples(ejemplos)).catch(() => {})
    classify(initialText)
    // Solo ejecuta el caso inicial una vez.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const selectExample = (example) => {
    setDescription(example.descripcion)
    classify(example.descripcion)
  }

  return (
    <div className="view-shell">
      <header className="view-header view-header--compact">
        <div>
          <div className="week-kicker"><span>SEMANA 03</span><i /> CONOCIMIENTO EXPLÍCITO</div>
          <h1>Clasificar con reglas<br /><em>que sí se pueden auditar.</em></h1>
          <p>Escribe un requerimiento logístico y sigue la evidencia textual que activa cada área de inteligencia artificial.</p>
        </div>
        <div className="model-badge model-badge--violet"><Icon name="rules" size={24} /><span><small>MOTOR ACTIVO</small><strong>7 áreas · reglas deterministas</strong></span></div>
      </header>

      {error && <div className="alert alert--error" role="alert"><Icon name="alert" /><span><strong>No se pudo evaluar el texto.</strong>{error}</span></div>}

      <div className="symbolic-grid">
        <section className="panel analyzer-panel">
          <div className="panel-heading"><div><span className="eyebrow">ENTRADA EN LENGUAJE NATURAL</span><h2>Requerimiento logístico</h2></div><span className="count-pill">{description.length} caracteres</span></div>
          <textarea value={description} maxLength={1000} onChange={(event) => setDescription(event.target.value)} placeholder="Ej.: Replanificar la ruta cuando una vía esté cerrada…" />
          <div className="analyzer-actions"><p>Se normalizan tildes, puntuación y la expresión A* antes de comparar frases completas.</p><button className="primary-button primary-button--violet" onClick={() => classify()} disabled={loading || description.trim().length < 3}><Icon name="spark" />{loading ? 'Evaluando…' : 'Analizar reglas'}</button></div>
          <div className="examples">
            <span className="field-caption">CASOS DEL DATASET</span>
            <div>{examples.slice(0, 6).map((example) => <button key={example.id} onClick={() => selectExample(example)}><small>{example.id}</small><span>{example.descripcion}</span></button>)}</div>
          </div>
        </section>

        <section className="panel classification-result" aria-live="polite">
          <div className="result-orbit"><span className="result-icon"><Icon name="spark" size={28} /></span><i /><i /></div>
          <span className="eyebrow">ÁREA PRINCIPAL</span>
          <h2>{result?.principal || 'Evaluando reglas…'}</h2>
          <p>{result?.evidencia?.[0]?.componente || 'El motor está buscando evidencia literal en el texto.'}</p>
          <div className="confidence-note"><Icon name="check" /><span><strong>Decisión reproducible</strong><small>Misma entrada, misma salida y evidencia.</small></span></div>
        </section>
      </div>

      <section className="panel trace-panel">
        <div className="panel-heading"><div><span className="eyebrow">ÁRBOL DE ACTIVACIÓN</span><h2>Cómo se construyó la decisión</h2></div><span className="count-pill">{result?.detectadas?.length || 0} áreas detectadas</span></div>
        <div className="rule-flow">
          <div className="flow-node flow-node--source"><small>TEXTO NORMALIZADO</small><p>“{description.toLowerCase().replace('a*', 'a estrella').slice(0, 150)}{description.length > 150 ? '…' : ''}”</p></div>
          <span className="flow-arrow">↓</span>
          <div className="evidence-nodes">
            {(result?.evidencia || []).map((item, index) => (
              <article className={index === 0 ? 'evidence-node evidence-node--primary' : 'evidence-node'} key={item.area}>
                <div><span>{String(index + 1).padStart(2, '0')}</span><strong>{item.area}</strong><small>{item.puntaje} coincidencia{item.puntaje === 1 ? '' : 's'}</small></div>
                <div className="keyword-list">{item.palabras.map((word) => <code key={word}>{word}</code>)}</div>
                <p>{item.componente}</p>
              </article>
            ))}
            {!result?.evidencia?.length && <p className="empty-message">No se detectaron reglas para este texto.</p>}
          </div>
        </div>
      </section>

      <section className="explainability-strip">
        <div><Icon name="rules" /><span><strong>Palabras completas</strong><small>Evita falsos positivos por fragmentos.</small></span></div>
        <div><Icon name="activity" /><span><strong>Puntaje visible</strong><small>Cada coincidencia suma una evidencia.</small></span></div>
        <div><Icon name="check" /><span><strong>Desempate documentado</strong><small>El orden de categorías resuelve empates.</small></span></div>
      </section>
    </div>
  )
}
