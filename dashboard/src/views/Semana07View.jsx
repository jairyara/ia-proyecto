import { useEffect, useMemo, useState } from 'react'
import Icon from '../components/Icon.jsx'
import { api } from '../services/api.js'

const number = (value, digits = 3) => Number(value ?? 0).toLocaleString('es-CO', {
  minimumFractionDigits: digits,
  maximumFractionDigits: digits,
})

export default function Semana07View() {
  const [context, setContext] = useState(null)
  const [result, setResult] = useState(null)
  const [selected, setSelected] = useState('')
  const [sequence, setSequence] = useState('AVF')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.contextoRepresentaciones()
      .then((payload) => {
        setContext(payload)
        const initial = payload.amazon.perfiles.find((item) => item.codigo === 'triple') || payload.amazon.perfiles[0]
        const initialSequence = payload.automata_pod.secuencias[0].secuencia
        setSelected(initial.pedido_id)
        setSequence(initialSequence)
        return api.evaluarRepresentacion({ pedido_id: initial.pedido_id, secuencia_pod: initialSequence })
      })
      .then(setResult)
      .catch((requestError) => setError(requestError.message))
      .finally(() => setLoading(false))
  }, [])

  const evaluate = async (pedidoId = selected, pod = sequence) => {
    if (!pedidoId) return
    setLoading(true)
    setError('')
    try {
      setResult(await api.evaluarRepresentacion({ pedido_id: pedidoId, secuencia_pod: pod }))
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  const amazon = context?.amazon
  const podSequences = (context?.automata_pod?.secuencias || []).map((item) => item.secuencia)
  const maxContribution = useMemo(() => Math.max(...(result?.numerica?.campos || []).map((item) => item.contribucion_cuadrada), 0.001), [result])

  const chooseProfile = (pedidoId) => {
    setSelected(pedidoId)
    evaluate(pedidoId, sequence)
  }

  const chooseSequence = (pod) => {
    setSequence(pod)
    evaluate(selected, pod)
  }

  return (
    <div className="view-shell representation-view">
      <header className="view-header view-header--compact">
        <div>
          <div className="week-kicker"><span>SEMANA 07</span><i /> REPRESENTACIONES DEL RECONOCIMIENTO</div>
          <h1>Una parada real,<br /><em>tres formas de entenderla.</em></h1>
          <p>Sobre 14.411 paradas Amazon, cada representación conserva una parte distinta de la operación: magnitudes, decisiones explicables u orden de eventos.</p>
        </div>
        <div className="model-badge model-badge--mint"><Icon name="activity" size={24} /><span><small>SIN ENTRENAMIENTO</small><strong>Euclidiana · Reglas · AFD</strong></span></div>
      </header>

      {error && <div className="alert alert--error" role="alert"><Icon name="alert" /><span><strong>No se pudo evaluar.</strong>{error}</span></div>}

      <section className="provenance-banner">
        <div><strong>{amazon?.fuente?.total_registros?.toLocaleString('es-CO') || '14.411'}</strong><small>paradas reales</small></div>
        <div><strong>{amazon?.fuente?.rutas || 100}</strong><small>rutas Amazon</small></div>
        <div><strong>3 de 20</strong><small>variables observadas</small></div>
        <p><Icon name="check" /><span><b>Origen:</b> Amazon Last Mile Routing Challenge 2021. Referencia = mediana; escala = IQR; hechos = valores que superan P75.</span></p>
      </section>

      <section className="panel representation-controls">
        <div className="panel-heading"><div><span className="eyebrow">APLICACIÓN REAL · AMAZON</span><h2>Selecciona una parada trazable</h2></div><span className="count-pill">{result?.pedido?.pedido_id || 'cargando…'}</span></div>
        <div className="profile-picker">
          {(amazon?.perfiles || []).map((profile) => (
            <button className={selected === profile.pedido_id ? 'active' : ''} key={profile.pedido_id} onClick={() => chooseProfile(profile.pedido_id)} disabled={loading}>
              <small>{profile.codigo}</small><strong>{profile.pedido_id}</strong><span>{profile.criterio}</span>
            </button>
          ))}
        </div>
      </section>

      <div className="representation-columns">
        <section className="panel representation-card numeric-card">
          <div className="representation-title"><span>01</span><div><small>MÉTODO NUMÉRICO</small><h2>Euclidiana + IQR</h2></div></div>
          <div className="distance-pair">
            <div><small>CRUDA · MEZCLA UNIDADES</small><strong>{number(result?.numerica?.distancia_cruda)}</strong></div>
            <div><small>NORMALIZADA · PRINCIPAL</small><strong>{number(result?.numerica?.distancia_normalizada)}</strong></div>
          </div>
          <div className="vector-fields">
            {(result?.numerica?.campos || []).map((field) => (
              <div key={field.campo}>
                <div><span>{field.etiqueta}</span><strong>{number(field.valor, field.campo === 'volumen_total_m3' ? 4 : 2)} {field.unidad}</strong></div>
                <small>Mediana {number(field.referencia, field.campo === 'volumen_total_m3' ? 4 : 2)} · Δ/IQR {number(field.diferencia_normalizada)}</small>
                <i><b style={{ width: `${Math.max(4, field.contribucion_cuadrada / maxContribution * 100)}%` }} /></i>
              </div>
            ))}
          </div>
          <p className="method-note"><b>Fórmula:</b> ‖(x − mediana) / IQR‖₂. Las 14.411 filas calculan referencia y escala; no hay train/test.</p>
        </section>

        <section className="panel representation-card symbolic-card">
          <div className="representation-title"><span>02</span><div><small>MÉTODO SIMBÓLICO</small><h2>Hechos + reglas</h2></div></div>
          <div className="fact-list">
            {(result?.simbolica?.hechos_detalle || []).map((fact) => <div key={fact.hecho}><Icon name="check" /><span><code>{fact.hecho}</code><small>{number(fact.valor, 4)} &gt; P75 {number(fact.limite, 4)}</small></span></div>)}
            {!result?.simbolica?.hechos?.length && <p>Ninguna variable supera su percentil 75.</p>}
          </div>
          <div className="rule-list">
            {(result?.simbolica?.reglas_activadas || []).map((rule) => <article key={rule.accion}><small>REGLA ACTIVADA</small><code>{rule.accion}</code><p>{rule.premisas.join(' ∧ ')}</p></article>)}
            {(result?.simbolica?.reglas_parciales || []).map((rule) => <article className="partial" key={rule.accion}><small>PARCIAL · FALTA {rule.faltantes.join(', ')}</small><code>{rule.accion}</code></article>)}
          </div>
          <p className="method-note"><b>Origen:</b> los hechos provienen de P75; las consecuencias son reglas didácticas explícitas, no etiquetas Amazon.</p>
        </section>

        <section className="panel representation-card automata-card">
          <div className="representation-title"><span>03</span><div><small>MÉTODO SECUENCIAL</small><h2>Autómata POD</h2></div></div>
          <div className="pod-picker">{podSequences.map((pod) => <button className={sequence === pod ? 'active' : ''} key={pod} onClick={() => chooseSequence(pod)} disabled={loading}>{pod}</button>)}</div>
          <div className={`automata-result ${result?.automata_pod?.aceptada ? 'accepted' : ''}`}>
            <small>ESTADO FINAL</small><strong>{result?.automata_pod?.estado_final || 'q0'}</strong><span>{result?.automata_pod?.aceptada ? 'Secuencia aceptada' : 'Secuencia no aceptada'}</span>
          </div>
          <div className="automata-trace"><code>q0</code>{(result?.automata_pod?.traza || []).map((step) => <span key={`${step.paso}-${step.simbolo}`}><i>{step.simbolo}</i><code>{step.estado_destino}</code></span>)}</div>
          <p className="method-note"><b>Origen:</b> escenario controlado. Amazon no registra eventos A/V/F/C; no se presenta como observación real.</p>
        </section>
      </div>

      <section className="panel provenance-table">
        <div className="panel-heading"><div><span className="eyebrow">TRAZABILIDAD</span><h2>De dónde sale cada resultado</h2></div></div>
        <div>{Object.entries(result?.procedencia || {}).map(([key, value]) => <article key={key}><code>{key}</code><span>{value}</span></article>)}</div>
      </section>
    </div>
  )
}
