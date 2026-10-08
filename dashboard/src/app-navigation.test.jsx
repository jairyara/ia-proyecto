import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import App from './App.jsx'
import { api } from './services/api.js'

vi.mock('./views/Semana02View.jsx', () => ({ default: () => <div>Laboratorio de riesgo</div> }))
vi.mock('./views/ResumenView.jsx', () => ({ default: () => <div>Resumen nuevo</div> }))

afterEach(() => { cleanup(); vi.restoreAllMocks() })

describe('navegación existente', () => {
  it('abre Semana 9 desde el Corte 2 y conserva las tres pestañas', () => {
    vi.spyOn(api, 'health').mockResolvedValue({ estado: 'ok' })
    vi.spyOn(api, 'contenidoSemanas').mockResolvedValue({ semanas: [] })
    vi.spyOn(api, 'resultadosVision09').mockResolvedValue({
      otsu_umbral_0_255: 105, regiones_conectadas: 2, mascara_porcentaje: 23.13,
      ancho_px: 960, alto_px: 540, origen: 'escena sintética', sha256_imagen: 'a'.repeat(64),
      intensidad_media_0_255: 71.35, color_medio_rgb: [74, 71, 66], canny: [],
    })
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: 'Corte 2' }))
    fireEvent.click(screen.getByRole('button', { name: /Semana 9: Visión de paquetes/i }))
    expect(screen.getByText(/Del píxel a la/i)).toBeTruthy()
    expect(screen.getByRole('button', { name: /código explicado/i })).toBeTruthy()
    expect(screen.getByRole('button', { name: /^informe/i })).toBeTruthy()
  })
  it('abre el laboratorio anterior con sus pestañas de demostración, código e informe', () => {
    vi.spyOn(api, 'health').mockResolvedValue({ estado: 'ok' })
    vi.spyOn(api, 'contenidoSemanas').mockResolvedValue({ semanas: [] })
    render(<App />)
    expect(screen.getByText('Laboratorio de riesgo')).toBeTruthy()
    expect(screen.getByRole('button', { name: /laboratorio/i })).toBeTruthy()
    expect(screen.getByRole('button', { name: /código explicado/i })).toBeTruthy()
    expect(screen.getByRole('button', { name: /^informe/i })).toBeTruthy()
  })

  it('abre Semana 10 desde el Corte 2 con el espacio didáctico completo', () => {
    vi.spyOn(api, 'health').mockResolvedValue({ estado: 'ok' })
    vi.spyOn(api, 'contenidoSemanas').mockResolvedValue({ semanas: [] })
    vi.spyOn(api, 'resultadosVision10').mockResolvedValue({
      entrenamiento: 150, prueba_reservada_sin_descriptores: 50,
      vector: { dimension: 53 }, origen: 'piloto sintético',
      manifiesto_sha256: 'a'.repeat(64), dimensiones_analisis: [480, 270],
      conectividad: 8, filtro_area_px: 50, ejemplos: [], resumen_clases: {},
      advertencia: 'Sin decisión operativa.',
    })
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: 'Corte 2' }))
    fireEvent.click(screen.getByRole('button', { name: /Semana 10: Textura de paquetes/i }))
    expect(screen.getByText(/Del paquete a un/i)).toBeTruthy()
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
