import { useState } from 'react'
import Icon from './Icon.jsx'

const corteOneSections = [
  { id: 'semana02', week: '02', title: 'Riesgo de retraso', subtitle: 'Aprendizaje supervisado', icon: 'brain' },
  { id: 'semana03', week: '03', title: 'Reglas simbólicas', subtitle: 'Clasificación explicable', icon: 'rules' },
  { id: 'semana04', week: '04', title: 'Búsqueda heurística', subtitle: 'A* · Dijkstra · BFS', icon: 'route' },
  { id: 'semana05', week: '05', title: 'Sistema híbrido', subtitle: 'Reglas · TF-IDF · LogReg', icon: 'spark' },
].sort((left, right) => Number(left.week) - Number(right.week))

const cuts = [
  { id: 'corte1', number: 1, sections: corteOneSections },
  { id: 'corte2', number: 2, sections: [] },
  { id: 'corte3', number: 3, sections: [] },
]

export default function Navbar({ active, onChange, apiOnline, mobileOpen, onToggle, collapsed }) {
  const activeCut = cuts.find((cut) => cut.sections.some((section) => section.id === active))?.id ?? 'corte1'
  const [openCut, setOpenCut] = useState(activeCut)

  const toggleCut = (cutId) => {
    setOpenCut((current) => current === cutId ? null : cutId)
  }

  return (
    <>
      <header className="mobile-header">
        <a className="brand brand--mobile" href="#main" aria-label="Ir al contenido principal">
          <span className="brand-mark"><span /></span>
          <span>ÓRBITA</span>
        </a>
        <button className="icon-button" onClick={onToggle} aria-label={mobileOpen ? 'Cerrar menú' : 'Abrir menú'}>
          <Icon name={mobileOpen ? 'close' : 'menu'} />
        </button>
      </header>
      <aside
        id="sidebar-navigation"
        className={`sidebar ${collapsed ? 'sidebar--collapsed' : ''} ${mobileOpen ? 'sidebar--open' : ''}`}
        aria-label="Navegación principal"
      >
        <div>
          <a className="brand" href="#main" aria-label="Órbita, laboratorio de IA logística">
            <span className="brand-mark"><span /></span>
            <span className="brand-copy">
              <strong>ÓRBITA</strong>
              <small>IA LOGÍSTICA</small>
            </span>
          </a>
          <p className="nav-label">PLAN ACADÉMICO</p>
          <nav className="nav-groups" aria-label="Cortes y temas del proyecto">
            {cuts.map((cut) => {
              const isOpen = openCut === cut.id
              const topicCount = cut.sections.length

              return (
                <section className={`nav-group ${isOpen ? 'nav-group--open' : ''}`} key={cut.id}>
                  <button
                    className="nav-group-toggle"
                    type="button"
                    onClick={() => toggleCut(cut.id)}
                    aria-label={`Corte ${cut.number}`}
                    aria-expanded={isOpen}
                    aria-controls={`${cut.id}-topics`}
                    title={collapsed ? `Corte ${cut.number}` : undefined}
                  >
                    <span className="nav-cut-icon">
                      <Icon name="calendar" size={18} />
                      <small>{cut.number}</small>
                    </span>
                    <span className="nav-group-copy">
                      <strong>Corte {cut.number}</strong>
                      <small>{topicCount ? `${topicCount} temas` : 'Sin temas aún'}</small>
                    </span>
                    <Icon name="chevronRight" className="nav-group-chevron" size={16} />
                  </button>

                  <div className="nav-group-content" id={`${cut.id}-topics`} hidden={!isOpen}>
                    {topicCount > 0 ? (
                      <div className="nav-list" role="group" aria-label={`Temas del Corte ${cut.number}`}>
                        {cut.sections.map((section) => (
                          <button
                            className={`nav-item ${active === section.id ? 'nav-item--active' : ''}`}
                            key={section.id}
                            onClick={() => { onChange(section.id); onToggle(false) }}
                            aria-current={active === section.id ? 'page' : undefined}
                            aria-label={`Semana ${Number(section.week)}: ${section.title}`}
                            title={collapsed ? `Semana ${Number(section.week)} · ${section.title}` : undefined}
                          >
                            <span className="nav-icon"><Icon name={section.icon} /></span>
                            <span className="nav-copy">
                              <strong>{section.title}</strong>
                              <small>{section.subtitle}</small>
                            </span>
                            <span className="nav-week">S{section.week}</span>
                          </button>
                        ))}
                      </div>
                    ) : (
                      <p className="nav-empty">Los temas aparecerán aquí.</p>
                    )}
                  </div>
                </section>
              )
            })}
          </nav>
        </div>
        <div className="sidebar-footer">
          <div className="api-state">
            <span className={`status-dot ${apiOnline ? 'status-dot--online' : ''}`} />
            <span className="api-copy">
              <strong>{apiOnline ? 'API conectada' : 'API sin conexión'}</strong>
              <small>FastAPI · Python</small>
            </span>
          </div>
          <p>Proyecto 8 · Cortes 1–3</p>
          <p>Jair Yara · Catherinne Gutierrez</p>
        </div>
      </aside>
      {mobileOpen && <button className="nav-backdrop" aria-label="Cerrar menú" onClick={() => onToggle(false)} />}
    </>
  )
}
