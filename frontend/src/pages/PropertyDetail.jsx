import React, { useState, useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Home, ArrowLeft, Bed, Bath, Maximize, Clock, CheckCircle, XCircle, Loader } from 'lucide-react'
import axios from 'axios'

const PropertyDetail = () => {
  const { id } = useParams()
  const [property, setProperty] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadProperty()
  }, [id])

  // Separate effect for polling
  useEffect(() => {
    if (property?.status === 'processing') {
      const interval = setInterval(() => {
        loadProperty()
      }, 5000)
      
      return () => clearInterval(interval)
    }
  }, [property?.status])

  const loadProperty = async () => {
    try {
      const response = await axios.get(`/api/properties/${id}`)
      setProperty(response.data.property)
      setLoading(false)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load property')
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      'processing': { icon: Loader, color: 'bg-yellow-100 text-yellow-800', text: 'Processing' },
      'parsing_complete': { icon: CheckCircle, color: 'bg-green-100 text-green-800', text: 'Analysis Complete' },
      'failed': { icon: XCircle, color: 'bg-red-100 text-red-800', text: 'Failed' }
    }
    const badge = badges[status] || badges['processing']
    const Icon = badge.icon
    
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${badge.color}`}>
        <Icon className="w-4 h-4 mr-1" />
        {badge.text}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-2xl mx-auto px-4 py-16 text-center">
          <XCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Property</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Link to="/dashboard" className="btn-primary">
            Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  const extracted = property.extracted_data || {}

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Link to="/dashboard" className="text-gray-600 hover:text-gray-900">
                <ArrowLeft className="w-6 h-6" />
              </Link>
              <h1 className="text-xl font-bold text-gray-900">Property Details</h1>
            </div>
            {getStatusBadge(property.status)}
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Floor Plan Image */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Floor Plan</h2>
            {property.image_url ? (
              <img 
                src={property.image_url} 
                alt="Floor Plan" 
                className="w-full rounded-lg border border-gray-200"
              />
            ) : (
              <div className="bg-gray-100 rounded-lg h-64 flex items-center justify-center">
                <Home className="w-16 h-16 text-gray-400" />
              </div>
            )}
          </div>

          {/* Property Information */}
          <div className="space-y-6">
            {/* Address */}
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">Address</h2>
              <p className="text-gray-700">
                {extracted.address || 'Not specified'}
              </p>
            </div>

            {/* Key Stats */}
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Property Details</h2>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <Bed className="w-8 h-8 text-primary-600 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-gray-900">{extracted.bedrooms || 0}</p>
                  <p className="text-sm text-gray-600">Bedrooms</p>
                </div>
                <div className="text-center">
                  <Bath className="w-8 h-8 text-primary-600 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-gray-900">{extracted.bathrooms || 0}</p>
                  <p className="text-sm text-gray-600">Bathrooms</p>
                </div>
                <div className="text-center">
                  <Maximize className="w-8 h-8 text-primary-600 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-gray-900">{extracted.square_footage || 0}</p>
                  <p className="text-sm text-gray-600">Sq Ft</p>
                </div>
              </div>
            </div>

            {/* Layout Type */}
            {extracted.layout_type && (
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-3">Layout</h2>
                <p className="text-gray-700">{extracted.layout_type}</p>
              </div>
            )}

            {/* Features */}
            {extracted.features && extracted.features.length > 0 && (
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-3">Features</h2>
                <div className="flex flex-wrap gap-2">
                  {extracted.features.map((feature, index) => (
                    <span 
                      key={index}
                      className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm"
                    >
                      {feature}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Rooms */}
            {extracted.rooms && extracted.rooms.length > 0 && (
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-3">Rooms</h2>
                <div className="space-y-2">
                  {extracted.rooms.map((room, index) => (
                    <div key={index} className="flex justify-between items-center py-2 border-b border-gray-200 last:border-0">
                      <span className="font-medium text-gray-900">{room.type}</span>
                      <span className="text-gray-600">{room.dimensions}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* AI Notes */}
            {extracted.notes && (
              <div className="card bg-yellow-50 border-yellow-200">
                <h2 className="text-lg font-semibold text-gray-900 mb-3">AI Analysis Notes</h2>
                <p className="text-sm text-gray-700">{extracted.notes}</p>
              </div>
            )}

            {/* Metadata */}
            <div className="card bg-gray-50">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">Details</h2>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Property ID:</span>
                  <span className="text-gray-900 font-mono text-xs">{property.id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Input Type:</span>
                  <span className="text-gray-900">{property.input_type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Created:</span>
                  <span className="text-gray-900">
                    {new Date(property.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className="text-gray-900">{property.status}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
export default PropertyDetail
