import { useEffect, useState } from 'react'
import { api } from '../services/api.js'

export function useResumen() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => {
    let active = true
    api.resumenDatos().then((result) => { if (active) setData(result) }).catch((e) => { if (active) setError(e.message) })
    return () => { active = false }
  }, [])
  return { data, error }
}

export function PageHeader({ eyebrow, title, description }) {
  return <header className="view-header"><div><div className="week-kicker"><span>{eyebrow}</span></div>
    <h1>{title}</h1><p>{description}</p></div></header>
}

export function DataState({ data, error }) {
  if (error) return <div role="alert" className="alert alert--error">{error} Consulta si PostgreSQL está activo y las migraciones y semillas están aplicadas.</div>
  if (!data) return <div role="status" className="learning-loading"><span className="spinner" />Cargando datos…</div>
  return null
}

export default function ResumenView({ onNavigate }) {
  const { data, error } = useResumen()
  const [modelo, setModelo] = useState(null)
  const [errorModelo, setErrorModelo] = useState('')
  useEffect(() => {
    let active = true
    api.resumenModeloVisual()
      .then((result) => { if (active) setModelo(result) })
      .catch((requestError) => { if (active) setErrorModelo(requestError.message) })
    return () => { active = false }
  }, [])
  const evaluado = modelo?.estado === 'evaluado'
  return <div className="view-shell data-view">
    <PageHeader eyebrow="PROYECTO 8" title="IA para logística" description="Del dato a la decisión: riesgo, reglas, rutas y prácticas semanales. El experimento visual es independiente de las entregas Amazon." />
    <DataState data={data} error={error} />
    {data && <>
      <div className="data-stats">
        <article className="panel"><small>PARADAS AMAZON</small><strong>{data.amazon?.paradas?.toLocaleString('es-CO') ?? '—'}</strong><span>Observaciones logísticas importadas</span></article>
        <article className="panel"><small>RUTAS / ESTACIONES</small><strong>{data.amazon ? `${data.amazon.rutas} / ${data.amazon.estaciones}` : '—'}</strong><span>Fuente: Amazon Last Mile</span></article>
        <article className="panel"><small>IMÁGENES DE DEMOSTRACIÓN</small><strong>{data.visual?.imagenes ?? '—'}</strong><span>Empaques sintéticos para Semana 8</span></article>
        <article className="panel"><small>ASOCIACIONES SIMULADAS</small><strong>{data.visual?.asociaciones ?? '—'}</strong><span>No representan una relación causal</span></article>
      </div>
      <div className="data-grid">
        <section className="panel data-section"><span className="eyebrow">DATOS E INSPECCIÓN</span><h2>Explora la evidencia</h2>
          <p>Consulta las paradas persistidas. Las imágenes de demostración fueron asociadas a algunas paradas al azar: no son fotos de esos envíos ni intervienen en el modelo de riesgo.</p>
          <div className="data-actions"><button className="primary-button" onClick={() => onNavigate('paradas')}>Ver paradas</button><button className="secondary-button" onClick={() => onNavigate('visual')}>Ver imágenes de demostración</button></div>
        </section>
        <section className="panel data-section"><span className="eyebrow">SEMANA 8 · RECONOCIMIENTO</span><h2>{evaluado ? `MLP evaluado · ${modelo.version}` : modelo?.estado === 'no_entrenado' ? 'Aún no entrenado' : errorModelo ? 'Estado no disponible' : 'Consultando modelo…'}</h2>
          {evaluado ? <p>{modelo.total_train} imágenes (75 %) para entrenamiento y {modelo.total_test} (25 %) reservadas para prueba. Accuracy: {(modelo.accuracy * 100).toFixed(1)} %; línea base: {(modelo.accuracy_baseline * 100).toFixed(1)} %. Es un experimento didáctico, no una decisión de despacho.</p>
            : <p>{errorModelo ? `No se pudo consultar el modelo: ${errorModelo}` : modelo ? 'Las imágenes pueden inspeccionarse, pero no hay evaluación ni predicciones registradas.' : 'Consultando la evaluación persistida en PostgreSQL.'}</p>}
          <button className="secondary-button" onClick={() => onNavigate('semana08')}>Ver Semana 8</button>
        </section>
      </div>
      {!data.amazon && <p className="data-note">No hay datos Amazon importados. Las vistas de inspección quedarán vacías hasta ejecutar el seed.</p>}
    </>}
  </div>
}
