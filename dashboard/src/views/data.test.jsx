import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import MlpView from './MlpView.jsx'
import ResumenView from './ResumenView.jsx'
import { api } from '../services/api.js'

const resumen = {
  amazon: { paradas: 14411, rutas: 100, estaciones: 17 },
  visual: { imagenes: 200, grupos: 200, clases: { intacto: 100, danado: 100 }, asociaciones: 200 },
  modelo_visual: null,
}

afterEach(() => { cleanup(); vi.restoreAllMocks() })

describe('datos y MLP visual', () => {
  it('muestra conteos consultados y no afirma que haya modelo', async () => {
    vi.spyOn(api, 'resumenDatos').mockResolvedValue(resumen)
    render(<ResumenView onNavigate={vi.fn()} />)
    await waitFor(() => expect(screen.getByText('14.411')).toBeTruthy())
    expect(screen.getByText('Aún no entrenado')).toBeTruthy()
  })

  it('mantiene evaluación y predicción vacías mientras no haya modelo', async () => {
    vi.spyOn(api, 'resumenDatos').mockResolvedValue(resumen)
    render(<MlpView onNavigate={vi.fn()} />)
    await waitFor(() => expect(screen.getByText('Sin predicción disponible')).toBeTruthy())
    expect(screen.getByText(/No existen particiones, métricas/)).toBeTruthy()
  })
})
