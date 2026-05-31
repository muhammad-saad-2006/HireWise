'use client'
import { useState, useCallback, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import axios from 'axios'

const ROLES = [
  'software engineer', 'data analyst', 'web developer',
  'cybersecurity analyst', 'machine learning engineer',
]

const STEPS = ['Select Role', 'Choose Company', 'Upload CV', 'Your Info', 'Processing']

export default function ApplyPage() {
  const router = useRouter()
  const [step, setStep] = useState(0)
  const [role, setRole] = useState('')
  const [companies, setCompanies] = useState<any[]>([])
  const [selectedCompany, setSelectedCompany] = useState<any>(null)
  const [file, setFile] = useState<File | null>(null)
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [progressLabel, setProgressLabel] = useState('')
  const [loadingCompanies, setLoadingCompanies] = useState(false)

  const fetchCompanies = async (r: string) => {
    setLoadingCompanies(true)
    try {
      const res = await axios.get(`/api/companies/role/${encodeURIComponent(r)}`)
      setCompanies(res.data.companies || [])
    } catch {
      setCompanies([])
    } finally {
      setLoadingCompanies(false)
    }
  }

  const handleRoleSelect = (r: string) => {
    setRole(r)
    fetchCompanies(r)
    setStep(1)
  }

  const handleCompanySelect = (c: any) => {
    setSelectedCompany(c)
    setStep(2)
  }

  const handleSkipCompany = () => {
    setSelectedCompany(null)
    setStep(2)
  }

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted[0]) { setFile(accepted[0]); setTimeout(() => setStep(3), 300) }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'application/pdf': ['.pdf'] }, maxFiles: 1,
  })

  const handleSubmit = async () => {
    if (!file || !email) { toast.error('Please fill all fields'); return }
    setLoading(true)
    setStep(4)

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

      let url = `/api/apply?role_title=${encodeURIComponent(role)}&candidate_email=${encodeURIComponent(email)}`
      if (selectedCompany) url += `&company_id=${selectedCompany.id}`

      const res = await axios.post(url, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      clearInterval(interval)
      setProgress(100)
      setProgressLabel('Complete!')
      setTimeout(() => {
        router.push('/results?data=' + encodeURIComponent(JSON.stringify(res.data)))
      }, 800)
    } catch (err: any) {
      clearInterval(interval)
      setLoading(false)
      setStep(3)
      toast.error(err?.response?.data?.detail || 'Evaluation failed. Please try again.')
    }
  }

  return (
    <div style={{ position: 'relative', minHeight: '100vh', padding: '60px 24px' }}>
      <div className="grid-bg" style={{ position: 'fixed', inset: 0, zIndex: 0, opacity: 0.4 }} />
      <div className="orb" style={{ width: 500, height: 500, background: 'rgba(251,191,36,0.05)', top: 0, right: 0 }} />

      <div style={{ maxWidth: 720, margin: '0 auto', position: 'relative', zIndex: 1 }}>

        {/* Header */}
        <div style={{ marginBottom: 40 }}>
          <div style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--accent)', letterSpacing: '0.12em', marginBottom: 12 }}>
            CANDIDATE PORTAL
          </div>
          <h1 style={{ fontSize: 40, letterSpacing: '-0.03em', marginBottom: 8 }}>Apply for a Role</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 15, fontWeight: 300 }}>
            Choose a role, pick a company, and upload your CV for an instant AI evaluation.
          </p>
        </div>

        {/* Step indicator */}
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 40, flexWrap: 'wrap', gap: 4 }}>
          {STEPS.slice(0, 4).map((s, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{
                  width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
                  border: `2px solid ${i < step ? 'var(--accent)' : i === step ? 'var(--accent)' : 'var(--text-muted)'}`,
                  background: i < step ? 'var(--accent)' : 'transparent',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: 'JetBrains Mono', fontSize: 11, fontWeight: 700,
                  color: i < step ? '#0A0A0B' : i === step ? 'var(--accent)' : 'var(--text-muted)',
                  transition: 'all 0.3s',
                }}>
                  {i < step ? '✓' : i + 1}
                </div>
                <span style={{ fontSize: 12, fontFamily: 'Syne', fontWeight: 600, color: i === step ? 'var(--text-primary)' : 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                  {s}
                </span>
              </div>
              {i < 3 && <div style={{ width: 24, height: 1, background: i < step ? 'var(--accent)' : 'var(--border)', margin: '0 8px', transition: 'background 0.3s' }} />}
            </div>
          ))}
        </div>

        {/* ── STEP 0: Select Role ── */}
        {step === 0 && (
          <div style={{ animation: 'countUp 0.4s ease' }}>
            <div style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.08em', marginBottom: 20 }}>
              WHICH ROLE ARE YOU APPLYING FOR?
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {ROLES.map(r => (
                <button key={r} onClick={() => handleRoleSelect(r)} style={{
                  background: 'var(--bg-card)', border: '1px solid var(--border)',
                  borderRadius: 10, padding: '20px 24px', cursor: 'pointer',
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  transition: 'border-color 0.2s, background 0.2s', textAlign: 'left',
                }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent)'; e.currentTarget.style.background = 'var(--accent-dim)' }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.background = 'var(--bg-card)' }}
                >
                  <span style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: 17 }}>
                    {r.split(' ').map(w => w[0].toUpperCase() + w.slice(1)).join(' ')}
                  </span>
                  <span style={{ color: 'var(--accent)', fontSize: 18 }}>→</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* ── STEP 1: Choose Company ── */}
        {step === 1 && (
          <div style={{ animation: 'countUp 0.4s ease' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
              <div style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.08em' }}>
                COMPANIES HIRING FOR {role.toUpperCase()}
              </div>
              <button onClick={() => setStep(0)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 13, fontFamily: 'Syne' }}>
                ← Change Role
              </button>
            </div>

            {loadingCompanies ? (
              <div style={{ textAlign: 'center', padding: 60, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono', fontSize: 13 }}>
                Loading companies...
              </div>
            ) : companies.length === 0 ? (
              <div className="card" style={{ padding: 48, textAlign: 'center' }}>
                <div style={{ fontSize: 32, marginBottom: 16 }}>🔍</div>
                <h3 style={{ fontSize: 20, marginBottom: 8 }}>No companies listed yet</h3>
                <p style={{ color: 'var(--text-secondary)', marginBottom: 24, fontSize: 14 }}>
                  No companies are currently hiring for this role. You can still evaluate your CV independently.
                </p>
                <button className="btn-accent" onClick={handleSkipCompany}>
                  Evaluate CV Independently →
                </button>
              </div>
            ) : (
              <>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 16 }}>
                  {companies.map((c: any) => (
                    <button key={c.id} onClick={() => handleCompanySelect(c)} style={{
                      background: 'var(--bg-card)', border: '1px solid var(--border)',
                      borderRadius: 12, padding: '20px 24px', cursor: 'pointer',
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                      transition: 'border-color 0.2s, background 0.2s', textAlign: 'left', width: '100%',
                    }}
                      onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent)'; e.currentTarget.style.background = 'var(--accent-dim)' }}
                      onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.background = 'var(--bg-card)' }}
                    >
                      <div>
                        <div style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: 18, marginBottom: 6 }}>{c.company_name}</div>
                        <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                          {c.description || 'No description provided.'}
                        </div>
                      </div>
                      <div style={{ textAlign: 'right', marginLeft: 20, flexShrink: 0 }}>
                        <div className="mono" style={{ fontSize: 22, fontWeight: 700, color: 'var(--accent)' }}>
                          {Math.round(c.threshold * 100)}%
                        </div>
                        <div style={{ fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.06em', fontFamily: 'Syne' }}>
                          THRESHOLD
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
                <button className="btn-ghost" style={{ width: '100%' }} onClick={handleSkipCompany}>
                  Evaluate CV Without Applying to a Company
                </button>
              </>
            )}
          </div>
        )}

        {/* ── STEP 2: Upload CV ── */}
        {step === 2 && (
          <div style={{ animation: 'countUp 0.4s ease' }}>
            {selectedCompany && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24, padding: '14px 20px', background: 'var(--accent-dim)', border: '1px solid var(--accent)', borderRadius: 10 }}>
                <span style={{ color: 'var(--accent)', fontSize: 18 }}>🏢</span>
                <div>
                  <div style={{ fontFamily: 'Syne', fontWeight: 700, fontSize: 15 }}>Applying to: {selectedCompany.company_name}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Pass threshold: {Math.round(selectedCompany.threshold * 100)}%</div>
                </div>
                <button onClick={() => setStep(1)} style={{ marginLeft: 'auto', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 18 }}>×</button>
              </div>
            )}

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
                or click to browse — PDF only
              </p>
              <button className="btn-ghost" style={{ pointerEvents: 'none' }}>Choose File</button>
            </div>
          </div>
        )}

        {/* ── STEP 3: Info + Submit ── */}
        {step === 3 && (
          <div style={{ animation: 'countUp 0.4s ease' }}>
            {/* File confirmed */}
            <div className="card" style={{ padding: '14px 20px', marginBottom: 24, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ width: 36, height: 36, background: 'var(--success-dim)', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--success)', fontSize: 16 }}>✓</div>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 500 }}>{file?.name}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{((file?.size || 0) / 1024).toFixed(0)} KB</div>
                </div>
              </div>
              <button onClick={() => { setFile(null); setStep(2) }} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 20 }}>×</button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <div>
                <label style={{ fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8, letterSpacing: '0.04em' }}>
                  YOUR EMAIL ADDRESS
                </label>
                <input className="input-field" type="email" placeholder="you@example.com"
                  value={email} onChange={e => setEmail(e.target.value)} />
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6 }}>
                  {selectedCompany
                    ? 'Your result email (interview invite or rejection with PDF) will be sent here.'
                    : 'Your evaluation result will be sent to this email.'
                  }
                </div>
              </div>

              {/* Summary */}
              <div style={{ background: 'var(--bg-secondary)', borderRadius: 8, padding: 20 }}>
                <div style={{ fontFamily: 'JetBrains Mono', fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.08em', marginBottom: 12 }}>
                  EVALUATION SUMMARY
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {[
                    ['Role', role.split(' ').map(w => w[0].toUpperCase() + w.slice(1)).join(' ')],
                    ['Company', selectedCompany ? selectedCompany.company_name : 'Independent (no company)'],
                    ['Threshold', selectedCompany ? `${Math.round(selectedCompany.threshold * 100)}%` : '75%'],
                    ['File', file?.name || '-'],
                  ].map(([k, v]) => (
                    <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
                      <span style={{ color: 'var(--text-muted)' }}>{k}</span>
                      <span style={{ fontFamily: 'JetBrains Mono', color: 'var(--text-primary)', fontSize: 12 }}>{v}</span>
                    </div>
                  ))}
                </div>
              </div>

              <button className="btn-accent" style={{ width: '100%', padding: 16, fontSize: 14 }}
                onClick={handleSubmit} disabled={!email || loading}>
                Run Evaluation →
              </button>
            </div>
          </div>
        )}

        {/* ── STEP 4: Processing ── */}
        {step === 4 && (
          <div style={{ animation: 'countUp 0.4s ease' }}>
            <div className="card" style={{ padding: 48, textAlign: 'center' }}>
              <div style={{ position: 'relative', width: 120, height: 120, margin: '0 auto 32px' }}>
                <svg viewBox="0 0 120 120" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
                  <circle cx="60" cy="60" r="50" fill="none" stroke="var(--border)" strokeWidth="6" />
                  <circle cx="60" cy="60" r="50" fill="none" stroke="var(--accent)" strokeWidth="6"
                    strokeDasharray={314} strokeDashoffset={314 - (314 * progress) / 100}
                    strokeLinecap="round" style={{ transition: 'stroke-dashoffset 0.5s ease' }} />
                </svg>
                <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <span className="mono" style={{ fontSize: 22, fontWeight: 700, color: 'var(--accent)' }}>{progress}%</span>
                </div>
              </div>
              <h3 style={{ fontSize: 22, marginBottom: 8 }}>Analysing your profile</h3>
              <p style={{ color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono', fontSize: 13 }}>{progressLabel}</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 32, textAlign: 'left' }}>
                {['CV Parsing', 'Expert Rules', 'Fuzzy Scoring', 'RAG Tips', 'PDF Report'].map((s, i) => {
                  const thresholds = [15, 55, 70, 85, 95]
                  const done = progress >= thresholds[i]
                  const active = progress >= (thresholds[i - 1] ?? 0) && !done
                  return (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 16px', borderRadius: 8, background: done ? 'var(--success-dim)' : active ? 'var(--accent-dim)' : 'var(--bg-secondary)', transition: 'background 0.3s' }}>
                      <span style={{ color: done ? 'var(--success)' : active ? 'var(--accent)' : 'var(--text-muted)', width: 20, textAlign: 'center' }}>
                        {done ? '✓' : active ? '◎' : '○'}
                      </span>
                      <span style={{ fontSize: 13, fontFamily: 'JetBrains Mono', color: done ? 'var(--success)' : active ? 'var(--accent)' : 'var(--text-muted)' }}>
                        {s}
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