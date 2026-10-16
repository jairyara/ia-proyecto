import { useEffect, useState } from 'react'
import Icon from '../components/Icon.jsx'
import { api } from '../services/api.js'
import './Semana11View.css'

const labels = {
  logistic: 'Regresión logística',
  forest: 'Random Forest',
  mlp: 'MLP',
  hist: 'HistGradientBoosting',
}

function percent(value) {
  return `${(value * 100).toFixed(1).replace('.', ',')} %`
}

export default function Semana11View() {
  const [payload, setPayload] = useState(null)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState('forest')

  useEffect(() => {
    api.benchmarkSemana11().then(setPayload).catch((failure) => setError(failure.message))
  }, [])

  const rows = payload?.resultados ?? []
  const current = rows.find((row) => row.modelo === selected)
  const detail = payload?.evidencia.modelos?.[selected]

  return <div className="view-shell semana11-view">
    <header className="view-header view-header--compact">
      <div>
        <div className="week-kicker"><span>SEMANA 11</span><i /> DECISIÓN CON EVIDENCIA</div>
        <h1>Cuatro modelos.<br /><em>Una regla bajo examen.</em></h1>
        <p>Benchmark sobre paradas Amazon Last Mile del proyecto. La etiqueta es <strong>riesgo heurístico estimado</strong>, no retraso observado: una métrica alta no equivale a anticipar demoras reales.</p>
      </div>
      <div className="model-badge model-badge--mint"><Icon name="activity" size={24} /><span><small>RIESGO LOGÍSTICO</small><strong>Benchmark · ADR-011</strong></span></div>
    </header>

    {error && <div className="alert alert--error" role="alert"><Icon name="alert" /><span><strong>Evidencia no disponible.</strong> {error}</span></div>}
    {!payload && !error && <div className="panel">Cargando evidencia de Semana 11…</div>}
    {payload && <>
      <section className="provenance-banner" aria-label="Procedencia del benchmark">
        <div><strong>{payload.evidencia.n_total.toLocaleString('es-CO')}</strong><small>entregas Amazon elegibles</small></div>
        <div><strong>{payload.evidencia.n_train.toLocaleString('es-CO')} / {payload.evidencia.n_test.toLocaleString('es-CO')}</strong><small>train / test por rutas</small></div>
        <div><strong>{payload.evidencia.n_routes_train} / {payload.evidencia.n_routes_test}</strong><small>rutas disjuntas</small></div>
        <p><Icon name="check" /><span><b>Fuente:</b> {payload.evidencia.dataset} · SHA-256 {payload.evidencia.sha256_dataset.slice(0, 12)}…</span></p>
      </section>

      <section className="panel data-section semana11-stage" aria-label="Mapa de fuentes y conteos">
        <span className="eyebrow">ANTES DE COMPARAR · PROCEDENCIA</span>
        <h2>Qué cuenta cada número</h2>
        <div className="semana11-source-grid">
          <div><strong>{payload.evidencia.n_raw.toLocaleString('es-CO')}</strong><span>paradas Amazon importadas</span><small><code>{payload.evidencia.dataset}</code>; incluyen {payload.evidencia.n_excluded_station} estaciones sin entrega.</small></div>
          <div><strong>{payload.evidencia.n_total.toLocaleString('es-CO')}</strong><span>entregas elegibles</span><small>Paradas Dropoff usadas por los cuatro modelos; no paquetes individuales.</small></div>
          <div><strong>{payload.evidencia.n_test.toLocaleString('es-CO')}</strong><span>entregas de prueba</span><small>{payload.evidencia.n_routes_test} rutas completas reservadas, sin mezclarlas con entrenamiento.</small></div>
          <div><strong>800 / 200</strong><span>otras prácticas</span><small>Pedidos sintéticos de Semana 2 / imágenes del piloto visual: ninguno entra aquí.</small></div>
        </div>
        <p className="method-note"><strong>Importante:</strong> <code>retrasado_estimado</code> se calculó con reglas. En este CSV, dos cláusulas visibles reproducen todos los positivos; Forest e Hist pueden aprenderlas casi exactamente. Eso no valida una predicción de tardanza real.</p>
      </section>

      <section className="panel data-section semana11-stage">
        <span className="eyebrow">01 · COMPARACIÓN CONTROLADA</span>
        <h2>Aprender una etiqueta heurística, no daño visual</h2>
        <p>Todos los candidatos usan siete variables disponibles antes del despacho. El split deja rutas enteras fuera de train; cinco pliegues también agrupan por ruta. El umbral se elige con F2 solo en entrenamiento y el test de {payload.evidencia.n_test.toLocaleString('es-CO')} entregas se consulta una vez.</p>
        <div className="semana11-grid" role="list" aria-label="Resultados del benchmark">
          {rows.map((row) => <button type="button" role="listitem" key={row.modelo} className={`semana11-model ${selected === row.modelo ? 'semana11-model--active' : ''}`} onClick={() => setSelected(row.modelo)} aria-pressed={selected === row.modelo}>
            <small>{row.modelo === 'forest' ? 'GANADOR ACADÉMICO' : row.modelo === 'hist' ? 'RETADOR' : 'COMPARADOR'}</small>
            <strong>{labels[row.modelo]}</strong>
            <span className="semana11-model__number">{percent(row.f1_retraso)}</span>
            <span>F1 de etiqueta heurística</span>
            <span className="semana11-model__bar"><i style={{ width: `${row.f1_retraso * 100}%` }} /></span>
            <span className="semana11-model__foot">Recall {percent(row.recall_retraso)} · FN {row.falsos_negativos} · FP {row.falsos_positivos}</span>
          </button>)}
        </div>
      </section>

      {current && detail && <section className="panel data-section semana11-stage">
        <span className="eyebrow">02 · LEER EL COSTO DEL ERROR</span>
        <h2>{labels[selected]}</h2>
        <div className="semana11-facts">
          <div><strong>{percent(current.accuracy)}</strong><small>accuracy</small></div>
          <div><strong>{percent(current.precision_retraso)}</strong><small>precision · retraso</small></div>
          <div><strong>{percent(current.recall_retraso)}</strong><small>recall · retraso</small></div>
          <div><strong>{current.umbral.toFixed(3)}</strong><small>umbral F2 · train</small></div>
        </div>
        <div className="semana11-confusion">
          <div><b>{detail.matriz_confusion[0][0]}</b><span>A tiempo, detectado</span></div>
          <div><b>{detail.matriz_confusion[0][1]}</b><span>Falsa alerta</span></div>
          <div className="semana11-confusion__risk"><b>{detail.matriz_confusion[1][0]}</b><span>Retraso no detectado</span></div>
          <div><b>{detail.matriz_confusion[1][1]}</b><span>Retraso detectado</span></div>
        </div>
        <p className="method-note">Matriz: filas = etiqueta heurística [0, 1]; columnas = predicción [0, 1]. Tiempo de ajuste final {current.fit_seconds.toFixed(3)} s; inferencia p95 {current.infer_ms_por_pedido_p95.toFixed(4)} ms/parada en lote de {payload.evidencia.n_test.toLocaleString('es-CO')}, no latencia HTTP ni E2E.</p>
        {detail.advertencias_convergencia.length > 0 && <p className="method-note"><strong>Advertencia:</strong> MLP no convergió en 350 iteraciones; su posición no debe interpretarse como optimización exhaustiva.</p>}
      </section>}

      <section className="panel data-section semana11-stage">
        <span className="eyebrow">03 · MAPA INTERACTIVO</span>
        <h2>Del dato a la decisión de Torre</h2>
        <p>Explora el flujo del benchmark y sus límites. El diagrama no representa servicios productivos ya desplegados.</p>
        <div className="semana11-diagram"><iframe title="Flujo interactivo del benchmark de Semana 11, generado con archify" src="/semana11-benchmark.html" loading="lazy" sandbox="allow-scripts allow-downloads" /></div>
        <a className="semana11-open-diagram" href="/semana11-benchmark.html" target="_blank" rel="noreferrer">Abrir diagrama a pantalla completa ↗</a>
      </section>

      <section className="panel data-section semana11-stage">
        <span className="eyebrow">04 · DECISIÓN Y SIGUIENTE INCREMENTO</span>
        <h2>Forest gana el laboratorio; la regla sigue vigente</h2>
        <p>Forest obtiene F1 {percent(rows.find((row) => row.modelo === 'forest').f1_retraso)} sobre la etiqueta heurística: cero falsos negativos y una falsa alerta. Hist queda cerca. Sin embargo, la regla explícita que creó la etiqueta reproduce todos los positivos del CSV; reemplazarla por ML no aporta todavía una mejora operativa demostrada.</p>
        <div className="learning-conclusion"><Icon name="alert" /><p><strong>Límite operativo:</strong> {payload.evidencia.advertencia} El benchmark no clasifica paquetes; el SVC visual está previsto para Semana 15 y requiere evaluación independiente. La definición de retraso real queda pendiente para el Corte 3.</p></div>
      </section>
    </>}
  </div>
}
