import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Home, AlertCircle } from 'lucide-react'

const Register = () => {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    setLoading(true)

    const result = await register(formData.email, formData.password, formData.fullName)
    
    if (result.success) {
      navigate('/dashboard')
    } else {
      setError(result.error)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8" style={{background: '#F6F1EB'}}>
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full mb-4" style={{background: '#FF5959'}}>
            <Home className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl font-black uppercase mb-2" style={{color: '#000000', letterSpacing: '-2px', lineHeight: '0.95'}}>Create <span style={{color: '#FF5959'}}>Account</span></h1>
          <p className="text-base" style={{color: '#666666'}}>Register as a real estate agent</p>
        </div>

        <div className="bg-white p-8" style={{borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', border: '2px solid #000000'}}>
          {error && (
            <div className="mb-6 p-4 flex items-start" style={{background: '#FEE2E2', border: '2px solid #FF5959', borderRadius: '4px'}}>
              <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" style={{color: '#FF5959'}} />
              <p className="text-sm font-medium" style={{color: '#FF5959'}}>{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="fullName" className="block text-sm font-bold uppercase mb-2" style={{color: '#000000', letterSpacing: '1px'}}>
                Full Name
              </label>
              <input
                id="fullName"
                name="fullName"
                type="text"
                value={formData.fullName}
                onChange={handleChange}
                className="w-full px-4 py-3 border-2 focus:outline-none transition-colors"
                style={{borderColor: '#000000', borderRadius: '4px'}}
                onFocus={(e) => {e.target.style.borderColor = '#FF5959'; e.target.style.boxShadow = '0 0 0 2px rgba(255,89,89,0.1)'}}
                onBlur={(e) => {e.target.style.borderColor = '#000000'; e.target.style.boxShadow = 'none'}}
                placeholder="Jane Smith"
                required
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-bold uppercase mb-2" style={{color: '#000000', letterSpacing: '1px'}}>
                Email Address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 border-2 focus:outline-none transition-colors"
                style={{borderColor: '#000000', borderRadius: '4px'}}
                onFocus={(e) => {e.target.style.borderColor = '#FF5959'; e.target.style.boxShadow = '0 0 0 2px rgba(255,89,89,0.1)'}}
                onBlur={(e) => {e.target.style.borderColor = '#000000'; e.target.style.boxShadow = 'none'}}
                placeholder="agent@example.com"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-bold uppercase mb-2" style={{color: '#000000', letterSpacing: '1px'}}>
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full px-4 py-3 border-2 focus:outline-none transition-colors"
                style={{borderColor: '#000000', borderRadius: '4px'}}
                onFocus={(e) => {e.target.style.borderColor = '#FF5959'; e.target.style.boxShadow = '0 0 0 2px rgba(255,89,89,0.1)'}}
                onBlur={(e) => {e.target.style.borderColor = '#000000'; e.target.style.boxShadow = 'none'}}
                placeholder="••••••••"
                required
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-bold uppercase mb-2" style={{color: '#000000', letterSpacing: '1px'}}>
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={handleChange}
                className="w-full px-4 py-3 border-2 focus:outline-none transition-colors"
                style={{borderColor: '#000000', borderRadius: '4px'}}
                onFocus={(e) => {e.target.style.borderColor = '#FF5959'; e.target.style.boxShadow = '0 0 0 2px rgba(255,89,89,0.1)'}}
                onBlur={(e) => {e.target.style.borderColor = '#000000'; e.target.style.boxShadow = 'none'}}
                placeholder="••••••••"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full text-white px-8 py-4 font-bold uppercase tracking-wide transition-all"
              style={{background: loading ? '#CCCCCC' : '#FF5959', borderRadius: '4px', cursor: loading ? 'not-allowed' : 'pointer'}}
              onMouseEnter={(e) => {if (!loading) {e.currentTarget.style.background = '#E54545'; e.currentTarget.style.transform = 'translateY(-1px)'; e.currentTarget.style.boxShadow = '0 4px 12px rgba(255,89,89,0.3)'}}}
              onMouseLeave={(e) => {if (!loading) {e.currentTarget.style.background = '#FF5959'; e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none'}}}
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm">
            <span style={{color: '#666666'}}>Already have an account? </span>
            <Link to="/login" className="font-bold transition-colors" style={{color: '#FF5959'}} onMouseEnter={(e) => e.currentTarget.style.color = '#E54545'} onMouseLeave={(e) => e.currentTarget.style.color = '#FF5959'}>
              Sign in here
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Register
