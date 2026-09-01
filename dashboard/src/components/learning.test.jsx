import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { CodeDocument } from './CodeExplorer.jsx'
import { MarkdownRenderer, slugify } from './MarkdownViewer.jsx'

afterEach(cleanup)

const source = {
  titulo: 'Ejemplo A*',
  ruta: 'src/busqueda/a_estrella.py',
  hash: 'abc123',
  total_lineas: 2,
  outline: [{ nombre: 'a_estrella', tipo: 'función', linea: 1, fin: 2, descripcion: 'Busca la ruta.' }],
  lineas: [
    { numero: 1, codigo: 'def a_estrella():', tipo: 'función', explicacion: 'Declara la búsqueda.', bloque: 'a_estrella', resumen_bloque: 'Busca la ruta.' },
    { numero: 2, codigo: '    return ruta', tipo: 'retorno', explicacion: 'Entrega la ruta óptima.', bloque: 'a_estrella', resumen_bloque: 'Busca la ruta.' },
  ],
}

describe('CodeDocument', () => {
  it('permite seleccionar una línea y muestra su explicación', () => {
    const onSelect = vi.fn()
    const { rerender } = render(
      <CodeDocument document={source} selectedLine={1} onSelect={onSelect} playing={false} onPlay={vi.fn()} onMove={vi.fn()} onOutline={vi.fn()} />,
    )

    fireEvent.click(screen.getByText('return ruta'))
    expect(onSelect).toHaveBeenCalledWith(2)

    rerender(<CodeDocument document={source} selectedLine={2} onSelect={onSelect} playing={false} onPlay={vi.fn()} onMove={vi.fn()} onOutline={vi.fn()} />)
    expect(screen.getByText('Entrega la ruta óptima.')).toBeTruthy()
    expect(screen.getByText('LÍNEA 2')).toBeTruthy()
  })
})

describe('MarkdownRenderer', () => {
  it('renderiza encabezados, tablas GFM y fórmulas KaTeX', () => {
    const { container } = render(<MarkdownRenderer content={'# Métricas de búsqueda\n\n| Modelo | F1 |\n|---|---:|\n| A* | 0.91 |\n\n$f(n)=g(n)+h(n)$'} />)

    expect(container.querySelector('#metricas-de-busqueda')).toBeTruthy()
    expect(container.querySelector('table')).toBeTruthy()
    expect(container.querySelector('.katex')).toBeTruthy()
    expect(slugify('Clasificación simbólica')).toBe('clasificacion-simbolica')
  })
})
