import http from './http'

export const authApi = {
  login: (username, password) =>
    http.post('/api/v1/auth/login', { username, password }).then((r) => r.data)
}

export const llmApi = {
  list: () => http.get('/api/v1/llm_configs').then((r) => r.data),
  create: (body) => http.post('/api/v1/llm_configs', body).then((r) => r.data),
  update: (id, body) => http.put(`/api/v1/llm_configs/${id}`, body).then((r) => r.data),
  remove: (id) => http.delete(`/api/v1/llm_configs/${id}`).then((r) => r.data),
  providers: () => http.get('/api/v1/llm_configs/providers').then((r) => r.data)
}

export const datasourceApi = {
  list: () => http.get('/api/v1/datasources').then((r) => r.data),
  create: (body) => http.post('/api/v1/datasources', body).then((r) => r.data),
  update: (id, body) => http.put(`/api/v1/datasources/${id}`, body).then((r) => r.data),
  remove: (id) => http.delete(`/api/v1/datasources/${id}`).then((r) => r.data),
  test: (id) => http.post(`/api/v1/datasources/${id}/test`).then((r) => r.data)
}

export const agentApi = {
  list: () => http.get('/api/v1/agents').then((r) => r.data),
  create: (body) => http.post('/api/v1/agents', body).then((r) => r.data),
  update: (id, body) => http.put(`/api/v1/agents/${id}`, body).then((r) => r.data),
  remove: (id) => http.delete(`/api/v1/agents/${id}`).then((r) => r.data)
}

export const skillApi = {
  list: () => http.get('/api/v1/skills').then((r) => r.data),
  upload: (file, overwrite = false) => {
    const form = new FormData()
    form.append('file', file)
    return http
      .post(`/api/v1/skills/upload?overwrite=${overwrite}`, form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      .then((r) => r.data)
  },
  setEnabled: (id, enabled) =>
    http.post(`/api/v1/skills/${id}/${enabled ? 'enable' : 'disable'}`).then((r) => r.data),
  remove: (id) => http.delete(`/api/v1/skills/${id}`).then((r) => r.data),
  skillMd: (id) => http.get(`/api/v1/skills/${id}/skill_md`).then((r) => r.data)
}

export const apiKeyApi = {
  list: () => http.get('/api/v1/apikeys').then((r) => r.data),
  create: (body) => http.post('/api/v1/apikeys', body).then((r) => r.data),
  remove: (id) => http.delete(`/api/v1/apikeys/${id}`).then((r) => r.data)
}

/**
 * Streaming chat via fetch + ReadableStream.
 * onEvent(evt) called for each parsed SSE data object.
 */
export async function chatStream({ agentId, message, conversationId, onEvent, signal }) {
  const { useAuthStore } = await import('../stores/auth')
  const auth = useAuthStore()
  const resp = await fetch('/api/v1/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {})
    },
    body: JSON.stringify({
      agent_id: agentId,
      message,
      ...(conversationId ? { conversation_id: conversationId } : {})
    }),
    signal
  })

  if (!resp.ok) {
    let detail = ''
    try {
      const j = await resp.json()
      detail = j.detail || j.message || JSON.stringify(j)
    } catch (e) {
      detail = await resp.text().catch(() => '')
    }
    throw new Error(detail || `请求失败 (${resp.status})`)
  }

  const reader = resp.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    let idx
    while ((idx = buffer.indexOf('\n\n')) >= 0) {
      const chunk = buffer.slice(0, idx)
      buffer = buffer.slice(idx + 2)
      const lines = chunk.split('\n')
      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed.startsWith('data:')) continue
        const payload = trimmed.slice(5).trim()
        if (!payload) continue
        try {
          onEvent(JSON.parse(payload))
        } catch (e) {
          // ignore non-json line
        }
      }
    }
  }
}

export const chatSync = (body) => http.post('/api/v1/chat/sync', body).then((r) => r.data)

export default {
  authApi,
  llmApi,
  datasourceApi,
  agentApi,
  skillApi,
  apiKeyApi,
  chatStream,
  chatSync
}
