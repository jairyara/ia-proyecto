export default function CodeExplainer({ code = [], step, fileName = 'a_estrella.py' }) {
  const active = step?.linea_activa || 'init'
  const explanation = code.find((line) => line.id === active)

  return (
    <section className="panel code-panel" aria-labelledby="code-title">
      <div className="panel-heading panel-heading--dark">
        <div>
          <span className="eyebrow eyebrow--mint">TRAZA DE EJECUCIÓN</span>
          <h2 id="code-title">Dentro del algoritmo</h2>
        </div>
        <span className="file-pill"><i /> {fileName}</span>
      </div>
      <div className="code-window" role="region" aria-live="polite" aria-label="Código con línea activa">
        {code.map((line) => (
          <div className={`code-line ${line.id === active ? 'code-line--active' : ''}`} key={line.id}>
            <span className="line-number">{line.linea}</span>
            <code>{line.codigo}</code>
          </div>
        ))}
      </div>
      <div className="code-explanation">
        <span className="explanation-index">{explanation?.linea || 1}</span>
        <div>
          <strong>{step?.mensaje || explanation?.explicacion}</strong>
          <p>{explanation?.explicacion}</p>
        </div>
      </div>
      <div className="variable-strip">
        <div><span>ACTUAL</span><strong>{step?.actual || '—'}</strong></div>
        <div><span>g(n)</span><strong>{step?.g ?? '—'}</strong></div>
        <div><span>h(n)</span><strong>{step?.h ?? '—'}</strong></div>
        <div><span>f(n)</span><strong>{step?.f ?? '—'}</strong></div>
      </div>
    </section>
  )
}
