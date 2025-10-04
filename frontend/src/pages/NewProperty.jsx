import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Home, ArrowLeft, Upload, AlertCircle, CheckCircle } from 'lucide-react'
import axios from 'axios'

const NewProperty = () => {
  const [file, setFile] = useState(null)
  const [address, setAddress] = useState('')
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const navigate = useNavigate()

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

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('address', address)

      const response = await axios.post('/api/properties/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setSuccess(true)
      
      // Redirect to property detail after 2 seconds
      setTimeout(() => {
        navigate(`/property/${response.data.property.id}`)
      }, 2000)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to upload floor plan')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center space-x-3">
            <Link to="/dashboard" className="text-gray-600 hover:text-gray-900">
              <ArrowLeft className="w-6 h-6" />
            </Link>
            <h1 className="text-xl font-bold text-gray-900">Upload Floor Plan</h1>
          </div>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {success ? (
          <div className="card text-center py-12">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Upload Successful!</h3>
            <p className="text-gray-600 mb-4">AI is analyzing your floor plan...</p>
            <p className="text-sm text-gray-500">Redirecting to property details...</p>
          </div>
        ) : (
          <div className="card">
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
                <AlertCircle className="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* File Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Floor Plan Image *
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-500 transition-colors">
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/jpg,application/pdf"
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    {preview ? (
                      <img src={preview} alt="Preview" className="max-h-64 mx-auto mb-4 rounded" />
                    ) : (
                      <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    )}
                    <p className="text-sm text-gray-600 mb-2">
                      {file ? file.name : 'Click to upload or drag and drop'}
                    </p>
                    <p className="text-xs text-gray-500">PNG, JPG, or PDF (max 10MB)</p>
                  </label>
                </div>
              </div>

              {/* Address Input */}
              <div>
                <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-2">
                  Property Address *
                </label>
                <input
                  id="address"
                  type="text"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  className="input-field"
                  placeholder="123 Main Street, City, State ZIP"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Enter the full property address
                </p>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || !file}
                className="w-full btn-primary"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Uploading & Analyzing...
                  </>
                ) : (
                  'Upload Floor Plan'
                )}
              </button>

              <p className="text-xs text-gray-500 text-center">
                AI will automatically analyze the floor plan and extract property details
              </p>
            </form>
          </div>
        )}
      </main>
    </div>
  )
}

export default NewProperty
