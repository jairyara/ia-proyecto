import { useMemo } from 'react'

function Grid({ graph, step, start, goal, obstacles, onToggle }) {
  const frontier = new Set(step?.frontera?.map((item) => item.nodo) || [])
  const closed = new Set(step?.cerrados || [])
  const route = new Set(step?.ruta_parcial || [])
  const obstacleSet = new Set(obstacles.map(([r, c]) => `(${r},${c})`))
  const cells = Array.from({ length: 25 }, (_, index) => {
    const row = Math.floor(index / 5)
    const col = index % 5
    return { row, col, id: `(${row},${col})` }
  })
  return (
    <svg className="route-svg" viewBox="0 0 400 400" role="img" aria-label="Cuadrícula interactiva de cinco por cinco">
      <defs>
        <pattern id="micro-grid" width="14" height="14" patternUnits="userSpaceOnUse">
          <path d="M 14 0 L 0 0 0 14" fill="none" stroke="currentColor" strokeOpacity=".045" strokeWidth="1" />
        </pattern>
      </defs>
      <rect width="400" height="400" rx="18" className="canvas-bg" />
      <rect width="400" height="400" rx="18" fill="url(#micro-grid)" />
      {cells.map(({ row, col, id }) => {
        const blocked = obstacleSet.has(id)
        const states = [
          blocked && 'cell--blocked',
          closed.has(id) && 'cell--closed',
          frontier.has(id) && 'cell--frontier',
          route.has(id) && 'cell--route',
          step?.actual === id && 'cell--current',
          start === id && 'cell--start',
          goal === id && 'cell--goal',
        ].filter(Boolean).join(' ')
        return (
          <g key={id} className={`grid-cell ${states}`} role="button" tabIndex="0"
            aria-label={`Celda ${row}, ${col}${blocked ? ', bloqueada' : ''}`}
            onClick={() => onToggle(row, col)}
            onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); onToggle(row, col) } }}>
            <rect x={27 + col * 70} y={27 + row * 70} width="58" height="58" rx="10" />
            {blocked && <text x={56 + col * 70} y={64 + row * 70}>×</text>}
            {!blocked && <text x={56 + col * 70} y={63 + row * 70}>{start === id ? 'S' : goal === id ? 'G' : `${row},${col}`}</text>}
          </g>
        )
      })}
    </svg>
  )
}

function AmazonGraph({ graph, step, start, goal }) {
  const projection = useMemo(() => {
    const nodes = graph?.nodos || []
    if (!nodes.length) return new Map()
    const lngs = nodes.map((n) => n.lng)
    const lats = nodes.map((n) => n.lat)
    const [minX, maxX] = [Math.min(...lngs), Math.max(...lngs)]
    const [minY, maxY] = [Math.min(...lats), Math.max(...lats)]
    return new Map(nodes.map((node) => [node.id, {
      x: 34 + ((node.lng - minX) / (maxX - minX || 1)) * 532,
      y: 326 - ((node.lat - minY) / (maxY - minY || 1)) * 292,
    }]))
  }, [graph])
  const frontier = new Set(step?.frontera?.map((item) => item.nodo) || [])
  const closed = new Set(step?.cerrados || [])
  const routeIds = step?.ruta_parcial || []
  const path = routeIds.map((id) => projection.get(id)).filter(Boolean).map((p) => `${p.x},${p.y}`).join(' ')
  return (
    <svg className="route-svg route-svg--amazon" viewBox="0 0 600 360" role="img" aria-label="Grafo geográfico de una ruta Amazon Last Mile">
      <rect width="600" height="360" rx="18" className="canvas-bg" />
      <path className="map-road map-road--one" d="M-20 275C93 227 128 302 222 253s155-159 398-125" />
      <path className="map-road map-road--two" d="M60-20c33 99 80 124 128 160s61 122 85 240M413-20c-32 100-10 201 126 400" />
      {path && <polyline className="amazon-route" points={path} />}
      {(graph?.nodos || []).map((node) => {
        const point = projection.get(node.id)
        const current = step?.actual === node.id
        const className = [
          'amazon-node',
          closed.has(node.id) && 'amazon-node--closed',
          frontier.has(node.id) && 'amazon-node--frontier',
          routeIds.includes(node.id) && 'amazon-node--route',
          current && 'amazon-node--current',
          start === node.id && 'amazon-node--start',
          goal === node.id && 'amazon-node--goal',
        ].filter(Boolean).join(' ')
        return <circle key={node.id} className={className} cx={point.x} cy={point.y} r={current ? 6 : 3.2}><title>{node.id}</title></circle>
      })}
    </svg>
  )
}

export default function GridCanvas(props) {
  if (props.environment === 'amazon') return <AmazonGraph {...props} />
  return <Grid {...props} />
}
