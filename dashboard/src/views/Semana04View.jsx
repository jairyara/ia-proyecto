import { useCallback, useEffect, useMemo, useState } from 'react'
import CodeExplainer from '../components/CodeExplainer.jsx'
import GridCanvas from '../components/GridCanvas.jsx'
import Icon from '../components/Icon.jsx'
import MetricsCard from '../components/MetricsCard.jsx'
import StepPlayer from '../components/StepPlayer.jsx'
import { api } from '../services/api.js'

const DEFAULT_OBSTACLES = [[1, 1], [1, 2], [1, 3], [2, 3], [3, 1]]

function toPayload({ environment, algorithm, heuristic, obstacles, route, start, goal, blockedEdges = [] }) {
  return {
    entorno: environment,
    algoritmo: algorithm,
    heuristica: environment === 'amazon' ? 'haversine' : heuristic,
    inicio: start || null,
    meta: goal || null,
    obstaculos: environment === 'cuadricula' ? obstacles.map(([fila, columna]) => ({ fila, columna })) : [],
    route_id: environment === 'amazon' ? route : null,
    aristas_bloqueadas: blockedEdges,
  }
}

export default function Semana04View() {
  const [environment, setEnvironment] = useState('cuadricula')
  const [algorithm, setAlgorithm] = useState('a_estrella')
  const [heuristic, setHeuristic] = useState('manhattan')
  const [obstacles, setObstacles] = useState(DEFAULT_OBSTACLES)
  const [amazonRoutes, setAmazonRoutes] = useState([])
  const [route, setRoute] = useState('')
  const [start, setStart] = useState('(0,0)')
  const [goal, setGoal] = useState('(4,4)')
  const [simulation, setSimulation] = useState(null)
  const [index, setIndex] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [speed, setSpeed] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [dirty, setDirty] = useState(false)

  const selectedRoute = useMemo(
    () => amazonRoutes.find((item) => item.route_id === route),
    [amazonRoutes, route],
  )

  const runSimulation = useCallback(async (override = {}) => {
    setLoading(true)
    setError('')
    setNotice('')
    setPlaying(false)
    try {
      const config = { environment, algorithm, heuristic, obstacles, route, start, goal, ...override }
      const response = await api.simularBusqueda(toPayload(config))
      setSimulation(response)
      setStart(response.inicio)
      setGoal(response.meta)
      setIndex(0)
      setDirty(false)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }, [algorithm, environment, goal, heuristic, obstacles, route, start])

  useEffect(() => {
    runSimulation()
    api.rutasAmazon().then(({ rutas }) => {
      setAmazonRoutes(rutas)
      if (rutas.length) setRoute(rutas[0].route_id)
    }).catch(() => {})
    // La simulación inicial solo debe usar la configuración por defecto.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (!playing || !simulation?.pasos?.length) return undefined
    if (index >= simulation.pasos.length - 1) {
      setPlaying(false)
      return undefined
    }
    const timeout = window.setTimeout(
      () => setIndex((current) => Math.min(current + 1, simulation.pasos.length - 1)),
      620 / speed,
    )
    return () => window.clearTimeout(timeout)
  }, [index, playing, simulation, speed])

  const step = simulation?.pasos?.[index]

  const changeEnvironment = (value) => {
    setEnvironment(value)
    setDirty(true)
    if (value === 'cuadricula') {
      setStart('(0,0)')
      setGoal('(4,4)')
      setHeuristic('manhattan')
    } else if (selectedRoute) {
      setStart(selectedRoute.deposito)
      setGoal(selectedRoute.paradas.find((item) => item.id !== selectedRoute.deposito)?.id || '')
      setHeuristic('haversine')
    }
  }

  const changeRoute = (routeId) => {
    const next = amazonRoutes.find((item) => item.route_id === routeId)
    setRoute(routeId)
    if (next) {
      setStart(next.deposito)
      setGoal(next.paradas.find((item) => item.id !== next.deposito)?.id || '')
    }
    setDirty(true)
  }

  const toggleObstacle = (row, col) => {
    const id = `(${row},${col})`
    if (id === start || id === goal) return
    setObstacles((current) => {
      const exists = current.some(([r, c]) => r === row && c === col)
      return exists
        ? current.filter(([r, c]) => r !== row || c !== col)
        : [...current, [row, col]]
    })
    setDirty(true)
    setPlaying(false)
  }

  const replanify = async () => {
    const original = simulation?.resultado?.ruta || []
    if (original.length < 2) return
    const blockIndex = Math.min(1, original.length - 2)
    setLoading(true)
    setError('')
    setPlaying(false)
    try {
      const response = await api.replanificar({
        simulacion: toPayload({ environment, algorithm, heuristic, obstacles, route, start: simulation.inicio, goal: simulation.meta }),
        ruta_original: original,
        paso_bloqueo: blockIndex,
      })
      setSimulation(response.simulacion)
      setStart(response.simulacion.inicio)
      setGoal(response.simulacion.meta)
      setIndex(0)
      setNotice(`Tramo ${original[blockIndex]} → ${original[blockIndex + 1]} bloqueado. Se calculó una nueva subruta.`)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="view-shell">
      <header className="view-header">
        <div>
          <div className="week-kicker"><span>SEMANA 04</span><i /> BÚSQUEDA INFORMADA</div>
          <h1>Encontrar la mejor ruta,<br /><em>paso a paso.</em></h1>
          <p>Observa cómo A* equilibra el costo recorrido con una estimación admisible, y contrástalo con búsquedas no informadas.</p>
        </div>
        <div className="header-stat">
          <span>ESTADO DEL EXPERIMENTO</span>
          <strong><i className={loading ? 'pulse' : ''} /> {loading ? 'Calculando' : simulation?.resultado?.encontrado ? 'Ruta encontrada' : 'Sin solución'}</strong>
          <small>{simulation ? `${simulation.pasos.length} estados trazables` : 'Esperando API'}</small>
        </div>
      </header>

      <section className="control-deck" aria-label="Configuración del experimento">
        <div className="segmented-control">
          <button className={environment === 'cuadricula' ? 'active' : ''} onClick={() => changeEnvironment('cuadricula')}>Cuadrícula 5×5</button>
          <button className={environment === 'amazon' ? 'active' : ''} onClick={() => changeEnvironment('amazon')}>Amazon Last Mile</button>
        </div>
        <label className="field compact-field">
          <span>ALGORITMO</span>
          <select value={algorithm} onChange={(event) => { setAlgorithm(event.target.value); setDirty(true) }}>
            <option value="a_estrella">A* — informada</option>
            <option value="dijkstra">Dijkstra — costo uniforme</option>
            <option value="bfs">BFS — por niveles</option>
          </select>
        </label>
        <label className="field compact-field">
          <span>HEURÍSTICA</span>
          <select value={environment === 'amazon' ? 'haversine' : heuristic} disabled={algorithm !== 'a_estrella' || environment === 'amazon'} onChange={(event) => { setHeuristic(event.target.value); setDirty(true) }}>
            <option value="manhattan">Manhattan</option>
            <option value="euclidiana">Euclidiana</option>
            {environment === 'amazon' && <option value="haversine">Haversine / v máx.</option>}
          </select>
        </label>
        {environment === 'amazon' && (
          <label className="field compact-field route-field">
            <span>RUTA REAL</span>
            <select value={route} onChange={(event) => changeRoute(event.target.value)}>
              {amazonRoutes.map((item) => <option key={item.route_id} value={item.route_id}>{item.estacion} · {item.num_paradas} paradas</option>)}
            </select>
          </label>
        )}
        <button className="primary-button" onClick={() => runSimulation()} disabled={loading || (environment === 'amazon' && !route)}>
          <Icon name="spark" /> {dirty ? 'Aplicar cambios' : 'Simular de nuevo'}
        </button>
      </section>

      {environment === 'amazon' && selectedRoute && (
        <section className="node-selectors">
          <label className="field"><span>ORIGEN</span><select value={start} onChange={(event) => { setStart(event.target.value); setDirty(true) }}>{selectedRoute.paradas.map((item) => <option key={item.id} value={item.id}>{item.id}{item.id === selectedRoute.deposito ? ' · depósito' : ''}</option>)}</select></label>
          <span className="node-arrow">→</span>
          <label className="field"><span>DESTINO</span><select value={goal} onChange={(event) => { setGoal(event.target.value); setDirty(true) }}>{selectedRoute.paradas.filter((item) => item.id !== start).map((item) => <option key={item.id} value={item.id}>{item.id}</option>)}</select></label>
          <p>Ruta {selectedRoute.fecha} · estación {selectedRoute.estacion}</p>
        </section>
      )}

      {error && <div className="alert alert--error" role="alert"><Icon name="alert" /><span><strong>No fue posible ejecutar la simulación.</strong>{error}</span></div>}
      {notice && <div className="alert alert--success" role="status"><Icon name="check" /><span><strong>Replanificación completada.</strong>{notice}</span></div>}

      <div className="lab-grid">
        <section className="panel canvas-panel">
          <div className="panel-heading">
            <div><span className="eyebrow">ESPACIO DE ESTADOS</span><h2>{environment === 'cuadricula' ? 'Red urbana sintética' : 'Paradas geográficas reales'}</h2></div>
            <div className="legend"><span><i className="legend-start" />Origen</span><span><i className="legend-frontier" />Frontera</span><span><i className="legend-closed" />Explorado</span><span><i className="legend-route" />Ruta</span></div>
          </div>
          <div className={`canvas-wrap ${loading ? 'canvas-wrap--loading' : ''}`}>
            <GridCanvas environment={environment} graph={simulation?.grafo} step={step} start={simulation?.inicio || start} goal={simulation?.meta || goal} obstacles={obstacles} onToggle={toggleObstacle} />
            {loading && <div className="loading-overlay"><span className="loader" />Calculando estados…</div>}
          </div>
          {environment === 'cuadricula' && <p className="canvas-hint">Haz clic o presiona Enter sobre una celda para bloquearla. Luego aplica los cambios.</p>}
          <StepPlayer index={index} total={simulation?.pasos?.length || 0} playing={playing} speed={speed} onPlaying={setPlaying} onStep={(delta) => { setPlaying(false); setIndex((current) => Math.max(0, Math.min(current + delta, (simulation?.pasos?.length || 1) - 1))) }} onReset={() => { setPlaying(false); setIndex(0) }} onSpeed={setSpeed} />
        </section>
        <CodeExplainer code={simulation?.codigo} step={step} fileName={simulation?.archivo_codigo} />
      </div>

      <MetricsCard simulation={simulation} step={step} />

      <div className="detail-grid">
        <section className="panel data-panel">
          <div className="panel-heading"><div><span className="eyebrow">COLA DE PRIORIDAD</span><h2>Candidatos en frontera</h2></div><span className="count-pill">{step?.frontera?.length || 0} visibles</span></div>
          <div className="table-wrap"><table><thead><tr><th>Nodo</th><th>g(n)</th><th>h(n)</th><th>f(n)</th></tr></thead><tbody>
            {(step?.frontera || []).map((item, itemIndex) => <tr key={`${item.nodo}-${itemIndex}`}><td><i className="node-dot" />{item.nodo}</td><td>{item.g}</td><td>{item.h}</td><td><strong>{item.f}</strong></td></tr>)}
            {!step?.frontera?.length && <tr><td colSpan="4" className="empty-cell">La frontera está vacía en este paso.</td></tr>}
          </tbody></table></div>
        </section>
        <section className="panel replanning-panel">
          <div><span className="eyebrow eyebrow--warm">EVENTO DINÁMICO</span><h2>¿Y si una vía se cierra?</h2><p>Bloquea un tramo de la ruta óptima y observa cómo el agente vuelve a planificar desde el punto actual.</p></div>
          <button className="danger-button" onClick={replanify} disabled={loading || dirty || !simulation?.resultado?.encontrado}><Icon name="alert" /> Bloquear siguiente tramo</button>
          <small>El grafo original no se modifica: el bloqueo vive solo en esta simulación.</small>
        </section>
      </div>
    </div>
  )
}
