import { PageHeader, DataState, useResumen } from './ResumenView.jsx'

export default function MlpView({ onNavigate }) {
  const { data, error } = useResumen()
  return <div className="view-shell data-view">
    <PageHeader eyebrow="CORTE 2 · PROPUESTA" title="MLP visual" description="Clasificación provisional del estado visible de un empaque sintético: intacto o dañado. El método final depende de la guía académica." />
    <DataState data={data} error={error} />
    {data && <>
      <div className="data-warning"><strong>Aún no entrenado.</strong> No existen particiones, métricas, matriz de confusión ni predicciones guardadas. No se muestra una predicción inventada.</div>
      <div className="data-grid">
        <section className="panel data-section"><span className="eyebrow">01 · DATOS</span><h2>Un piloto pequeño</h2>
          <p>{data.visual ? `${data.visual.imagenes} imágenes · ${data.visual.clases.intacto ?? 0} intactas · ${data.visual.clases.danado ?? 0} dañadas · ${data.visual.grupos} grupos.` : 'El piloto visual no está importado todavía.'} Son imágenes sintéticas; no representan fotografías reales de envíos.</p>
          <button className="secondary-button" onClick={() => onNavigate('visual')}>Inspeccionar imágenes</button></section>
        <section className="panel data-section"><span className="eyebrow">02 · MÉTODO CANDIDATO</span><h2>Imagen → clase</h2><div className="flow-strip"><span>Imagen</span><span>Preparación</span><span>Vector de píxeles</span><span>MLP</span><span>Clase</span></div>
          <p>El tamaño, color, arquitectura y parámetros se definirán cuando llegue la guía. Las variables Amazon no serán entradas del modelo visual.</p></section>
        <section className="panel data-section"><span className="eyebrow">03 · EVALUACIÓN</span><h2>Pendiente de entrenamiento</h2><p>Se separarán grupos antes de entrenar y se reservará una prueba final. Aquí aparecerán tamaños de particiones, matriz de confusión y métricas por clase cuando existan resultados reproducibles.</p></section>
        <section className="panel data-section"><span className="eyebrow">04 · EJEMPLO</span><h2>Sin predicción disponible</h2><p>Cuando exista un modelo válido, podrás elegir una imagen del conjunto reservado para comparar su etiqueta de origen y la predicción guardada, junto con la versión del modelo.</p></section>
      </div>
    </>}
  </div>
}
