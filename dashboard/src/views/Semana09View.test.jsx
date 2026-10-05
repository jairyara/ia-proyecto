import { afterEach, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import Semana09View from './Semana09View.jsx'
import { api } from '../services/api.js'

afterEach(() => { cleanup(); vi.restoreAllMocks() })

it('compara las mediciones Canny sin presentar una reclasificación', async () => {
  vi.spyOn(api, 'resultadosVision09').mockResolvedValue({
    otsu_umbral_0_255: 105, regiones_conectadas: 2, mascara_porcentaje: 23.13,
    ancho_px: 960, alto_px: 540, origen: 'escena sintética', sha256_imagen: 'a'.repeat(64),
    intensidad_media_0_255: 71.35, intensidad_desviacion_0_255: 56.16,
    mascara_pixeles: 119925, conectividad: 8,
    regiones_mayores: [{ etiqueta: 1, area_px: 98085 }, { etiqueta: 2, area_px: 21840 }],
    color_medio_rgb: [74, 71, 66],
    canny: [
      { sigma: 1, pixeles_borde: 10694, densidad_porcentaje: 2.06 },
      { sigma: 4, pixeles_borde: 3027, densidad_porcentaje: 0.58 },
    ],
  })
  render(<Semana09View />)
  await waitFor(() => expect(screen.getByText('10.694')).toBeTruthy())
  fireEvent.click(screen.getByRole('button', { name: 'σ = 4' }))
  expect(screen.getByText('3.027')).toBeTruthy()
  expect(screen.getByRole('button', { name: 'σ = 4' }).getAttribute('aria-pressed')).toBe('true')
  expect(screen.getByText(/no se recalcula la imagen/i)).toBeTruthy()
  expect(screen.getByText(/Otsu trabaja con la imagen gris original/i)).toBeTruthy()
  expect(screen.getByText(/Regiones de píxeles ≠ paquetes/i)).toBeTruthy()
})
