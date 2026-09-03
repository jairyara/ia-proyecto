const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

async function request(path, options = {}) {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 15000)
  try {
    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    })
    const body = await response.json().catch(() => ({}))
    if (!response.ok) {
      const detail = Array.isArray(body.detail)
        ? body.detail.map((item) => item.msg).join(' · ')
        : body.detail
      throw new Error(detail || `La API respondió con estado ${response.status}`)
    }
    return body
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('La operación tardó demasiado. Verifica que la API esté activa.')
    }
    throw error
  } finally {
    window.clearTimeout(timeout)
  }
}

export const api = {
  health: () => request('/api/health'),
  rutasAmazon: () => request('/api/busqueda/amazon/rutas'),
  simularBusqueda: (payload) =>
    request('/api/busqueda/a-estrella/simular', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  replanificar: (payload) =>
    request('/api/busqueda/replanificar', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  metricas: () => request('/api/modelado/metricas'),
  predecirRiesgo: (payload) =>
    request('/api/modelado/predecir-riesgo', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  ejemplos: () => request('/api/clasificacion/ejemplos'),
  clasificar: (descripcion) =>
    request('/api/clasificacion/evaluar-requerimiento', {
      method: 'POST',
      body: JSON.stringify({ descripcion }),
    }),
  contextoHibrido: () => request('/api/hibrido/contexto'),
  responderHibrido: (consulta) =>
    request('/api/hibrido/responder', {
      method: 'POST',
      body: JSON.stringify({ consulta }),
    }),
  contenidoSemanas: () => request('/api/contenido/semanas'),
  codigo: (archivoId) => request(`/api/contenido/codigo/${encodeURIComponent(archivoId)}`),
  informe: (informeId) => request(`/api/contenido/informes/${encodeURIComponent(informeId)}`),
}
