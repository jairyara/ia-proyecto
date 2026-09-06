export const EDITORS = {
  vscode: { label: 'VS Code', scheme: 'vscode' },
  pycharm: { label: 'PyCharm', scheme: 'pycharm' },
}

const EDITOR_STORAGE_KEY = 'orbita.editor'

export function storedEditor() {
  try {
    const saved = window.localStorage?.getItem(EDITOR_STORAGE_KEY)
    return EDITORS[saved] ? saved : 'vscode'
  } catch {
    return 'vscode'
  }
}

export function storeEditor(editor) {
  try {
    if (EDITORS[editor]) {
      window.localStorage?.setItem(EDITOR_STORAGE_KEY, editor)
      window.dispatchEvent(new CustomEvent('editor-change', { detail: editor }))
    }
  } catch {
    // El enlace sigue funcionando si el navegador bloquea almacenamiento local.
  }
}

function normalizedLine(value) {
  const line = Number.parseInt(value, 10)
  return Number.isFinite(line) && line > 0 ? line : 1
}

function absoluteFilePath(workspaceRoot, relativePath) {
  const root = String(workspaceRoot || '').trim().replace(/\\/g, '/').replace(/\/+$/, '')
  const relative = String(relativePath || '').trim().replace(/\\/g, '/').replace(/^\/+/, '')

  if (!root || (!root.startsWith('/') && !/^[A-Za-z]:\//.test(root))) {
    throw new Error('La ruta local del proyecto debe ser absoluta.')
  }
  if (!relative || relative.split('/').some((part) => part === '..')) {
    throw new Error('La ruta del archivo no es segura.')
  }
  return `${root}/${relative}`
}

function encodePath(path) {
  return path.split('/').map((part) => encodeURIComponent(part)).join('/')
}

export function buildEditorUri({ editor, workspaceRoot, relativePath, line, column = 1 }) {
  if (!EDITORS[editor]) throw new Error(`IDE no soportado: ${editor}`)

  const file = absoluteFilePath(workspaceRoot, relativePath)
  const targetLine = normalizedLine(line)
  const targetColumn = normalizedLine(column)

  if (editor === 'vscode') {
    return `vscode://file${encodePath(file)}:${targetLine}:${targetColumn}`
  }

  const params = new URLSearchParams({
    file,
    line: String(targetLine),
    column: String(targetColumn),
  })
  return `pycharm://open?${params.toString()}`
}
