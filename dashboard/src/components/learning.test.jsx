import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { CodeDocument } from './CodeExplorer.jsx'
import { MarkdownRenderer, slugify } from './MarkdownViewer.jsx'
import { buildEditorUri } from '../services/editor.js'

afterEach(cleanup)

const source = {
  titulo: 'Ejemplo A*',
  ruta: 'src/busqueda/a_estrella.py',
  workspace_editor: '/Users/estudiante/ia proyecto',
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

  it('abre la línea seleccionada en el IDE elegido', () => {
    render(
      <CodeDocument document={source} selectedLine={2} onSelect={vi.fn()} playing={false} onPlay={vi.fn()} onMove={vi.fn()} onOutline={vi.fn()} />,
    )

    const link = screen.getByRole('link', { name: /línea 2.*PyCharm/i })
    expect(link.getAttribute('href')).toBe(
      'pycharm://open?file=%2FUsers%2Festudiante%2Fia+proyecto%2Fsrc%2Fbusqueda%2Fa_estrella.py&line=2&column=1',
    )
  })
})

describe('buildEditorUri', () => {
  it('construye un deep link de VS Code con archivo y línea', () => {
    expect(buildEditorUri({
      editor: 'vscode',
      workspaceRoot: '/Users/estudiante/ia proyecto',
      relativePath: 'src/modelado/riesgo_retraso.py',
      line: 94,
    })).toBe('vscode://file/Users/estudiante/ia%20proyecto/src/modelado/riesgo_retraso.py:94:1')
  })

  it('rechaza rutas que intenten salir del repositorio', () => {
    expect(() => buildEditorUri({
      editor: 'pycharm',
      workspaceRoot: '/Users/estudiante/proyecto',
      relativePath: '../secreto.py',
      line: 1,
    })).toThrow('no es segura')
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
