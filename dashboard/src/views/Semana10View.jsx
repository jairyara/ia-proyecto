import { lazy, Suspense, useEffect, useState } from 'react'
import Icon from '../components/Icon.jsx'
import { api } from '../services/api.js'

const Semana10Charts = lazy(() => import('./Semana10Charts.jsx'))

export default function Semana10View() {
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [selection, setSelection] = useState('ambos')

  useEffect(() => {
    api.resultadosVision10().then(setResult).catch((requestError) => setError(requestError.message))
  }, [])

  const visibles = result?.ejemplos.filter((ejemplo) => selection === 'ambos' || ejemplo.etiqueta === selection) ?? []

  return (
    <div className="view-shell semana10-view">
      <header className="view-header view-header--compact">
        <div>
          <div className="week-kicker"><span>SEMANA 10</span><i /> RECONOCIMIENTO DE IMÁGENES</div>
          <h1>Del paquete a un<br /><em>vector explicable.</em></h1>
          <p>Regiones, tonos y textura medidos sobre la misma imagen. Comparamos evidencia descriptiva; todavía no diagnosticamos daños.</p>
        </div>
        <div className="model-badge model-badge--mint"><Icon name="texture" size={24} /><span><small>SIN CLASIFICADOR</small><strong>Otsu · regiones · LBP</strong></span></div>
      </header>

      {error && <div className="alert alert--error" role="alert"><Icon name="alert" /><span><strong>Evidencia no disponible.</strong> {error}</span></div>}
      {!result && !error && <div className="panel">Cargando evidencia de Semana 10…</div>}
      {result && <>
        <section className="provenance-banner">
          <div><strong>{result.entrenamiento}</strong><small>imágenes analizadas</small></div>
          <div><strong>{result.prueba_reservada_sin_descriptores}</strong><small>reservadas, sin descriptores</small></div>
          <div><strong>{result.vector.dimension}D</strong><small>por imagen</small></div>
          <p><Icon name="check" /><span><b>Origen:</b> {result.origen}. Manifiesto SHA-256 {result.manifiesto_sha256.slice(0, 12)}…</span></p>
        </section>

        <section className="panel data-section learning-vision-stage">
          <span className="eyebrow">01 · UNA IMAGEN, TRES BLOQUES</span>
          <h2>Un descriptor por paquete observado</h2>
          <p>La misma vista lateral pasa a gris {result.dimensiones_analisis[0]} × {result.dimensiones_analisis[1]}. Otsu produce una máscara; sus componentes se miden con conectividad de {result.conectividad} vecinos y filtro de área &gt; {result.filtro_area_px} px. El histograma de intensidad y LBP se calculan sobre la imagen gris completa.</p>
          <div className="learning-facts"><div><strong>3</strong><small>medidas de región</small></div><div><strong>32</strong><small>probabilidades de intensidad</small></div><div><strong>18</strong><small>probabilidades LBP</small></div></div>
          <p className="method-note">El área se expresa como fracción de la imagen. Histograma y LBP suman 1 por separado. El fondo puede influir: este vector no identifica qué píxeles son daño.</p>
        </section>

        <section className="panel data-section learning-vision-stage">
          <span className="eyebrow">02 · COMPARACIÓN REPRODUCIBLE</span>
          <h2>Dos ejemplos, no una validación</h2>
          <p>Selecciona un caso para seguir su imagen, máscara y descriptores, o conserva ambos para compararlos.</p>
          <div className="semana10-mode-switch" role="group" aria-label="Modo de comparación de Semana 10">
            {[
              ['ambos', 'Ambos'], ['danado', 'Dañado'], ['intacto', 'Intacto'],
            ].map(([value, label]) => <button key={value} type="button" className={selection === value ? 'active' : ''}
              aria-pressed={selection === value} onClick={() => setSelection(value)}>{label}</button>)}
          </div>
          <div className={`symbolic-grid semana10-examples ${selection !== 'ambos' ? 'semana10-examples--solo' : ''}`}>
            {visibles.map((ejemplo) => <article className="panel" key={ejemplo.id_origen}>
              <span className="eyebrow">{ejemplo.etiqueta.toUpperCase()} · ID {ejemplo.id_origen}</span>
              <div className="semana10-image-pair">
                <figure><img src={api.ejemploVision10(ejemplo.etiqueta, 'gris')} alt={`Vista lateral gris del ejemplo ${ejemplo.etiqueta}`} /><figcaption>Imagen analizada</figcaption></figure>
                <figure><img src={api.ejemploVision10(ejemplo.etiqueta, 'mascara')} alt={`Máscara Otsu del ejemplo ${ejemplo.etiqueta}; incluye banda y fondo`} /><figcaption>Máscara Otsu · no es daño</figcaption></figure>
              </div>
              <h3>{ejemplo.regiones_validas} regiones válidas</h3>
              <p>Otsu {ejemplo.umbral_otsu_0_255}/255 · máscara {ejemplo.mascara_porcentaje}% · área media {ejemplo.area_media_porcentaje}% de la imagen.</p>
              <p>Desviación de área {ejemplo.area_desviacion_porcentaje}%. {ejemplo.sin_regiones_validas && 'No se detectaron regiones válidas; los ceros no indican un paquete intacto.'}</p>
            </article>)}
          </div>
          <p>Estos IDs se eligen de forma determinista dentro de entrenamiento. Sus etiquetas provienen del manifiesto; <strong>ningún descriptor predijo la clase</strong>.</p>
        </section>

        <Suspense fallback={<div className="panel semana10-chart-loading">Preparando gráficas comparativas…</div>}>
          <Semana10Charts ejemplos={visibles} referencia={result.ejemplos} />
        </Suspense>

        <details className="panel semana10-raw-evidence">
          <summary><span><span className="eyebrow">EVIDENCIA TÉCNICA</span><strong>Ver imagen, máscara y figura reproducible</strong></span><Icon name="chevronRight" /></summary>
          <div className="semana10-raw-evidence__body">
            <p>La figura original de Matplotlib permanece versionada para comprobar el método y la máscara Otsu. No sustituye las gráficas interactivas anteriores.</p>
            <img src={api.evidenciaVision10()} alt="Comparación técnica de un paquete dañado y uno intacto: imagen gris, máscara Otsu, histograma de intensidad e histograma LBP" />
          </div>
        </details>

        <section className="panel data-section learning-vision-stage">
          <span className="eyebrow">04 · LECTURA RESPONSABLE</span><h2>Qué podemos concluir</h2>
          <div className="learning-facts">{Object.entries(result.resumen_clases).map(([clase, resumen]) => <div key={clase}><strong>{resumen.regiones_validas_mediana}</strong><small>mediana de regiones · {clase} (n={resumen.n})</small></div>)}</div>
          <p>La comparación resume propiedades del piloto sintético. Una región conectada no es un paquete físico; diferencias entre clases pueden reflejar fondo, encuadre o iluminación. No se entrenó ni evaluó un clasificador esta semana.</p>
          <div className="learning-conclusion"><Icon name="alert" /><p><strong>Límite operativo:</strong> {result.advertencia} Tampoco se modifica A*, cuarentena ni autorización de despacho.</p></div>
        </section>
      </>}
    </div>
  )
}
