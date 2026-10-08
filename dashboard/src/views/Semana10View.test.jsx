import { afterEach, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import Semana10View from './Semana10View.jsx'
import { api } from '../services/api.js'

afterEach(() => { cleanup(); vi.restoreAllMocks() })

it('muestra evidencia sin convertir descriptores en un diagnóstico', async () => {
  vi.spyOn(api, 'resultadosVision10').mockResolvedValue({
    origen: 'piloto sintético', manifiesto_sha256: 'a'.repeat(64),
    entrenamiento: 150, prueba_reservada_sin_descriptores: 50,
    vector: { dimension: 53 }, dimensiones_analisis: [480, 270],
    conectividad: 8, filtro_area_px: 50,
    resumen_clases: {
      danado: { n: 75, regiones_validas_mediana: 33 },
      intacto: { n: 75, regiones_validas_mediana: 34 },
    },
    ejemplos: [
      { id_origen: 'uno', etiqueta: 'danado', regiones_validas: 32, umbral_otsu_0_255: 131,
        mascara_porcentaje: 40, area_media_porcentaje: 1.5, area_desviacion_porcentaje: 2,
        histograma_intensidad: Array(32).fill(1 / 32), histograma_lbp: Array(18).fill(1 / 18) },
      { id_origen: 'dos', etiqueta: 'intacto', regiones_validas: 34, umbral_otsu_0_255: 130,
        mascara_porcentaje: 42, area_media_porcentaje: 1.4, area_desviacion_porcentaje: 2,
        histograma_intensidad: Array(32).fill(1 / 32), histograma_lbp: Array(18).fill(1 / 18) },
    ],
    advertencia: 'No valida clasificación ni despacho.',
  })
  render(<Semana10View />)
  await waitFor(() => expect(screen.getByText(/Dos ejemplos, no una validación/i)).toBeTruthy())
  expect(screen.getByText(/ningún descriptor predijo la clase/i)).toBeTruthy()
  expect(screen.getByText(/Una región conectada no es un paquete físico/i)).toBeTruthy()
  expect(screen.getByText(/reservadas, sin descriptores/i)).toBeTruthy()
  await waitFor(() => expect(screen.getByText(/Dos firmas visuales, lado a lado/i)).toBeTruthy())
  expect(screen.getByText(/Ver imagen, máscara y figura reproducible/i)).toBeTruthy()
  expect(screen.getByAltText(/Vista lateral gris del ejemplo danado/i)).toBeTruthy()
  expect(screen.getByAltText(/Vista lateral gris del ejemplo intacto/i)).toBeTruthy()
  fireEvent.click(screen.getByRole('button', { name: 'Dañado' }))
  expect(screen.getByRole('button', { name: 'Dañado' }).getAttribute('aria-pressed')).toBe('true')
  expect(screen.queryByAltText(/Vista lateral gris del ejemplo intacto/i)).toBeNull()
  expect(screen.getByAltText(/Máscara Otsu del ejemplo danado/i)).toBeTruthy()
  fireEvent.click(screen.getByRole('button', { name: 'Intacto' }))
  expect(screen.queryByAltText(/Vista lateral gris del ejemplo danado/i)).toBeNull()
  expect(screen.getByAltText(/Vista lateral gris del ejemplo intacto/i)).toBeTruthy()
  fireEvent.click(screen.getByRole('button', { name: 'Ambos' }))
  expect(screen.getByAltText(/Vista lateral gris del ejemplo danado/i)).toBeTruthy()
  expect(screen.getByAltText(/Vista lateral gris del ejemplo intacto/i)).toBeTruthy()
})
