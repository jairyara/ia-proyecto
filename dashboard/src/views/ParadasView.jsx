import { useEffect, useState } from 'react'
import { api } from '../services/api.js'
import { PageHeader, DataState, useResumen } from './ResumenView.jsx'

export default function ParadasView({ onNavigate }) {
  const { data, error: summaryError } = useResumen()
  const [ruta, setRuta] = useState('')
  const [estacion, setEstacion] = useState('')
  const [filters, setFilters] = useState({})
  const [offset, setOffset] = useState(0)
  const [page, setPage] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => {
    let active = true
    api.paradasDatos({ ...filters, limite: 20, offset }).then((result) => { if (active) { setPage(result); setError('') } })
      .catch((e) => { if (active) { setError(e.message); setPage(null) } })
    return () => { active = false }
  }, [filters, offset])
  return <div className="view-shell data-view">
    <PageHeader eyebrow="DATOS · AMAZON" title="Paradas importadas" description="Una fila representa una parada de la fuente logística. Las imágenes asociadas son una demostración simulada, no evidencia de una entrega." />
    <DataState data={data} error={summaryError} />
    {data?.amazon && <p className="data-note">{data.amazon.fuente} · versión {data.amazon.version} · {data.amazon.paradas.toLocaleString('es-CO')} paradas · distancia al depósito en km.</p>}
    <form className="panel data-filters" onSubmit={(event) => { event.preventDefault(); setOffset(0); setFilters({ ...(ruta ? { ruta } : {}), ...(estacion ? { estacion } : {}) }) }}>
      <label>Ruta <input value={ruta} onChange={(e) => setRuta(e.target.value)} placeholder="ID exacto de ruta" /></label>
      <label>Estación <input value={estacion} onChange={(e) => setEstacion(e.target.value)} placeholder="Código exacto" /></label>
      <button className="primary-button" type="submit">Filtrar</button>
      <button className="secondary-button" type="button" onClick={() => { setRuta(''); setEstacion(''); setFilters({}); setOffset(0) }}>Limpiar</button>
    </form>
    {error ? <div role="alert" className="alert alert--error">{error}</div> : !page ? <div role="status" className="learning-loading">Cargando paradas…</div> : <section className="panel data-table-panel">
      <div className="panel-heading"><h2>Resultados</h2><span className="count-pill">{page.total.toLocaleString('es-CO')} paradas</span></div>
      <div className="table-wrap"><table><thead><tr><th>Pedido</th><th>Ruta</th><th>Estación</th><th>Tipo</th><th>Paquetes</th><th>Distancia</th><th>Imagen</th></tr></thead>
      <tbody>{page.items.map((item) => <tr key={item.id}><td>{item.pedido_id}</td><td>{item.route_id}</td><td>{item.station_code}</td><td>{item.tipo_parada}</td><td>{item.num_paquetes}</td><td>{item.distancia_deposito_km.toFixed(1)} km</td><td>{item.imagen_id ? <button className="text-button" onClick={() => onNavigate('visual', item.imagen_id)}>Asociada #{item.imagen_id}</button> : 'Sin asociación'}</td></tr>)}</tbody></table></div>
      {!page.items.length && <p className="data-empty">No hay paradas con estos filtros.</p>}
      <div className="data-pagination"><button className="secondary-button" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - 20))}>Anterior</button><span>{page.total ? `${offset + 1}–${Math.min(offset + 20, page.total)} de ${page.total}` : '0 resultados'}</span><button className="secondary-button" disabled={offset + 20 >= page.total} onClick={() => setOffset(offset + 20)}>Siguiente</button></div>
    </section>}
  </div>
}
