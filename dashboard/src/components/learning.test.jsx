import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { readFileSync } from 'node:fs'
import { CodeDocument } from './CodeExplorer.jsx'
import GridCanvas from './GridCanvas.jsx'
import { MarkdownRenderer, slugify } from './MarkdownViewer.jsx'
import Navbar from './Navbar.jsx'
import { buildEditorUri } from '../services/editor.js'

const dashboardStyles = readFileSync('src/index.css', 'utf8')

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

  it('abre la línea seleccionada en el IDE elegido (VS Code por defecto)', () => {
    render(
      <CodeDocument document={source} selectedLine={2} onSelect={vi.fn()} playing={false} onPlay={vi.fn()} onMove={vi.fn()} onOutline={vi.fn()} />,
    )

    const links = screen.getAllByRole('link', { name: /línea 2.*VS Code/i })
    expect(links.length).toBeGreaterThan(0)
    expect(links[0].getAttribute('href')).toBe(
      'vscode://file/Users/estudiante/ia%20proyecto/src/busqueda/a_estrella.py:2:1',
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

describe('Navbar', () => {
  it('permite contraer y expandir el menú lateral con una etiqueta accesible', () => {
    const onCollapse = vi.fn()
    const props = {
      active: 'semana02',
      onChange: vi.fn(),
      apiOnline: true,
      mobileOpen: false,
      onToggle: vi.fn(),
      onCollapse,
    }
    const { rerender } = render(<Navbar {...props} collapsed={false} />)

    fireEvent.click(screen.getByRole('button', { name: 'Contraer menú lateral' }))
    expect(onCollapse).toHaveBeenCalledOnce()

    rerender(<Navbar {...props} collapsed />)
    expect(screen.getByRole('button', { name: 'Expandir menú lateral' }).getAttribute('aria-expanded')).toBe('false')
    expect(screen.getByRole('button', { name: 'Semana 2: Riesgo de retraso' }).getAttribute('title')).toContain('Riesgo de retraso')
    expect(screen.getByRole('complementary', { name: 'Navegación principal' }).classList.contains('sidebar--collapsed')).toBe(true)
  })
})

describe('GridCanvas', () => {
  it('no representa una celda bloqueada como parte de la ruta', () => {
    render(
      <GridCanvas
        environment="cuadricula"
        graph={null}
        step={{ ruta_parcial: ['(0,0)', '(1,0)'], frontera: [], cerrados: [] }}
        start="(0,0)"
        goal="(4,4)"
        obstacles={[[1, 0]]}
        onToggle={vi.fn()}
      />,
    )

    const blockedCell = screen.getByRole('button', { name: 'Celda 1, 0, bloqueada' })
    expect(blockedCell.classList.contains('cell--blocked')).toBe(true)
    expect(blockedCell.classList.contains('cell--route')).toBe(false)
  })
})

describe('legibilidad de presentación', () => {
  it('no usa tipografías explícitas menores de 11 px', () => {
    expect(dashboardStyles).not.toMatch(/font-size:\s*(?:[1-9]|10)px\b/)
    expect(dashboardStyles).not.toMatch(/font:\s*[^;]*(?<!\d)(?:[1-9]|10)px\b/)
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
