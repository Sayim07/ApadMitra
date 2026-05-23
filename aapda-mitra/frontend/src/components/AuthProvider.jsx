import React, { createContext, useContext, useEffect, useState } from 'react'
import { createUserWithEmailAndPassword, GoogleAuthProvider, onAuthStateChanged, signInWithEmailAndPassword, signInWithPopup, signOut as fbSignOut } from 'firebase/auth'
import { auth, isFirebaseConfigured } from '../firebase'

// helper to exchange idToken for backend profile
async function fetchBackendProfile(idToken) {
  try {
    const res = await fetch('/auth/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id_token: idToken })
    })
    if (!res.ok) return { profile: null, error: `http_${res.status}` }
    const data = await res.json()
    return { profile: data.user || null, error: null }
  } catch (e) {
    return { profile: null, error: 'network' }
  }
}

const AuthContext = createContext({ user: null })

export function useAuth() {
  return useContext(AuthContext)
}

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [profileLoaded, setProfileLoaded] = useState(false)
  const [profileError, setProfileError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!auth) {
      setLoading(false)
      setProfileLoaded(true)
      return undefined
    }

    const unsub = onAuthStateChanged(auth, (u) => {
      setUser(u)
      setLoading(false)
      if (u) {
        setProfile(null)
        setProfileLoaded(false)
        setProfileError(null)
        u.getIdToken().then(async (t) => {
          const r = await fetchBackendProfile(t)
          setProfile(r.profile)
          setProfileError(r.error)
          setProfileLoaded(true)
        }).catch(()=> {
          setProfile(null)
          setProfileError('token')
          setProfileLoaded(true)
        })
      } else {
        setProfile(null)
        setProfileLoaded(true)
        setProfileError(null)
      }
    })
    return () => unsub()
  }, [])

  const login = async (email, password) => {
    if (!auth) {
      throw new Error('Firebase auth is not configured for this local preview')
    }

    const cred = await signInWithEmailAndPassword(auth, email, password)
    const token = await cred.user.getIdToken()
    const r = await fetchBackendProfile(token)
    setProfile(r.profile)
    setProfileError(r.error)
    setProfileLoaded(true)
    return { cred, profile: r.profile }
  }

  const register = async (email, password) => {
    if (!auth) {
      throw new Error('Firebase auth is not configured for this local preview')
    }

    const cred = await createUserWithEmailAndPassword(auth, email, password)
    const token = await cred.user.getIdToken()
    const r = await fetchBackendProfile(token)
    setProfile(r.profile)
    setProfileError(r.error)
    setProfileLoaded(true)
    return { cred, profile: r.profile }
  }

  const loginWithGoogle = async () => {
    if (!auth) {
      throw new Error('Firebase auth is not configured for this local preview')
    }

    const provider = new GoogleAuthProvider()
    const cred = await signInWithPopup(auth, provider)
    const token = await cred.user.getIdToken()
    const r = await fetchBackendProfile(token)
    setProfile(r.profile)
    setProfileError(r.error)
    setProfileLoaded(true)
    return { cred, profile: r.profile }
  }
  const logout = async () => {
    if (!auth) {
      setProfile(null)
      setProfileLoaded(true)
      setProfileError(null)
      return
    }

    await fbSignOut(auth)
    setProfile(null)
    setProfileLoaded(true)
    setProfileError(null)
  }

  return (
    <AuthContext.Provider value={{ user, profile, profileLoaded, profileError, login, register, loginWithGoogle, logout, loading, isFirebaseConfigured }}>
      {children}
    </AuthContext.Provider>
  )
}
