import { useEffect, useMemo, useState } from 'react'
import Icon from './Icon.jsx'
import { buildEditorUri, EDITORS, storedEditor, storeEditor } from '../services/editor.js'

export default function CodeExplainer({ code = [], step, fileName = 'a_estrella.py', workspaceRoot }) {
  const active = step?.linea_activa || 'init'
  const explanation = code.find((line) => line.id === active)
  const relativePath = fileName.includes('no_informada') ? 'src/busqueda/no_informada.py' : 'src/busqueda/a_estrella.py'
  const lineNum = explanation?.linea || 1

  const [editor, setEditor] = useState(() => storedEditor())

  useEffect(() => {
    const handler = (e) => {
      if (e.detail && EDITORS[e.detail]) {
        setEditor(e.detail)
      }
    }
    window.addEventListener('editor-change', handler)
    return () => window.removeEventListener('editor-change', handler)
  }, [])

  const editorUri = useMemo(() => {
    try {
      return buildEditorUri({
        editor,
        workspaceRoot: workspaceRoot || '',
        relativePath,
        line: lineNum,
      })
    } catch {
      return ''
    }
  }, [editor, lineNum, relativePath, workspaceRoot])

  const selectEditor = (event) => {
    const value = event.target.value
    setEditor(value)
    storeEditor(value)
  }

  return (
    <section className="panel code-panel" aria-labelledby="code-title">
      <div className="panel-heading panel-heading--dark">
        <div>
          <span className="eyebrow eyebrow--mint">TRAZA DE EJECUCIÓN</span>
          <h2 id="code-title">Dentro del algoritmo</h2>
        </div>
        <div className="code-explainer-toolbar">
          <label className="ide-picker ide-picker--compact">
            <span className="sr-only">IDE</span>
            <select value={editor} onChange={selectEditor} aria-label="IDE para edición">
              {Object.entries(EDITORS).map(([id, item]) => <option value={id} key={id}>{item.label}</option>)}
            </select>
          </label>
          <a
            className={`file-pill ${!editorUri ? 'disabled' : ''}`}
            href={editorUri || undefined}
            title={`Abrir ${relativePath} en línea ${lineNum} en ${EDITORS[editor]?.label || 'IDE'}`}
          >
            <Icon name="external" size={11} />
            {fileName} · L{lineNum}
          </a>
        </div>
      </div>
      <div className="code-window" role="region" aria-live="polite" aria-label="Código con línea activa">
        {code.map((line) => (
          <div className={`code-line ${line.id === active ? 'code-line--active' : ''}`} key={line.id}>
            <span className="line-number">{line.linea}</span>
            <code>{line.codigo}</code>
          </div>
        ))}
      </div>
      <div className="code-explanation">
        <span className="explanation-index">{explanation?.linea || 1}</span>
        <div>
          <strong>{step?.mensaje || explanation?.explicacion}</strong>
          <p>{explanation?.explicacion}</p>
          <a
            className={`code-editor-link ${!editorUri ? 'disabled' : ''}`}
            href={editorUri || undefined}
            title={`Abrir en ${EDITORS[editor]?.label || 'IDE'} en esta línea exacta`}
          >
            <Icon name="external" size={12} />
            Ver en {EDITORS[editor]?.label || 'IDE'} (L{lineNum})
          </a>
        </div>
      </div>
      <div className="variable-strip">
        <div><span>ACTUAL</span><strong>{step?.actual || '—'}</strong></div>
        <div><span>g(n)</span><strong>{step?.g ?? '—'}</strong></div>
        <div><span>h(n)</span><strong>{step?.h ?? '—'}</strong></div>
        <div><span>f(n)</span><strong>{step?.f ?? '—'}</strong></div>
      </div>
    </section>
  )
}
