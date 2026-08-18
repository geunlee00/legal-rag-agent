import { Link } from 'react-router-dom'

const features = [
  {
    icon: '📋',
    title: '적용법령 진단',
    desc: '우리 회사의 업종·취급 데이터를 입력하면, 지켜야 할 법령을 자동으로 골라냅니다.',
  },
  {
    icon: '✅',
    title: '준비사항 체크리스트',
    desc: '"그래서 뭘 준비해야 하나?" — 실행 항목을 근거 조문과 함께 제시합니다.',
  },
  {
    icon: '🔔',
    title: '의안 모니터링',
    desc: '매일 새 법안을 확인해, 우리 회사에 영향이 갈 만한 것만 알려줍니다.',
  },
]

const steps = [
  { no: '1', title: '회사 정보 입력', desc: '업종, 취급하는 데이터 종류, 사업 형태를 선택합니다.' },
  { no: '2', title: '자동 진단', desc: 'AI가 적용 법령을 판정하고 근거 조문을 검색합니다.' },
  { no: '3', title: '근거 리포트', desc: '적용 법령·준비사항·인용 근거가 담긴 리포트를 받습니다.' },
]

export default function Landing() {
  return (
    <>
      {/* 히어로 */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-brand-50 to-white" />
        <div className="relative mx-auto max-w-6xl px-6 py-24 text-center">
          <span className="inline-block rounded-full bg-brand-100 px-4 py-1.5 text-sm font-medium text-brand-700">
            신생기업을 위한 컴플라이언스 나침반
          </span>
          <h1 className="mt-6 text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
            변호사 없이도,<br />법을 아는 스타트업
          </h1>
          <p className="mt-6 max-w-2xl mx-auto text-lg text-slate-600">
            법침반이 우리 회사에 적용되는 법령을 찾아 <b className="text-slate-900">근거와 함께</b> 알려드립니다.
            매일 새 법안까지 모니터링해, 규제 리스크를 미리 짚어드립니다.
          </p>
          <div className="mt-10 flex items-center justify-center gap-4">
            <Link
              to="/diagnose"
              className="rounded-xl bg-brand-600 px-7 py-3.5 text-white font-semibold hover:bg-brand-700 transition shadow-lg shadow-brand-600/20"
            >
              무료로 진단 시작 →
            </Link>
            <a href="#how" className="rounded-xl px-7 py-3.5 font-semibold text-slate-700 hover:bg-slate-100 transition">
              진단 방식 보기
            </a>
          </div>
        </div>
      </section>

      {/* 기능 */}
      <section id="features" className="mx-auto max-w-6xl px-6 py-20">
        <h2 className="text-center text-3xl font-bold text-slate-900">무엇을 해주나요?</h2>
        <div className="mt-12 grid gap-6 sm:grid-cols-3">
          {features.map((f) => (
            <div
              key={f.title}
              className="rounded-2xl border border-slate-200 p-7 hover:shadow-md hover:border-brand-200 transition"
            >
              <div className="text-3xl">{f.icon}</div>
              <h3 className="mt-4 text-lg font-semibold text-slate-900">{f.title}</h3>
              <p className="mt-2 text-slate-600 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 진단 방식 */}
      <section id="how" className="bg-slate-50 border-y border-slate-200">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <h2 className="text-center text-3xl font-bold text-slate-900">어떻게 진단하나요?</h2>
          <div className="mt-12 grid gap-8 sm:grid-cols-3">
            {steps.map((s) => (
              <div key={s.no} className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-brand-600 text-white font-bold text-lg">
                  {s.no}
                </div>
                <h3 className="mt-5 text-lg font-semibold text-slate-900">{s.title}</h3>
                <p className="mt-2 text-slate-600">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-6xl px-6 py-20 text-center">
        <h2 className="text-3xl font-bold text-slate-900">지금 우리 회사 상태를 확인해보세요</h2>
        <p className="mt-4 text-slate-600">3분이면 우리 회사에 적용되는 법령을 알 수 있습니다.</p>
        <Link
          to="/diagnose"
          className="mt-8 inline-block rounded-xl bg-brand-600 px-7 py-3.5 text-white font-semibold hover:bg-brand-700 transition shadow-lg shadow-brand-600/20"
        >
          무료로 진단 시작 →
        </Link>
      </section>
    </>
  )
}
