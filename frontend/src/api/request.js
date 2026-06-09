export async function api(url, options = {}) {
  const body = options.body
  const isFormData = typeof FormData !== 'undefined' && body instanceof FormData
  let requestUrl = url
  if (typeof window !== 'undefined' && url.startsWith('/api') && isFormData) {
    const backendPort = '8000'
    const currentPort = window.location.port
    if (currentPort && currentPort !== backendPort) {
      requestUrl = `${window.location.protocol}//${window.location.hostname}:${backendPort}${url}`
    }
  }
  const init = {
    credentials: 'include',
    headers: { ...(isFormData ? {} : { 'Content-Type': 'application/json' }), ...(options.headers || {}) },
    ...options
  }
  if (init.body && typeof init.body !== 'string' && !isFormData) init.body = JSON.stringify(init.body)
  const response = await fetch(requestUrl, init)
  const data = await response.json().catch(() => ({}))
  if (!response.ok || data.ok === false) {
    throw new Error(data.message || '请求失败')
  }
  return data
}
