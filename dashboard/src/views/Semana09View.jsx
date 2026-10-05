import { useEffect, useState } from 'react'
import Icon from '../components/Icon.jsx'
import { api } from '../services/api.js'

export default function Semana09View() {
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [selectedSigma, setSelectedSigma] = useState(null)

  useEffect(() => {
    api.resultadosVision09().then(setResult).catch((err) => setError(err.message))
  }, [])

  const activeCanny = result?.canny?.find((item) => item.sigma === selectedSigma) || result?.canny?.[0]

  return (
    <div className="view-shell semana09-view">
      <header className="view-header view-header--compact">
        <div>
          <div className="week-kicker"><span>SEMANA 09</span><i /> VISIÓN POR COMPUTADOR</div>
          <h1>Del píxel a la<br /><em>región analizable.</em></h1>
          <p>Explora cómo Canny detecta bordes y cómo Otsu separa regiones en una escena logística sintética, antes de cualquier clasificación.</p>
        </div>
        <div className="model-badge model-badge--mint"><Icon name="search" size={24} /><span><small>SIN CLASIFICACIÓN</small><strong>Canny · Otsu · 8 vecinos</strong></span></div>
      </header>

      {error && <div className="alert alert--error" role="alert"><Icon name="alert" /><span><strong>Evidencia no disponible.</strong> {error}</span></div>}
      {!result && !error && <div className="panel">Cargando evidencia de Semana 9…</div>}
      {result && <>
        <section className="provenance-banner">
          <div><strong>{result.otsu_umbral_0_255}/255</strong><small>umbral Otsu</small></div>
          <div><strong>{result.regiones_conectadas}</strong><small>regiones conectadas</small></div>
          <div><strong>{result.mascara_porcentaje}%</strong><small>píxeles de máscara</small></div>
          <p><Icon name="check" /><span><b>Origen:</b> {result.origen}. {result.ancho_px} × {result.alto_px} píxeles; SHA-256 {result.sha256_imagen.slice(0, 12)}…</span></p>
        </section>

        <section className="panel data-section learning-vision-stage">
          <span className="eyebrow">01 · ENTRADA Y CARACTERÍSTICAS</span><h2>Una escena, valores medibles</h2>
          <div className="learning-vision-input"><img src={api.imagenVision09()} alt="Escena sintética de un paquete sobre una banda transportadora" /><div>
            <p>La imagen de {result.ancho_px} × {result.alto_px} píxeles representa un paquete dibujado para esta práctica. <strong>No es una imagen del piloto MLP de la semana 8</strong> ni una fotografía de Amazon.</p>
            <p><strong>Intensidad media:</strong> {result.intensidad_media_0_255}/255 · <strong>desviación:</strong> {result.intensidad_desviacion_0_255 ?? '—'}/255 · <strong>RGB medio:</strong> {result.color_medio_rgb.join(' · ')}.</p>
            <p className="learning-equation"><code>media = suma de intensidades / ({result.ancho_px} × {result.alto_px})</code></p>
            <p>El contraste entre caja clara y fondo oscuro motiva probar un umbral. La media global por sí sola no identifica el paquete.</p>
          </div></div>
        </section>

        <div className="symbolic-grid semana09-lab-grid">
          <section className="panel semana09-controls">
            <div className="panel-heading"><div><span className="eyebrow">02 · DETECCIÓN DE BORDES</span><h2>Compara la sensibilidad de Canny</h2></div><span className="count-pill">{result.canny.length} mediciones</span></div>
            <div className="semana09-card-body">
              <p><strong>Teoría:</strong> Canny suaviza con una gaussiana, calcula gradientes, conserva máximos locales y conecta bordes fuertes con débiles. <code>σ</code> controla el suavizado; no significa «probabilidad de daño».</p>
              <p>Selecciona una medición del experimento. Los paneles de la figura muestran todas las variantes; aquí cambia el dato resaltado, no se recalcula la imagen.</p>
              <div className="semana09-sigma-picker" aria-label="Valores de sigma">
                {result.canny.map((item) => <button key={item.sigma} type="button" className={activeCanny?.sigma === item.sigma ? 'active' : ''} aria-pressed={activeCanny?.sigma === item.sigma} onClick={() => setSelectedSigma(item.sigma)}>σ = {item.sigma}</button>)}
              </div>
              <p className="method-note"><b>Compromiso:</b> menos sigma conserva detalles de cinta y banda; más sigma elimina ruido, pero puede borrar rasgos finos. Otsu se calcula por separado y no cambia aquí.</p>
            </div>
          </section>
          <section className="panel classification-result classification-result--mint semana09-result" aria-live="polite">
            <div className="result-orbit"><span className="result-icon"><Icon name="search" size={28} /></span><i /><i /></div>
            <span className="eyebrow">BORDES DETECTADOS · σ = {activeCanny?.sigma ?? '—'}</span>
            <h2>{activeCanny ? activeCanny.pixeles_borde.toLocaleString('es-CO') : '—'}</h2>
            <p>píxeles de borde · {activeCanny?.densidad_porcentaje ?? '—'} % de la escena</p>
            <div className="confidence-note"><Icon name="check" /><span><strong>Medición reproducible</strong><small>Valor leído de la evidencia guardada, no una clasificación.</small></span></div>
          </section>
        </div>
        <section className="panel data-section learning-vision-stage">
          <span className="eyebrow">03 · UMBRAL Y MÁSCARA</span><h2>Otsu separa claro de oscuro</h2>
          <p>Otsu trabaja con la imagen gris original, <strong>no</strong> con los bordes de Canny. Busca el umbral que maximiza la separación entre fondo y objeto:</p>
          <p className="learning-equation"><code>t* = arg maxₜ [ω₀(t) · ω₁(t) · (μ₀(t) − μ₁(t))²]</code></p>
          <div className="learning-facts"><div><strong>{result.otsu_umbral_0_255}/255</strong><small>umbral calculado</small></div><div><strong>{result.mascara_pixeles?.toLocaleString('es-CO') ?? '—'}</strong><small>píxeles con gris &gt; umbral</small></div><div><strong>{result.mascara_porcentaje}%</strong><small>de la escena</small></div></div>
          <p>La máscara binaria vale 1 donde la intensidad supera {result.otsu_umbral_0_255}; no etiqueta «daño», solo separa zonas por brillo.</p>
        </section>
        <section className="panel data-section learning-vision-stage">
          <span className="eyebrow">04 · CONECTIVIDAD E INTERPRETACIÓN</span><h2>Regiones de píxeles ≠ paquetes</h2>
          <p>Se agrupan píxeles verdaderos que se tocan por lados o diagonales (<strong>{result.conectividad}-vecinos</strong>). En esta escena aparecen <strong>{result.regiones_conectadas} regiones</strong>{result.regiones_mayores?.length ? `, de ${result.regiones_mayores.map((item) => item.area_px.toLocaleString('es-CO')).join(' y ')} píxeles` : ''}.</p>
          <p>Una línea oscura separa caras del mismo paquete. Por eso {result.regiones_conectadas} regiones no prueban que existan {result.regiones_conectadas} paquetes ni permiten diagnosticar una rasgadura.</p>
          <div className="learning-conclusion"><Icon name="alert" /><p><strong>Conclusión de esta semana:</strong> bordes y regiones son señales visuales candidatas para inspección humana, no una decisión de despacho. Probar fotografías reales y conectar una segmentación validada con reconocimiento son mejoras futuras.</p></div>
        </section>
        <section className="panel semana09-figure trace-panel">
          <div className="panel-heading"><div><span className="eyebrow">EVIDENCIA DE LOS PASOS 01–04</span><h2>Original, contornos, máscara y regiones</h2></div><span className="count-pill">{result.ancho_px} × {result.alto_px} px</span></div>
          <img src={api.evidenciaVision09()} alt="Comparación de la escena original, Canny con sigma 1, 2 y 4, máscara de Otsu y regiones conectadas" />
        </section>
        <section className="explainability-strip explainability-strip--mint">
          <div><Icon name="search" /><span><strong>Bordes medidos</strong><small>Sigma cambia el suavizado de Canny.</small></span></div>
          <div><Icon name="activity" /><span><strong>Máscara separada</strong><small>Otsu no depende del sigma elegido.</small></span></div>
          <div><Icon name="check" /><span><strong>Sin diagnóstico</strong><small>Segmentar no equivale a clasificar.</small></span></div>
        </section>
      </>}
    </div>
  )
}
