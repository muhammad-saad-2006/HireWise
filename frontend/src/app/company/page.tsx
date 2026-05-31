'use client'
import { useState } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'
import Link from 'next/link'

const ROLES = [
  'Software Engineer', 'Data Analyst', 'Web Developer',
  'Cybersecurity Analyst', 'Machine Learning Engineer'
]

const ROLE_RULES: Record<string, string[]> = {
  'Software Engineer':         ['Python 2yr', 'Java', 'SQL', 'Git', 'Docker', 'REST API', 'Linux', 'Cloud', 'Bachelors+', 'Exp 2yr', 'Projects 2+'],
  'Data Analyst':              ['SQL 2yr', 'Python', 'Excel', 'Pandas', 'Statistics', 'Visualization', 'Data Wrangling', 'Bachelors+', 'Exp 1yr'],
  'Web Developer':             ['HTML', 'CSS', 'JS 2yr', 'React', 'Node.js', 'Git', 'REST API', 'Projects 3+', 'TypeScript'],
  'Cybersecurity Analyst':     ['Network Sec', 'Linux', 'Python', 'Pen Testing', 'OWASP', 'SIEM', 'Cryptography', 'Bash', 'Exp 2yr'],
  'Machine Learning Engineer': ['Python 2yr', 'sklearn', 'PyTorch/TF', 'Pandas', 'NumPy', 'Statistics', 'NLP', 'Git', 'MLOps'],
}

export default function CompanyPage() {
  const [form, setForm] = useState({
    company_name: '',
    role_title: ROLES[0],
    description: '',
    contact_email: '',
    custom_threshold: 75,
  })
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState<any>(null)

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
      })
      setDone(res.data.company)
      toast.success('Company registered successfully!')
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to register company')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ position: 'relative', minHeight: '100vh', padding: '60px 24px' }}>
      <div className="grid-bg" style={{ position: 'fixed', inset: 0, zIndex: 0, opacity: 0.4 }} />
      <div className="orb" style={{ width: 500, height: 500, background: 'rgba(251,191,36,0.05)', top: -100, left: -100 }} />

      <div style={{ maxWidth: 720, margin: '0 auto', position: 'relative', zIndex: 1 }}>

        <div style={{ marginBottom: 48 }}>
          <div style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--accent)', letterSpacing: '0.12em', marginBottom: 12 }}>
            COMPANY PORTAL
          </div>
          <h1 style={{ fontSize: 40, letterSpacing: '-0.03em', marginBottom: 12 }}>Post a Job Role</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 15, fontWeight: 300, maxWidth: 520 }}>
            Register your company and define the role. Candidates will find your listing and apply directly.
            You will receive an email for every qualified candidate that passes your threshold.
          </p>
        </div>

        {done ? (
          <div className="card" style={{ padding: 48, textAlign: 'center', animation: 'countUp 0.4s ease' }}>
            <div style={{ width: 64, height: 64, background: 'var(--success-dim)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 28, margin: '0 auto 24px' }}>✓</div>
            <h2 style={{ fontSize: 28, marginBottom: 8, letterSpacing: '-0.02em', color: 'var(--success)' }}>
              Role Posted!
            </h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 12, fontSize: 15 }}>
              <strong style={{ color: 'var(--text-primary)' }}>{done.role_title.split(' ').map((w: string) => w[0].toUpperCase() + w.slice(1)).join(' ')}</strong>
              {' '}at{' '}
              <strong style={{ color: 'var(--text-primary)' }}>{done.company_name}</strong>
            </p>
            <div style={{ display: 'inline-flex', gap: 24, background: 'var(--bg-secondary)', padding: '16px 32px', borderRadius: 8, marginBottom: 32 }}>
              <div style={{ textAlign: 'center' }}>
                <div className="mono" style={{ fontSize: 24, fontWeight: 700, color: 'var(--accent)' }}>
                  {Math.round(done.threshold * 100)}%
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'Syne', letterSpacing: '0.04em' }}>THRESHOLD</div>
              </div>
              <div style={{ width: 1, background: 'var(--border)' }} />
              <div style={{ textAlign: 'center' }}>
                <div className="mono" style={{ fontSize: 24, fontWeight: 700, color: 'var(--text-primary)' }}>#{done.id}</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'Syne', letterSpacing: '0.04em' }}>COMPANY ID</div>
              </div>
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 32 }}>
              Qualified candidates will be notified by email and you will receive a notification at{' '}
              <strong style={{ color: 'var(--text-secondary)' }}>{done.contact_email}</strong>
            </p>
            <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
              <button className="btn-accent" onClick={() => { setDone(null); setForm({ company_name: '', role_title: ROLES[0], description: '', contact_email: '', custom_threshold: 75 }) }}>
                Post Another Role
              </button>
              <Link href="/apply">
                <button className="btn-ghost">View as Candidate →</button>
              </Link>
            </div>
          </div>
        ) : (
          <div className="card" style={{ padding: 40, animation: 'countUp 0.4s ease' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

              {/* Company name */}
              <div>
                <label style={{ fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8, letterSpacing: '0.04em' }}>
                  COMPANY NAME *
                </label>
                <input className="input-field" placeholder="e.g. Systems Ltd."
                  value={form.company_name} onChange={e => setForm({ ...form, company_name: e.target.value })} />
              </div>

              {/* Contact email */}
              <div>
                <label style={{ fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8, letterSpacing: '0.04em' }}>
                  CONTACT EMAIL * <span style={{ color: 'var(--text-muted)', fontSize: 11, fontWeight: 400 }}>(you will receive qualified candidate notifications here)</span>
                </label>
                <input className="input-field" type="email" placeholder="hr@company.com"
                  value={form.contact_email} onChange={e => setForm({ ...form, contact_email: e.target.value })} />
              </div>

              {/* Role */}
              <div>
                <label style={{ fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8, letterSpacing: '0.04em' }}>
                  ROLE *
                </label>
                <select className="input-field" value={form.role_title}
                  onChange={e => setForm({ ...form, role_title: e.target.value })}
                  style={{ appearance: 'none', cursor: 'pointer' }}>
                  {ROLES.map(r => <option key={r} value={r} style={{ background: 'var(--bg-card)' }}>{r}</option>)}
                </select>
              </div>

              {/* Custom threshold */}
              <div>
                <label style={{ fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8, letterSpacing: '0.04em' }}>
                  PASS THRESHOLD — <span className="mono" style={{ color: 'var(--accent)', fontSize: 15 }}>{form.custom_threshold}%</span>
                  <span style={{ color: 'var(--text-muted)', fontSize: 11, fontWeight: 400, marginLeft: 8 }}>
                    (candidates scoring above this are invited for interview)
                  </span>
                </label>
                <input type="range" min={50} max={95} step={5} value={form.custom_threshold}
                  onChange={e => setForm({ ...form, custom_threshold: parseInt(e.target.value) })}
                  style={{ width: '100%', accentColor: 'var(--accent)', cursor: 'pointer' }} />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'JetBrains Mono', fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
                  <span>50% (lenient)</span>
                  <span>75% (standard)</span>
                  <span>95% (strict)</span>
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

              {/* Rules preview */}
              <div style={{ background: 'var(--bg-secondary)', borderRadius: 8, padding: 20 }}>
                <div style={{ fontFamily: 'JetBrains Mono', fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.08em', marginBottom: 12 }}>
                  AUTO-APPLIED EVALUATION RULES
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {(ROLE_RULES[form.role_title] || []).map(r => (
                    <span key={r} style={{ fontFamily: 'JetBrains Mono', fontSize: 11, padding: '3px 8px', background: 'var(--accent-dim)', color: 'var(--accent)', borderRadius: 4 }}>
                      {r}
                    </span>
                  ))}
                </div>
                <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 12 }}>
                  These rules are evaluated automatically for every candidate CV submitted to your role.
                </p>
              </div>

              <button className="btn-accent" style={{ padding: 16, width: '100%' }}
                onClick={handleSubmit} disabled={loading}>
                {loading ? 'Registering...' : 'Post Role →'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}