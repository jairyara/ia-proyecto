import { useEffect, useState } from 'react'
import Navbar from './components/Navbar.jsx'
import WeekWorkspace from './components/WeekWorkspace.jsx'
import Semana02View from './views/Semana02View.jsx'
import Semana03View from './views/Semana03View.jsx'
import Semana04View from './views/Semana04View.jsx'
import Semana05View from './views/Semana05View.jsx'
import Semana07View from './views/Semana07View.jsx'
import ResumenView from './views/ResumenView.jsx'
import ParadasView from './views/ParadasView.jsx'
import VisualView from './views/VisualView.jsx'
import MlpView from './views/MlpView.jsx'
import { api } from './services/api.js'

const SIDEBAR_STORAGE_KEY = 'orbita.sidebarCollapsed'

const views = {
  resumen: ResumenView,
  paradas: ParadasView,
  visual: VisualView,
  mlp: MlpView,
  semana02: Semana02View,
  semana03: Semana03View,
  semana04: Semana04View,
  semana05: Semana05View,
  semana07: Semana07View,
}

export default function App() {
  const [active, setActive] = useState('resumen')
  const [selectedImageId, setSelectedImageId] = useState(null)
  const [apiOnline, setApiOnline] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    try {
      return window.localStorage.getItem(SIDEBAR_STORAGE_KEY) === 'true'
    } catch {
      return false
    }
  })
  const View = views[active]

  useEffect(() => {
    api.health().then(() => setApiOnline(true)).catch(() => setApiOnline(false))
  }, [])

  useEffect(() => {
    try {
      window.localStorage.setItem(SIDEBAR_STORAGE_KEY, String(sidebarCollapsed))
    } catch {
      // La navegación sigue funcionando aunque el navegador bloquee el almacenamiento.
    }
  }, [sidebarCollapsed])

  return (
    <div className={`app-shell ${sidebarCollapsed ? 'app-shell--sidebar-collapsed' : ''}`}>
      <Navbar
        active={active}
        onChange={setActive}
        apiOnline={apiOnline}
        mobileOpen={mobileOpen}
        onToggle={(value) => setMobileOpen((current) => typeof value === 'boolean' ? value : !current)}
        collapsed={sidebarCollapsed}
      />
      <main id="main" className="main-content">
        {active.startsWith('semana') ? (
          <WeekWorkspace key={active} weekId={active} sidebarCollapsed={sidebarCollapsed}
            onSidebarCollapse={() => setSidebarCollapsed((current) => !current)}><View /></WeekWorkspace>
        ) : (
          <><div className="workspace-bar"><button type="button" className="content-sidebar-toggle"
            onClick={() => setSidebarCollapsed((current) => !current)}
            aria-label={sidebarCollapsed ? 'Expandir menú lateral' : 'Contraer menú lateral'}>
            ☰</button><span className="workspace-context">ÓRBITA · DATOS Y PROYECTO</span></div>
            <View initialImageId={selectedImageId} onNavigate={(target, imageId = null) => {
              setSelectedImageId(imageId)
              setActive(target)
            }} /></>
        )}
      </main>
    </div>
  )
}
