import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { readFileSync } from 'node:fs'
import { CodeDocument } from './CodeExplorer.jsx'
import GridCanvas from './GridCanvas.jsx'
import { MarkdownRenderer, slugify } from './MarkdownViewer.jsx'
import Navbar from './Navbar.jsx'
import WeekWorkspace from './WeekWorkspace.jsx'
import { buildEditorUri } from '../services/editor.js'
import { api } from '../services/api.js'
import { ConfusionMatrix } from '../views/Semana02View.jsx'
import { LocalContributions } from '../views/Semana05View.jsx'

const dashboardStyles = readFileSync('src/index.css', 'utf8')

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
  vi.unstubAllGlobals()
})

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

  it('restablece el desplazamiento al cambiar de archivo', () => {
    const { container, rerender } = render(
      <CodeDocument document={source} selectedLine={2} onSelect={vi.fn()} playing={false} onPlay={vi.fn()} onMove={vi.fn()} onOutline={vi.fn()} />,
    )
    const sourceCode = container.querySelector('.source-code')
    sourceCode.scrollTop = 320
    sourceCode.scrollLeft = 180

    rerender(
      <CodeDocument
        document={{ ...source, hash: 'archivo-nuevo', ruta: 'src/busqueda/grafo.py' }}
        selectedLine={1}
        onSelect={vi.fn()}
        playing={false}
        onPlay={vi.fn()}
        onMove={vi.fn()}
        onOutline={vi.fn()}
      />,
    )

    const newSourceCode = container.querySelector('.source-code')
    expect(newSourceCode).not.toBe(sourceCode)
    expect(newSourceCode.scrollTop).toBe(0)
    expect(newSourceCode.scrollLeft).toBe(0)
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
  it('mantiene etiquetas accesibles cuando el menú está colapsado', () => {
    const props = {
      active: 'semana02',
      onChange: vi.fn(),
      apiOnline: true,
      mobileOpen: false,
      onToggle: vi.fn(),
    }
    const { rerender } = render(<Navbar {...props} collapsed={false} />)

    rerender(<Navbar {...props} collapsed />)
    expect(screen.getByRole('button', { name: 'Semana 2: Riesgo de retraso' }).getAttribute('title')).toContain('Riesgo de retraso')
    expect(screen.getByRole('complementary', { name: 'Navegación principal' }).classList.contains('sidebar--collapsed')).toBe(true)
  })
})

describe('WeekWorkspace', () => {
  it('ubica el control del menú lateral en el header del contenido', () => {
    const onSidebarCollapse = vi.fn()
    vi.stubGlobal('scrollTo', vi.fn())
    vi.spyOn(api, 'contenidoSemanas').mockReturnValue(new Promise(() => {}))
    const { rerender } = render(
      <WeekWorkspace weekId="semana03" sidebarCollapsed={false} onSidebarCollapse={onSidebarCollapse}><div /></WeekWorkspace>,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Contraer menú lateral' }))
    expect(onSidebarCollapse).toHaveBeenCalledOnce()

    rerender(<WeekWorkspace weekId="semana03" sidebarCollapsed onSidebarCollapse={onSidebarCollapse}><div /></WeekWorkspace>)
    expect(screen.getByRole('button', { name: 'Expandir menú lateral' }).getAttribute('aria-expanded')).toBe('false')
  })

  it('vuelve al inicio al cambiar de pestaña para mostrar la línea seleccionada', () => {
    const scrollTo = vi.fn()
    vi.stubGlobal('scrollTo', scrollTo)
    vi.spyOn(api, 'contenidoSemanas').mockReturnValue(new Promise(() => {}))
    render(<WeekWorkspace weekId="semana03"><div>Laboratorio de prueba</div></WeekWorkspace>)
    scrollTo.mockClear()

    fireEvent.click(screen.getByRole('button', { name: /Código explicado/i }))

    expect(scrollTo).toHaveBeenCalledWith({ top: 0, left: 0, behavior: 'auto' })
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

  it('oculta toda la ruta anterior cuando hay cambios de obstáculos pendientes', () => {
    render(
      <GridCanvas
        environment="cuadricula"
        graph={null}
        step={{ ruta_parcial: ['(0,0)', '(1,0)', '(2,0)', '(3,0)', '(4,0)', '(4,1)'], frontera: [], cerrados: [] }}
        start="(0,0)"
        goal="(4,4)"
        obstacles={[[4, 0]]}
        stale
        onToggle={vi.fn()}
      />,
    )

    expect(screen.getByRole('button', { name: 'Celda 3, 0' }).classList.contains('cell--route')).toBe(false)
    expect(screen.getByRole('button', { name: 'Celda 4, 1' }).classList.contains('cell--route')).toBe(false)
  })
})

describe('ConfusionMatrix', () => {
  it('identifica visualmente aciertos y errores con una guía breve', () => {
    render(<ConfusionMatrix matrix={[[82, 7], [4, 107]]} />)

    expect(screen.getByTitle('Verdadero negativo').textContent).toContain('82')
    expect(screen.getByTitle('Falso positivo').textContent).toContain('7')
    expect(screen.getByTitle('Falso negativo').textContent).toContain('4')
    expect(screen.getByTitle('Verdadero positivo').textContent).toContain('107')
    expect(screen.getByText('Alerta falsa')).toBeTruthy()
    expect(screen.getByText('Retraso no detectado')).toBeTruthy()
  })
})

describe('LocalContributions', () => {
  it('diferencia visualmente el aporte local de las probabilidades de clase', () => {
    render(<LocalContributions factors={[{ termino: 'temperatura', peso: 0.433, tfidf: 0.416, aporte: 0.180 }]} />)

    expect(screen.getByText('APORTE LOCAL · PESO × TF-IDF')).toBeTruthy()
    expect(screen.getByText('temperatura')).toBeTruthy()
    expect(screen.getByText('+0.180')).toBeTruthy()
    expect(screen.getByTitle(/Peso del modelo 0.433 × TF-IDF 0.416/)).toBeTruthy()
  })
})

describe('legibilidad de presentación', () => {
  it('no usa tipografías explícitas menores de 11 px', () => {
    expect(dashboardStyles).not.toMatch(/font-size:\s*(?:[1-9]|10)px\b/)
    expect(dashboardStyles).not.toMatch(/font:\s*[^;]*(?<!\d)(?:[1-9]|10)px\b/)
  })

  it('permite que el código ocupe toda la altura disponible del panel', () => {
    expect(dashboardStyles).not.toMatch(/\.source-code\s*\{[^}]*max-height\s*:/s)
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
