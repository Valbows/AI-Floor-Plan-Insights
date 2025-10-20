import React, { createContext, useState, useContext, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  // Configure axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete axios.defaults.headers.common['Authorization']
    }
  }, [token])

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      const savedToken = localStorage.getItem('token')
      if (savedToken) {
        try {
          // Ensure Authorization header is set before verification
          axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`
          setToken(savedToken)
          // Verify token is still valid by making a test request
          const response = await axios.get('/auth/verify')
          setUser(response.data.user)
        } catch (error) {
          // Do NOT clear token automatically on 401 in dev; keep user null and allow UI to handle gracefully
          setUser(null)
        }
      }
      setLoading(false)
    }

    checkAuth()
  }, [])

  const login = async (email, password) => {
    try {
      const response = await axios.post('/auth/login', { email, password })
      const { token: newToken, user: userData } = response.data
      
      localStorage.setItem('token', newToken)
      setToken(newToken)
      setUser(userData)
      
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Login failed'
      }
    }
  }

  const register = async (email, password, fullName) => {
    try {
      const response = await axios.post('/auth/register', {
        email,
        password,
        full_name: fullName
      })
      
      const { token: newToken, user: userData } = response.data
      
      localStorage.setItem('token', newToken)
      setToken(newToken)
      setUser(userData)
      
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Registration failed'
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    // Consider presence of token as authenticated (prevents abrupt logout during transient 401s)
    isAuthenticated: !!token
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
