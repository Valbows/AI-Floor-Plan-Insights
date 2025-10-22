import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Home, ArrowLeft, Upload, AlertCircle, CheckCircle, Loader, Eye, DollarSign, FileText } from 'lucide-react'
import axios from 'axios'
import Chatbot from '../components/Chatbot'

const NewProperty = () => {
  const [file, setFile] = useState(null)
  const [address, setAddress] = useState('')
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [analysisStep, setAnalysisStep] = useState(0)
  const navigate = useNavigate()

  const analysisSteps = [
    { icon: Upload, text: 'Uploading floor plan...', color: 'text-blue-600' },
    { icon: Eye, text: 'Analyzing layout and rooms...', color: 'text-purple-600' },
    { icon: DollarSign, text: 'Calculating market value...', color: 'text-green-600' },
    { icon: FileText, text: 'Generating listing content...', color: 'text-orange-600' }
  ]

  useEffect(() => {
    document.title = 'Add Property | FloorIQ'
  }, [])

  useEffect(() => {
    if (loading && !success) {
      const interval = setInterval(() => {
        setAnalysisStep(prev => {
          if (prev < analysisSteps.length - 1) {
            return prev + 1
          }
          return prev
        })
      }, 2500) // 2.5 seconds per step
      return () => clearInterval(interval)
    }
  }, [loading, success])

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      // Validate file type
      const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'application/pdf']
      if (!validTypes.includes(selectedFile.type)) {
        setError('Please upload a PNG, JPG, or PDF file')
        return
      }

      // Validate file size (10MB max)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB')
        return
      }

      setFile(selectedFile)
      setError('')

      // Create preview for images
      if (selectedFile.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onloadend = () => {
          setPreview(reader.result)
        }
        reader.readAsDataURL(selectedFile)
      } else {
        setPreview(null)
      }
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!file) {
      setError('Please select a floor plan image')
      return
    }

    if (!address.trim()) {
      setError('Please enter a property address')
      return
    }

    setLoading(true)
    setError('')
    setAnalysisStep(0)
    const startTime = Date.now()

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('address', address)

      // Start API call and immediately redirect with loading state
      const response = await axios.post('/api/properties/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      const propertyId = response.data.property.id
      
      // Immediately redirect to property page with loading overlay
      navigate(`/properties/${propertyId}?showProgress=true`)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to upload floor plan')
      setLoading(false)
      setAnalysisStep(0)
    }
  }

  return (
    <div className="min-h-screen" style={{background: '#F6F1EB'}}>
      <main className="max-w-[1400px] mx-auto px-4 py-16">
        {!loading && (
          <div className="max-w-3xl mx-auto">
            {/* Page Title */}
            <div className="text-center mb-12">
              <h1 className="text-5xl font-black uppercase tracking-tight mb-3" style={{color: '#000000', letterSpacing: '-2px', lineHeight: '0.95'}}>
                UPLOAD <span style={{color: '#FF5959', position: 'relative', display: 'inline-block'}}>
                  FLOOR PLAN
                  <div className="absolute left-1/2 -translate-x-1/2" style={{width: '120px', height: '6px', background: '#FF5959', bottom: '-12px', marginLeft: '80px'}}></div>
                </span>
              </h1>
              <div className="mb-6"></div>
              <p className="text-lg" style={{color: '#666666'}}>Let our AI analyze your property and generate insights instantly</p>
            </div>

            <div className="bg-white p-10" style={{borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)'}}>
              {error && (
                <div className="mb-8 p-4 flex items-start" style={{background: '#FEE2E2', border: '2px solid #FF5959', borderRadius: '4px'}}>
                  <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" style={{color: '#FF5959'}} />
                  <p className="text-sm font-medium" style={{color: '#FF5959'}}>{error}</p>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-8">
              {/* File Upload */}
              <div>
                <label className="block text-base font-bold uppercase mb-4" style={{color: '#000000', letterSpacing: '1px'}}>
                  1. Upload Floor Plan Image
                </label>
                <div 
                  className="border-2 border-dashed p-12 text-center transition-all cursor-pointer" 
                  style={{borderColor: file ? '#FF5959' : '#000000', borderRadius: '8px', background: file ? '#FFF5F5' : 'transparent'}}
                  onMouseEnter={(e) => {if (!file) e.currentTarget.style.borderColor = '#FF5959'}}
                  onMouseLeave={(e) => {if (!file) e.currentTarget.style.borderColor = '#000000'}}
                >
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/jpg,application/pdf"
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer block">
                    {preview ? (
                      <div>
                        <img src={preview} alt="Preview" className="max-h-80 mx-auto mb-4 rounded-lg shadow-md" />
                        <div className="inline-flex items-center space-x-2 px-4 py-2 font-bold uppercase text-sm" style={{background: '#FF5959', color: '#FFFFFF', borderRadius: '4px'}}>
                          <Upload className="w-4 h-4" />
                          <span>Change Image</span>
                        </div>
                      </div>
                    ) : (
                      <div>
                        <div className="w-20 h-20 mx-auto mb-4 rounded-full flex items-center justify-center" style={{background: '#F6F1EB'}}>
                          <Upload className="w-10 h-10" style={{color: '#FF5959'}} />
                        </div>
                        <p className="text-lg font-bold mb-2" style={{color: '#000000'}}>
                          Click to upload or drag and drop
                        </p>
                        <p className="text-sm" style={{color: '#666666'}}>PNG, JPG, or PDF (max 10MB)</p>
                      </div>
                    )}
                    {file && !preview && (
                      <div className="mt-4">
                        <p className="text-sm font-medium" style={{color: '#000000'}}>{file.name}</p>
                        <p className="text-xs" style={{color: '#666666'}}>{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                      </div>
                    )}
                  </label>
                </div>
              </div>

              {/* Address Input */}
              <div>
                <label htmlFor="address" className="block text-base font-bold uppercase mb-4" style={{color: '#000000', letterSpacing: '1px'}}>
                  2. Enter Property Address
                </label>
                <input
                  id="address"
                  type="text"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  className="w-full px-5 py-4 border-2 focus:outline-none transition-colors text-base"
                  style={{borderColor: '#000000', borderRadius: '8px'}}
                  onFocus={(e) => {e.target.style.borderColor = '#FF5959'; e.target.style.boxShadow = '0 0 0 3px rgba(255,89,89,0.1)'}}
                  onBlur={(e) => {e.target.style.borderColor = '#000000'; e.target.style.boxShadow = 'none'}}
                  placeholder="123 Main Street, City, State ZIP"
                  required
                />
                <p className="text-sm mt-2" style={{color: '#666666'}}>
                  Enter the complete property address for accurate analysis
                </p>
              </div>

              {/* Submit Button */}
              <div className="pt-4">
                <button
                  type="submit"
                  disabled={loading || !file || !address.trim()}
                  className="w-full text-white px-8 py-5 font-black uppercase tracking-wide transition-all text-lg flex items-center justify-center"
                  style={{background: loading || !file || !address.trim() ? '#CCCCCC' : '#FF5959', borderRadius: '8px', cursor: loading || !file || !address.trim() ? 'not-allowed' : 'pointer'}}
                  onMouseEnter={(e) => {if (!loading && file && address.trim()) {e.currentTarget.style.background = '#E54545'; e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 8px 20px rgba(255,89,89,0.4)'}}}
                  onMouseLeave={(e) => {if (!loading && file && address.trim()) {e.currentTarget.style.background = '#FF5959'; e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none'}}}
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Analyzing Your Property...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-6 h-6 mr-2" />
                      Start AI Analysis
                    </>
                  )}
                </button>

                <div className="mt-6 p-4 rounded-lg" style={{background: '#F6F1EB'}}>
                  <p className="text-sm font-medium mb-2" style={{color: '#000000'}}>What happens next?</p>
                  <ul className="text-sm space-y-1" style={{color: '#666666'}}>
                    <li>✓ AI analyzes floor plan layout and dimensions</li>
                    <li>✓ Extracts bedrooms, bathrooms, and square footage</li>
                    <li>✓ Generates market value estimates</li>
                    <li>✓ Creates professional listing content</li>
                  </ul>
                </div>
              </div>
            </form>
          </div>
        </div>
        )}
      </main>
      
      {/* Chatbot */}
      <Chatbot />
    </div>
  )
}

export default NewProperty
