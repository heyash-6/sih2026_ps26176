import React, { useState } from 'react'
import { signInWithEmail, signUpWithEmail } from '../services/supabaseClient'

const AUTH_T = {
  en: {
    portalAccess: 'ORCA Portal Access',
    portalDesc: 'Marine Ecosystem Reasoning & Decision Platform',
    signIn: 'Sign In',
    createAccount: 'Create Account',
    fullName: 'Full Name',
    emailAddress: 'Email Address',
    password: 'Password',
    role: 'Role / Operational Profile',
    roleCaptain: 'Fisherman / Vessel Captain',
    roleResearcher: 'Marine Researcher / Oceanographer',
    roleAdmin: 'Port Authority / Fleet Manager',
    signInBtn: 'Sign In to Workspace →',
    registerBtn: 'Register Account →',
    processing: 'Processing...',
    quickAccess: 'or quick access',
    demoCaptain: '⚓ Demo Captain',
    demoResearcher: '🔬 Demo Researcher',
    securityFooter: 'Protected by Encrypted Maritime Identity & Row Level Security',
    enterBoth: 'Please enter both email and password.',
    signedInSuccess: 'Successfully signed in!',
    accountCreatedSuccess: 'Account created successfully! You are now logged in.'
  },
  hi: {
    portalAccess: 'ORCA पोर्टल प्रवेश',
    portalDesc: 'समुद्री पारिस्थितिकी व निर्णय प्रणाली',
    signIn: 'साइन इन',
    createAccount: 'खाता बनाएं',
    fullName: 'पूरा नाम',
    emailAddress: 'ईमेल पता',
    password: 'पासवर्ड',
    role: 'भूमिका / परिचालन प्रोफाइल',
    roleCaptain: 'मछुआरा / पोत कप्तान',
    roleResearcher: 'समुद्री शोधकर्ता / समुद्र विज्ञानी',
    roleAdmin: 'बंदरगाह प्राधिकरण / बेड़ा प्रबंधक',
    signInBtn: 'कार्यक्षेत्र में साइन इन करें →',
    registerBtn: 'खाता पंजीकृत करें →',
    processing: 'प्रक्रिया जारी है...',
    quickAccess: 'या त्वरित प्रवेश',
    demoCaptain: '⚓ डेमो कप्तान',
    demoResearcher: '🔬 डेमो शोधकर्ता',
    securityFooter: 'कूटबद्ध समुद्री पहचान व पंक्ति-स्तरीय सुरक्षा द्वारा संरक्षित',
    enterBoth: 'कृपया ईमेल और पासवर्ड दोनों दर्ज करें।',
    signedInSuccess: 'सफलतापूर्वक साइन इन हुआ!',
    accountCreatedSuccess: 'खाता सफलतापूर्वक बनाया गया! आप लॉगिन हैं।'
  },
  mr: {
    portalAccess: 'ORCA पोर्टल प्रवेश',
    portalDesc: 'सागरी परिसंस्था व निर्णय प्रणाली',
    signIn: 'साइन इन',
    createAccount: 'खाते तयार करा',
    fullName: 'पूर्ण नाव',
    emailAddress: 'ईमेल पत्ता',
    password: 'पासवर्ड',
    role: 'भूमिका / ऑपरेशनल प्रोफाइल',
    roleCaptain: 'मासेमार / जहाज कॅप्टन',
    roleResearcher: 'सागरी संशोधक / समुद्रशास्त्रज्ञ',
    roleAdmin: 'बंदर प्राधिकरण / फ्लीट व्यवस्थापक',
    signInBtn: 'कार्यक्षेत्रात साइन इन करा →',
    registerBtn: 'खाते नोंदणी करा →',
    processing: 'प्रक्रिया सुरू आहे...',
    quickAccess: 'किंवा जलद प्रवेश',
    demoCaptain: '⚓ डेमो कॅप्टन',
    demoResearcher: '🔬 डेमो संशोधक',
    securityFooter: 'कूटबद्ध सागरी ओळख व रो-पातळी सुरक्षिततेने संरक्षित',
    enterBoth: 'कृपया ईमेल आणि पासवर्ड दोन्ही टाका.',
    signedInSuccess: 'यशस्वीरीत्या साइन इन झाले!',
    accountCreatedSuccess: 'खाते यशस्वीरीत्या तयार केले! आपण आता लॉगिन आहात.'
  }
}

export default function AuthModal({ isOpen, onClose, onAuthSuccess, lang = 'en' }) {
  const [tab, setTab] = useState('signin') // 'signin' | 'signup'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [role, setRole] = useState('user')
  const [loading, setLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')
  const [successMsg, setSuccessMsg] = useState('')

  const t = (k) => AUTH_T[lang]?.[k] ?? AUTH_T.en[k] ?? k

  if (!isOpen) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrorMsg('')
    setSuccessMsg('')

    if (!email || !password) {
      setErrorMsg(t('enterBoth'))
      return
    }

    setLoading(true)
    try {
      if (tab === 'signin') {
        const res = await signInWithEmail(email, password)
        if (res.success) {
          setSuccessMsg(t('signedInSuccess'))
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
          setSuccessMsg(t('accountCreatedSuccess'))
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
          <h2>{t('portalAccess')}</h2>
          <p>{t('portalDesc')}</p>
        </div>

        <div className="authTabs">
          <button 
            type="button"
            className={`authTab ${tab === 'signin' ? 'active' : ''}`}
            onClick={() => { setTab('signin'); setErrorMsg(''); setSuccessMsg(''); }}
          >
            {t('signIn')}
          </button>
          <button 
            type="button"
            className={`authTab ${tab === 'signup' ? 'active' : ''}`}
            onClick={() => { setTab('signup'); setErrorMsg(''); setSuccessMsg(''); }}
          >
            {t('createAccount')}
          </button>
        </div>

        {errorMsg && <div className="authAlert error">⚠️ {errorMsg}</div>}
        {successMsg && <div className="authAlert success">✓ {successMsg}</div>}

        <form onSubmit={handleSubmit} className="authForm">
          {tab === 'signup' && (
            <div className="authField">
              <label>{t('fullName')}</label>
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
            <label>{t('emailAddress')}</label>
            <input 
              type="email" 
              placeholder="name@example.com" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="authField">
            <label>{t('password')}</label>
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
              <label>{t('role')}</label>
              <select value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="user">{t('roleCaptain')}</option>
                <option value="researcher">{t('roleResearcher')}</option>
                <option value="admin">{t('roleAdmin')}</option>
              </select>
            </div>
          )}

          <button type="submit" className="authSubmitBtn" disabled={loading}>
            {loading ? t('processing') : (tab === 'signin' ? t('signInBtn') : t('registerBtn'))}
          </button>
        </form>

        <div className="authDivider">
          <span>{t('quickAccess')}</span>
        </div>

        <div className="authQuickDemo">
          <button type="button" className="authDemoBtn" onClick={() => handleDemoLogin('Captain')}>
            {t('demoCaptain')}
          </button>
          <button type="button" className="authDemoBtn" onClick={() => handleDemoLogin('Researcher')}>
            {t('demoResearcher')}
          </button>
        </div>

        <div className="authFooter">
          <small>{t('securityFooter')}</small>
        </div>
      </div>
    </div>
  )
}
