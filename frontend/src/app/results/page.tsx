'use client'
import { useSearchParams } from 'next/navigation'
import { useEffect, useRef, useState, Suspense } from 'react'
import Link from 'next/link'

function useInView(ref: React.RefObject<HTMLElement>) {
  const [inView, setInView] = useState(false)
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setInView(true) }, { threshold: 0.1 })
    if (ref.current) obs.observe(ref.current)
    return () => obs.disconnect()
  }, [ref])
  return inView
}

function ScoreGauge({ score }: { score: number }) {
  const [animated, setAnimated] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const inView = useInView(ref as React.RefObject<HTMLElement>)
  const [displayScore, setDisplayScore] = useState(0)

  useEffect(() => {
    if (!inView || animated) return
    setAnimated(true)
    const start = Date.now()
    const dur = 2000
    const target = Math.round(score * 100)
    const tick = () => {
      const p = Math.min((Date.now() - start) / dur, 1)
      const ease = 1 - Math.pow(1 - p, 4)
      setDisplayScore(Math.round(ease * target))
      if (p < 1) requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)
  }, [inView, animated, score])

  // Gauge: 180° arc (half circle), radius 90
  const R = 90
  const circumference = Math.PI * R  // half circle
  const pct = animated ? score : 0
  const offset = circumference * (1 - pct)

  const color = score >= 0.9 ? 'var(--success)' : score >= 0.65 ? 'var(--accent)' : 'var(--danger)'
  const label = score >= 0.9 ? 'INTERVIEW INVITED' : score >= 0.65 ? 'CLOSE — KEEP IMPROVING' : 'NEEDS WORK'
  const labelColor = score >= 0.9 ? 'var(--success)' : score >= 0.65 ? 'var(--accent)' : 'var(--danger)'

  return (
    <div ref={ref} style={{ textAlign: 'center', padding: '48px 32px' }}>
      <div style={{ position: 'relative', width: 240, height: 130, margin: '0 auto 16px' }}>
        <svg viewBox="0 0 220 120" style={{ width: '100%', height: '100%', overflow: 'visible' }}>
          {/* Track */}
          <path
            d="M 20 110 A 90 90 0 0 1 200 110"
            fill="none" stroke="var(--border)" strokeWidth="14" strokeLinecap="round"
          />
          {/* Animated fill */}
          <path
            d="M 20 110 A 90 90 0 0 1 200 110"
            fill="none" stroke={color} strokeWidth="14" strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={animated ? offset : circumference}
            style={{ transition: 'stroke-dashoffset 2s cubic-bezier(0.34, 1.56, 0.64, 1), stroke 0.5s' }}
          />
          {/* Tick marks */}
          {[0, 25, 50, 75, 100].map((t, i) => {
            const angle = -180 + (t / 100) * 180
            const rad = (angle * Math.PI) / 180
            const x1 = 110 + 90 * Math.cos(rad)
            const y1 = 110 + 90 * Math.sin(rad)
            const x2 = 110 + 78 * Math.cos(rad)
            const y2 = 110 + 78 * Math.sin(rad)
            return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--text-muted)" strokeWidth="1.5" />
          })}
        </svg>

        {/* Score in center */}
        <div style={{ position: 'absolute', bottom: 0, left: '50%', transform: 'translateX(-50%)', textAlign: 'center' }}>
          <div className="mono" style={{ fontSize: 52, fontWeight: 700, color, lineHeight: 1 }}>
            {displayScore}<span style={{ fontSize: 24 }}>%</span>
          </div>
        </div>
      </div>

      {/* Status badge */}
      <div style={{
        display: 'inline-block', padding: '8px 20px', borderRadius: 6,
        background: score >= 0.9 ? 'var(--success-dim)' : score >= 0.65 ? 'var(--accent-dim)' : 'var(--danger-dim)',
        fontFamily: 'JetBrains Mono', fontSize: 12, fontWeight: 700,
        color: labelColor, letterSpacing: '0.1em', marginBottom: 8,
      }}>
        {label}
      </div>

      {/* Scale labels */}
      <div style={{ display: 'flex', justifyContent: 'space-between', maxWidth: 240, margin: '12px auto 0', fontFamily: 'JetBrains Mono', fontSize: 10, color: 'var(--text-muted)' }}>
        <span>0%</span>
        <span>50%</span>
        <span>100%</span>
      </div>
    </div>
  )
}

function RuleCard({ rule, idx }: { rule: any, idx: number }) {
  const ref = useRef<HTMLDivElement>(null)
  const inView = useInView(ref as React.RefObject<HTMLElement>)

  return (
    <div ref={ref} style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '14px 20px', borderRadius: 8,
      background: rule.passed ? 'var(--success-dim)' : 'var(--danger-dim)',
      border: `1px solid ${rule.passed ? 'rgba(52,211,153,0.2)' : 'rgba(248,113,113,0.2)'}`,
      opacity: inView ? 1 : 0,
      transform: inView ? 'none' : 'translateX(-20px)',
      transition: `opacity 0.4s ${idx * 0.05}s, transform 0.4s ${idx * 0.05}s`,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 16, color: rule.passed ? 'var(--success)' : 'var(--danger)', flexShrink: 0 }}>
          {rule.passed ? '✓' : '✗'}
        </span>
        <div>
          <div style={{ fontSize: 13, fontFamily: 'Syne', fontWeight: 600 }}>{rule.description}</div>
          <div style={{ fontFamily: 'JetBrains Mono', fontSize: 10, color: rule.passed ? 'var(--success)' : 'var(--danger)', opacity: 0.7, marginTop: 2 }}>
            {rule.rule}
          </div>
        </div>
      </div>
      <div style={{ flexShrink: 0, marginLeft: 16 }}>
        <div style={{ fontFamily: 'JetBrains Mono', fontSize: 13, fontWeight: 700, color: rule.passed ? 'var(--success)' : 'var(--danger)', textAlign: 'right' }}>
          {Math.round(rule.weight * 100)}%
        </div>
        <div style={{ fontSize: 10, color: 'var(--text-muted)', textAlign: 'right' }}>weight</div>
      </div>
    </div>
  )
}

function WeightBar({ label, value, max }: { label: string, value: number, max: number }) {
  const ref = useRef<HTMLDivElement>(null)
  const inView = useInView(ref as React.RefObject<HTMLElement>)
  return (
    <div ref={ref}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <span style={{ fontSize: 12, color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono' }}>{label}</span>
        <span style={{ fontSize: 12, color: 'var(--accent)', fontFamily: 'JetBrains Mono' }}>{Math.round(value * 100)}%</span>
      </div>
      <div style={{ height: 4, background: 'var(--border)', borderRadius: 2 }}>
        <div style={{
          height: '100%', background: 'var(--accent)', borderRadius: 2,
          width: inView ? `${(value / max) * 100}%` : '0%',
          transition: 'width 1.2s cubic-bezier(0.34, 1.56, 0.64, 1)',
        }} />
      </div>
    </div>
  )
}

function ResultsContent() {
  const params = useSearchParams()
  const raw = params.get('data')
  const [data, setData] = useState<any>(null)
  const [tab, setTab] = useState<'passed' | 'failed'>('passed')

  useEffect(() => {
    if (raw) {
      try { setData(JSON.parse(decodeURIComponent(raw))) }
      catch { setData(null) }
    }
  }, [raw])

  if (!data) {
    return (
      <div style={{ textAlign: 'center', padding: '120px 24px' }}>
        <div style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--accent)', marginBottom: 16 }}>NO RESULTS FOUND</div>
        <h2 style={{ fontSize: 32, marginBottom: 24, letterSpacing: '-0.02em' }}>Run an evaluation first</h2>
        <Link href="/apply"><button className="btn-accent">Upload CV →</button></Link>
      </div>
    )
  }

  const passed = data.rules_passed || []
  const failed = data.rules_failed || []
  const allRules = [
    ...passed.map((r: any) => ({ ...r, passed: true })),
    ...failed.map((r: any) => ({ ...r, passed: false })),
  ]
  const totalWeight = allRules.reduce((s: number, r: any) => s + r.weight, 0)

  return (
    <div style={{ maxWidth: 860, margin: '0 auto', padding: '48px 24px', position: 'relative', zIndex: 1 }}>

      {/* Header */}
      <div style={{ marginBottom: 40 }}>
        <div style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--accent)', letterSpacing: '0.12em', marginBottom: 12 }}>
          EVALUATION COMPLETE
        </div>
        <h1 style={{ fontSize: 40, letterSpacing: '-0.03em', marginBottom: 8 }}>Your Results</h1>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <span style={{ fontFamily: 'JetBrains Mono', fontSize: 12, color: 'var(--text-muted)' }}>
            {data.candidate_email}
          </span>
          <span style={{ fontFamily: 'JetBrains Mono', fontSize: 12, color: 'var(--accent)' }}>
            {data.role_title?.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Score gauge + summary stats */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1, background: 'var(--border)', marginBottom: 1 }}>
        <div className="card" style={{ borderRadius: 0, border: 'none' }}>
          <ScoreGauge score={data.score} />
        </div>
        <div className="card" style={{ borderRadius: 0, border: 'none', padding: 32 }}>
          <div style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.08em', marginBottom: 24 }}>RULE BREAKDOWN</div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 28 }}>
            {[
              { label: 'Rules Passed', val: passed.length, color: 'var(--success)' },
              { label: 'Rules Failed', val: failed.length, color: 'var(--danger)' },
              { label: 'Total Rules', val: allRules.length, color: 'var(--text-primary)' },
              { label: 'Pass Rate', val: `${Math.round((passed.length / allRules.length) * 100)}%`, color: 'var(--accent)' },
            ].map((s, i) => (
              <div key={i} style={{ textAlign: 'center', padding: '16px 8px', background: 'var(--bg-secondary)', borderRadius: 8 }}>
                <div className="mono" style={{ fontSize: 28, fontWeight: 700, color: s.color }}>{s.val}</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4, fontFamily: 'Syne', letterSpacing: '0.04em' }}>{s.label}</div>
              </div>
            ))}
          </div>

          {/* Weight bars for top rules */}
          <div style={{ fontFamily: 'JetBrains Mono', fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.08em', marginBottom: 12 }}>TOP RULE WEIGHTS</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {allRules.sort((a: any, b: any) => b.weight - a.weight).slice(0, 5).map((r: any, i: number) => (
              <WeightBar key={i} label={r.rule} value={r.weight} max={totalWeight} />
            ))}
          </div>
        </div>
      </div>

      {/* Rules detail */}
      <div className="card" style={{ marginBottom: 1, borderRadius: 0, border: 'none', borderTop: '1px solid var(--border)', padding: '32px' }}>
        <div style={{ display: 'flex', gap: 0, marginBottom: 24, border: '1px solid var(--border)', borderRadius: 8, overflow: 'hidden' }}>
          {(['passed', 'failed'] as const).map(t => (
            <button key={t} onClick={() => setTab(t)} style={{
              flex: 1, padding: '12px 0', fontFamily: 'Syne', fontWeight: 700, fontSize: 13,
              letterSpacing: '0.05em', textTransform: 'uppercase', cursor: 'pointer', border: 'none',
              background: tab === t ? (t === 'passed' ? 'var(--success-dim)' : 'var(--danger-dim)') : 'var(--bg-card)',
              color: tab === t ? (t === 'passed' ? 'var(--success)' : 'var(--danger)') : 'var(--text-muted)',
              transition: 'all 0.2s',
            }}>
              {t === 'passed' ? `✓ ${passed.length} Passed` : `✗ ${failed.length} Failed`}
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {(tab === 'passed' ? passed : failed).map((r: any, i: number) => (
            <RuleCard key={i} rule={{ ...r, passed: tab === 'passed' }} idx={i} />
          ))}
        </div>
      </div>

      {/* Improvement tips */}
      {data.improvement_tips?.length > 0 && (
        <div className="card" style={{ borderRadius: 0, border: 'none', borderTop: '1px solid var(--border)', padding: 32 }}>
          <div style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--accent)', letterSpacing: '0.12em', marginBottom: 20 }}>
            PERSONALISED IMPROVEMENT TIPS
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {data.improvement_tips.map((tip: string, i: number) => (
              <div key={i} style={{
                padding: '16px 20px', borderRadius: 8,
                background: 'var(--accent-dim)', border: '1px solid var(--border)',
                display: 'flex', gap: 14, alignItems: 'flex-start',
                opacity: 0, transform: 'translateY(12px)',
                animation: `countUp 0.4s ease ${i * 0.1 + 0.2}s forwards`,
              }}>
                <span className="mono" style={{ color: 'var(--accent)', fontWeight: 700, fontSize: 13, flexShrink: 0, marginTop: 1 }}>
                  {String(i + 1).padStart(2, '0')}
                </span>
                <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{tip}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div style={{ display: 'flex', gap: 12, marginTop: 32, flexWrap: 'wrap' }}>
        <Link href="/apply">
          <button className="btn-accent">Evaluate Another CV →</button>
        </Link>
        {data.report_path && (
          <a href={`http://localhost:8000${data.report_path}`} target="_blank" rel="noreferrer">
            <button className="btn-ghost">Download PDF Report</button>
          </a>
        )}
      </div>
    </div>
  )
}

export default function ResultsPage() {
  return (
    <div style={{ position: 'relative', minHeight: '100vh' }}>
      <div className="grid-bg" style={{ position: 'fixed', inset: 0, zIndex: 0, opacity: 0.3 }} />
      <div className="orb" style={{ width: 400, height: 400, background: 'rgba(52,211,153,0.04)', top: 100, right: 0 }} />
      <Suspense fallback={
        <div style={{ textAlign: 'center', padding: 120 }}>
          <div className="mono" style={{ color: 'var(--accent)' }}>Loading results...</div>
        </div>
      }>
        <ResultsContent />
      </Suspense>
    </div>
  )
}
