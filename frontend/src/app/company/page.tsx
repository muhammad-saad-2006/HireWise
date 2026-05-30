'use client'
import { useState } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'

const ROLES = ['Software Engineer', 'Data Analyst', 'Web Developer', 'Cybersecurity Analyst', 'Machine Learning Engineer']

export default function CompanyPage() {
  const [form, setForm] = useState({ company_name: '', role_title: ROLES[0], description: '' })
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)

  const handleSubmit = async () => {
    if (!form.company_name) { toast.error('Company name required'); return }
    setLoading(true)
    try {
      await axios.post('/api/roles/create', form)
      setDone(true)
      toast.success('Job role posted successfully!')
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to post role')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ position: 'relative', minHeight: '100vh', padding: '60px 24px' }}>
      <div className="grid-bg" style={{ position: 'fixed', inset: 0, zIndex: 0, opacity: 0.4 }} />
      <div className="orb" style={{ width: 500, height: 500, background: 'rgba(251,191,36,0.05)', top: -100, left: -100 }} />

      <div style={{ maxWidth: 680, margin: '0 auto', position: 'relative', zIndex: 1 }}>

        <div style={{ marginBottom: 48 }}>
          <div style={{ fontFamily: 'JetBrains Mono', fontSize: 11, color: 'var(--accent)', letterSpacing: '0.12em', marginBottom: 12 }}>
            COMPANY PORTAL
          </div>
          <h1 style={{ fontSize: 40, letterSpacing: '-0.03em', marginBottom: 12 }}>Post a Job Role</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 15, fontWeight: 300 }}>
            Define the role and let HireWise automatically evaluate every candidate against your requirements.
          </p>
        </div>

        {done ? (
          <div className="card" style={{ padding: 48, textAlign: 'center', animation: 'countUp 0.4s ease' }}>
            <div style={{ fontSize: 48, marginBottom: 20 }}>✓</div>
            <h2 style={{ fontSize: 28, marginBottom: 12, letterSpacing: '-0.02em', color: 'var(--success)' }}>Role Posted!</h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 32, fontSize: 15 }}>
              <strong style={{ color: 'var(--text-primary)' }}>{form.role_title}</strong> at{' '}
              <strong style={{ color: 'var(--text-primary)' }}>{form.company_name}</strong> is now active.
            </p>
            <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
              <button className="btn-accent" onClick={() => { setDone(false); setForm({ company_name: '', role_title: ROLES[0], description: '' }) }}>
                Post Another Role
              </button>
            </div>
          </div>
        ) : (
          <div className="card" style={{ padding: 40, animation: 'countUp 0.4s ease' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

              <div>
                <label style={{ fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8, letterSpacing: '0.04em' }}>
                  COMPANY NAME *
                </label>
                <input className="input-field" placeholder="e.g. Systems Ltd." value={form.company_name}
                  onChange={e => setForm({ ...form, company_name: e.target.value })} />
              </div>

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

              <div>
                <label style={{ fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 8, letterSpacing: '0.04em' }}>
                  JOB DESCRIPTION (optional)
                </label>
                <textarea className="input-field" placeholder="Describe the role, responsibilities, and any additional requirements..."
                  rows={5} value={form.description}
                  onChange={e => setForm({ ...form, description: e.target.value })}
                  style={{ resize: 'vertical', lineHeight: 1.6 }} />
              </div>

              {/* Rule preview */}
              <div style={{ background: 'var(--bg-secondary)', borderRadius: 8, padding: 20 }}>
                <div style={{ fontFamily: 'JetBrains Mono', fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.08em', marginBottom: 12 }}>
                  AUTO-APPLIED RULES FOR {form.role_title.toUpperCase()}
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {getRoleRules(form.role_title).map(r => (
                    <span key={r} style={{ fontFamily: 'JetBrains Mono', fontSize: 11, padding: '3px 8px', background: 'var(--accent-dim)', color: 'var(--accent)', borderRadius: 4 }}>
                      {r}
                    </span>
                  ))}
                </div>
              </div>

              <button className="btn-accent" style={{ padding: 16, width: '100%' }}
                onClick={handleSubmit} disabled={loading}>
                {loading ? 'Posting...' : 'Post Role →'}
              </button>
            </div>
          </div>
        )}

        {/* Info cards */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 32 }}>
          {[
            { icon: '⚡', title: 'Instant Evaluation', desc: 'Every CV is scored automatically against your role requirements.' },
            { icon: '📊', title: 'Detailed Reports', desc: 'Candidates receive PDF reports with scores and improvement tips.' },
            { icon: '◎', title: 'Fuzzy Scoring', desc: 'Near-miss candidates get fair partial credit, not binary rejection.' },
            { icon: '✉', title: 'Auto Email', desc: 'Interview invites and rejection emails sent automatically.' },
          ].map((c, i) => (
            <div key={i} className="card" style={{ padding: 20 }}>
              <div style={{ fontSize: 24, marginBottom: 10 }}>{c.icon}</div>
              <div style={{ fontFamily: 'Syne', fontWeight: 600, fontSize: 14, marginBottom: 6 }}>{c.title}</div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{c.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function getRoleRules(role: string): string[] {
  const map: Record<string, string[]> = {
    'Software Engineer': ['Python 2yr', 'Java', 'SQL', 'Git', 'Docker', 'REST API', 'Linux', 'Cloud', 'Bachelor+', 'Exp 2yr', 'Projects 2+'],
    'Data Analyst': ['SQL 2yr', 'Python', 'Excel', 'Pandas', 'Statistics', 'Visualization', 'Data Wrangling', 'R', 'Bachelor+', 'Exp 1yr'],
    'Web Developer': ['HTML', 'CSS', 'JS 2yr', 'React', 'Node.js', 'Git', 'REST API', 'Projects 3+', 'Database', 'TypeScript'],
    'Cybersecurity Analyst': ['Network Sec', 'Linux', 'Python', 'Pen Testing', 'OWASP', 'SIEM', 'Cryptography', 'Bash', 'Exp 2yr', 'Certs'],
    'Machine Learning Engineer': ['Python 2yr', 'sklearn', 'PyTorch/TF', 'Pandas', 'NumPy', 'Statistics', 'NLP', 'Git', 'MLOps', 'Bachelor+'],
  }
  return map[role] || []
}
