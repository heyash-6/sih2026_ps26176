import React, { useState } from 'react'
import { signInWithEmail, signUpWithEmail } from '../services/supabaseClient'

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [tab, setTab] = useState('signin') // 'signin' | 'signup'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [role, setRole] = useState('user')
  const [loading, setLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')
  const [successMsg, setSuccessMsg] = useState('')

  if (!isOpen) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrorMsg('')
    setSuccessMsg('')

    if (!email || !password) {
      setErrorMsg('Please enter both email and password.')
      return
    }

    setLoading(true)
    try {
      if (tab === 'signin') {
        const res = await signInWithEmail(email, password)
        if (res.success) {
          setSuccessMsg('Successfully signed in!')
          setTimeout(() => {
            onAuthSuccess(res.user)
            onClose()
          }, 800)
        } else {
          setErrorMsg(res.error || 'Failed to sign in. Check your credentials.')
        }
      } else {
        const res = await signUpWithEmail(email, password, fullName, role)
        if (res.success) {
          setSuccessMsg('Account created successfully! You are now logged in.')
          setTimeout(() => {
            onAuthSuccess(res.user)
            onClose()
          }, 1200)
        } else {
          setErrorMsg(res.error || 'Failed to create account.')
        }
      }
    } catch (err) {
      setErrorMsg(err.message || 'An unexpected error occurred.')
    } finally {
      setLoading(false)
    }
  }

  const handleDemoLogin = (demoRole = 'Captain') => {
    const demoUser = {
      id: 'demo-captain-001',
      email: demoRole === 'Captain' ? 'captain.devesh@orca-marine.in' : 'researcher@incois.gov.in',
      user_metadata: {
        full_name: demoRole === 'Captain' ? 'Capt. Devesh Madhavi' : 'Dr. A. Sharma',
        role: demoRole === 'Captain' ? 'user' : 'researcher'
      }
    }
    setSuccessMsg(`Logged in as ${demoUser.user_metadata.full_name}!`)
    setTimeout(() => {
      onAuthSuccess(demoUser)
      onClose()
    }, 600)
  }

  return (
    <div className="authModalBackdrop" onClick={onClose}>
      <div className="authModal" onClick={(e) => e.stopPropagation()}>
        <button className="authCloseBtn" onClick={onClose} aria-label="Close">✕</button>
        
        <div className="authHeader">
          <div className="authIcon">⚓</div>
          <h2>ORCA Portal Access</h2>
          <p>Marine Ecosystem Reasoning & Decision Platform</p>
        </div>

        <div className="authTabs">
          <button 
            type="button"
            className={`authTab ${tab === 'signin' ? 'active' : ''}`}
            onClick={() => { setTab('signin'); setErrorMsg(''); setSuccessMsg(''); }}
          >
            Sign In
          </button>
          <button 
            type="button"
            className={`authTab ${tab === 'signup' ? 'active' : ''}`}
            onClick={() => { setTab('signup'); setErrorMsg(''); setSuccessMsg(''); }}
          >
            Create Account
          </button>
        </div>

        {errorMsg && <div className="authAlert error">⚠️ {errorMsg}</div>}
        {successMsg && <div className="authAlert success">✓ {successMsg}</div>}

        <form onSubmit={handleSubmit} className="authForm">
          {tab === 'signup' && (
            <div className="authField">
              <label>Full Name</label>
              <input 
                type="text" 
                placeholder="e.g. Captain Devesh Madhavi" 
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />
            </div>
          )}

          <div className="authField">
            <label>Email Address</label>
            <input 
              type="email" 
              placeholder="name@example.com" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="authField">
            <label>Password</label>
            <input 
              type="password" 
              placeholder="••••••••" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {tab === 'signup' && (
            <div className="authField">
              <label>Role / Operational Profile</label>
              <select value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="user">Fisherman / Vessel Captain</option>
                <option value="researcher">Marine Researcher / Oceanographer</option>
                <option value="admin">Port Authority / Fleet Manager</option>
              </select>
            </div>
          )}

          <button type="submit" className="authSubmitBtn" disabled={loading}>
            {loading ? 'Processing...' : (tab === 'signin' ? 'Sign In to Workspace →' : 'Register Account →')}
          </button>
        </form>

        <div className="authDivider">
          <span>or quick access</span>
        </div>

        <div className="authQuickDemo">
          <button type="button" className="authDemoBtn" onClick={() => handleDemoLogin('Captain')}>
            ⚓ Demo Captain
          </button>
          <button type="button" className="authDemoBtn" onClick={() => handleDemoLogin('Researcher')}>
            🔬 Demo Researcher
          </button>
        </div>

        <div className="authFooter">
          <small>Protected by Encrypted Maritime Identity & Row Level Security</small>
        </div>
      </div>
    </div>
  )
}
