import { useEffect, useState } from 'react'
import Navbar from './components/Navbar.jsx'
import WeekWorkspace from './components/WeekWorkspace.jsx'
import Semana02View from './views/Semana02View.jsx'
import Semana03View from './views/Semana03View.jsx'
import Semana04View from './views/Semana04View.jsx'
import Semana05View from './views/Semana05View.jsx'
import { api } from './services/api.js'

const SIDEBAR_STORAGE_KEY = 'orbita.sidebarCollapsed'

const views = {
  semana02: Semana02View,
  semana03: Semana03View,
  semana04: Semana04View,
  semana05: Semana05View,
}

export default function App() {
  const [active, setActive] = useState('semana02')
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
        <WeekWorkspace
          key={active}
          weekId={active}
          sidebarCollapsed={sidebarCollapsed}
          onSidebarCollapse={() => setSidebarCollapsed((current) => !current)}
        >
          <View />
        </WeekWorkspace>
      </main>
    </div>
  )
}
