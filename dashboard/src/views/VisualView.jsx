import { useEffect, useState } from 'react'
import { api } from '../services/api.js'
import { PageHeader, DataState, useResumen } from './ResumenView.jsx'

export default function VisualView({ initialImageId = null }) {
  const { data, error: summaryError } = useResumen()
  const [etiqueta, setEtiqueta] = useState('')
  const [offset, setOffset] = useState(0)
  const [page, setPage] = useState(null)
  const [selected, setSelected] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => {
    let active = true
    api.imagenesDatos({ limite: 12, offset, ...(etiqueta ? { etiqueta } : {}) })
      .then((result) => { if (active) { setPage(result); setError('') } })
      .catch((e) => { if (active) { setError(e.message); setPage(null) } })
    return () => { active = false }
  }, [etiqueta, offset])
  useEffect(() => {
    if (!page?.items.length) { setSelected(null); return }
    let active = true
    api.detalleImagen(initialImageId && offset === 0 && !etiqueta ? initialImageId : page.items[0].id)
      .then((result) => { if (active) setSelected(result) }).catch((e) => { if (active) setError(e.message) })
    return () => { active = false }
  }, [page, initialImageId, offset, etiqueta])
  const select = (id) => api.detalleImagen(id).then(setSelected).catch((e) => setError(e.message))
  return <div className="view-shell data-view">
    <PageHeader eyebrow="DATOS · PILOTO VISUAL" title="Inspección de imágenes" description="Explora los empaques sintéticos y su etiqueta de origen. La asociación con una parada Amazon fue aleatoria." />
    <DataState data={data} error={summaryError} />
    {data?.visual && <div className="data-stats"><article className="panel"><small>IMÁGENES</small><strong>{data.visual.imagenes}</strong><span>Archivos PNG originales</span></article><article className="panel"><small>INTACTO / DAÑADO</small><strong>{data.visual.clases.intacto ?? 0} / {data.visual.clases.danado ?? 0}</strong><span>Etiquetas de origen</span></article><article className="panel"><small>GRUPOS</small><strong>{data.visual.grupos}</strong><span>Para futuras particiones</span></article><article className="panel"><small>SIN IMAGEN</small><strong>{data.visual.sin_asociacion?.toLocaleString('es-CO') ?? '—'}</strong><span>Paradas Amazon sin asociación</span></article></div>}
    <div className="data-warning" role="note"><strong>Asociación simulada.</strong> Imagen sintética asociada aleatoriamente para demostración. No corresponde al envío original de Amazon.</div>
    <label className="data-select">Etiqueta de origen <select value={etiqueta} onChange={(e) => { setEtiqueta(e.target.value); setOffset(0) }}><option value="">Todas</option><option value="intacto">Intacto</option><option value="danado">Dañado</option></select></label>
    {error && <div role="alert" className="alert alert--error">{error}</div>}
    {!page && !error && <div role="status" className="learning-loading">Cargando imágenes…</div>}
    {page && <div className="visual-layout">
      <section className="panel visual-gallery" aria-label="Imágenes del piloto">
        {page.items.map((image) => <button key={image.id} className={`visual-tile ${selected?.id === image.id ? 'active' : ''}`} onClick={() => select(image.id)}>
          <img src={image.archivo_url} alt={`Empaque sintético ${image.id_origen}`} loading="lazy" /><span>#{image.id} · {image.etiqueta === 'danado' ? 'Dañado' : 'Intacto'}</span>
        </button>)}
        {!page.items.length && <p className="data-empty">No hay imágenes importadas con esta etiqueta.</p>}
        <div className="data-pagination"><button className="secondary-button" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - 12))}>Anterior</button><span>{page.total ? `${offset + 1}–${Math.min(offset + 12, page.total)} de ${page.total}` : '0 resultados'}</span><button className="secondary-button" disabled={offset + 12 >= page.total} onClick={() => setOffset(offset + 12)}>Siguiente</button></div>
      </section>
      <aside className="panel visual-detail"><div className="panel-heading"><h2>Detalle de origen</h2></div>{selected ? <>
        <img className="visual-preview" src={selected.archivo_url} alt={`Empaque sintético ${selected.id_origen}, etiqueta de origen ${selected.etiqueta}`} />
        <dl><dt>Etiqueta de origen</dt><dd>{selected.etiqueta === 'danado' ? 'Dañado' : 'Intacto'} ({selected.etiqueta_origen})</dd><dt>Grupo visual</dt><dd>{selected.grupo_origen}</dd><dt>ID de origen</dt><dd>{selected.id_origen}</dd><dt>Resolución</dt><dd>{selected.ancho} × {selected.alto} px</dd><dt>Parada asociada</dt><dd>{selected.asociacion ? `${selected.asociacion.pedido_id} · ${selected.asociacion.route_id} · ${selected.asociacion.station_code}` : 'Ninguna'}</dd></dl>
        <p className="data-note">No es una predicción del modelo ni una fotografía de la parada.</p>
      </> : <p className="data-empty">Selecciona una imagen.</p>}</aside>
    </div>}
  </div>
}
