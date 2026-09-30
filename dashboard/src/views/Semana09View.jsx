import { useEffect, useState } from 'react'
import Icon from '../components/Icon.jsx'
import { api } from '../services/api.js'

export default function Semana09View() {
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.resultadosVision09().then(setResult).catch((err) => setError(err.message))
  }, [])

  return (
    <div className="view-shell semana09-view">
      <header className="view-header view-header--compact">
        <div>
          <div className="week-kicker"><span>SEMANA 09</span><i /> VISIÓN POR COMPUTADOR</div>
          <h1>Del píxel a la<br /><em>región analizable.</em></h1>
          <p>Una escena logística sintética y reproducible muestra qué separan Canny y Otsu antes de cualquier clasificación.</p>
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

        <section className="panel semana09-figure">
          <div className="panel-heading"><div><span className="eyebrow">EVIDENCIA REPRODUCIBLE</span><h2>Original, contornos, máscara y regiones</h2></div></div>
          <img src={api.evidenciaVision09()} alt="Comparación de la escena original, Canny con sigma 1, 2 y 4, máscara de Otsu y regiones conectadas" />
        </section>

        <div className="semana09-grid">
          <section className="panel">
            <div className="panel-heading"><div><span className="eyebrow">CARACTERÍSTICAS</span><h2>Qué medimos</h2></div></div>
            <p>Intensidad media: <b>{result.intensidad_media_0_255}/255</b>. Color medio RGB: <b>{result.color_medio_rgb.join(' · ')}</b>. El contraste claro/oscuro permite aislar el paquete; los bordes muestran también cinta, etiqueta y rasgadura.</p>
          </section>
          <section className="panel">
            <div className="panel-heading"><div><span className="eyebrow">SENSIBILIDAD</span><h2>Sigma en Canny</h2></div></div>
            <ul>{result.canny.map((item) => <li key={item.sigma}>σ={item.sigma}: <b>{item.pixeles_borde.toLocaleString('es-CO')}</b> píxeles de borde ({item.densidad_porcentaje}%)</li>)}</ul>
            <p>Más sigma suaviza el detalle; Otsu se calcula aparte y no cambia al variar este parámetro.</p>
          </section>
          <section className="panel">
            <div className="panel-heading"><div><span className="eyebrow">INTERPRETACIÓN</span><h2>Dos regiones ≠ dos paquetes</h2></div></div>
            <p>La máscara divide las caras claras de un único paquete por sus líneas oscuras. Las regiones reflejan conectividad de píxeles, no un conteo fiable de objetos físicos ni un diagnóstico de daño.</p>
          </section>
        </div>
      </>}
    </div>
  )
}
