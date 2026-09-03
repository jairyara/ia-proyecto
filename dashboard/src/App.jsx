import { useEffect, useState } from 'react'
import Navbar from './components/Navbar.jsx'
import WeekWorkspace from './components/WeekWorkspace.jsx'
import Semana02View from './views/Semana02View.jsx'
import Semana03View from './views/Semana03View.jsx'
import Semana04View from './views/Semana04View.jsx'
import Semana05View from './views/Semana05View.jsx'
import { api } from './services/api.js'

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
  const View = views[active]

  useEffect(() => {
    api.health().then(() => setApiOnline(true)).catch(() => setApiOnline(false))
  }, [])

  return (
    <div className="app-shell">
      <Navbar
        active={active}
        onChange={setActive}
        apiOnline={apiOnline}
        mobileOpen={mobileOpen}
        onToggle={(value) => setMobileOpen((current) => typeof value === 'boolean' ? value : !current)}
      />
      <main id="main" className="main-content">
        <WeekWorkspace key={active} weekId={active}>
          <View />
        </WeekWorkspace>
      </main>
    </div>
  )
}
