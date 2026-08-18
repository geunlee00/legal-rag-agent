import { Link, Outlet } from 'react-router-dom'

// 모든 페이지를 감싸는 공통 뼈대: 상단 헤더 + 본문(Outlet) + 하단 푸터.
// <Outlet />: 현재 주소에 맞는 페이지가 이 자리에 끼워진다.
export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col bg-white">
      {/* 헤더 */}
      <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto max-w-6xl px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <span className="text-2xl">🧭</span>
            <span className="font-bold text-lg tracking-tight text-slate-900">
              법침반
              <span className="ml-1.5 text-xs font-semibold text-brand-600 align-top">LOPAS</span>
            </span>
          </Link>
          <nav className="flex items-center gap-6 text-sm font-medium text-slate-600">
            <a href="#features" className="hover:text-slate-900">기능</a>
            <a href="#how" className="hover:text-slate-900">진단 방식</a>
            <Link
              to="/diagnose"
              className="rounded-lg bg-brand-600 px-4 py-2 text-white hover:bg-brand-700 transition"
            >
              진단 시작
            </Link>
          </nav>
        </div>
      </header>

      {/* 본문 */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* 푸터 */}
      <footer className="border-t border-slate-200 bg-slate-50">
        <div className="mx-auto max-w-6xl px-6 py-8 text-sm text-slate-500 flex flex-col sm:flex-row justify-between gap-2">
          <p>© 2026 법침반 (LOPAS) — 법령 속에서 근거를 짚어주는 AI 나침반</p>
          <p className="text-slate-400">본 서비스는 정보 제공용이며 법률 자문이 아닙니다.</p>
        </div>
      </footer>
    </div>
  )
}
