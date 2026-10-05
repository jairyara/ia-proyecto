import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import MlpView from './MlpView.jsx'
import ResumenView from './ResumenView.jsx'
import { api } from '../services/api.js'

const resumen = {
  amazon: { paradas: 14411, rutas: 100, estaciones: 17 },
  visual: { imagenes: 200, grupos: 200, clases: { intacto: 100, danado: 100 }, asociaciones: 200 },
}

afterEach(() => { cleanup(); vi.restoreAllMocks() })

describe('datos y MLP visual', () => {
  it('muestra conteos consultados y no afirma que haya modelo', async () => {
    vi.spyOn(api, 'resumenDatos').mockResolvedValue(resumen)
    vi.spyOn(api, 'resumenModeloVisual').mockResolvedValue({ estado: 'no_entrenado' })
    render(<ResumenView onNavigate={vi.fn()} />)
    await waitFor(() => expect(screen.getByText('14.411')).toBeTruthy())
    await waitFor(() => expect(screen.getByText('Aún no entrenado')).toBeTruthy())
  })

  it('el resumen reconoce el modelo y explica la partición 75/25', async () => {
    vi.spyOn(api, 'resumenDatos').mockResolvedValue(resumen)
    vi.spyOn(api, 'resumenModeloVisual').mockResolvedValue({
      estado: 'evaluado', version: 'mlp-visual-v1', total_train: 150, total_test: 50,
      accuracy: 0.48, accuracy_baseline: 0.5,
    })
    render(<ResumenView onNavigate={vi.fn()} />)
    await waitFor(() => expect(screen.getByText('MLP evaluado · mlp-visual-v1')).toBeTruthy())
    expect(screen.getByText(/150 imágenes \(75 %\)/)).toBeTruthy()
  })

  it('mantiene evaluación y predicción vacías mientras no haya modelo', async () => {
    vi.spyOn(api, 'resumenDatos').mockResolvedValue(resumen)
    vi.spyOn(api, 'resumenModeloVisual').mockResolvedValue({ estado: 'no_entrenado' })
    vi.spyOn(api, 'prediccionesModeloVisual').mockResolvedValue({ items: [], total: 0 })
    render(<MlpView onNavigate={vi.fn()} />)
    await waitFor(() => expect(screen.getByText('Sin predicción disponible')).toBeTruthy())
    expect(screen.getByText(/Modelo no registrado/)).toBeTruthy()
    expect(screen.getByText('Separación 75 % / 25 %')).toBeTruthy()
  })

  it('muestra métricas reales y advierte cuando MLP no supera la línea base', async () => {
    vi.spyOn(api, 'resumenDatos').mockResolvedValue(resumen)
    vi.spyOn(api, 'resumenModeloVisual').mockResolvedValue({
      estado: 'evaluado', version: 'mlp-visual-v1', total_train: 150, total_test: 50,
      accuracy: 0.48, accuracy_baseline: 0.5, matriz_confusion: [[13, 12], [14, 11]],
      por_clase: { danado: { 'f1-score': 0.5 }, intacto: { 'f1-score': 0.458 } },
      convergencia_advertida: true, aviso: 'Piloto sintético didáctico.',
    })
    vi.spyOn(api, 'prediccionesModeloVisual').mockResolvedValue({ items: [{
      imagen_id: 7, id_origen: 'PKG-007_side', etiqueta_real: 'danado',
      clase_predicha: 'intacto', probabilidad_predicha: 0.62,
      archivo_url: '/api/datos/imagenes/7/archivo',
    }, {
      imagen_id: 8, id_origen: 'PKG-008_side', etiqueta_real: 'intacto',
      clase_predicha: 'danado', probabilidad_predicha: 0.55,
      archivo_url: '/api/datos/imagenes/8/archivo',
    }], total: 50 })
    const ontologia = vi.spyOn(api, 'ontologiaModeloVisual').mockImplementation(async (id) => ({
      version: 'ontologia-logistica-v1', ejemplo_imagen_id: id,
      relaciones: [{ origen: `imagen:PKG-00${id}_side`, relacion: 'genera', destino: `prediccion:PKG-00${id}_side` }],
    }))
    render(<MlpView onNavigate={vi.fn()} />)
    await waitFor(() => expect(screen.getByText(/Accuracy MLP: 48.0 %/)).toBeTruthy())
    expect(screen.getByRole('heading', { name: 'De la imagen a la interpretación' })).toBeTruthy()
    expect(screen.getByText('RUTA DE ENTRENAMIENTO')).toBeTruthy()
    expect(screen.getByText('RUTA DE PRUEBA')).toBeTruthy()
    expect(screen.getByText(/no supera la línea base/)).toBeTruthy()
    expect(screen.getByText(/256 entradas/)).toBeTruthy()
    expect(screen.getByText(/accuracy = aciertos \/ total = 24 \/ 50/)).toBeTruthy()
    expect(screen.getByText((_, element) => element?.tagName === 'P' && element.textContent.includes('12 imágenes dañadas predichas intactas'))).toBeTruthy()
    expect(screen.getByAltText('Empaque sintético PKG-007_side')).toBeTruthy()
    expect(screen.getByText(/75 % · 150 imágenes/)).toBeTruthy()
    expect(screen.getByText(/25 % · 50 imágenes/)).toBeTruthy()
    await waitFor(() => expect(ontologia).toHaveBeenCalledWith(7))
    fireEvent.change(screen.getByLabelText('Imagen reservada para prueba'), { target: { value: '8' } })
    await waitFor(() => expect(ontologia).toHaveBeenCalledWith(8))
    expect(screen.getByAltText('Empaque sintético PKG-008_side')).toBeTruthy()
  })

  it('no confunde un error de consulta con un modelo no entrenado', async () => {
    vi.spyOn(api, 'resumenDatos').mockResolvedValue(resumen)
    vi.spyOn(api, 'resumenModeloVisual').mockRejectedValue(new Error('BD no disponible'))
    vi.spyOn(api, 'prediccionesModeloVisual').mockResolvedValue({ items: [] })
    render(<MlpView onNavigate={vi.fn()} />)
    await waitFor(() => expect(screen.getByRole('alert').textContent).toContain('BD no disponible'))
    expect(screen.queryByText(/Modelo no registrado/)).toBeNull()
  })
})
