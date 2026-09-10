import { createClient } from '@supabase/supabase-js'

export const SUPABASE_URL = 'https://byikekhtwiewlpxbuwgo.supabase.co'
export const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ5aWtla2h0d2lld2xweGJ1d2dvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkwMzM2OTksImV4cCI6MjEwNDYwOTY5OX0.R3OLDUPuPgWHHAGJsWMbgqM8vSDfjUltGeQzwyR_BAE'

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true
  }
})

/**
 * Sign Up with Supabase Auth
 */
export async function signUpWithEmail(email, password, fullName = '', role = 'user') {
  try {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
          role: role
        }
      }
    })
    if (error) throw error
    return { success: true, user: data.user, session: data.session }
  } catch (err) {
    console.error('[Supabase Auth] Sign up error:', err)
    return { success: false, error: err.message }
  }
}

/**
 * Sign In with Supabase Auth
 */
export async function signInWithEmail(email, password) {
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })
    if (error) throw error
    return { success: true, user: data.user, session: data.session }
  } catch (err) {
    console.error('[Supabase Auth] Sign in error:', err)
    return { success: false, error: err.message }
  }
}

/**
 * Sign Out
 */
export async function signOutUser() {
  try {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
    return { success: true }
  } catch (err) {
    console.error('[Supabase Auth] Sign out error:', err)
    return { success: false, error: err.message }
  }
}

/**
 * Get current session and user
 */
export async function getSession() {
  try {
    const { data: { session } } = await supabase.auth.getSession()
    return session
  } catch (err) {
    return null
  }
}

/**
 * Listen to auth state changes
 */
export function onAuthStateChange(callback) {
  return supabase.auth.onAuthStateChange((event, session) => {
    callback(event, session?.user ?? null, session)
  })
}
