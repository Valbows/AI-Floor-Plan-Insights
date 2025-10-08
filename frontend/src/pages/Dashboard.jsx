import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Home, Plus, LogOut, Bed, Bath, Maximize, Clock, AlertCircle, CheckCircle, Loader, Search, SlidersHorizontal, ChevronLeft, ChevronRight, ChevronUp, ChevronDown, Maximize2, Minimize2 } from 'lucide-react'
import axios from 'axios'
import Chatbot from '../components/Chatbot'

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

const PropertyTable = ({ properties, sortConfig, onSort }) => {
  const navigate = useNavigate()
  const [expandedRows, setExpandedRows] = useState(new Set())
  
  const toggleExpand = (propertyId, e) => {
    e.stopPropagation()
    setExpandedRows(prev => {
      const newSet = new Set(prev)
      if (newSet.has(propertyId)) {
        newSet.delete(propertyId)
      } else {
        newSet.add(propertyId)
      }
      return newSet
    })
  }
  
  const SortableHeader = ({ column, label, align = 'left', width, style }) => {
    const isSorted = sortConfig.key === column
    const alignClass = align === 'center' ? 'text-center' : align === 'right' ? 'text-right' : 'text-left'
    
    return (
      <th 
        className={`${alignClass} py-3 px-6 text-xs font-semibold text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors select-none ${width || ''}`}
        onClick={() => onSort(column)}
        style={style}
      >
        <div className={`inline-flex items-center gap-1 ${align === 'center' ? 'justify-center' : align === 'right' ? 'justify-end' : 'justify-start'}`}>
          <span className="whitespace-nowrap">{label}</span>
          <div className="w-3 h-3 flex-shrink-0 flex items-center justify-center">
            {isSorted ? (
              sortConfig.direction === 'asc' ? 
                <ChevronUp className="w-3 h-3" /> : 
                <ChevronDown className="w-3 h-3" />
            ) : (
              <div className="w-3 h-3" />
            )}
          </div>
        </div>
      </th>
    )
  }
  
  return (
    <div className="bg-white rounded-lg overflow-hidden border border-gray-200">
      <div className="overflow-x-auto">
        <table className="w-full" style={{tableLayout: 'fixed'}}>
        <thead>
          <tr className="border-b border-gray-200 bg-gray-50">
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider" style={{width: '80px'}}>Floor Plan</th>
            <SortableHeader column="address" label="Address" align="left" style={{width: '200px', maxWidth: '200px'}} />
            <SortableHeader column="bedrooms" label="Beds" align="center" style={{width: '60px', maxWidth: '60px'}} />
            <SortableHeader column="bathrooms" label="Baths" align="center" style={{width: '60px', maxWidth: '60px'}} />
            <th 
              className="text-left py-3 px-6 text-xs font-semibold text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors select-none"
              style={{width: '200px', maxWidth: '200px'}}
              onClick={() => onSort('layout')}
            >
              <div className="inline-flex items-center gap-1">
                <span className="whitespace-nowrap">Layout</span>
                <div className="w-3 h-3 flex-shrink-0 flex items-center justify-center">
                  {sortConfig.key === 'layout' ? (
                    sortConfig.direction === 'asc' ? 
                      <ChevronUp className="w-3 h-3" /> : 
                      <ChevronDown className="w-3 h-3" />
                  ) : (
                    <div className="w-3 h-3" />
                  )}
                </div>
              </div>
            </th>
            <SortableHeader column="size" label="Size" align="right" style={{width: '100px', maxWidth: '100px'}} />
            <SortableHeader column="price" label="Price" align="right" width="w-32" />
            <SortableHeader column="date" label="Date Added" align="left" style={{width: '90px', maxWidth: '90px'}} />
            <SortableHeader column="status" label="Status" align="center" width="w-36" />
            <th className="text-center py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider" style={{width: '80px'}}>Details</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {properties.map((property) => {
            const extractedData = property.extracted_data || {}
            const marketData = extractedData.market_insights || {}
            const address = extractedData.address || property.address || 'Property Address'
            const price = marketData.price_estimate?.estimated_value || 0
            const sqft = extractedData.square_footage || 0
            const bedrooms = extractedData.bedrooms || 0
            const bathrooms = extractedData.bathrooms || 0
            
            const isExpanded = expandedRows.has(property.id)
            
            return (
              <React.Fragment key={property.id}>
                <tr 
                  onClick={() => navigate(`/properties/${property.id}`)}
                  className="hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <td className="py-4 px-4" style={{width: '80px', minWidth: '80px'}}>
                    <div className="w-12 h-12 bg-gray-50 rounded border border-gray-200 flex items-center justify-center flex-shrink-0">
                      {property.image_url ? (
                        <img
                          src={property.image_url}
                          alt="Floor plan"
                          className="w-full h-full object-contain p-1"
                        />
                      ) : (
                        <Home className="w-5 h-5 text-gray-300" />
                      )}
                    </div>
                  </td>
                  <td className="py-4 px-4" style={{width: '200px', minWidth: '200px'}}>
                    <p className="text-sm font-medium text-gray-900 leading-tight">{address}</p>
                  </td>
                  <td className="py-4 px-4 text-center whitespace-nowrap" style={{width: '60px', minWidth: '60px'}}>
                    <span className="text-sm text-gray-900">{bedrooms || '-'}</span>
                  </td>
                  <td className="py-4 px-4 text-center whitespace-nowrap" style={{width: '60px', minWidth: '60px'}}>
                    <span className="text-sm text-gray-900">{bathrooms || '-'}</span>
                  </td>
                  <td className="py-4 px-4" style={{width: '200px', maxWidth: '200px'}}>
                    <span className="text-sm text-gray-700 line-clamp-2">{extractedData.layout_type || '-'}</span>
                  </td>
                  <td className="py-4 px-4 text-right whitespace-nowrap" style={{width: '100px', minWidth: '100px'}}>
                    <span className="text-sm text-gray-900">{sqft > 0 ? `${sqft.toLocaleString()} sq ft` : '-'}</span>
                  </td>
                  <td className="py-4 px-4 text-right whitespace-nowrap" style={{width: '130px', minWidth: '130px'}}>
                    <span className="text-sm font-semibold text-gray-900">{price > 0 ? `$${price.toLocaleString()}` : '-'}</span>
                  </td>
                  <td className="py-4 px-4 whitespace-nowrap" style={{width: '90px', minWidth: '90px'}}>
                    <span className="text-xs text-gray-500">{new Date(property.created_at).toLocaleDateString()}</span>
                  </td>
                  <td className="py-4 px-4 whitespace-nowrap" style={{width: '150px', minWidth: '150px'}}>
                    <div className="flex justify-center">
                      <StatusBadge status={property.status} />
                    </div>
                  </td>
                  <td className="py-4 px-4 text-center" style={{width: '80px', minWidth: '80px'}}>
                    <button
                      onClick={(e) => toggleExpand(property.id, e)}
                      className="p-1 hover:bg-gray-200 rounded transition-colors"
                      title={isExpanded ? 'Collapse' : 'Expand details'}
                    >
                      {isExpanded ? <Minimize2 className="w-4 h-4 text-gray-600" /> : <Maximize2 className="w-4 h-4 text-gray-600" />}
                    </button>
                  </td>
                </tr>
                {isExpanded && (
                  <tr className="bg-gray-50">
                    <td colSpan="10" className="py-4 px-6">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-semibold text-gray-700">Full Address:</span>
                          <p className="text-gray-900 mt-1">{address}</p>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-700">Layout Type:</span>
                          <p className="text-gray-900 mt-1">{extractedData.layout_type || 'Not specified'}</p>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-700">Property Details:</span>
                          <p className="text-gray-900 mt-1">{bedrooms} Beds • {bathrooms} Baths • {sqft > 0 ? `${sqft.toLocaleString()} sq ft` : 'Size pending'}</p>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-700">Estimated Value:</span>
                          <p className="text-gray-900 mt-1 font-semibold">{price > 0 ? `$${price.toLocaleString()}` : 'Analyzing...'}</p>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            )
          })}
        </tbody>
        </table>
      </div>
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 text-xs text-gray-500 text-center">
        Click <Maximize2 className="w-3 h-3 inline" /> to expand row details • Scroll horizontally if needed
      </div>
    </div>
  )
}

const PropertyCard = ({ property }) => {
  const navigate = useNavigate()
  const extractedData = property.extracted_data || {}
  const marketData = extractedData.market_insights || {}
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
  const [viewMode, setViewMode] = useState('grid') // 'grid' or 'list'
  const [listItemsToShow, setListItemsToShow] = useState(10)
  const [sortConfig, setSortConfig] = useState({ key: 'date', direction: 'desc' })

  useEffect(() => {
    fetchProperties()
  }, [])

  const fetchProperties = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Get token from localStorage
      const token = localStorage.getItem('token')
      
      if (!token) {
        setError('Authentication required. Please log in.')
        setLoading(false)
        return
      }
      
      // Make request with explicit Authorization header
      const response = await axios.get('/api/properties', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      setProperties(response.data.properties || [])
    } catch (err) {
      console.error('Error fetching properties:', err)
      if (err.response?.status === 401) {
        setError('Session expired. Please log in again.')
        // Optional: Clear token and redirect to login
        localStorage.removeItem('token')
        window.location.href = '/login'
      } else {
        setError('Failed to load properties. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  // Filter and search properties
  const filteredProperties = properties.filter(property => {
    const extractedData = property.extracted_data || {}
    const address = extractedData.address || property.address || ''
    const matchesSearch = address.toLowerCase().includes(searchTerm.toLowerCase())
    
    // Only show properties with extracted data (hide those still in initial processing)
    const hasBasicData = extractedData.bedrooms || extractedData.bathrooms || extractedData.square_footage
    
    return matchesSearch && hasBasicData
  })

  // Sort properties
  const sortedProperties = [...filteredProperties].sort((a, b) => {
    const aData = a.extracted_data || {}
    const bData = b.extracted_data || {}
    const aMarket = a.market_insights || {}
    const bMarket = b.market_insights || {}
    
    let aValue, bValue
    
    switch (sortConfig.key) {
      case 'address':
        aValue = (aData.address || a.address || '').toLowerCase()
        bValue = (bData.address || b.address || '').toLowerCase()
        break
      case 'bedrooms':
        aValue = aData.bedrooms || 0
        bValue = bData.bedrooms || 0
        break
      case 'bathrooms':
        aValue = aData.bathrooms || 0
        bValue = bData.bathrooms || 0
        break
      case 'layout':
        aValue = (aData.layout_type || '').toLowerCase()
        bValue = (bData.layout_type || '').toLowerCase()
        break
      case 'size':
        aValue = aData.square_footage || 0
        bValue = bData.square_footage || 0
        break
      case 'price':
        aValue = aMarket.price_estimate?.estimated_value || 0
        bValue = bMarket.price_estimate?.estimated_value || 0
        break
      case 'date':
        aValue = new Date(a.created_at).getTime()
        bValue = new Date(b.created_at).getTime()
        break
      case 'status':
        const statusOrder = { complete: 4, enrichment_complete: 3, parsing_complete: 2, processing: 1, failed: 0 }
        aValue = statusOrder[a.status] || 0
        bValue = statusOrder[b.status] || 0
        break
      default:
        return 0
    }
    
    if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1
    if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1
    return 0
  })

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
  }


  return (
    <div className="min-h-screen" style={{background: '#F6F1EB'}}>
      {/* Header */}
      <header className="bg-black border-b-4" style={{borderBottomColor: '#FF5959'}}>
        <div className="max-w-[1400px] mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Home className="w-5 h-5" style={{color: '#FF5959'}} />
              <span className="text-lg font-black uppercase tracking-tight text-white">FP AI</span>
            </div>
            <div className="flex items-center space-x-6">
              <span className="text-sm text-white">{user?.email}</span>
              <button
                onClick={logout}
                className="transition-colors"
                style={{color: '#FF5959'}}
                onMouseEnter={(e) => e.currentTarget.style.color = '#E54545'}
                onMouseLeave={(e) => e.currentTarget.style.color = '#FF5959'}
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1400px] mx-auto px-4 py-16">
        {/* Centered Title */}
        <div className="text-center mb-16">
          <h1 className="text-6xl font-black uppercase tracking-tight mb-2" style={{color: '#000000', letterSpacing: '-2px', lineHeight: '0.95'}}>
            MY <span style={{color: '#FF5959'}}>PROPERTIES</span>
          </h1>
          <div className="w-24 h-1.5 mx-auto mb-8" style={{background: '#FF5959'}}></div>
          
          {/* Search Bar */}
          <div className="max-w-md mx-auto mb-8">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by address..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border-2 focus:outline-none focus:ring-2 focus:border-transparent"
                style={{borderColor: '#000000', borderRadius: '4px'}}
                onFocus={(e) => {e.target.style.borderColor = '#FF5959'; e.target.style.boxShadow = '0 0 0 2px rgba(255,89,89,0.2)'}}
                onBlur={(e) => {e.target.style.borderColor = '#000000'; e.target.style.boxShadow = 'none'}}
              />
            </div>
          </div>

          {/* Stats */}
          {filteredProperties.length > 0 && (
            <div className="flex items-center justify-center space-x-8 text-sm text-gray-600 mb-8">
              <span>{filteredProperties.length} {filteredProperties.length === 1 ? 'property' : 'properties'}</span>
              {filteredProperties.filter(p => p.status === 'complete').length > 0 && (
                <>
                  <span className="text-gray-400">•</span>
                  <span>Portfolio value: ${filteredProperties
                    .filter(p => p.status === 'complete')
                    .reduce((sum, p) => sum + (p.market_insights?.price_estimate?.estimated_value || 0), 0)
                    .toLocaleString()}
                  </span>
                </>
              )}
            </div>
          )}

          {/* Add Property Button */}
          <Link 
            to="/properties/new"
            className="inline-flex items-center space-x-2 text-white px-8 py-4 font-bold uppercase tracking-wide transition-all"
            style={{background: '#FF5959', borderRadius: '4px'}}
            onMouseEnter={(e) => {e.currentTarget.style.background = '#E54545'; e.currentTarget.style.transform = 'translateY(-1px)'; e.currentTarget.style.boxShadow = '0 4px 12px rgba(255,89,89,0.3)'}}
            onMouseLeave={(e) => {e.currentTarget.style.background = '#FF5959'; e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none'}}
          >
            <Plus className="w-4 h-4" />
            <span>Add Property</span>
          </Link>
        </div>

        {/* View Toggle */}
        {filteredProperties.length > 0 && (
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                Showing {viewMode === 'list' && sortedProperties.length > listItemsToShow 
                  ? `${listItemsToShow} of ${sortedProperties.length}` 
                  : sortedProperties.length} {sortedProperties.length === 1 ? 'property' : 'properties'}
              </div>
            </div>
          <div className="flex items-center space-x-2">
            <button 
              onClick={() => setViewMode('grid')}
              className="p-2 transition-colors"
              style={{
                background: viewMode === 'grid' ? '#FF5959' : 'transparent',
                color: viewMode === 'grid' ? '#FFFFFF' : '#666666',
                borderRadius: '4px'
              }}
              onMouseEnter={(e) => {if (viewMode !== 'grid') e.currentTarget.style.color = '#000000'}}
              onMouseLeave={(e) => {if (viewMode !== 'grid') e.currentTarget.style.color = '#666666'}}
            >
              <div className="grid grid-cols-2 gap-0.5 w-4 h-4">
                <div className="bg-current rounded-sm"></div>
                <div className="bg-current rounded-sm"></div>
                <div className="bg-current rounded-sm"></div>
                <div className="bg-current rounded-sm"></div>
              </div>
            </button>
            <button 
              onClick={() => setViewMode('list')}
              className="p-2 transition-colors"
              style={{
                background: viewMode === 'list' ? '#FF5959' : 'transparent',
                color: viewMode === 'list' ? '#FFFFFF' : '#666666',
                borderRadius: '4px'
              }}
              onMouseEnter={(e) => {if (viewMode !== 'list') e.currentTarget.style.color = '#000000'}}
              onMouseLeave={(e) => {if (viewMode !== 'list') e.currentTarget.style.color = '#666666'}}
            >
              <div className="flex flex-col space-y-1 w-4 h-4">
                <div className="h-0.5 bg-current rounded"></div>
                <div className="h-0.5 bg-current rounded"></div>
                <div className="h-0.5 bg-current rounded"></div>
              </div>
            </button>
          </div>
          </div>
        )}

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
              className="text-white px-8 py-3 font-bold uppercase tracking-wide transition-all"
              style={{background: '#FF5959', borderRadius: '4px'}}
              onMouseEnter={(e) => {e.currentTarget.style.background = '#E54545'; e.currentTarget.style.transform = 'translateY(-1px)'}}
              onMouseLeave={(e) => {e.currentTarget.style.background = '#FF5959'; e.currentTarget.style.transform = 'translateY(0)'}}
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
              className="text-white px-8 py-4 font-bold uppercase tracking-wide transition-all inline-flex items-center space-x-2"
              style={{background: '#FF5959', borderRadius: '4px'}}
              onMouseEnter={(e) => {e.currentTarget.style.background = '#E54545'; e.currentTarget.style.transform = 'translateY(-1px)'; e.currentTarget.style.boxShadow = '0 4px 12px rgba(255,89,89,0.3)'}}
              onMouseLeave={(e) => {e.currentTarget.style.background = '#FF5959'; e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none'}}
            >
              <Plus className="w-5 h-5" />
              <span>Add Your First Property</span>
            </Link>
          </div>
        )}


        {/* Properties Grid View */}
        {!loading && !error && sortedProperties.length > 0 && viewMode === 'grid' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {sortedProperties.slice(0, listItemsToShow).map((property) => (
                <PropertyCard key={property.id} property={property} />
              ))}
            </div>
            
            {/* Load More Button */}
            {sortedProperties.length > listItemsToShow && (
              <div className="flex justify-center">
                <button
                  onClick={() => setListItemsToShow(prev => prev + 10)}
                  className="px-8 py-3 text-sm font-bold uppercase tracking-wide transition-all"
                  style={{background: 'transparent', color: '#000000', border: '3px solid #000000', borderRadius: '4px'}}
                  onMouseEnter={(e) => {e.currentTarget.style.background = '#000000'; e.currentTarget.style.color = '#FFFFFF'}}
                  onMouseLeave={(e) => {e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#000000'}}
                >
                  Load More ({sortedProperties.length - listItemsToShow} remaining)
                </button>
              </div>
            )}
          </div>
        )}

        {/* Properties Table/List View */}
        {!loading && !error && sortedProperties.length > 0 && viewMode === 'list' && (
          <div className="space-y-6">
            <PropertyTable 
              properties={sortedProperties.slice(0, listItemsToShow)} 
              sortConfig={sortConfig}
              onSort={handleSort}
            />
            
            {/* Load More Button */}
            {sortedProperties.length > listItemsToShow && (
              <div className="flex justify-center">
                <button
                  onClick={() => setListItemsToShow(prev => prev + 10)}
                  className="px-8 py-3 text-sm font-bold uppercase tracking-wide transition-all"
                  style={{background: 'transparent', color: '#000000', border: '3px solid #000000', borderRadius: '4px'}}
                  onMouseEnter={(e) => {e.currentTarget.style.background = '#000000'; e.currentTarget.style.color = '#FFFFFF'}}
                  onMouseLeave={(e) => {e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#000000'}}
                >
                  Load More ({sortedProperties.length - listItemsToShow} remaining)
                </button>
              </div>
            )}
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
      
      {/* Chatbot */}
      <Chatbot />
      
      {/* Footer */}
      <footer className="mt-20 py-16 bg-black w-full">
        <div className="max-w-[1400px] mx-auto px-4">
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
