// Django API 호출을 한 곳에서 관리하는 작은 헬퍼.
// vite.config.js의 proxy 덕분에 '/api/...' 로만 부르면 Django(8000)로 전달된다.

const BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${await res.text()}`)
  }
  // 204(No Content) 같은 빈 응답 대비
  return res.status === 204 ? null : res.json()
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: 'POST', body: JSON.stringify(body) }),
}
