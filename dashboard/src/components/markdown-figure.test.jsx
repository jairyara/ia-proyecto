import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MarkdownRenderer } from './MarkdownViewer.jsx'

describe('figuras del informe', () => {
  it('muestra el diagrama de Semana 11 desde una URL pública absoluta', () => {
    render(<MarkdownRenderer
      content="![F1 de cuatro modelos](figuras/semana11-f1-diagram-design.svg)\n\n[Abrir HTML](figuras/semana11-f1-diagram-design.html)"
      sourcePath="reports/semana11.md"
    />)

    expect(screen.getByRole('img', { name: 'F1 de cuatro modelos' }).getAttribute('src'))
      .toBe('/figuras/semana11-f1-diagram-design.svg')
    expect(screen.getByRole('link', { name: 'Abrir HTML' }).getAttribute('href'))
      .toBe('/figuras/semana11-f1-diagram-design.html')
  })
})
