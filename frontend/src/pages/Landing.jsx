import { Link } from 'react-router-dom'
import { FileSearch, ListChecks, Radar, FileText } from 'lucide-react'

const features = [
  {
    Icon: FileSearch,   // 법령을 찾아준다
    title: '적용법령 진단',
    desc: '우리 회사의 업종·취급 데이터를 입력하면, 지켜야 할 법령을 자동으로 골라냅니다.',
  },
  {
    Icon: ListChecks,   // 체크리스트
    title: '준비사항 체크리스트',
    desc: '"그래서 뭘 준비해야 하나?" — 실행 항목을 근거 조문과 함께 제시합니다.',
  },
  {
    Icon: Radar,        // 모니터링(레이더)
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
        <div className="relative mx-auto max-w-6xl px-6 py-20 lg:py-28 grid lg:grid-cols-2 gap-12 items-center">
          {/* 왼쪽: 카피 */}
          <div>
            <span className="inline-block rounded-full bg-brand-100 px-4 py-1.5 text-sm font-medium text-brand-700">
              신생기업을 위한 컴플라이언스 나침반
            </span>
            <h1 className="mt-6 text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
              변호사 없이도,<br />법을 아는 스타트업
            </h1>
            <p className="mt-6 text-lg text-slate-600">
              법침반이 우리 회사에 적용되는 법령을 찾아 <b className="text-slate-900">근거와 함께</b> 알려드립니다.
              매일 새 법안까지 모니터링해, 규제 리스크를 미리 짚어드립니다.
            </p>
            <div className="mt-10 flex items-center gap-4">
              <Link
                to="/diagnose"
                className="rounded-xl bg-brand-600 px-7 py-3.5 text-white font-semibold hover:bg-brand-700 transition shadow-lg shadow-brand-600/20"
              >
                무료로 진단 시작 →
              </Link>
              <a href="#how" className="rounded-xl px-7 py-3.5 font-semibold text-slate-700 hover:bg-white/60 transition">
                진단 방식 보기
              </a>
            </div>
          </div>

          {/* 오른쪽: 제품 목업 */}
          <HeroMockup />
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
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-100 text-brand-600">
                <f.Icon className="h-6 w-6" strokeWidth={2} />
              </div>
              <h3 className="mt-4 text-lg font-semibold text-slate-900">{f.title}</h3>
              <p className="mt-2 text-slate-600 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 진단 방식 */}
      <section id="how" className="bg-cream border-y border-slate-200">
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

// 히어로 오른쪽에 들어가는 '가짜 앱 창' 목업.
// 외부 이미지 없이 HTML/CSS로 진단 결과 화면을 미니로 재현한다.
function HeroMockup() {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-2xl shadow-brand-900/10 overflow-hidden">
      {/* 창 상단바 (신호등 점 + 제목) */}
      <div className="flex items-center gap-2 border-b border-slate-100 bg-slate-50 px-4 py-3">
        <span className="h-3 w-3 rounded-full bg-red-400" />
        <span className="h-3 w-3 rounded-full bg-yellow-400" />
        <span className="h-3 w-3 rounded-full bg-green-400" />
        <span className="ml-3 text-xs text-slate-400">법침반 · 진단 결과</span>
      </div>

      {/* 본문 */}
      <div className="p-5">
        <div className="flex items-center gap-2 text-sm">
          <span className="rounded-lg bg-brand-100 px-2.5 py-1 font-medium text-brand-700">헬스핏 · 헬스케어</span>
          <span className="text-slate-400">적용 법령 3건</span>
        </div>

        <div className="mt-4 space-y-3">
          {/* 법령 카드 1 */}
          <div className="rounded-xl border border-slate-200 p-4">
            <p className="flex items-center gap-1.5 font-semibold text-brand-700 text-sm">
              <FileText className="h-4 w-4" /> 개인정보 보호법 (민감정보)
            </p>
            <div className="mt-2 rounded-lg bg-brand-50 p-3">
              <p className="text-xs font-medium text-slate-700">제23조 민감정보의 처리 제한</p>
              <p className="mt-1 text-[11px] text-slate-400 leading-relaxed">
                건강 등 민감정보를 처리하려면 별도 동의 등 강화된 요건을 갖춰야…
              </p>
            </div>
          </div>

          {/* 법령 카드 2 */}
          <div className="rounded-xl border border-slate-200 p-4">
            <p className="flex items-center gap-1.5 font-semibold text-brand-700 text-sm">
              <FileText className="h-4 w-4" /> 정보통신망법
            </p>
            <div className="mt-2 rounded-lg bg-brand-50 p-3">
              <p className="text-xs font-medium text-slate-700">제50조 영리목적의 광고성 정보 전송 제한</p>
              <p className="mt-1 text-[11px] text-slate-400 leading-relaxed">
                광고성 정보를 전송하려면 수신자의 사전 동의가 필요…
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
