function formatCost(value, environment) {
  if (value === null || value === undefined) return 'Sin ruta'
  if (environment === 'amazon') return `${Number(value).toFixed(1)} s`
  return Number(value).toFixed(1)
}

export default function MetricsCard({ simulation, step }) {
  const result = simulation?.resultado
  const astar = simulation?.comparacion?.a_estrella
  const dijkstra = simulation?.comparacion?.dijkstra
  const saving = astar && dijkstra && dijkstra.nodos_expandidos
    ? Math.max(0, ((dijkstra.nodos_expandidos - astar.nodos_expandidos) / dijkstra.nodos_expandidos) * 100)
    : 0
  const metrics = [
    { label: 'Costo de ruta', value: formatCost(result?.costo_total, simulation?.entorno), hint: 'g(meta)', tone: 'mint' },
    { label: 'Nodos expandidos', value: step?.cerrados?.length ?? 0, hint: `de ${result?.nodos_expandidos || 0}`, tone: 'blue' },
    { label: 'En frontera', value: step?.frontera?.length ?? 0, hint: 'candidatos visibles', tone: 'amber' },
    { label: 'Ahorro vs Dijkstra', value: `${saving.toFixed(0)}%`, hint: `${astar?.nodos_expandidos || 0} vs ${dijkstra?.nodos_expandidos || 0}`, tone: 'violet' },
  ]
  return (
    <div className="metrics-grid">
      {metrics.map((metric) => (
        <article className="metric-card" key={metric.label}>
          <span className={`metric-accent metric-accent--${metric.tone}`} />
          <span>{metric.label}</span>
          <strong>{metric.value}</strong>
          <small>{metric.hint}</small>
        </article>
      ))}
    </div>
  )
}
