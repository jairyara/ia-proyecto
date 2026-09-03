import { useEffect, useState } from 'react'
import Icon from '../components/Icon.jsx'
import { api } from '../services/api.js'

const initialText = 'El furgón refrigerado perdió temperatura y la carga láctea corre riesgo'

export default function Semana05View() {
  const [query, setQuery] = useState(initialText)
  const [context, setContext] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const responder = async (text = query) => {
    if (text.trim().length < 3) return
    setLoading(true)
    setError('')
    try {
      setResult(await api.responderHibrido(text))
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    api.contextoHibrido().then(setContext).catch(() => {})
    responder(initialText)
    // Solo ejecuta la consulta inicial una vez.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const selectExample = (text) => {
    setQuery(text)
    responder(text)
  }

  const clasificacion = result?.clasificacion
  const similitud = result?.evidencia?.similitud ?? 0

  return (
    <div className="view-shell">
      <header className="view-header view-header--compact">
        <div>
          <div className="week-kicker"><span>SEMANA 05</span><i /> SISTEMA HÍBRIDO TRAZABLE</div>
          <h1>Responder con evidencia,<br /><em>no solo con una salida.</em></h1>
          <p>Tres técnicas del marco tecnológico evalúan la misma consulta logística: reglas expertas, recuperación documental TF-IDF y clasificación supervisada.</p>
        </div>
        <div className="model-badge model-badge--mint"><Icon name="spark" size={24} /><span><small>MOTOR HÍBRIDO</small><strong>Reglas · TF-IDF · LogReg</strong></span></div>
      </header>

      {error && <div className="alert alert--error" role="alert"><Icon name="alert" /><span><strong>No se pudo evaluar la consulta.</strong>{error}</span></div>}

      <div className="symbolic-grid">
        <section className="panel analyzer-panel">
          <div className="panel-heading"><div><span className="eyebrow">NOVEDAD OPERATIVA</span><h2>Consulta en lenguaje natural</h2></div><span className="count-pill">{query.length} caracteres</span></div>
          <textarea value={query} maxLength={1000} onChange={(event) => setQuery(event.target.value)} placeholder="Ej.: El camión reporta una falla de refrigeración con carga de fármacos…" />
          <div className="analyzer-actions"><p>El texto se normaliza (minúsculas, sin tildes) antes de alimentar las tres técnicas.</p><button className="primary-button" onClick={() => responder()} disabled={loading || query.trim().length < 3}><Icon name="spark" />{loading ? 'Evaluando…' : 'Responder con trazabilidad'}</button></div>
          <div className="examples">
            <span className="field-caption">CONSULTAS DE LA GUÍA</span>
            <div>{(context?.consultas_ejemplo || []).map((example, index) => <button key={example} onClick={() => selectExample(example)}><small>C{index + 1}</small><span>{example}</span></button>)}</div>
          </div>
        </section>

        <section className="panel classification-result classification-result--mint" aria-live="polite">
          <div className="result-orbit"><span className="result-icon"><Icon name="spark" size={28} /></span><i /><i /></div>
          <span className="eyebrow">CATEGORÍA OPERATIVA</span>
          <h2>{clasificacion?.clase?.replace(/_/g, ' ') || 'Evaluando…'}</h2>
          <p>{clasificacion?.descripcion || 'El clasificador está comparando la consulta con los ejemplos etiquetados.'}</p>
          <div className="prob-bars">
            {(clasificacion?.probabilidades || []).map((item) => (
              <div className="prob-bar" key={item.clase}>
                <div className="prob-bar__label"><span>{item.clase.replace(/_/g, ' ')}</span><strong>{(item.probabilidad * 100).toFixed(0)}%</strong></div>
                <div className="prob-bar__track"><i style={{ width: `${Math.max(3, item.probabilidad * 100)}%` }} /></div>
              </div>
            ))}
          </div>
          <div className="confidence-note"><Icon name="check" /><span><strong>Triple señal auditada</strong><small>Regla + protocolo + clase para la misma entrada.</small></span></div>
        </section>
      </div>

      <section className="panel trace-panel">
        <div className="panel-heading"><div><span className="eyebrow">TRAZABILIDAD DE LA DECISIÓN</span><h2>Cómo se construyó la respuesta</h2></div><span className="count-pill">{result?.reglas?.length || 0} reglas · similitud {similitud.toFixed(3)}</span></div>
        <div className="rule-flow">
          <div className="flow-node flow-node--source"><small>CONSULTA NORMALIZADA</small><p>“{query.toLowerCase().slice(0, 150)}{query.length > 150 ? '…' : ''}”</p></div>
          <span className="flow-arrow">↓</span>
          <div className="evidence-nodes">
            <article className="evidence-node evidence-node--primary">
              <div><span>01</span><strong>Reglas expertas</strong><small>{result?.reglas?.length || 0} disparada{(result?.reglas?.length || 0) === 1 ? '' : 's'}</small></div>
              {(result?.reglas || []).map((regla) => (
                <div className="rule-hit" key={regla.accion}>
                  <code>{regla.accion}</code>
                  <div className="keyword-list">{regla.detonantes.map((word) => <code key={word}>{word}</code>)}</div>
                  <p>{regla.descripcion}</p>
                </div>
              ))}
              {!result?.reglas?.length && <p className="empty-message">Ninguna regla se activó con esta consulta.</p>}
            </article>
            <article className="evidence-node">
              <div><span>02</span><strong>Evidencia documental</strong><small>TF-IDF + coseno</small></div>
              <div className="sim-meter"><i style={{ width: `${Math.max(3, similitud * 100)}%` }} /></div>
              <p className="sim-value">Similitud coseno: <strong>{similitud.toFixed(3)}</strong></p>
              <p>{result?.evidencia?.documento || 'Buscando el protocolo más afín en la base de conocimiento…'}</p>
            </article>
            <article className="evidence-node">
              <div><span>03</span><strong>Clasificación supervisada</strong><small>regresión logística</small></div>
              <div className="keyword-list"><code>{clasificacion?.clase || '…'}</code></div>
              <p>{clasificacion?.descripcion}</p>
              <p>Entrenada con {context?.entrenamiento?.total_ejemplos ?? 16} ejemplos balanceados del dominio logístico.</p>
            </article>
          </div>
        </div>
      </section>

      <section className="panel trace-panel">
        <div className="panel-heading"><div><span className="eyebrow">INGENIERÍA DEL CONOCIMIENTO</span><h2>Reglas expertas del dominio logístico</h2></div><span className="count-pill">{context?.reglas?.length || 5} reglas · {context?.base_conocimiento?.total_documentos || 10} SOP</span></div>
        <div className="rule-flow">
          <div className="evidence-nodes">
            {(context?.reglas || []).map((regla, index) => (
              <article className="evidence-node" key={regla.accion}>
                <div><span>{String(index + 1).padStart(2, '0')}</span><strong>{regla.accion}</strong></div>
                <div className="keyword-list">{regla.palabras.map((word) => <code key={word}>{word}</code>)}</div>
                <p>{regla.descripcion}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="explainability-strip explainability-strip--mint">
        <div><Icon name="rules" /><span><strong>Regla + detonante</strong><small>Cada disparo cita la palabra exacta que lo activó.</small></span></div>
        <div><Icon name="search" /><span><strong>Similitud visible</strong><small>La evidencia documental se cuantifica con coseno.</small></span></div>
        <div><Icon name="activity" /><span><strong>Probabilidad por clase</strong><small>La predicción muestra su distribución completa.</small></span></div>
      </section>
    </div>
  )
}
