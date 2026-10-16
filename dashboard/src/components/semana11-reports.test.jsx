import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import MarkdownViewer from './MarkdownViewer.jsx'
import { api } from '../services/api.js'

afterEach(() => { cleanup(); vi.restoreAllMocks() })

const semana11 = {
  id: 'semana11', numero: 11,
  informes: [
    { id: 'semana11', titulo: 'Resultados y límites de Semana 11' },
    { id: 'semana11-adr', titulo: 'ADR-011 · Modelo de riesgo' },
  ],
}

describe('informes de Semana 11', () => {
  it('expone el informe y el ADR como opciones visibles y permite alternarlos', async () => {
    vi.spyOn(api, 'informe').mockImplementation(async (id) => ({
      ruta: `reports/${id}.md`,
      contenido: `# ${id === 'semana11-adr' ? 'Decisión ADR-011' : 'Benchmark Semana 11'}`,
      encabezados: [], palabras: 3, hash: 'abc123',
    }))

    render(<MarkdownViewer week={semana11} />)
    expect(screen.getByRole('button', { name: /Informe de resultados/i })).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: /ADR-011/i }))
    expect(await screen.findByRole('heading', { name: 'Decisión ADR-011' })).toBeTruthy()
    expect(api.informe).toHaveBeenCalledWith('semana11-adr')
  })

  it('conserva el selector habitual en otras semanas', () => {
    render(<MarkdownViewer week={{ id: 'semana10', numero: 10, informes: [{ id: 'semana10', titulo: 'Semana 10' }] }} />)
    expect(screen.getByRole('combobox', { name: 'INFORME' })).toBeTruthy()
    expect(screen.queryByRole('button', { name: /ADR-011/i })).toBeNull()
  })
})
