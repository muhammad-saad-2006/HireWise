'use client'
import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import axios from 'axios'

const ROLES = [
  'software engineer',
  'data analyst',
  'web developer',
  'cybersecurity analyst',
  'machine learning engineer',
]

const STEPS = ['Upload CV', 'Your Info', 'Submit']

export default function ApplyPage() {
  const router = useRouter()
  const [step, setStep] = useState(0)
  const [file, setFile] = useState<File | null>(null)
  const [email, setEmail] = useState('')
  const [role, setRole] = useState(ROLES[0])
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [progressLabel, setProgressLabel] = useState('')

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted[0]) {
      setFile(accepted[0])
      setTimeout(() => setStep(1), 400)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
  })

  const handleSubmit = async () => {
    if (!file || !email) { toast.error('Please fill all fields'); return }
    setLoading(true)
    setStep(2)

    const stages = [
      [15, 'Parsing your CV...'],
      [35, 'Extracting skills & experience...'],
      [55, 'Running expert system rules...'],
      [70, 'Applying fuzzy scoring...'],
      [85, 'Generating improvement tips...'],
      [95, 'Building your PDF report...'],
    ]

    let si = 0
    const interval = setInterval(() => {
      if (si < stages.length) {
        setProgress(stages[si][0] as number)
        setProgressLabel(stages[si][1] as string)
        si++
      }
    }, 900)

    try {
      const fd = new FormData()
      fd.append('cv_file', file)

      const res = await axios.post(
        `/api/apply?role_title=${encodeURIComponent(role)}&candidate_email=${encodeURIComponent(email)}`,
        fd,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )

      clearInterval(interval)
      setProgress(100)
      setProgressLabel('Complete!')
      setTimeout(() => {
        router.push('/results?data=' + encodeURIComponent(JSON.stringify(res.data)))
      }, 800)
    } catch (err: any) {
      clearInterval(interval)
      setLoading(false)
      setStep(1)
      toast.error(err?.response?.data?.detail || 'Evaluation failed. Please try again.')
    }
  }

  return (
    <div style={{ position: 'relative', minHeight: '100vh', padding: '60px 24px' }}>
      <div className="grid-bg" style={{ position: 'fixed', inset: 0, zIndex: 0, opacity: 0.4 }} />
      <div className="orb" style={{ width: 500, height: 500, background: 'rgba(251,191,36,0.05)', top: 0, right: 0 }} />

      <div style={{ maxWidth: 680, margin: '0 auto', position: 'relative', zIndex: 1 }}>

        {/* Page header */}
        <div style={{ marginBottom: 48 }}>
          <div style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--accent)', letterSpacing: '0.12em', marginBottom: 12 }}>
            CANDIDATE PORTAL
          </div>
          <h1 style={{ fontSize: 40, letterSpacing: '-0.03em', marginBottom: 12 }}>
            Evaluate your CV
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 15, fontWeight: 300 }}>
            Get an instant AI-powered score with detailed feedback in under 30 seconds.
          </p>
        </div>

        {/* Step indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 0, marginBottom: 48 }}>
          {STEPS.map((s, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{
                  width: 32, height: 32, borderRadius: '50%',
                  border: `2px solid ${i < step ? 'var(--accent)' : i === step ? 'var(--accent)' : 'var(--text-muted)'}`,
                  background: i < step ? 'var(--accent)' : 'transparent',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: 'JetBrains Mono', fontSize: 12, fontWeight: 700,
                  color: i < step ? '#0A0A0B' : i === step ? 'var(--accent)' : 'var(--text-muted)',
                  transition: 'all 0.3s',
                  flexShrink: 0,
                }}>
                  {i < step ? '✓' : i + 1}
                </div>
                <span style={{ fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: i === step ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                  {s}
                </span>
              </div>
              {i < STEPS.length - 1 && (
                <div style={{ width: 40, height: 1, background: i < step ? 'var(--accent)' : 'var(--border)', margin: '0 12px', transition: 'background 0.3s' }} />
              )}
            </div>
          ))}
        </div>

        {/* Step 0 — Upload CV */}
        {step === 0 && (
          <div style={{ animation: 'countUp 0.4s ease' }}>
            <div {...getRootProps()} style={{
              border: `2px dashed ${isDragActive ? 'var(--accent)' : 'var(--border)'}`,
              borderRadius: 16, padding: '80px 40px', textAlign: 'center',
              background: isDragActive ? 'var(--accent-dim)' : 'var(--bg-card)',
              cursor: 'pointer', transition: 'all 0.2s',
            }}>
              <input {...getInputProps()} />
              <div style={{ fontSize: 48, marginBottom: 20 }}>📄</div>
              <h3 style={{ fontSize: 20, marginBottom: 8, letterSpacing: '-0.02em' }}>
                {isDragActive ? 'Drop it here' : 'Drop your CV here'}
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginBottom: 20 }}>
                or click to browse — PDF only, max 10MB
              </p>
              <button className="btn-ghost" style={{ pointerEvents: 'none' }}>
                Choose File
              </button>
            </div>
          </div>
        )}

        {/* Step 1 — Info form */}
        {step === 1 && (
          <div style={{ animation: 'countUp 0.4s ease' }}>
            {/* File confirmed */}
            <div className="card" style={{ padding: '16px 20px', marginBottom: 24, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ width: 36, height: 36, background: 'var(--success-dim)', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--success)', fontSize: 18 }}>✓</div>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 500 }}>{file?.name}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{((file?.size || 0) / 1024).toFixed(0)} KB</div>
                </div>
              </div>
              <button onClick={() => { setFile(null); setStep(0) }} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 18 }}>×</button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <div>
                <label style={{ fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8, letterSpacing: '0.04em' }}>
                  EMAIL ADDRESS
                </label>
                <input
                  className="input-field"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                />
              </div>

              <div>
                <label style={{ fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8, letterSpacing: '0.04em' }}>
                  TARGET ROLE
                </label>
                <select className="input-field" value={role} onChange={e => setRole(e.target.value)}
                  style={{ appearance: 'none', cursor: 'pointer' }}>
                  {ROLES.map(r => (
                    <option key={r} value={r} style={{ background: 'var(--bg-card)', textTransform: 'capitalize' }}>
                      {r.split(' ').map(w => w[0].toUpperCase() + w.slice(1)).join(' ')}
                    </option>
                  ))}
                </select>
              </div>

              <button
                className="btn-accent"
                style={{ width: '100%', padding: 16, fontSize: 14, marginTop: 8 }}
                onClick={handleSubmit}
                disabled={!email || loading}
              >
                Run Evaluation →
              </button>
            </div>
          </div>
        )}

        {/* Step 2 — Processing */}
        {step === 2 && (
          <div style={{ animation: 'countUp 0.4s ease' }}>
            <div className="card" style={{ padding: 48, textAlign: 'center' }}>
              {/* Spinning ring */}
              <div style={{ position: 'relative', width: 120, height: 120, margin: '0 auto 32px' }}>
                <svg viewBox="0 0 120 120" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
                  <circle cx="60" cy="60" r="50" fill="none" stroke="var(--border)" strokeWidth="6" />
                  <circle cx="60" cy="60" r="50" fill="none" stroke="var(--accent)" strokeWidth="6"
                    strokeDasharray={314}
                    strokeDashoffset={314 - (314 * progress) / 100}
                    strokeLinecap="round"
                    style={{ transition: 'stroke-dashoffset 0.5s ease' }}
                  />
                </svg>
                <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <span className="mono" style={{ fontSize: 22, fontWeight: 700, color: 'var(--accent)' }}>{progress}%</span>
                </div>
              </div>

              <h3 style={{ fontSize: 22, marginBottom: 8, letterSpacing: '-0.02em' }}>Analysing your profile</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: 14, fontFamily: 'JetBrains Mono' }}>{progressLabel}</p>

              {/* Stage indicators */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 32, textAlign: 'left' }}>
                {['CV Parsing', 'Expert Rules', 'Fuzzy Scoring', 'RAG Tips', 'PDF Report'].map((stage, i) => {
                  const threshold = [15, 55, 70, 85, 95]
                  const done = progress >= threshold[i]
                  const active = progress >= (threshold[i - 1] ?? 0) && !done
                  return (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 16px', borderRadius: 8, background: done ? 'var(--success-dim)' : active ? 'var(--accent-dim)' : 'var(--bg-secondary)', transition: 'background 0.3s' }}>
                      <span style={{ color: done ? 'var(--success)' : active ? 'var(--accent)' : 'var(--text-muted)', fontSize: 14, width: 20, textAlign: 'center' }}>
                        {done ? '✓' : active ? '◎' : '○'}
                      </span>
                      <span style={{ fontSize: 13, fontFamily: 'JetBrains Mono', color: done ? 'var(--success)' : active ? 'var(--accent)' : 'var(--text-muted)' }}>
                        {stage}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
