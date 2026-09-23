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
  return <div className="view-shell data-view">
    <PageHeader eyebrow="PROYECTO 8" title="IA para logística" description="Del dato a la decisión: riesgo, reglas, rutas, representaciones y un piloto visual independiente." />
    <DataState data={data} error={error} />
    {data && <>
      <div className="data-stats">
        <article className="panel"><small>PARADAS AMAZON</small><strong>{data.amazon?.paradas?.toLocaleString('es-CO') ?? '—'}</strong><span>Observaciones logísticas importadas</span></article>
        <article className="panel"><small>RUTAS / ESTACIONES</small><strong>{data.amazon ? `${data.amazon.rutas} / ${data.amazon.estaciones}` : '—'}</strong><span>Fuente: Amazon Last Mile</span></article>
        <article className="panel"><small>IMÁGENES DEL PILOTO</small><strong>{data.visual?.imagenes ?? '—'}</strong><span>Empaques sintéticos, no entregas reales</span></article>
        <article className="panel"><small>ASOCIACIONES SIMULADAS</small><strong>{data.visual?.asociaciones ?? '—'}</strong><span>No representan una relación causal</span></article>
      </div>
      <div className="data-grid">
        <section className="panel data-section"><span className="eyebrow">DATOS E INSPECCIÓN</span><h2>Explora la evidencia</h2>
          <p>Consulta las paradas persistidas, filtra por ruta o estación y revisa qué imágenes fueron asociadas al azar.</p>
          <div className="data-actions"><button className="primary-button" onClick={() => onNavigate('paradas')}>Ver paradas</button><button className="secondary-button" onClick={() => onNavigate('visual')}>Ver piloto visual</button></div>
        </section>
        <section className="panel data-section"><span className="eyebrow">ESTADO DEL MODELO VISUAL</span><h2>Aún no entrenado</h2>
          <p>Hay datos para explorar, pero no existe todavía un MLP visual, evaluación ni predicciones guardadas. La guía académica definirá la tarea y el método.</p>
          <button className="secondary-button" onClick={() => onNavigate('mlp')}>Ver propuesta MLP</button>
        </section>
      </div>
      {!data.amazon && <p className="data-note">No hay datos Amazon importados. Las vistas de inspección quedarán vacías hasta ejecutar el seed.</p>}
    </>}
  </div>
}
