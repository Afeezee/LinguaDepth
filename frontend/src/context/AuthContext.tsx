import {
  createContext,
  useContext,
  useReducer,
  useEffect,
  type ReactNode,
} from 'react'
import client from '../api/client'
import type { User } from '../types'

interface AuthState {
  user: User | null
  token: string | null
  loading: boolean
}

type AuthAction =
  | { type: 'LOGIN'; user: User; token: string }
  | { type: 'UPDATE_USER'; user: User }
  | { type: 'LOGOUT' }
  | { type: 'LOADED' }

interface AuthContextValue extends AuthState {
  login: (user: User, token: string) => void
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

function reducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'LOGIN':
      return { user: action.user, token: action.token, loading: false }
    case 'UPDATE_USER':
      return { ...state, user: action.user }
    case 'LOGOUT':
      return { user: null, token: null, loading: false }
    case 'LOADED':
      return { ...state, loading: false }
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, {
    user: null,
    token: null,
    loading: true,
  })

  useEffect(() => {
    const token = localStorage.getItem('token')
    const userJson = localStorage.getItem('user')
    if (token && userJson) {
      const parsedUser = JSON.parse(userJson) as User
      dispatch({ type: 'LOGIN', user: parsedUser, token })

      client
        .get('/auth/me')
        .then(({ data }) => {
          localStorage.setItem('user', JSON.stringify(data.user))
          dispatch({ type: 'UPDATE_USER', user: data.user })
        })
        .catch(() => {
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          dispatch({ type: 'LOGOUT' })
        })
    } else {
      dispatch({ type: 'LOADED' })
    }
  }, [])

  const login = (user: User, token: string) => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
    dispatch({ type: 'LOGIN', user, token })
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    dispatch({ type: 'LOGOUT' })
  }

  const refreshUser = async () => {
    const { data } = await client.get('/auth/me')
    localStorage.setItem('user', JSON.stringify(data.user))
    dispatch({ type: 'UPDATE_USER', user: data.user })
  }

  return (
    <AuthContext.Provider value={{ ...state, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
