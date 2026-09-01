import { useEffect, useMemo, useRef, useState } from 'react'
import Icon from './Icon.jsx'
import LearningHeader from './LearningHeader.jsx'
import { api } from '../services/api.js'

export default function CodeExplorer({ week }) {
  const [exerciseId, setExerciseId] = useState(week.ejercicios[0]?.id || '')
  const exercise = useMemo(
    () => week.ejercicios.find((item) => item.id === exerciseId) || week.ejercicios[0],
    [exerciseId, week],
  )
  const [fileId, setFileId] = useState(exercise?.archivos[0]?.id || '')
  const [document, setDocument] = useState(null)
  const [selectedLine, setSelectedLine] = useState(1)
  const [playing, setPlaying] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const firstFile = exercise?.archivos[0]?.id || ''
    if (!exercise?.archivos.some((item) => item.id === fileId)) setFileId(firstFile)
  }, [exercise, fileId])

  useEffect(() => {
    if (!fileId) return undefined
    let current = true
    setDocument(null)
    setError('')
    setPlaying(false)
    api.codigo(fileId)
      .then((result) => {
        if (!current) return
        setDocument(result)
        setSelectedLine(result.lineas[0]?.numero || 1)
      })
      .catch((requestError) => current && setError(requestError.message))
    return () => { current = false }
  }, [fileId])

  const move = (offset) => {
    if (!document) return
    setSelectedLine((line) => Math.min(document.total_lineas, Math.max(1, line + offset)))
  }

  useEffect(() => {
    if (!playing || !document) return undefined
    const timeout = window.setTimeout(() => {
      if (selectedLine >= document.total_lineas) setPlaying(false)
      else move(1)
    }, 1300)
    return () => window.clearTimeout(timeout)
  }, [document, playing, selectedLine])

  const selectOutline = (line) => {
    setSelectedLine(line)
    window.document.getElementById(`source-line-${line}`)?.scrollIntoView?.({ block: 'center', behavior: 'smooth' })
  }

  return (
    <div className="view-shell learning-view">
      <LearningHeader
        eyebrow={`SEMANA ${String(week.numero).padStart(2, '0')} · CÓDIGO REAL`}
        title={<>Explora el código <em>línea a línea</em></>}
        description="Selecciona un ejercicio, recorre su implementación real y relaciona cada sentencia con el concepto de IA que materializa."
      />

      <div className="learning-controls panel">
        <label className="field">
          EJERCICIO
          <select value={exercise?.id || ''} onChange={(event) => setExerciseId(event.target.value)}>
            {week.ejercicios.map((item) => <option value={item.id} key={item.id}>{item.titulo}</option>)}
          </select>
        </label>
        <label className="field">
          ARCHIVO
          <select value={fileId} onChange={(event) => setFileId(event.target.value)}>
            {exercise?.archivos.map((item) => <option value={item.id} key={item.id}>{item.titulo}</option>)}
          </select>
        </label>
        <p>{exercise?.descripcion}</p>
      </div>

      {error && <div className="alert alert--error"><Icon name="alert" />{error}</div>}
      {!document && !error && <div className="learning-loading"><span className="spinner" />Leyendo el archivo registrado…</div>}
      {document && (
        <CodeDocument
          document={document}
          selectedLine={selectedLine}
          onSelect={setSelectedLine}
          playing={playing}
          onPlay={() => setPlaying((value) => !value)}
          onMove={move}
          onOutline={selectOutline}
        />
      )}
    </div>
  )
}

export function CodeDocument({ document, selectedLine, onSelect, playing, onPlay, onMove, onOutline }) {
  const selected = document.lineas.find((line) => line.numero === selectedLine) || document.lineas[0]
  const progress = document.total_lineas ? (selectedLine / document.total_lineas) * 100 : 0
  const sourceRef = useRef(null)

  useEffect(() => {
    const active = sourceRef.current?.querySelector(`[data-line="${selectedLine}"]`)
    active?.scrollIntoView?.({ block: 'nearest' })
  }, [selectedLine])

  return (
    <section className="code-explorer">
      <aside className="outline-panel panel">
        <div className="panel-heading"><div><span className="eyebrow">ESTRUCTURA</span><h2>Mapa del archivo</h2></div></div>
        <div className="outline-list">
          {document.outline.length
            ? document.outline.map((item) => (
              <button key={`${item.nombre}-${item.linea}`} onClick={() => onOutline(item.linea)}>
                <span>{item.tipo}</span><strong>{item.nombre}</strong><small>L{item.linea}–{item.fin}</small>
              </button>
            ))
            : <p>Este archivo no declara funciones o clases.</p>}
        </div>
      </aside>

      <div className="source-panel panel">
        <div className="source-toolbar">
          <span><i />{document.ruta}</span>
          <small>{document.total_lineas} líneas · {document.hash}</small>
        </div>
        <div className="source-code" ref={sourceRef} role="listbox" aria-label={`Código de ${document.titulo}`}>
          {document.lineas.map((line) => (
            <button
              id={`source-line-${line.numero}`}
              data-line={line.numero}
              className={selectedLine === line.numero ? 'active' : ''}
              key={line.numero}
              onClick={() => onSelect(line.numero)}
              role="option"
              aria-selected={selectedLine === line.numero}
            >
              <span>{line.numero}</span><code>{line.codigo || ' '}</code>
            </button>
          ))}
        </div>
        <div className="source-player">
          <button onClick={() => onMove(-1)} disabled={selectedLine <= 1} aria-label="Línea anterior"><Icon name="back" /></button>
          <button className="source-play" onClick={onPlay} aria-label={playing ? 'Pausar recorrido' : 'Reproducir recorrido'}><Icon name={playing ? 'pause' : 'play'} /></button>
          <button onClick={() => onMove(1)} disabled={selectedLine >= document.total_lineas} aria-label="Línea siguiente"><Icon name="next" /></button>
          <div><i style={{ width: `${progress}%` }} /></div>
          <output>L{selectedLine} / {document.total_lineas}</output>
        </div>
      </div>

      <aside className="explanation-panel panel" aria-live="polite">
        <div className="explanation-label"><span>{selected?.tipo}</span><small>LÍNEA {selected?.numero}</small></div>
        <h2>¿Qué hace esta línea?</h2>
        <p>{selected?.explicacion}</p>
        <pre><code>{selected?.codigo || 'línea en blanco'}</code></pre>
        {selected?.bloque && (
          <div className="block-context">
            <span>CONTEXTO · {selected.bloque}</span>
            <p>{selected.resumen_bloque}</p>
          </div>
        )}
        <small className="source-truth">Fuente real · hash {document.hash}</small>
      </aside>
    </section>
  )
}
