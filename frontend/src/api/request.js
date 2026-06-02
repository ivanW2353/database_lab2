export async function api(url, options = {}) {
  const init = {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options
  }
  if (init.body && typeof init.body !== 'string') init.body = JSON.stringify(init.body)
  const response = await fetch(url, init)
  const data = await response.json().catch(() => ({}))
  if (!response.ok || data.ok === false) {
    throw new Error(data.message || '请求失败')
  }
  return data
}
