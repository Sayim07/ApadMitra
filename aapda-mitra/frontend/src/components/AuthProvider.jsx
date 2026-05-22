import React, { createContext, useContext, useEffect, useState } from 'react'
import { onAuthStateChanged, signInWithEmailAndPassword, signOut as fbSignOut } from 'firebase/auth'
import { auth } from '../firebase'

// helper to exchange idToken for backend profile
async function fetchBackendProfile(idToken) {
  try {
    const res = await fetch('/auth/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id_token: idToken })
    })
    if (!res.ok) return null
    const data = await res.json()
    return data.user
  } catch (e) {
    return null
  }
}

const AuthContext = createContext({ user: null })

export function useAuth() {
  return useContext(AuthContext)
}

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!auth) {
      setLoading(false)
      return undefined
    }

    const unsub = onAuthStateChanged(auth, (u) => {
      setUser(u)
      setLoading(false)
      if (u) {
        u.getIdToken().then(async (t) => {
          const profile = await fetchBackendProfile(t)
          setProfile(profile)
        }).catch(()=>{})
      } else {
        setProfile(null)
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
    const profile = await fetchBackendProfile(token)
    setProfile(profile)
    return cred
  }
  const logout = async () => {
    if (!auth) {
      setProfile(null)
      return
    }

    await fbSignOut(auth)
    setProfile(null)
  }

  return (
    <AuthContext.Provider value={{ user, profile, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}
