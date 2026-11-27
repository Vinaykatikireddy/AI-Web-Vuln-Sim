import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import axios from 'axios'
import { retry } from '../utils/retry'
import { cancelRequest } from '../utils/cancelRequest'

interface User {
  username: string
  email?: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  loading: boolean
  login: (username: string, password: string, navigate: (path: string) => void) => Promise<void>
  logout: (navigate?: (path: string) => void) => Promise<void>
  checkAuth: () => Promise<void>
  updateSession: (newToken: string | null, updatedUser: User) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  const checkAuth = async () => {
    setLoading(true)
    const { cancelTokenSource, cancelRequest: cancel } = cancelRequest();
    try {
      const storedToken = localStorage.getItem('auth')
      const storedUser = localStorage.getItem('user')
      
      if (storedToken && storedUser) {
        const API_BASE_URL = import.meta.env.VITE_AWVS_BASE_URL
        await retry(() => axios.get(`${API_BASE_URL}/auth/me`, {
          headers: {
            Authorization: `Bearer ${storedToken}`
          },
          cancelToken: cancelTokenSource.token
        }));
        setToken(storedToken)
        setUser(JSON.parse(storedUser))
      }
    } catch (err) {
      if (!axios.isCancel(err)) {
        logout();
      }
    } finally {
      setLoading(false)
    }
    return cancel;
  }

  const login = async (username: string, password: string, navigate: (path: string) => void) => {
    setLoading(true)
    const { cancelTokenSource, cancelRequest: cancel } = cancelRequest();
    try {
      const formDataToSend = new URLSearchParams()
      formDataToSend.append("username", username)
      formDataToSend.append("password", password)

      const API_BASE_URL = import.meta.env.VITE_AWVS_BASE_URL
      const response = await retry(() => axios.post(
        `${API_BASE_URL}/auth/login`,
        formDataToSend,
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          cancelToken: cancelTokenSource.token
        }
      ));

      const token = response.data.access_token
      const user = { username }
      
      localStorage.setItem("auth", token)
      localStorage.setItem("user", JSON.stringify(user))
      
      setToken(token)
      setUser(user)
      navigate("/dashboard")
    } catch (err) {
      if (!axios.isCancel(err)) {
        throw err;
      }
    } finally {
      setLoading(false)
    }
    return cancel;
  }

  const logout = async (navigate?: (path: string) => void) => {
    const currentToken = token || localStorage.getItem('auth')
    localStorage.removeItem('auth')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)

    if (currentToken) {
      const API_BASE_URL = import.meta.env.VITE_AWVS_BASE_URL
      try {
        await axios.post(
          `${API_BASE_URL}/auth/logout`,
          {},
          {
            headers: {
              Authorization: `Bearer ${currentToken}`
            }
          }
        )
      } catch {
        // Client state is already cleared; ignore server/network errors on logout
      }
    }

    if (navigate) {
      navigate('/login')
    }
  }

  const updateSession = (newToken: string | null, updatedUser: User) => {
    if (newToken) {
      localStorage.setItem('auth', newToken)
      setToken(newToken)
    }
    localStorage.setItem('user', JSON.stringify(updatedUser))
    setUser(updatedUser)
  }

  useEffect(() => {
    checkAuth()

    const handleUnauthorized = () => {
      localStorage.removeItem('auth')
      localStorage.removeItem('user')
      setToken(null)
      setUser(null)
      if (window.location.pathname !== '/ai-web-vuln-sim/login') {
        window.location.assign('/ai-web-vuln-sim/login')
      }
    }

    window.addEventListener('auth:unauthorized', handleUnauthorized)
    return () => {
      window.removeEventListener('auth:unauthorized', handleUnauthorized)
    }
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, checkAuth, updateSession }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}