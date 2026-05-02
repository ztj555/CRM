/**
 * apiFetch - 统一的fetch封装，自动携带token
 */
export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('token')
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {})
  }
  const res = await fetch(`/api${path.startsWith('/api') ? path.slice(4) : path}`, {
    ...options,
    headers
  })
  if (res.status === 401) {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    window.location.href = '/'
    return null
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  // 204 No Content
  if (res.status === 204) return null
  return res.json()
}

export default apiFetch
