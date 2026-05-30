'use client'
import { useEffect, useRef, useState } from 'react'
import Link from 'next/link'

function useInView(ref: React.RefObject<HTMLElement>) {
  const [inView, setInView] = useState(false)
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setInView(true) }, { threshold: 0.15 })
    if (ref.current) obs.observe(ref.current)
    return () => obs.disconnect()
  }, [ref])
  return inView
}

function AnimatedNumber({ target, suffix = '' }: { target: number, suffix?: string }) {
  const [val, setVal] = useState(0)
  const ref = useRef<HTMLSpanElement>(null)
  const inView = useInView(ref as React.RefObject<HTMLElement>)
  useEffect(() => {
    if (!inView) return
    const start = Date.now()
    const dur = 1800
    const tick = () => {
      const p = Math.min((Date.now() - start) / dur, 1)
      const ease = 1 - Math.pow(1 - p, 3)
      setVal(Math.round(ease * target))
      if (p < 1) requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)
  }, [inView, target])
  return <span ref={ref}>{val}{suffix}</span>
}

const ROLES = ['Software Engineer', 'Data Analyst', 'Web Developer', 'ML Engineer', 'Cyber Analyst']

export default function Home() {
  const [roleIdx, setRoleIdx] = useState(0)
  const [displayed, setDisplayed] = useState('')
  const [typing, setTyping] = useState(true)
  const statsRef = useRef<HTMLDivElement>(null)
  const featRef = useRef<HTMLDivElement>(null)
  const statsInView = useInView(statsRef)
  const featInView = useInView(featRef)

  // Typewriter effect
  useEffect(() => {
    const role = ROLES[roleIdx]
    let i = displayed.length
    if (typing) {
      if (i < role.length) {
        const t = setTimeout(() => setDisplayed(role.slice(0, i + 1)), 60)
        return () => clearTimeout(t)
      } else {
        const t = setTimeout(() => setTyping(false), 1800)
        return () => clearTimeout(t)
      }
    } else {
      if (i > 0) {
        const t = setTimeout(() => setDisplayed(role.slice(0, i - 1)), 35)
        return () => clearTimeout(t)
      } else {
        setRoleIdx((roleIdx + 1) % ROLES.length)
        setTyping(true)
      }
    }
  }, [displayed, typing, roleIdx])

  return (
    <div style={{ position: 'relative', overflow: 'hidden' }}>

      {/* Grid background */}
      <div className="grid-bg" style={{ position: 'fixed', inset: 0, zIndex: 0, opacity: 0.6 }} />

      {/* Ambient orbs */}
      <div className="orb" style={{ width: 600, height: 600, background: 'rgba(251,191,36,0.06)', top: -200, right: -100 }} />
      <div className="orb" style={{ width: 400, height: 400, background: 'rgba(52,211,153,0.04)', bottom: 100, left: -100 }} />

      {/* ── HERO ───────────────────────────────── */}
      <section style={{ position: 'relative', zIndex: 1, minHeight: '100vh', display: 'flex', alignItems: 'center', padding: '80px 24px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', width: '100%' }}>

          {/* Tag */}
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            background: 'var(--accent-dim)', border: '1px solid var(--accent)',
            borderRadius: 100, padding: '6px 16px', marginBottom: 32,
            animation: 'countUp 0.6s ease forwards',
          }}>
            <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent)', animation: 'pulse 2s infinite' }} />
            <span style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--accent)', letterSpacing: '0.1em', fontWeight: 700 }}>
              AI-POWERED RECRUITMENT
            </span>
          </div>

          {/* Headline */}
          <h1 style={{ fontSize: 'clamp(48px, 8vw, 96px)', letterSpacing: '-0.04em', lineHeight: 1, marginBottom: 24, maxWidth: 900 }}>
            Hire the right<br />
            <span style={{ color: 'var(--accent)' }}>{displayed}</span>
            <span style={{ color: 'var(--accent)', animation: 'pulse 1s infinite' }}>|</span>
          </h1>

          <p style={{ fontSize: 18, color: 'var(--text-secondary)', maxWidth: 560, lineHeight: 1.7, marginBottom: 48, fontWeight: 300 }}>
            Expert system meets fuzzy logic. Upload a CV, get an instant AI evaluation
            with explainable scores, skill gap analysis, and personalised improvement tips.
          </p>

          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <Link href="/apply">
              <button className="btn-accent" style={{ padding: '14px 36px', fontSize: 14 }}>
                Upload Your CV →
              </button>
            </Link>
            <Link href="/company">
              <button className="btn-ghost" style={{ padding: '14px 32px', fontSize: 14 }}>
                Post a Job
              </button>
            </Link>
          </div>

          {/* Floating card preview */}
          <div style={{
            position: 'absolute', right: 40, top: '50%', transform: 'translateY(-50%)',
            width: 300, display: 'none',
          }} className="hidden lg:block">
            <ScorePreviewCard />
          </div>
        </div>
      </section>

      {/* ── STATS ──────────────────────────────── */}
      <section ref={statsRef} style={{ position: 'relative', zIndex: 1, padding: '80px 24px', borderTop: '1px solid var(--border)' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 1, background: 'var(--border)' }}>
            {[
              { val: 60, suffix: '+', label: 'Expert Rules' },
              { val: 5, suffix: '', label: 'Job Roles' },
              { val: 90, suffix: '%', label: 'Pass Threshold' },
              { val: 100, suffix: 'ms', label: 'Evaluation Speed' },
            ].map((s, i) => (
              <div key={i} style={{ background: 'var(--bg-primary)', padding: '48px 32px', textAlign: 'center' }}>
                <div className="mono" style={{ fontSize: 56, fontWeight: 700, color: 'var(--accent)', lineHeight: 1 }}>
                  {statsInView ? <AnimatedNumber target={s.val} suffix={s.suffix} /> : `0${s.suffix}`}
                </div>
                <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 8, letterSpacing: '0.06em', textTransform: 'uppercase', fontFamily: 'Syne' }}>
                  {s.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ───────────────────────── */}
      <section style={{ position: 'relative', zIndex: 1, padding: '100px 24px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div style={{ marginBottom: 64 }}>
            <div style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--accent)', letterSpacing: '0.12em', marginBottom: 16 }}>
              HOW IT WORKS
            </div>
            <h2 style={{ fontSize: 'clamp(32px, 5vw, 56px)', letterSpacing: '-0.03em' }}>
              From PDF to decision<br />in seconds
            </h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 1, background: 'var(--border)' }}>
            {[
              { num: '01', title: 'Upload CV', desc: 'Drag and drop your PDF. Our parser extracts skills, education, experience, and projects automatically.', icon: '⬆' },
              { num: '02', title: 'Expert Rules Fire', desc: '60+ PyKnow rules evaluate your profile against the role. Each rule has a weight and certainty factor.', icon: '⚡' },
              { num: '03', title: 'Fuzzy Scoring', desc: 'scikit-fuzzy membership functions add partial credit for near-misses. No harsh binary cutoffs.', icon: '◎' },
              { num: '04', title: 'Instant Report', desc: 'Get a detailed PDF with score gauge, rule breakdown, and personalised improvement tips via RAG.', icon: '📊' },
            ].map((step, i) => (
              <div key={i} style={{
                background: 'var(--bg-primary)', padding: '48px 32px',
                position: 'relative', overflow: 'hidden',
              }}>
                <div style={{ fontFamily: 'JetBrains Mono', fontSize: 72, fontWeight: 700, color: 'var(--accent-dim2)', position: 'absolute', top: 16, right: 24, lineHeight: 1 }}>
                  {step.num}
                </div>
                <div style={{ fontSize: 32, marginBottom: 20 }}>{step.icon}</div>
                <h3 style={{ fontSize: 20, marginBottom: 12, letterSpacing: '-0.02em' }}>{step.title}</h3>
                <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7 }}>{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── ROLES ──────────────────────────────── */}
      <section ref={featRef} style={{ position: 'relative', zIndex: 1, padding: '100px 24px', borderTop: '1px solid var(--border)' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div style={{ marginBottom: 64 }}>
            <div style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--accent)', letterSpacing: '0.12em', marginBottom: 16 }}>
              SUPPORTED ROLES
            </div>
            <h2 style={{ fontSize: 'clamp(32px, 5vw, 56px)', letterSpacing: '-0.03em' }}>
              Five roles, 12 rules each
            </h2>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 1, background: 'var(--border)' }}>
            {[
              { role: 'Software Engineer', skills: ['Python', 'Java', 'SQL', 'Git', 'Docker', 'REST API'], threshold: '90%' },
              { role: 'Data Analyst', skills: ['SQL', 'Python', 'Pandas', 'Statistics', 'Excel', 'Tableau'], threshold: '90%' },
              { role: 'Web Developer', skills: ['HTML', 'CSS', 'JavaScript', 'React', 'Node.js', 'Git'], threshold: '90%' },
              { role: 'Cybersecurity Analyst', skills: ['Network Security', 'Linux', 'Pen Testing', 'OWASP', 'SIEM'], threshold: '90%' },
              { role: 'ML Engineer', skills: ['Python', 'scikit-learn', 'PyTorch', 'NumPy', 'Statistics', 'Git'], threshold: '90%' },
            ].map((r, i) => (
              <div key={i}
                style={{
                  background: 'var(--bg-primary)', padding: '28px 32px',
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  flexWrap: 'wrap', gap: 16,
                  transition: 'background 0.2s',
                  cursor: 'default',
                  opacity: featInView ? 1 : 0,
                  transform: featInView ? 'none' : 'translateY(20px)',
                  transition: `opacity 0.5s ${i * 0.08}s, transform 0.5s ${i * 0.08}s, background 0.2s`,
                }}
                onMouseEnter={e => (e.currentTarget.style.background = 'var(--bg-card)')}
                onMouseLeave={e => (e.currentTarget.style.background = 'var(--bg-primary)')}
              >
                <div>
                  <div style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: 18, marginBottom: 8 }}>{r.role}</div>
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    {r.skills.map(s => (
                      <span key={s} style={{
                        fontFamily: 'JetBrains Mono', fontSize: 11, padding: '3px 8px',
                        background: 'var(--accent-dim)', color: 'var(--accent)',
                        borderRadius: 4, letterSpacing: '0.04em',
                      }}>{s}</span>
                    ))}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div className="mono" style={{ fontSize: 28, fontWeight: 700, color: 'var(--accent)' }}>{r.threshold}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.06em' }}>PASS THRESHOLD</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ────────────────────────────────── */}
      <section style={{ position: 'relative', zIndex: 1, padding: '120px 24px', textAlign: 'center', borderTop: '1px solid var(--border)' }}>
        <div style={{ maxWidth: 700, margin: '0 auto' }}>
          <h2 style={{ fontSize: 'clamp(36px, 6vw, 72px)', letterSpacing: '-0.04em', marginBottom: 24 }}>
            Ready to find out<br />where you stand?
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 40, fontSize: 16, fontWeight: 300 }}>
            Upload your CV in seconds. Get a detailed AI evaluation report instantly.
          </p>
          <Link href="/apply">
            <button className="btn-accent" style={{ padding: '16px 48px', fontSize: 16 }}>
              Start Your Evaluation →
            </button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--border)', padding: '32px 24px', position: 'relative', zIndex: 1 }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
          <span style={{ fontFamily: 'Syne', fontWeight: 800, fontSize: 16, color: 'var(--text-primary)' }}>HireWise</span>
          <span style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--text-muted)' }}>
            BS CS AI Term Project — 2026
          </span>
        </div>
      </footer>
    </div>
  )
}

function ScorePreviewCard() {
  return (
    <div className="card" style={{ padding: 24, animation: 'float 6s ease-in-out infinite' }}>
      <div style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--text-muted)', marginBottom: 16, letterSpacing: '0.08em' }}>
        SAMPLE EVALUATION
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 20 }}>
        <div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 4 }}>Final Score</div>
          <div className="mono" style={{ fontSize: 48, fontWeight: 700, color: 'var(--accent)', lineHeight: 1 }}>86%</div>
        </div>
        <span className="badge-fail">REJECTED</span>
      </div>
      {[
        { label: 'Python 2yr', pass: true },
        { label: 'SQL', pass: true },
        { label: 'Git', pass: false },
        { label: 'Docker', pass: true },
        { label: 'Cloud (AWS)', pass: false },
      ].map((r, i) => (
        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border)', fontSize: 12 }}>
          <span style={{ color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono' }}>{r.label}</span>
          <span style={{ color: r.pass ? 'var(--success)' : 'var(--danger)' }}>{r.pass ? '✓' : '✗'}</span>
        </div>
      ))}
    </div>
  )
}
