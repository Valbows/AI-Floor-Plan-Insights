import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Home, Plus, LogOut, Bed, Bath, Maximize, Clock, AlertCircle, CheckCircle, Loader } from 'lucide-react'
import axios from 'axios'

const StatusBadge = ({ status }) => {
  const statusConfig = {
    processing: {
      color: 'bg-blue-100 text-blue-800',
      icon: <Clock className="w-3 h-3" />,
      text: 'Processing'
    },
    parsing_complete: {
      color: 'bg-yellow-100 text-yellow-800',
      icon: <Loader className="w-3 h-3" />,
      text: 'Analyzing'
    },
    enrichment_complete: {
      color: 'bg-purple-100 text-purple-800',
      icon: <Loader className="w-3 h-3" />,
      text: 'Finalizing'
    },
    complete: {
      color: 'bg-green-100 text-green-800',
      icon: <CheckCircle className="w-3 h-3" />,
      text: 'Complete'
    },
    failed: {
      color: 'bg-red-100 text-red-800',
      icon: <AlertCircle className="w-3 h-3" />,
      text: 'Failed'
    }
  }

  const config = statusConfig[status] || statusConfig.processing

  return (
    <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
      {config.icon}
      <span>{config.text}</span>
    </span>
  )
}

const PropertyCard = ({ property }) => {
  const navigate = useNavigate()
  const extractedData = property.extracted_data || {}
  const address = extractedData.address || property.address || 'Address not available'

  return (
    <div
      onClick={() => navigate(`/properties/${property.id}`)}
      className="card hover:shadow-lg transition-shadow duration-200 cursor-pointer"
    >
      {/* Floor Plan Image */}
      {property.image_url && (
        <div className="w-full h-48 bg-gray-100 rounded-t-lg overflow-hidden">
          <img
            src={property.image_url}
            alt={address}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.style.display = 'none'
            }}
          />
        </div>
      )}

      <div className="p-4">
        {/* Status Badge */}
        <div className="mb-3">
          <StatusBadge status={property.status} />
        </div>

        {/* Address */}
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
          {address}
        </h3>

        {/* Property Stats */}
        <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
          <div className="flex items-center space-x-1">
            <Bed className="w-4 h-4" />
            <span>{extractedData.bedrooms || 0} BR</span>
          </div>
          <div className="flex items-center space-x-1">
            <Bath className="w-4 h-4" />
            <span>{extractedData.bathrooms || 0} BA</span>
          </div>
          <div className="flex items-center space-x-1">
            <Maximize className="w-4 h-4" />
            <span>{extractedData.square_footage || 0} sq ft</span>
          </div>
        </div>

        {/* Created Date */}
        <p className="text-xs text-gray-500">
          Created {new Date(property.created_at).toLocaleDateString()}
        </p>
      </div>
    </div>
  )
}

const Dashboard = () => {
  const { user, logout } = useAuth()
  const [properties, setProperties] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchProperties()
  }, [])

  const fetchProperties = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await axios.get('/api/properties')
      setProperties(response.data.properties || [])
    } catch (err) {
      console.error('Error fetching properties:', err)
      setError('Failed to load properties. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                <Home className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">AI Floor Plan Insights</h1>
                <p className="text-sm text-gray-600">Agent Dashboard</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">Welcome, {user?.full_name || user?.email}</span>
              <button
                onClick={logout}
                className="btn-secondary flex items-center space-x-2"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">My Properties</h2>
            {!loading && (
              <p className="text-sm text-gray-600 mt-1">
                {properties.length} {properties.length === 1 ? 'property' : 'properties'}
              </p>
            )}
          </div>
          <Link to="/properties/new" className="btn-primary flex items-center space-x-2">
            <Plus className="w-5 h-5" />
            <span>New Property</span>
          </Link>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="card text-center py-12">
            <Loader className="w-8 h-8 text-primary-600 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Loading properties...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="card bg-red-50 border-red-200 text-center py-8">
            <AlertCircle className="w-8 h-8 text-red-600 mx-auto mb-3" />
            <p className="text-red-800 mb-4">{error}</p>
            <button onClick={fetchProperties} className="btn-secondary">
              Try Again
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && properties.length === 0 && (
          <div className="card text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full mx-auto mb-4 flex items-center justify-center">
              <Home className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No properties yet</h3>
            <p className="text-gray-600 mb-6">
              Get started by uploading a floor plan or searching for a property address.
            </p>
            <Link to="/properties/new" className="btn-primary inline-flex items-center space-x-2">
              <Plus className="w-5 h-5" />
              <span>Create Your First Property</span>
            </Link>
          </div>
        )}

        {/* Properties Grid */}
        {!loading && !error && properties.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {properties.map((property) => (
              <PropertyCard key={property.id} property={property} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

export default Dashboard
