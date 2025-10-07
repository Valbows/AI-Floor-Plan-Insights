import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Home, Plus, LogOut, Bed, Bath, Maximize, Clock, AlertCircle, CheckCircle, Loader, Search, SlidersHorizontal, ChevronLeft, ChevronRight } from 'lucide-react'
import axios from 'axios'

const StatusBadge = ({ status }) => {
  const statusConfig = {
    processing: {
      color: 'bg-white border-2 border-blue-500 text-blue-600 shadow-sm',
      icon: <Clock className="w-3 h-3" />,
      text: 'Processing',
      pulse: true
    },
    parsing_complete: {
      color: 'bg-white border-2 border-amber-500 text-amber-600 shadow-sm',
      icon: <Loader className="w-3 h-3 animate-spin" />,
      text: 'Analyzing',
      pulse: true
    },
    enrichment_complete: {
      color: 'bg-white border-2 border-purple-500 text-purple-600 shadow-sm',
      icon: <Loader className="w-3 h-3 animate-spin" />,
      text: 'Finalizing',
      pulse: true
    },
    complete: {
      color: 'bg-white border-2 border-green-500 text-green-600 shadow-sm',
      icon: <CheckCircle className="w-3 h-3" />,
      text: 'Ready',
      pulse: false
    },
    failed: {
      color: 'bg-white border-2 border-red-500 text-red-600 shadow-sm',
      icon: <AlertCircle className="w-3 h-3" />,
      text: 'Error',
      pulse: false
    }
  }

  const config = statusConfig[status] || statusConfig.processing

  return (
    <span className={`inline-flex items-center space-x-1 px-3 py-1.5 rounded-full text-xs font-semibold ${config.color} ${config.pulse ? 'animate-pulse' : ''}`}>
      {config.icon}
      <span>{config.text}</span>
    </span>
  )
}

const PropertyCard = ({ property }) => {
  const navigate = useNavigate()
  const extractedData = property.extracted_data || {}
  const marketData = property.market_insights || {}
  const address = extractedData.address || property.address || 'Property Address'
  const price = marketData.price_estimate?.estimated_value || 0
  const sqft = extractedData.square_footage || 0
  const bedrooms = extractedData.bedrooms || 0
  const bathrooms = extractedData.bathrooms || 0
  const pricePerSqft = sqft > 0 && price > 0 ? Math.round(price / sqft) : 0
  const investmentScore = marketData.investment_analysis?.investment_score || 0

  return (
    <div
      onClick={() => navigate(`/properties/${property.id}`)}
      className="bg-white rounded-lg overflow-hidden hover:shadow-lg transition-all duration-200 cursor-pointer border border-gray-200"
    >
      {/* Status Tags - Top */}
      <div className="p-4 pb-2">
        <div className="flex justify-between items-start mb-3">
          <div className="flex gap-2 flex-wrap">
            {bedrooms > 0 && (
              <span className="px-2 py-1 border border-gray-300 text-gray-700 text-xs rounded-full font-medium flex items-center gap-1">
                <Bed className="w-3 h-3 text-gray-700" />
                {bedrooms} Room{bedrooms !== 1 ? 's' : ''}
              </span>
            )}
            {bathrooms > 0 && (
              <span className="px-2 py-1 border border-gray-300 text-gray-700 text-xs rounded-full font-medium flex items-center gap-1">
                <Bath className="w-3 h-3 text-gray-700" />
                {bathrooms} Bath{bathrooms !== 1 ? 's' : ''}
              </span>
            )}
          </div>
          <StatusBadge status={property.status} />
        </div>
      </div>

      {/* Floor Plan Image */}
      <div className="relative h-44 bg-gray-50 overflow-hidden mx-4 mb-4 rounded-lg flex items-center justify-center">
        {property.image_url ? (
          <img
            src={property.image_url}
            alt={`Floor plan for ${address}`}
            className="max-w-full max-h-full object-contain"
            onError={(e) => {
              e.target.style.display = 'none'
            }}
          />
        ) : (
          <div className="text-center">
            <Home className="w-12 h-12 text-gray-300 mx-auto mb-2" />
            <p className="text-xs text-gray-400">Floor plan pending</p>
          </div>
        )}
      </div>

      <div className="px-4 pb-4">
        {/* Property Address */}
        <div className="mb-2">
          <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Property</p>
          <h3 className="text-base font-semibold text-gray-900 line-clamp-2 leading-tight">
            {address}
          </h3>
        </div>

        {/* Property Details */}
        <div className="space-y-2 mb-3">
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-600">Size:</span>
            <span className="font-medium text-gray-900">
              {sqft > 0 ? `${sqft.toLocaleString()} sq ft` : 'Analyzing...'}
            </span>
          </div>
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-600">Layout:</span>
            <span className="font-medium text-gray-900 truncate ml-2">
              {extractedData.layout_type || 'Analyzing...'}
            </span>
          </div>
          {investmentScore > 0 && (
            <div className="flex justify-between items-center text-sm">
              <span className="text-gray-600">Investment Score:</span>
              <span className={`font-medium ${
                investmentScore >= 70 ? 'text-green-600' : 
                investmentScore >= 50 ? 'text-yellow-600' : 'text-red-600'
              }`}>
                {investmentScore}/100
              </span>
            </div>
          )}
        </div>

        {/* Price Section */}
        <div className="border-t border-gray-100 pt-3">
          <div className="flex justify-between items-center mb-1">
            <span className="text-lg font-bold text-gray-900">
              {price > 0 ? `$${price.toLocaleString()}` : 'Analyzing price...'}
            </span>
            {pricePerSqft > 0 && (
              <span className="text-sm text-gray-600">
                ${pricePerSqft}/sq ft
              </span>
            )}
          </div>
          
          {/* Analysis Status */}
          <div className="flex justify-between items-center text-xs text-gray-500">
            <span>Added {new Date(property.created_at).toLocaleDateString()}</span>
            <span className="capitalize">
              {property.status === 'complete' ? 'Analysis Complete' : 'Processing...'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

const Dashboard = () => {
  const { user, logout } = useAuth()
  const [properties, setProperties] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [currentPage, setCurrentPage] = useState(1)
  const [sortBy, setSortBy] = useState('newest')

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

  // Filter and search properties
  const filteredProperties = properties.filter(property => {
    const extractedData = property.extracted_data || {}
    const address = extractedData.address || property.address || ''
    const matchesSearch = address.toLowerCase().includes(searchTerm.toLowerCase())
    
    if (filterType === 'all') return matchesSearch
    if (filterType === 'complete') return matchesSearch && property.status === 'complete'
    if (filterType === 'processing') return matchesSearch && ['processing', 'parsing_complete', 'enrichment_complete'].includes(property.status)
    return matchesSearch
  })


  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Home className="w-5 h-5 text-gray-700" />
              <span className="text-lg font-medium text-gray-900">FP AI</span>
            </div>
            <div className="flex items-center space-x-6">
              <span className="text-sm text-gray-600">{user?.email}</span>
              <button
                onClick={logout}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-16">
        {/* Centered Title */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-light text-gray-900 mb-8 leading-tight">
            My Properties
          </h1>
          
          {/* Filter Buttons */}
          <div className="flex items-center justify-center space-x-4 mb-8">
            <button
              onClick={() => setFilterType('all')}
              className={`px-6 py-2 rounded-full text-sm transition-colors ${
                filterType === 'all'
                  ? 'bg-gray-900 text-white'
                  : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
              }`}
            >
              All Properties
            </button>
            <button
              onClick={() => setFilterType('complete')}
              className={`px-6 py-2 rounded-full text-sm transition-colors ${
                filterType === 'complete'
                  ? 'bg-gray-900 text-white'
                  : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
              }`}
            >
              Analyzed
            </button>
            <button
              onClick={() => setFilterType('processing')}
              className={`px-6 py-2 rounded-full text-sm transition-colors ${
                filterType === 'processing'
                  ? 'bg-gray-900 text-white'
                  : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
              }`}
            >
              Processing
            </button>
          </div>

          {/* Stats */}
          <div className="flex items-center justify-center space-x-8 text-sm text-gray-600 mb-8">
            <span>{filteredProperties.length} properties</span>
            <span>from ${properties.reduce((sum, p) => sum + (p.market_insights?.price_estimate?.estimated_value || 0), 0).toLocaleString()}</span>
          </div>

          {/* Add Property Button */}
          <Link 
            to="/properties/new"
            className="inline-flex items-center space-x-2 bg-gray-900 text-white px-6 py-3 rounded-lg hover:bg-gray-800 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Property</span>
          </Link>
        </div>

        {/* View Toggle */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <select className="border border-gray-300 rounded px-3 py-2 text-sm bg-white">
              <option>Sort by newest</option>
              <option>Sort by status</option>
              <option>Sort by price</option>
              <option>Sort by size</option>
              <option>Sort by bedrooms</option>
            </select>
          </div>
          <div className="flex items-center space-x-2">
            <button className="p-2 bg-gray-900 text-white rounded">
              <div className="grid grid-cols-2 gap-0.5 w-4 h-4">
                <div className="bg-current rounded-sm"></div>
                <div className="bg-current rounded-sm"></div>
                <div className="bg-current rounded-sm"></div>
                <div className="bg-current rounded-sm"></div>
              </div>
            </button>
            <button className="p-2 text-gray-400 hover:text-gray-600 rounded">
              <div className="flex flex-col space-y-1 w-4 h-4">
                <div className="h-0.5 bg-current rounded"></div>
                <div className="h-0.5 bg-current rounded"></div>
                <div className="h-0.5 bg-current rounded"></div>
              </div>
            </button>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-20">
            <Loader className="w-8 h-8 text-gray-400 animate-spin" />
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-white rounded-lg p-8 text-center">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <p className="text-gray-800 mb-4">{error}</p>
            <button 
              onClick={fetchProperties} 
              className="bg-gray-900 text-white px-6 py-2 rounded-md hover:bg-gray-800 transition-colors"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && properties.length === 0 && (
          <div className="bg-white rounded-lg p-12 text-center">
            <div className="w-20 h-20 bg-gray-100 rounded-full mx-auto mb-6 flex items-center justify-center">
              <Home className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-xl font-medium text-gray-900 mb-3">No properties yet</h3>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              Get started by uploading a floor plan or adding a new property to your portfolio.
            </p>
            <Link 
              to="/properties/new" 
              className="bg-gray-900 text-white px-8 py-3 rounded-md hover:bg-gray-800 transition-colors inline-flex items-center space-x-2"
            >
              <Plus className="w-5 h-5" />
              <span>Add Your First Property</span>
            </Link>
          </div>
        )}


        {/* Properties Grid */}
        {!loading && !error && filteredProperties.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {filteredProperties.map((property) => (
              <PropertyCard key={property.id} property={property} />
            ))}
          </div>
        )}

        {/* No Search Results */}
        {!loading && !error && properties.length > 0 && filteredProperties.length === 0 && (
          <div className="bg-white rounded-lg p-12 text-center">
            <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No properties found</h3>
            <p className="text-gray-600 mb-6">
              Try adjusting your search terms or filters to find what you're looking for.
            </p>
            <button 
              onClick={() => {
                setSearchTerm('')
                setFilterType('all')
              }}
              className="text-gray-900 hover:text-gray-700 font-medium"
            >
              Clear filters
            </button>
          </div>
        )}

      </main>
      
      {/* Footer */}
      <footer className="mt-20 py-16 bg-black w-full">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
            {/* Company Info */}
            <div>
              <div className="flex items-center space-x-2 mb-6">
                <Home className="w-8 h-8 text-white" />
                <span className="text-2xl font-bold text-white">FP AI</span>
              </div>
              <div className="text-gray-400 text-sm space-y-2 mb-6">
                <p>AI-Powered Real Estate Analytics</p>
                <p>San Francisco, CA 94105</p>
                <p>United States</p>
              </div>
              
              {/* Social Media */}
              <div className="flex space-x-4">
                <div className="w-8 h-8 bg-gray-800 rounded flex items-center justify-center hover:bg-gray-700 transition-colors cursor-pointer">
                  <span className="text-white text-xs font-bold">in</span>
                </div>
                <div className="w-8 h-8 bg-gray-800 rounded flex items-center justify-center hover:bg-gray-700 transition-colors cursor-pointer">
                  <span className="text-white text-xs font-bold">tw</span>
                </div>
                <div className="w-8 h-8 bg-gray-800 rounded flex items-center justify-center hover:bg-gray-700 transition-colors cursor-pointer">
                  <span className="text-white text-xs font-bold">yt</span>
                </div>
              </div>
            </div>

            {/* Services */}
            <div>
              <div className="space-y-3">
                <h4 className="text-red-500 font-bold text-lg uppercase tracking-wide">FLOOR PLAN</h4>
                <h4 className="text-red-500 font-bold text-lg uppercase tracking-wide">ANALYSIS</h4>
                <h4 className="text-red-500 font-bold text-lg uppercase tracking-wide">MARKET INSIGHTS</h4>
                <h4 className="text-white font-bold text-lg uppercase tracking-wide">LISTING GENERATION</h4>
                <h4 className="text-white font-bold text-lg uppercase tracking-wide">AGENT DASHBOARD</h4>
                <h4 className="text-white font-bold text-lg uppercase tracking-wide">API ACCESS</h4>
                <h4 className="text-white font-bold text-lg uppercase tracking-wide">CONTACT US</h4>
              </div>
            </div>

            {/* Legal & Compliance */}
            <div>
              <div className="text-gray-400 text-sm space-y-3">
                <p>Real Estate Data Privacy Notice & Terms</p>
                <p>MLS Data Usage Rights & Reasonable Accommodations</p>
                <p>Standardized Operating Procedures</p>
                <p>AI Model Accuracy Disclaimer</p>
              </div>
              
              {/* CTA Button */}
              <div className="mt-8">
                <Link 
                  to="/properties/new"
                  className="inline-block bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-6 rounded-full transition-colors"
                >
                  Try Demo
                </Link>
              </div>
            </div>

            {/* Newsletter */}
            <div>
              <h4 className="text-white font-bold text-lg mb-4 uppercase tracking-wide">STAY IN THE LOOP</h4>
              <div className="flex mb-4">
                <input
                  type="email"
                  placeholder="Enter your email"
                  className="flex-1 bg-transparent border-b border-gray-600 text-white placeholder-gray-400 py-2 focus:outline-none focus:border-white transition-colors"
                />
                <button className="ml-4 w-10 h-10 bg-gray-800 rounded flex items-center justify-center hover:bg-gray-700 transition-colors">
                  <span className="text-white">→</span>
                </button>
              </div>
              <p className="text-gray-400 text-xs">
                Get updates on new AI features, market data integrations, and real estate technology insights.
              </p>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="mt-12 pt-8 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center text-sm text-gray-400">
            <p>2025 FP AI Technologies®. All Rights Reserved.</p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a href="#" className="hover:text-white transition-colors">PRIVACY POLICY</a>
              <a href="#" className="hover:text-white transition-colors">TERMS OF SERVICE</a>
              <div className="border border-gray-600 px-3 py-1 text-xs">
                Crafted by FP AI Technologies
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Dashboard
