import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import App from './App.jsx'
import { api } from './services/api.js'

vi.mock('./views/Semana02View.jsx', () => ({ default: () => <div>Laboratorio de riesgo</div> }))
vi.mock('./views/ResumenView.jsx', () => ({ default: () => <div>Resumen nuevo</div> }))

afterEach(() => { cleanup(); vi.restoreAllMocks() })

describe('navegación existente', () => {
  it('abre el laboratorio anterior con sus pestañas de demostración, código e informe', () => {
    vi.spyOn(api, 'health').mockResolvedValue({ estado: 'ok' })
    vi.spyOn(api, 'contenidoSemanas').mockResolvedValue({ semanas: [] })
    render(<App />)
    expect(screen.getByText('Laboratorio de riesgo')).toBeTruthy()
    expect(screen.getByRole('button', { name: /laboratorio/i })).toBeTruthy()
    expect(screen.getByRole('button', { name: /código explicado/i })).toBeTruthy()
    expect(screen.getByRole('button', { name: /^informe/i })).toBeTruthy()
  })

  it('mantiene el icono y la acción original para contraer el aside en las vistas nuevas', () => {
    vi.spyOn(api, 'health').mockResolvedValue({ estado: 'ok' })
    vi.spyOn(api, 'contenidoSemanas').mockResolvedValue({ semanas: [] })
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: /resumen del proyecto/i }))
    const toggle = screen.getByRole('button', { name: 'Contraer menú lateral' })
    expect(toggle.querySelector('svg')).toBeTruthy()
    fireEvent.click(toggle)
    expect(screen.getByRole('button', { name: 'Expandir menú lateral' })).toBeTruthy()
  })
})
