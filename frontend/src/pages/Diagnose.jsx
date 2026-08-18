import { useState } from 'react'
import { api } from '../lib/api'

// 선택지(업종 / 사업형태) — Django 모델의 choices와 값(value)을 맞춰야 한다.
const INDUSTRIES = [
  ['healthcare', '헬스케어/의료'],
  ['fintech', '핀테크/금융'],
  ['ecommerce', '이커머스/쇼핑'],
  ['edutech', '교육'],
  ['saas', '일반 SaaS/IT서비스'],
  ['etc', '기타'],
]
const BUSINESS_TYPES = [
  ['b2c', '개인 대상(B2C)'],
  ['b2b', '기업 대상(B2B)'],
  ['both', '둘 다'],
]

// 체크박스 항목들 — 배열로 정의해두면 아래에서 map으로 한 번에 그린다.
const FLAGS = [
  ['handles_personal_data', '개인정보 취급'],
  ['handles_sensitive_data', '민감정보(건강 등) 취급'],
  ['handles_location_data', '위치정보 취급'],
  ['handles_financial_data', '신용/결제정보 취급'],
  ['handles_minor_data', '만 14세 미만 정보 취급'],
  ['does_online_sales', '온라인 판매'],
  ['does_marketing', '광고성 정보 전송(이메일/문자)'],
  ['overseas_transfer', '개인정보 국외 이전'],
]

export default function Diagnose() {
  // [개념 1] useState: 컴포넌트가 기억하는 값. 바뀌면 화면이 다시 그려진다.
  const [form, setForm] = useState({
    name: '',
    industry: 'saas',
    business_type: 'b2c',
    employee_count: 0,
    handles_personal_data: true,
    handles_sensitive_data: false,
    handles_location_data: false,
    handles_financial_data: false,
    handles_minor_data: false,
    does_online_sales: false,
    does_marketing: false,
    overseas_transfer: false,
  })
  const [result, setResult] = useState(null)   // API 응답 (처음엔 없음)
  const [loading, setLoading] = useState(false)

  // 입력이 바뀌면 form 중 해당 항목만 갱신한다.
  // {...prev} 로 기존 값을 복사하고 [key]만 새 값으로 덮어쓴다.
  function update(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  // [개념 3] 제출하면 API 호출 → 응답을 result에 저장
  async function handleSubmit(e) {
    e.preventDefault()          // 폼 기본 동작(새로고침) 막기
    setLoading(true)
    try {
      const data = await api.post('/compliance/diagnose/', form)
      setResult(data)
    } catch (err) {
      alert('진단 실패: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-12">
      <h1 className="text-3xl font-bold text-slate-900">우리 회사 법령 진단</h1>
      <p className="mt-2 text-slate-600">회사 정보를 입력하면 적용되는 법령을 찾아드립니다.</p>

      {/* ── 입력 폼 ── */}
      <form onSubmit={handleSubmit} className="mt-8 space-y-6">
        {/* 회사명 (controlled input: value ↔ state) */}
        <div>
          <label className="block text-sm font-medium text-slate-700">회사명</label>
          <input
            type="text"
            required
            value={form.name}
            onChange={(e) => update('name', e.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-brand-500 focus:outline-none"
            placeholder="예: 헬스핏"
          />
        </div>

        {/* 업종 / 사업형태 (select) */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700">업종</label>
            <select
              value={form.industry}
              onChange={(e) => update('industry', e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-brand-500 focus:outline-none"
            >
              {INDUSTRIES.map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">사업 형태</label>
            <select
              value={form.business_type}
              onChange={(e) => update('business_type', e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-brand-500 focus:outline-none"
            >
              {BUSINESS_TYPES.map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* 취급 데이터 / 사업 활동 (체크박스들 — FLAGS 배열을 map으로 그림) */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            취급 데이터 · 사업 활동 (해당하는 것 모두 체크)
          </label>
          <div className="grid sm:grid-cols-2 gap-2">
            {FLAGS.map(([key, label]) => (
              <label key={key} className="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 cursor-pointer hover:bg-slate-50">
                <input
                  type="checkbox"
                  checked={form[key]}
                  onChange={(e) => update(key, e.target.checked)}
                  className="h-4 w-4 accent-brand-600"
                />
                <span className="text-sm text-slate-700">{label}</span>
              </label>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="rounded-xl bg-brand-600 px-6 py-3 text-white font-semibold hover:bg-brand-700 transition disabled:opacity-50"
        >
          {loading ? '진단 중…' : '진단하기 →'}
        </button>
      </form>

      {/* ── 결과 (result가 있을 때만 보여줌: 조건부 렌더링) ── */}
      {result && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-slate-900">
            진단 결과 · 적용 법령 {result.diagnosis.length}개
          </h2>
          <div className="mt-6 space-y-3">
            {result.diagnosis.map((item, i) => (
              <div key={i} className="rounded-xl border border-slate-200 p-5">
                <h3 className="font-semibold text-brand-700">📋 {item.law}</h3>
                <p className="mt-1 text-slate-600 text-sm leading-relaxed">{item.reason}</p>

                {/* 근거 조문: evidence가 있으면 목록, 없으면 안내 문구 */}
                {item.evidence && item.evidence.length > 0 ? (
                  <div className="mt-3 space-y-2">
                    <p className="text-xs font-semibold text-slate-400">근거 조문</p>
                    {item.evidence.map((ev, j) => (
                      <div key={j} className="rounded-lg bg-slate-50 border border-slate-200 p-3">
                        <p className="text-sm font-medium text-slate-800">
                          {ev.article_no} {ev.article_title}
                        </p>
                        <p className="mt-1 text-xs text-slate-500 leading-relaxed">{ev.content}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="mt-3 text-xs text-slate-400">· 관련 조문 데이터가 아직 없습니다.</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
