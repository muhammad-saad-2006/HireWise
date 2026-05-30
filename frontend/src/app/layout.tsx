'use client'
import './globals.css'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import { Toaster } from 'react-hot-toast'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [light, setLight] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    document.body.classList.toggle('light-mode', light)
  }, [light])

  return (
    <html lang="en">
      <head>
        <title>HireWise — AI Recruitment</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>
        <Toaster position="top-right" toastOptions={{
          style: {
            background: 'var(--bg-card)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border)',
            fontFamily: 'Epilogue, sans-serif',
          }
        }} />

        <nav>
          <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px', height: 60, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            {/* Logo */}
            <Link href="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 28, height: 28, background: 'var(--accent)', borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ fontFamily: 'Syne', fontWeight: 800, fontSize: 14, color: '#0A0A0B' }}>H</span>
              </div>
              <span style={{ fontFamily: 'Syne', fontWeight: 800, fontSize: 18, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>HireWise</span>
            </Link>

            {/* Nav links */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Link href="/apply" style={{ textDecoration: 'none', padding: '8px 16px', borderRadius: 8, fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-secondary)', transition: 'color 0.2s' }}
                onMouseEnter={e => (e.currentTarget.style.color = 'var(--accent)')}
                onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-secondary)')}>
                Apply
              </Link>
              <Link href="/company" style={{ textDecoration: 'none', padding: '8px 16px', borderRadius: 8, fontSize: 13, fontFamily: 'Syne', fontWeight: 600, color: 'var(--text-secondary)', transition: 'color 0.2s' }}
                onMouseEnter={e => (e.currentTarget.style.color = 'var(--accent)')}
                onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-secondary)')}>
                Companies
              </Link>

              {/* Theme toggle */}
              <button onClick={() => setLight(!light)} style={{
                marginLeft: 8, width: 40, height: 22, borderRadius: 11,
                background: light ? 'var(--accent)' : 'var(--bg-card)',
                border: '1px solid var(--border)',
                cursor: 'pointer', position: 'relative', transition: 'background 0.3s',
              }}>
                <div style={{
                  position: 'absolute', top: 2,
                  left: light ? 20 : 2,
                  width: 16, height: 16, borderRadius: '50%',
                  background: light ? '#0A0A0B' : 'var(--text-muted)',
                  transition: 'left 0.3s',
                }} />
              </button>

              <Link href="/apply">
                <button className="btn-accent" style={{ marginLeft: 8, padding: '9px 20px', fontSize: 12 }}>
                  Get Started
                </button>
              </Link>
            </div>
          </div>
        </nav>

        <main style={{ paddingTop: 60 }}>
          {children}
        </main>
      </body>
    </html>
  )
}