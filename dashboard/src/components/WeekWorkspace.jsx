import { lazy, Suspense, useEffect, useState } from 'react'
import Icon from './Icon.jsx'
import { api } from '../services/api.js'

const CodeExplorer = lazy(() => import('./CodeExplorer.jsx'))
const MarkdownViewer = lazy(() => import('./MarkdownViewer.jsx'))

const tabs = [
  { id: 'laboratorio', label: 'Laboratorio', icon: 'lab' },
  { id: 'codigo', label: 'Código explicado', icon: 'code' },
  { id: 'informe', label: 'Informe', icon: 'document' },
]

export default function WeekWorkspace({ weekId, children }) {
  const [activeTab, setActiveTab] = useState('laboratorio')
  const [week, setWeek] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let current = true
    api.contenidoSemanas()
      .then(({ semanas }) => {
        if (current) setWeek(semanas.find((item) => item.id === weekId) || null)
      })
      .catch((requestError) => {
        if (current) setError(requestError.message)
      })
    return () => { current = false }
  }, [weekId])

  return (
    <>
      <div className="workspace-bar">
        <nav className="workspace-tabs" aria-label="Vistas de la semana">
          {tabs.map((tab) => {
            const count = tab.id === 'codigo'
              ? week?.ejercicios.reduce((total, exercise) => total + exercise.archivos.length, 0)
              : tab.id === 'informe' ? week?.informes.length : null
            return (
              <button
                className={activeTab === tab.id ? 'active' : ''}
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                aria-current={activeTab === tab.id ? 'page' : undefined}
              >
                <Icon name={tab.icon} size={16} />
                <span>{tab.label}</span>
                {Number.isFinite(count) && <small>{count}</small>}
              </button>
            )
          })}
        </nav>
        <span className="workspace-context">S{String(week?.numero || weekId.replace(/\D/g, '')).padStart(2, '0')}</span>
      </div>

      {activeTab === 'laboratorio' && children}
      {activeTab !== 'laboratorio' && error && (
        <div className="view-shell learning-view"><div className="alert alert--error"><Icon name="alert" />{error}</div></div>
      )}
      {activeTab === 'codigo' && !error && (
        week
          ? <Suspense fallback={<LoadingView message="Preparando el explorador…" />}><CodeExplorer week={week} /></Suspense>
          : <LoadingView message="Cargando catálogo de código…" />
      )}
      {activeTab === 'informe' && !error && (
        week
          ? <Suspense fallback={<LoadingView message="Preparando el visualizador…" />}><MarkdownViewer week={week} /></Suspense>
          : <LoadingView message="Cargando informes…" />
      )}
    </>
  )
}

function LoadingView({ message }) {
  return (
    <div className="view-shell learning-view">
      <div className="learning-loading"><span className="spinner" />{message}</div>
    </div>
  )
}
