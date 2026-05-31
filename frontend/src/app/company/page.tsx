'use client'
import { useState, useEffect } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'
import Link from 'next/link'

const ROLES = [
  'Software Engineer', 'Data Analyst', 'Web Developer',
  'Cybersecurity Analyst', 'Machine Learning Engineer'
]

// Human-readable labels for rule keys
const RULE_LABELS: Record<string, string> = {
  python_2yr: 'Python 2+ yrs', java: 'Java', javascript: 'JavaScript',
  sql: 'SQL', sql_2yr: 'SQL 2+ yrs', git: 'Git', docker: 'Docker',
  rest_api: 'REST API', linux: 'Linux', edu_bachelors: "Bachelor's+",
  edu_diploma: 'Diploma+', exp_2yr: 'Experience 2+ yrs', exp_1yr: 'Experience 1+ yr',
  projects_2: 'Projects 2+', projects_3: 'Projects 3+', projects_1: 'Projects 1+',
  cloud: 'Cloud (AWS/GCP/Azure)', react: 'React', nodejs: 'Node.js',
  typescript: 'TypeScript', html: 'HTML', css: 'CSS', js_2yr: 'JavaScript 2+ yrs',
  database: 'Database', excel: 'Excel', pandas: 'Pandas', statistics: 'Statistics',
  data_wrangling: 'Data Wrangling', visualization: 'Visualization', r_language: 'R Language',
  network_security: 'Network Security', pen_testing: 'Pen Testing',
  cryptography: 'Cryptography', siem: 'SIEM (Splunk)', vuln_assessment: 'Vulnerability Assessment',
  owasp: 'OWASP', bash: 'Bash Scripting', certifications: 'Security Certs',
  sklearn: 'scikit-learn', dl_framework: 'PyTorch / TensorFlow', numpy: 'NumPy',
  nlp: 'NLP', mlops: 'MLOps',
}

const ROLE_KEY_MAP: Record<string, string> = {
  'Software Engineer': 'software engineer',
  'Data Analyst': 'data analyst',
  'Web Developer': 'web developer',
  'Cybersecurity Analyst': 'cybersecurity analyst',
  'Machine Learning Engineer': 'machine learning engineer',
}

export default function CompanyPage() {
  const [tab, setTab] = useState<'post' | 'manage'>('post')
  const [form, setForm] = useState({
    company_name: '', role_title: ROLES[0],
    description: '', contact_email: '', custom_threshold: 75,
  })
  const [availableRules, setAvailableRules] = useState<string[]>([])
  const [disabledRules, setDisabledRules] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState<any>(null)
  const [companies, setCompanies] = useState<any[]>([])
  const [loadingCompanies, setLoadingCompanies] = useState(false)

  // Fetch rules when role changes
  useEffect(() => {
    const roleKey = ROLE_KEY_MAP[form.role_title]
    axios.get(`/api/companies/rules/${encodeURIComponent(roleKey)}`)
      .then(res => { setAvailableRules(res.data.rules || []); setDisabledRules([]) })
      .catch(() => setAvailableRules([]))
  }, [form.role_title])

  // Fetch companies for manage tab
  const fetchCompanies = async () => {
    setLoadingCompanies(true)
    try {
      const res = await axios.get('/api/companies')
      setCompanies(res.data.companies || [])
    } catch { setCompanies([]) }
    finally { setLoadingCompanies(false) }
  }

  useEffect(() => { if (tab === 'manage') fetchCompanies() }, [tab])

  const toggleRule = (rule: string) => {
    setDisabledRules(prev =>
      prev.includes(rule) ? prev.filter(r => r !== rule) : [...prev, rule]
    )
  }

  const handleSubmit = async () => {
    if (!form.company_name || !form.contact_email) {
      toast.error('Company name and contact email are required')
      return
    }
    setLoading(true)
    try {
      const res = await axios.post('/api/companies/create', {
        company_name: form.company_name,
        role_title: form.role_title,
        description: form.description,
        contact_email: form.contact_email,
        custom_threshold: form.custom_threshold / 100,
        disabled_rules: disabledRules,
      })
      setDone(res.data.company)
      toast.success('Company registered successfully!')
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to register company')
    } finally { setLoading(false) }
  }

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Remove "${name}" job posting?`)) return
    try {
      await axios.delete(`/api/companies/${id}`)
      toast.success('Job posting removed')
      fetchCompanies()
    } catch { toast.error('Failed to remove posting') }
  }

  return (
    <div style={{ position: 'relative', minHeight: '100vh', padding: '60px 24px' }}>
      <div className="grid-bg" style={{ position: 'fixed', inset: 0, zIndex: 0, opacity: 0.4 }} />
      <div className="orb" style={{ width: 500, height: 500, background: 'rgba(251,191,36,0.05)', top: -100, left: -100 }} />

      <div style={{ maxWidth: 760, margin: '0 auto', position: 'relative', zIndex: 1 }}>

        {/* Header */}
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--accent)', letterSpacing: '0.12em', marginBottom: 12 }}>
            COMPANY PORTAL
          </div>
          <h1 style={{ fontSize: 40, letterSpacing: '-0.03em', marginBottom: 12 }}>Company Dashboard</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 15, fontWeight: 300, maxWidth: 520 }}>
            Post job roles with custom requirements and thresholds. Manage your active listings.
          </p>
        </div>

        {/* Tab switcher */}
        <div style={{ display: 'flex', gap: 0, marginBottom: 32, border: '1px solid var(--border)', borderRadius: 8, overflow: 'hidden', width: 'fit-content' }}>
          {(['post', 'manage'] as const).map(t => (
            <button key={t} onClick={() => setTab(t)} style={{
              padding: '10px 28px', fontFamily: 'Syne', fontWeight: 700, fontSize: 13,
              letterSpacing: '0.05em', textTransform: 'uppercase', cursor: 'pointer', border: 'none',
              background: tab === t ? 'var(--accent)' : 'var(--bg-card)',
              color: tab === t ? '#0A0A0B' : 'var(--text-muted)',
              transition: 'all 0.2s',
            }}>
              {t === 'post' ? '+ Post Role' : '⚙ Manage'}
            </button>
          ))}
        </div>

        {/* ── POST TAB ── */}
        {tab === 'post' && (
          <>
            {done ? (
              <div className="card" style={{ padding: 48, textAlign: 'center', animation: 'countUp 0.4s ease' }}>
                <div style={{ width: 64, height: 64, background: 'var(--success-dim)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 28, margin: '0 auto 24px' }}>✓</div>
                <h2 style={{ fontSize: 28, marginBottom: 8, color: 'var(--success)' }}>Role Posted!</h2>
                <p style={{ color: 'var(--text-secondary)', marginBottom: 12, fontSize: 15 }}>
                  <strong style={{ color: 'var(--text-primary)' }}>
                    {done.role_title.split(' ').map((w: string) => w[0].toUpperCase() + w.slice(1)).join(' ')}
                  </strong>{' '}at{' '}
                  <strong style={{ color: 'var(--text-primary)' }}>{done.company_name}</strong>
                </p>
                <div style={{ display: 'inline-flex', gap: 24, background: 'var(--bg-secondary)', padding: '16px 32px', borderRadius: 8, marginBottom: 16 }}>
                  <div style={{ textAlign: 'center' }}>
                    <div className="mono" style={{ fontSize: 24, fontWeight: 700, color: 'var(--accent)' }}>{Math.round(done.threshold * 100)}%</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'Syne' }}>THRESHOLD</div>
                  </div>
                  <div style={{ width: 1, background: 'var(--border)' }} />
                  <div style={{ textAlign: 'center' }}>
                    <div className="mono" style={{ fontSize: 24, fontWeight: 700, color: 'var(--text-primary)' }}>#{done.id}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'Syne' }}>COMPANY ID</div>
                  </div>
                  <div style={{ width: 1, background: 'var(--border)' }} />
                  <div style={{ textAlign: 'center' }}>
                    <div className="mono" style={{ fontSize: 24, fontWeight: 700, color: 'var(--danger)' }}>
                      {done.disabled_rules?.length || 0}
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'Syne' }}>RULES REMOVED</div>
                  </div>
                </div>
                <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 32 }}>
                  Qualified candidates will notify you at{' '}
                  <strong style={{ color: 'var(--text-secondary)' }}>{done.contact_email}</strong>
                </p>
                <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
                  <button className="btn-accent" onClick={() => { setDone(null); setDisabledRules([]) }}>Post Another Role</button>
                  <button className="btn-ghost" onClick={() => setTab('manage')}>Manage Listings →</button>
                  <Link href="/apply"><button className="btn-ghost">View as Candidate →</button></Link>
                </div>
              </div>
            ) : (
              <div className="card" style={{ padding: 40 }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

                  {/* Company name */}
                  <div>
                    <label style={{ fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8, letterSpacing: '0.04em' }}>COMPANY NAME *</label>
                    <input className="input-field" placeholder="e.g. Systems Ltd." value={form.company_name}
                      onChange={e => setForm({ ...form, company_name: e.target.value })} />
                  </div>

                  {/* Contact email */}
                  <div>
                    <label style={{ fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8, letterSpacing: '0.04em' }}>
                      CONTACT EMAIL * <span style={{ color: 'var(--text-muted)', fontSize: 11, fontWeight: 400 }}>(qualified candidate notifications)</span>
                    </label>
                    <input className="input-field" type="email" placeholder="hr@company.com"
                      value={form.contact_email} onChange={e => setForm({ ...form, contact_email: e.target.value })} />
                  </div>

                  {/* Role */}
                  <div>
                    <label style={{ fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8, letterSpacing: '0.04em' }}>ROLE *</label>
                    <select className="input-field" value={form.role_title}
                      onChange={e => setForm({ ...form, role_title: e.target.value })}
                      style={{ appearance: 'none', cursor: 'pointer' }}>
                      {ROLES.map(r => <option key={r} value={r} style={{ background: 'var(--bg-card)' }}>{r}</option>)}
                    </select>
                  </div>

                  {/* Threshold slider */}
                  <div>
                    <label style={{ fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8, letterSpacing: '0.04em' }}>
                      PASS THRESHOLD — <span className="mono" style={{ color: 'var(--accent)', fontSize: 15 }}>{form.custom_threshold}%</span>
                      <span style={{ color: 'var(--text-muted)', fontSize: 11, fontWeight: 400, marginLeft: 8 }}>
                        (candidates scoring above this get interview invite)
                      </span>
                    </label>
                    <input type="range" min={50} max={95} step={5} value={form.custom_threshold}
                      onChange={e => setForm({ ...form, custom_threshold: parseInt(e.target.value) })}
                      style={{ width: '100%', accentColor: 'var(--accent)', cursor: 'pointer' }} />
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'JetBrains Mono', fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
                      <span>50% lenient</span><span>75% standard</span><span>95% strict</span>
                    </div>
                  </div>

                  {/* ── RULE CUSTOMIZATION ── */}
                  <div>
                    <label style={{ fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 4, letterSpacing: '0.04em' }}>
                      TECH REQUIREMENTS
                      <span style={{ color: 'var(--text-muted)', fontSize: 11, fontWeight: 400, marginLeft: 8 }}>
                        (toggle off requirements your role doesn't need)
                      </span>
                    </label>
                    <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 12 }}>
                      <span style={{ color: 'var(--success)', fontWeight: 600 }}>Green = required</span>
                      {' · '}
                      <span style={{ color: 'var(--danger)', fontWeight: 600 }}>Red = removed</span>
                      {disabledRules.length > 0 && ` · ${disabledRules.length} rule(s) removed`}
                    </p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                      {availableRules.map(rule => {
                        const isDisabled = disabledRules.includes(rule)
                        return (
                          <button key={rule} onClick={() => toggleRule(rule)} style={{
                            fontFamily: 'JetBrains Mono', fontSize: 11, padding: '6px 12px',
                            borderRadius: 6, cursor: 'pointer', border: 'none',
                            background: isDisabled ? 'var(--danger-dim)' : 'var(--success-dim)',
                            color: isDisabled ? 'var(--danger)' : 'var(--success)',
                            textDecoration: isDisabled ? 'line-through' : 'none',
                            transition: 'all 0.15s',
                            opacity: isDisabled ? 0.7 : 1,
                          }}>
                            {isDisabled ? '✗' : '✓'} {RULE_LABELS[rule] || rule}
                          </button>
                        )
                      })}
                    </div>
                  </div>

                  {/* Description */}
                  <div>
                    <label style={{ fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8, letterSpacing: '0.04em' }}>
                      JOB DESCRIPTION <span style={{ color: 'var(--text-muted)', fontSize: 11, fontWeight: 400 }}>(optional)</span>
                    </label>
                    <textarea className="input-field" placeholder="Describe the role and responsibilities..."
                      rows={4} value={form.description}
                      onChange={e => setForm({ ...form, description: e.target.value })}
                      style={{ resize: 'vertical', lineHeight: 1.6 }} />
                  </div>

                  <button className="btn-accent" style={{ padding: 16, width: '100%' }}
                    onClick={handleSubmit} disabled={loading}>
                    {loading ? 'Registering...' : 'Post Role →'}
                  </button>
                </div>
              </div>
            )}
          </>
        )}

        {/* ── MANAGE TAB ── */}
        {tab === 'manage' && (
          <div style={{ animation: 'countUp 0.4s ease' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <div style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--text-muted)', letterSpacing: '0.08em' }}>
                {companies.length} ACTIVE LISTING{companies.length !== 1 ? 'S' : ''}
              </div>
              <button className="btn-ghost" style={{ padding: '8px 16px', fontSize: 12 }} onClick={fetchCompanies}>
                ↻ Refresh
              </button>
            </div>

            {loadingCompanies ? (
              <div style={{ textAlign: 'center', padding: 60, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono' }}>
                Loading...
              </div>
            ) : companies.length === 0 ? (
              <div className="card" style={{ padding: 48, textAlign: 'center' }}>
                <div style={{ fontSize: 32, marginBottom: 16 }}>📋</div>
                <h3 style={{ fontSize: 20, marginBottom: 8 }}>No active listings</h3>
                <p style={{ color: 'var(--text-secondary)', marginBottom: 24, fontSize: 14 }}>
                  Post a job role to start receiving candidate applications.
                </p>
                <button className="btn-accent" onClick={() => setTab('post')}>Post a Role →</button>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {companies.map((c: any) => (
                  <div key={c.id} className="card" style={{ padding: '24px 28px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16 }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                          <h3 style={{ fontSize: 18, letterSpacing: '-0.02em' }}>{c.company_name}</h3>
                          <span style={{ fontFamily: 'JetBrains Mono', fontSize: 10, padding: '3px 8px', background: 'var(--accent-dim)', color: 'var(--accent)', borderRadius: 4 }}>
                            #{c.id}
                          </span>
                        </div>
                        <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12 }}>
                          {c.role_title.split(' ').map((w: string) => w[0].toUpperCase() + w.slice(1)).join(' ')}
                          {c.description && ` — ${c.description}`}
                        </div>
                        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                          <span style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--accent)' }}>
                            Threshold: {Math.round(c.threshold * 100)}%
                          </span>
                          <span style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--text-muted)' }}>
                            {c.contact_email}
                          </span>
                          {c.disabled_rules?.length > 0 && (
                            <span style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--danger)' }}>
                              {c.disabled_rules.length} rule(s) removed
                            </span>
                          )}
                        </div>
                        {c.disabled_rules?.length > 0 && (
                          <div style={{ marginTop: 10, display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                            {c.disabled_rules.map((r: string) => (
                              <span key={r} style={{ fontFamily: 'JetBrains Mono', fontSize: 10, padding: '2px 8px', background: 'var(--danger-dim)', color: 'var(--danger)', borderRadius: 4, textDecoration: 'line-through' }}>
                                {RULE_LABELS[r] || r}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <button onClick={() => handleDelete(c.id, c.company_name)} style={{
                        background: 'var(--danger-dim)', border: '1px solid rgba(248,113,113,0.2)',
                        color: 'var(--danger)', borderRadius: 8, padding: '8px 16px',
                        cursor: 'pointer', fontFamily: 'Syne', fontWeight: 600, fontSize: 12,
                        flexShrink: 0, transition: 'background 0.2s',
                      }}
                        onMouseEnter={e => (e.currentTarget.style.background = 'rgba(248,113,113,0.25)')}
                        onMouseLeave={e => (e.currentTarget.style.background = 'var(--danger-dim)')}>
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}