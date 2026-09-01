import { createElement, useEffect, useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import rehypeKatex from 'rehype-katex'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import 'katex/dist/katex.min.css'
import Icon from './Icon.jsx'
import LearningHeader from './LearningHeader.jsx'
import { api } from '../services/api.js'

export function slugify(value) {
  return String(value)
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')
}

function textContent(value) {
  if (Array.isArray(value)) return value.map(textContent).join('')
  if (value && typeof value === 'object') return textContent(value.props?.children)
  return value == null ? '' : String(value)
}

export function MarkdownRenderer({ content }) {
  const components = useMemo(() => {
    const headings = {}
    for (let level = 1; level <= 6; level += 1) {
      const tag = `h${level}`
      headings[tag] = ({ children, ...props }) => createElement(tag, { ...props, id: slugify(textContent(children)) }, children)
    }
    return {
      ...headings,
      a: ({ children, ...props }) => <a {...props} target="_blank" rel="noreferrer">{children}</a>,
      table: ({ children, ...props }) => <div className="markdown-table"><table {...props}>{children}</table></div>,
    }
  }, [])

  return (
    <article className="markdown-body">
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]} components={components}>
        {content}
      </ReactMarkdown>
    </article>
  )
}

export default function MarkdownViewer({ week }) {
  const [reportId, setReportId] = useState(week.informes[0]?.id || '')
  const [report, setReport] = useState(null)
  const [raw, setRaw] = useState(false)
  const [query, setQuery] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (!reportId) return undefined
    let current = true
    setReport(null)
    setError('')
    setQuery('')
    api.informe(reportId)
      .then((result) => current && setReport(result))
      .catch((requestError) => current && setError(requestError.message))
    return () => { current = false }
  }, [reportId])

  const matches = useMemo(() => {
    const term = query.trim().toLocaleLowerCase('es')
    if (!term || !report) return []
    return report.contenido.split('\n').map((line, index) => ({ line, number: index + 1 }))
      .filter((item) => item.line.toLocaleLowerCase('es').includes(term))
  }, [query, report])

  const goToHeading = (title) => document.getElementById(slugify(title))?.scrollIntoView?.({ block: 'start', behavior: 'smooth' })

  return (
    <div className="view-shell learning-view">
      <LearningHeader
        eyebrow={`SEMANA ${String(week.numero).padStart(2, '0')} · INFORME TÉCNICO`}
        title={<>Lee la evidencia en <em>Markdown</em></>}
        description="Consulta la entrega semanal con tablas, fórmulas y estructura navegable, sin salir del laboratorio."
      />

      <div className="report-toolbar panel">
        <label className="field">INFORME
          <select value={reportId} onChange={(event) => setReportId(event.target.value)}>
            {week.informes.map((item) => <option value={item.id} key={item.id}>{item.titulo}</option>)}
          </select>
        </label>
        <label className="report-search"><Icon name="search" size={16} /><span className="sr-only">Buscar en el informe</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar en el informe…" /></label>
        <button className={`raw-toggle ${raw ? 'active' : ''}`} onClick={() => setRaw((value) => !value)}><Icon name="raw" size={16} />{raw ? 'Vista renderizada' : 'Ver Markdown'}</button>
      </div>

      {error && <div className="alert alert--error"><Icon name="alert" />{error}</div>}
      {!report && !error && <div className="learning-loading"><span className="spinner" />Procesando el informe…</div>}
      {report && (
        <div className="report-layout">
          <aside className="report-toc panel">
            <span className="eyebrow">EN ESTA PÁGINA</span>
            <nav aria-label="Tabla de contenido">
              {report.encabezados.map((heading) => (
                <button className={`toc-level-${heading.nivel}`} onClick={() => goToHeading(heading.titulo)} key={`${heading.linea}-${heading.titulo}`}>{heading.titulo}</button>
              ))}
            </nav>
            <dl><div><dt>Palabras</dt><dd>{report.palabras.toLocaleString('es-CO')}</dd></div><div><dt>Versión</dt><dd>{report.hash}</dd></div></dl>
          </aside>
          <section className="report-paper panel">
            {matches.length > 0 && (
              <div className="search-results"><strong>{matches.length} coincidencia{matches.length === 1 ? '' : 's'}</strong>{matches.slice(0, 5).map((item) => <span key={item.number}>L{item.number} · {item.line.trim().slice(0, 100)}</span>)}</div>
            )}
            {query && matches.length === 0 && <div className="search-results">Sin coincidencias para “{query}”.</div>}
            {raw
              ? <pre className="raw-markdown"><code>{report.contenido}</code></pre>
              : <MarkdownRenderer content={report.contenido} />}
          </section>
        </div>
      )}
    </div>
  )
}
