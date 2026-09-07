import Icon from './Icon.jsx'

const sections = [
  { id: 'semana02', week: '02', title: 'Riesgo de retraso', subtitle: 'Aprendizaje supervisado', icon: 'brain' },
  { id: 'semana03', week: '03', title: 'Reglas simbólicas', subtitle: 'Clasificación explicable', icon: 'rules' },
  { id: 'semana04', week: '04', title: 'Búsqueda heurística', subtitle: 'A* · Dijkstra · BFS', icon: 'route' },
  { id: 'semana05', week: '05', title: 'Sistema híbrido', subtitle: 'Reglas · TF-IDF · LogReg', icon: 'spark' },
].sort((left, right) => Number(left.week) - Number(right.week))

export default function Navbar({ active, onChange, apiOnline, mobileOpen, onToggle, collapsed, onCollapse }) {
  const collapseLabel = collapsed ? 'Expandir menú lateral' : 'Contraer menú lateral'

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
        <button
          type="button"
          className="sidebar-toggle"
          onClick={onCollapse}
          aria-label={collapseLabel}
          aria-controls="sidebar-navigation"
          aria-expanded={!collapsed}
          title={collapseLabel}
        >
          <Icon name={collapsed ? 'chevronRight' : 'chevronLeft'} size={16} />
        </button>
        <div>
          <a className="brand" href="#main" aria-label="Órbita, laboratorio de IA logística">
            <span className="brand-mark"><span /></span>
            <span className="brand-copy">
              <strong>ÓRBITA</strong>
              <small>IA LOGÍSTICA</small>
            </span>
          </a>
          <p className="nav-label">LABORATORIOS ACTIVOS</p>
          <nav className="nav-list" aria-label="Laboratorios por semana">
            {sections.map((section) => (
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
          <p>Proyecto 8 · Corte 1</p>
          <p>Jair Yara · Catherinne Gutierrez</p>
        </div>
      </aside>
      {mobileOpen && <button className="nav-backdrop" aria-label="Cerrar menú" onClick={() => onToggle(false)} />}
    </>
  )
}
