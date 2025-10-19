import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { 
  Home, ArrowLeft, Bed, Bath, Maximize, Clock, CheckCircle, XCircle, Loader,
  DollarSign, TrendingUp, Building2, FileText, AlertCircle, Info,
  UtensilsCrossed, Wrench, Search, Copy, Star, Share2, Edit2, Save, X, Check, RefreshCw
} from 'lucide-react'
import axios from 'axios'
import Analytics from '../components/Analytics'

const AgentTools = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [property, setProperty] = useState(null)
  const [properties, setProperties] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('marketing')
  const [reEnriching, setReEnriching] = useState(false)
  const [showAllFeatures, setShowAllFeatures] = useState(false)
  
  // Share states
  const [showShareModal, setShowShareModal] = useState(false)
  const [shareableLink, setShareableLink] = useState(null)
  const [generatingLink, setGeneratingLink] = useState(false)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (id) {
      fetchProperty()
    } else {
      fetchProperties()
    }
  }, [id])

  const fetchProperties = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      if (!token) {
        setError('Authentication required')
        setLoading(false)
        return
      }

      const response = await axios.get('/api/properties', {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      setProperties(response.data.properties || [])
    } catch (err) {
      console.error('Error fetching properties:', err)
      setError('Failed to load properties')
    } finally {
      setLoading(false)
    }
  }

  const fetchProperty = async () => {
    try {
      setLoading(true)
      setError('')
      
      const token = localStorage.getItem('token')
      if (!token) {
        setError('Authentication required')
        setLoading(false)
        return
      }

      const response = await axios.get(`/api/properties/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      console.log('Agent Tools - Full API Response:', response)
      console.log('Agent Tools - response.data:', response.data)
      console.log('Agent Tools - response.data.property:', response.data.property)
      
      // Check if data is nested under 'property' key
      const propertyData = response.data.property || response.data
      console.log('Agent Tools - Using property data:', propertyData)
      console.log('Agent Tools - Property extracted_data:', propertyData.extracted_data)
      
      setProperty(propertyData)
    } catch (err) {
      console.error('Error fetching property:', err)
      setError(err.response?.data?.error || 'Failed to load property')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = async (text, label) => {
    try {
      await navigator.clipboard.writeText(text)
      alert(`${label} copied to clipboard!`)
    } catch (err) {
      console.error('Failed to copy:', err)
      alert('Failed to copy to clipboard')
    }
  }

  const handleGenerateLink = async () => {
    setGeneratingLink(true)
    setShareableLink(null)
    
    try {
      const token = localStorage.getItem('token')
      
      if (!token) {
        alert('Authentication required. Please log in again.')
        setGeneratingLink(false)
        return
      }
      
      // First try to get existing link
      try {
        const response = await axios.get(`/api/properties/${id}/shareable-link`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        setShareableLink(response.data)
      } catch (err) {
        // If no link exists, generate new one
        if (err.response?.status === 404) {
          const response = await axios.post(`/api/properties/${id}/generate-link`, {}, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          })
          setShareableLink(response.data)
        } else {
          throw err
        }
      }
    } catch (error) {
      console.error('Error generating link:', error)
      alert('Failed to generate shareable link')
    } finally {
      setGeneratingLink(false)
    }
  }

  const handleCopyLink = () => {
    if (shareableLink) {
      navigator.clipboard.writeText(shareableLink.shareable_url)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const openShareModal = async () => {
    setShowShareModal(true)
    await handleGenerateLink()
  }

  const handleReEnrich = async () => {
    setReEnriching(true)
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        alert('Authentication required')
        return
      }

      await axios.post(`/api/properties/${id}/re-enrich`, {}, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      alert('Re-enrichment started! This will take a moment...')
      
      // Reload property data after a few seconds
      setTimeout(() => {
        fetchProperty()
      }, 3000)
    } catch (error) {
      console.error('Error re-enriching:', error)
      alert('Failed to re-enrich property data')
    } finally {
      setReEnriching(false)
    }
  }

  // Property Selector View (when no ID is provided)
  if (!id) {
    const filteredProperties = properties.filter(property => {
      const extractedData = property.extracted_data || {}
      const address = extractedData.address || property.address || ''
      return address.toLowerCase().includes(searchTerm.toLowerCase())
    })

    return (
      <div className="min-h-screen" style={{background: '#F6F1EB'}}>
        {/* Header */}
        <div className="border-b-4" style={{background: '#FFFFFF', borderBottomColor: '#000000'}}>
          <div className="max-w-[1400px] mx-auto px-6 py-8">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-3 rounded" style={{background: '#FF5959'}}>
                <Wrench className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-black uppercase tracking-tight" style={{color: '#000000', letterSpacing: '-2px'}}>
                  Agent <span style={{color: '#FF5959'}}>Tools</span>
                </h1>
                <p className="text-sm mt-1" style={{color: '#666666'}}>Select a property to view professional management interface</p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <main className="max-w-[1400px] mx-auto px-6 py-12">
          {loading ? (
            <div className="flex justify-center items-center py-20">
              <Loader className="w-12 h-12 animate-spin" style={{color: '#FF5959'}} />
            </div>
          ) : (
            <>
              {/* Search Bar */}
              <div className="max-w-xl mx-auto mb-12">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search properties..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-12 pr-4 py-4 border-2 focus:outline-none text-lg"
                    style={{borderColor: '#000000', borderRadius: '8px'}}
                    onFocus={(e) => {e.target.style.borderColor = '#FF5959'; e.target.style.boxShadow = '0 0 0 3px rgba(255,89,89,0.1)'}}
                    onBlur={(e) => {e.target.style.borderColor = '#000000'; e.target.style.boxShadow = 'none'}}
                  />
                </div>
              </div>

              {/* Property Grid */}
              {filteredProperties.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredProperties.map((prop) => {
                    const extractedData = prop.extracted_data || {}
                    const marketData = extractedData.market_insights || {}
                    const address = extractedData.address || prop.address || 'Property Address'
                    const price = marketData.price_estimate?.estimated_value || 0

                    return (
                      <button
                        key={prop.id}
                        onClick={() => navigate(`/agent-tools/${prop.id}`)}
                        className="text-left rounded-lg overflow-hidden transition-all"
                        style={{background: '#FFFFFF', border: '2px solid #000000'}}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.transform = 'translateY(-4px)'
                          e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.15)'
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.transform = 'translateY(0)'
                          e.currentTarget.style.boxShadow = 'none'
                        }}
                      >
                        {/* Floor Plan Image */}
                        <div className="relative h-48 overflow-hidden flex items-center justify-center p-4" style={{background: '#F6F1EB'}}>
                          {prop.image_url ? (
                            <img
                              src={prop.image_url}
                              alt={`Floor plan for ${address}`}
                              className="max-w-full max-h-full object-contain"
                            />
                          ) : (
                            <Home className="w-16 h-16" style={{color: '#CCCCCC'}} />
                          )}
                        </div>

                        {/* Property Info */}
                        <div className="p-5">
                          <h3 className="text-lg font-black line-clamp-2 leading-tight mb-3" style={{color: '#000000'}}>
                            {address}
                          </h3>
                          
                          <div className="flex items-center gap-3 mb-4 text-sm" style={{color: '#666666'}}>
                            {extractedData.bedrooms > 0 && (
                              <div className="flex items-center gap-1">
                                <Bed className="w-4 h-4" style={{color: '#FF5959'}} />
                                <span className="font-bold" style={{color: '#000000'}}>{extractedData.bedrooms}</span>
                              </div>
                            )}
                            {extractedData.bathrooms > 0 && (
                              <div className="flex items-center gap-1">
                                <Bath className="w-4 h-4" style={{color: '#FF5959'}} />
                                <span className="font-bold" style={{color: '#000000'}}>{extractedData.bathrooms}</span>
                              </div>
                            )}
                            {extractedData.square_footage > 0 && (
                              <span className="font-bold" style={{color: '#000000'}}>{extractedData.square_footage.toLocaleString()} sq ft</span>
                            )}
                          </div>

                          <div className="pt-3" style={{borderTop: '2px solid #F6F1EB'}}>
                            <p className="text-2xl font-black" style={{color: '#FF5959'}}>
                              {price > 0 ? `$${price.toLocaleString()}` : 'Analyzing...'}
                            </p>
                          </div>
                        </div>
                      </button>
                    )
                  })}
                </div>
              ) : (
                <div className="text-center py-20">
                  <AlertCircle className="w-16 h-16 mx-auto mb-4" style={{color: '#CCCCCC'}} />
                  <h3 className="text-xl font-bold mb-2" style={{color: '#000000'}}>No properties found</h3>
                  <p className="text-sm mb-6" style={{color: '#666666'}}>
                    {searchTerm ? 'Try adjusting your search terms' : 'Add a property to get started'}
                  </p>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{background: '#F6F1EB'}}>
        <div className="text-center">
          <Loader className="w-12 h-12 animate-spin mx-auto mb-4" style={{color: '#FF5959'}} />
          <p className="text-lg font-bold" style={{color: '#000000'}}>Loading Agent Tools...</p>
        </div>
      </div>
    )
  }

  if (error || !property) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{background: '#F6F1EB'}}>
        <div className="text-center max-w-md">
          <AlertCircle className="w-16 h-16 mx-auto mb-4" style={{color: '#FF5959'}} />
          <p className="text-xl font-bold mb-4" style={{color: '#000000'}}>{error || 'Property not found'}</p>
          <button
            onClick={() => navigate('/agent-tools')}
            className="px-6 py-3 font-bold uppercase transition-all"
            style={{background: '#000000', color: '#FFFFFF', borderRadius: '4px'}}
            onMouseEnter={(e) => e.currentTarget.style.background = '#333333'}
            onMouseLeave={(e) => e.currentTarget.style.background = '#000000'}
          >
            Back to Agent Tools
          </button>
        </div>
      </div>
    )
  }

  const extracted = property.extracted_data || {}
  const marketData = extracted.market_insights || {}

  console.log('Agent Tools - Extracted data:', extracted)
  console.log('Agent Tools - Listing copy exists:', !!extracted.listing_copy)

  return (
    <div className="min-h-screen" style={{background: '#F6F1EB'}}>
      {/* Header */}
      <div className="border-b-4" style={{background: '#FFFFFF', borderBottomColor: '#000000'}}>
        <div className="max-w-[1400px] mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/agent-tools')}
                className="flex items-center space-x-2 transition-all px-4 py-2 rounded"
                style={{background: '#F6F1EB', color: '#000000'}}
                onMouseEnter={(e) => {e.currentTarget.style.background = '#000000'; e.currentTarget.style.color = '#FFFFFF'}}
                onMouseLeave={(e) => {e.currentTarget.style.background = '#F6F1EB'; e.currentTarget.style.color = '#000000'}}
              >
                <ArrowLeft className="w-4 h-4" />
                <span className="font-bold uppercase text-sm">Back</span>
              </button>
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded" style={{background: '#FF5959'}}>
                  <Wrench className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-black uppercase tracking-tight" style={{color: '#000000'}}>
                    Agent <span style={{color: '#FF5959'}}>Tools</span>
                  </h1>
                  <p className="text-sm" style={{color: '#666666'}}>Professional property management interface</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-[1400px] mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* LEFT COLUMN - Property Overview */}
          <div className="space-y-6">
            {/* Floor Plan Image */}
            <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
              <h3 className="text-xs font-bold uppercase mb-4" style={{color: '#666666', letterSpacing: '1px'}}>Floor Plan</h3>
              {property.image_url ? (
                <div className="relative rounded-lg overflow-hidden" style={{background: '#F6F1EB', padding: '20px'}}>
                  <img
                    src={property.image_url}
                    alt="Floor plan"
                    className="w-full h-auto object-contain"
                    style={{maxHeight: '400px'}}
                  />
                </div>
              ) : (
                <div className="flex items-center justify-center py-20" style={{background: '#F6F1EB', borderRadius: '8px'}}>
                  <Home className="w-16 h-16" style={{color: '#CCCCCC'}} />
                </div>
              )}
            </div>

            {/* Property Stats */}
            <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
              <h3 className="text-xs font-bold uppercase mb-4" style={{color: '#666666', letterSpacing: '1px'}}>Property Information</h3>
              <div className="space-y-4">
                <div>
                  <p className="text-xs font-bold uppercase mb-1" style={{color: '#666666', letterSpacing: '1px'}}>Address</p>
                  <p className="text-lg font-bold" style={{color: '#000000'}}>{extracted.address || 'Not specified'}</p>
                </div>
                <div className="grid grid-cols-3 gap-4 pt-4" style={{borderTop: '2px solid #F6F1EB'}}>
                  <div>
                    <p className="text-xs font-bold uppercase mb-1" style={{color: '#666666', letterSpacing: '1px'}}>Size</p>
                    <p className="text-2xl font-black" style={{color: '#000000'}}>{extracted.square_footage || 0}</p>
                    <p className="text-xs" style={{color: '#666666'}}>sq ft</p>
                  </div>
                  <div>
                    <p className="text-xs font-bold uppercase mb-1" style={{color: '#666666', letterSpacing: '1px'}}>Beds</p>
                    <p className="text-2xl font-black" style={{color: '#000000'}}>{extracted.bedrooms || 0}</p>
                  </div>
                  <div>
                    <p className="text-xs font-bold uppercase mb-1" style={{color: '#666666', letterSpacing: '1px'}}>Baths</p>
                    <p className="text-2xl font-black" style={{color: '#000000'}}>{extracted.bathrooms || 0}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Layout Type */}
            {extracted.layout_type && (
              <div className="rounded-lg p-4" style={{background: '#F6F1EB', border: '1px solid #E5E5E5'}}>
                <h3 className="text-xs font-bold uppercase mb-2" style={{color: '#666666', letterSpacing: '1px'}}>Layout Type</h3>
                <p className="text-sm leading-relaxed" style={{color: '#000000'}}>{extracted.layout_type}</p>
              </div>
            )}

            {/* Room Facilities */}
            {extracted.rooms && extracted.rooms.length > 0 && (
              <div className="rounded-lg p-4" style={{background: '#F6F1EB', border: '1px solid #E5E5E5'}}>
                <h3 className="text-xs font-bold uppercase mb-3" style={{color: '#666666', letterSpacing: '1px'}}>Room Facilities</h3>
                <div className="grid grid-cols-4 gap-2">
                  {extracted.rooms.slice(0, 8).map((room, index) => {
                    const getIcon = (type) => {
                      const lowerType = type.toLowerCase()
                      if (lowerType.includes('bedroom')) return <Bed className="w-full h-full" />
                      if (lowerType.includes('bath')) return <Bath className="w-full h-full" />
                      if (lowerType.includes('kitchen')) return <UtensilsCrossed className="w-full h-full" />
                      if (lowerType.includes('living') || lowerType.includes('dining')) return <Home className="w-full h-full" />
                      return <Maximize className="w-full h-full" />
                    }
                    
                    return (
                      <div 
                        key={index} 
                        className="flex flex-col items-center text-center p-2 rounded transition-colors" 
                        style={{background: '#FFFFFF'}} 
                        onMouseEnter={(e) => e.currentTarget.style.background = '#FFF5F5'} 
                        onMouseLeave={(e) => e.currentTarget.style.background = '#FFFFFF'}
                        title={room.type}
                      >
                        <div className="w-8 h-8 mb-1 flex items-center justify-center" style={{color: '#FF5959'}}>
                          {getIcon(room.type)}
                        </div>
                        <p className="text-xs font-medium truncate w-full" style={{color: '#000000'}}>{room.type}</p>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Data Sources + Re-run Button */}
            <div className="flex items-center justify-between rounded-lg p-3" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-black uppercase" style={{color: '#000000', letterSpacing: '1px'}}>Data Sources:</span>
                {extracted.data_sources ? (
                  <>
                    {extracted.data_sources.attom_property && (
                      <span className="px-2 py-1 text-[10px] font-bold uppercase" style={{border: '1px solid #000000', borderRadius: '9999px', color: '#000000'}}>Property Details</span>
                    )}
                    {extracted.data_sources.attom_avm && (
                      <span className="px-2 py-1 text-[10px] font-bold uppercase" style={{border: '1px solid #000000', borderRadius: '9999px', color: '#000000'}}>Market Valuation</span>
                    )}
                    {extracted.data_sources.attom_area && (
                      <span className="px-2 py-1 text-[10px] font-bold uppercase" style={{border: '1px solid #000000', borderRadius: '9999px', color: '#000000'}}>Neighborhood Data</span>
                    )}
                    {extracted.data_sources.parcel && (
                      <span className="px-2 py-1 text-[10px] font-bold uppercase" style={{border: '1px solid #000000', borderRadius: '9999px', color: '#000000'}}>Public Records</span>
                    )}
                    {extracted.data_sources.fallback && (
                      <span className="px-2 py-1 text-[10px] font-bold uppercase" style={{border: '1px solid #FF5959', borderRadius: '9999px', color: '#FF5959'}}>Fallback</span>
                    )}
                  </>
                ) : (
                  <span className="px-2 py-1 text-[10px] font-bold uppercase" style={{border: '1px solid #CCCCCC', borderRadius: '9999px', color: '#666666'}}>Unknown</span>
                )}
              </div>
              <button
                onClick={handleReEnrich}
                disabled={reEnriching}
                className="flex items-center space-x-1 px-2 py-1 text-xs font-bold uppercase"
                style={{border: '2px solid #000000', borderRadius: '6px', color: reEnriching ? '#666666' : '#000000', background: '#FFFFFF', cursor: reEnriching ? 'not-allowed' : 'pointer'}}
                onMouseEnter={(e) => { if (!reEnriching) { e.currentTarget.style.background = '#000000'; e.currentTarget.style.color = '#FFFFFF' } }}
                onMouseLeave={(e) => { if (!reEnriching) { e.currentTarget.style.background = '#FFFFFF'; e.currentTarget.style.color = '#000000' } }}
              >
                {reEnriching ? <Loader className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
                <span className="hidden sm:inline">{reEnriching ? 'Updating...' : 'Refresh'}</span>
              </button>
            </div>

            {/* Features */}
            {extracted.features && extracted.features.length > 0 && (
              <div className="rounded-lg p-4" style={{background: '#F6F1EB', border: '1px solid #E5E5E5'}}>
                <h3 className="text-xs font-bold uppercase mb-2" style={{color: '#666666', letterSpacing: '1px'}}>Features</h3>
                <ul className="space-y-1.5">
                  {extracted.features.slice(0, showAllFeatures ? extracted.features.length : 6).map((feature, index) => (
                    <li key={index} className="flex items-start text-sm">
                      <span className="mr-2" style={{color: '#FF5959'}}>•</span>
                      <span style={{color: '#000000'}}>{feature}</span>
                    </li>
                  ))}
                  {extracted.features.length > 6 && !showAllFeatures && (
                    <li>
                      <button
                        onClick={() => setShowAllFeatures(true)}
                        className="text-xs font-medium transition-all hover:underline cursor-pointer"
                        style={{color: '#FF5959'}}
                        onMouseEnter={(e) => e.currentTarget.style.color = '#E54545'}
                        onMouseLeave={(e) => e.currentTarget.style.color = '#FF5959'}
                      >
                        +{extracted.features.length - 6} more
                      </button>
                    </li>
                  )}
                  {showAllFeatures && extracted.features.length > 6 && (
                    <li>
                      <button
                        onClick={() => setShowAllFeatures(false)}
                        className="text-xs font-medium transition-all hover:underline cursor-pointer"
                        style={{color: '#666666'}}
                        onMouseEnter={(e) => e.currentTarget.style.color = '#000000'}
                        onMouseLeave={(e) => e.currentTarget.style.color = '#666666'}
                      >
                        Show less
                      </button>
                    </li>
                  )}
                </ul>
              </div>
            )}

            {/* Price Estimate */}
            {marketData.price_estimate && (
              <div className="rounded-lg p-6" style={{background: '#000000'}}>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-xs font-bold uppercase" style={{color: '#FFFFFF', letterSpacing: '1px'}}>Estimated Market Value</h3>
                  {marketData.price_estimate.confidence && (
                    <span className="px-2 py-1 text-xs font-bold uppercase" style={{
                      background: marketData.price_estimate.confidence === 'high' ? '#22C55E' : marketData.price_estimate.confidence === 'medium' ? '#F59E0B' : '#6B7280',
                      color: '#FFFFFF',
                      borderRadius: '4px'
                    }}>
                      {marketData.price_estimate.confidence}
                    </span>
                  )}
                </div>
                <p className="text-4xl font-black mb-2" style={{color: '#FF5959'}}>
                  {marketData.price_estimate.estimated_value 
                    ? `$${marketData.price_estimate.estimated_value.toLocaleString()}`
                    : 'Analyzing...'}
                </p>
                {marketData.price_estimate.price_range && (
                  <p className="text-sm" style={{color: '#CCCCCC'}}>
                    Range: ${marketData.price_estimate.price_range.min?.toLocaleString()} - ${marketData.price_estimate.price_range.max?.toLocaleString()}
                  </p>
                )}
              </div>
            )}

            {/* Comparable Properties */}
            {marketData.comparable_properties && marketData.comparable_properties.length > 0 && (
              <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                <h3 className="text-xs font-bold uppercase mb-4" style={{color: '#666666', letterSpacing: '1px'}}>
                  Comparable Properties
                </h3>
                <div className="space-y-3">
                  {marketData.comparable_properties.slice(0, 3).map((comp, index) => (
                    <div key={index} className="p-3 rounded" style={{background: '#F6F1EB'}}>
                      <div className="flex justify-between items-start mb-2">
                        <p className="text-sm font-bold flex-1" style={{color: '#000000'}}>{comp.address}</p>
                        <p className="text-sm font-black ml-2" style={{color: '#FF5959'}}>
                          ${comp.price?.toLocaleString()}
                        </p>
                      </div>
                      <div className="flex items-center space-x-3 text-xs" style={{color: '#666666'}}>
                        <span>{comp.bedrooms} beds</span>
                        <span>•</span>
                        <span>{comp.bathrooms} baths</span>
                        <span>•</span>
                        <span>{comp.square_footage?.toLocaleString()} sq ft</span>
                      </div>
                      {comp.distance && (
                        <p className="text-xs mt-1" style={{color: '#666666'}}>
                          {comp.distance} miles away
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Investment Analysis */}
            {marketData.investment_analysis && (
              <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                <h3 className="text-xs font-bold uppercase mb-4 flex items-center" style={{color: '#000000', letterSpacing: '1px'}}>
                  <Building2 className="w-4 h-4 mr-2" style={{color: '#FF5959'}} />
                  Investment Analysis
                </h3>
                {marketData.investment_analysis.investment_score && (
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium" style={{color: '#666666'}}>Investment Score</span>
                      <span className="text-3xl font-black" style={{color: '#000000'}}>
                        {marketData.investment_analysis.investment_score}<span className="text-lg" style={{color: '#666666'}}>/100</span>
                      </span>
                    </div>
                    <div className="w-full rounded-full h-3" style={{background: '#E5E5E5'}}>
                      <div 
                        className="h-3 rounded-full transition-all" 
                        style={{ width: `${marketData.investment_analysis.investment_score}%`, background: '#FF5959' }}
                      ></div>
                    </div>
                  </div>
                )}
                <div className="space-y-2 text-sm">
                  {marketData.investment_analysis.rental_potential && (
                    <div className="flex justify-between">
                      <span style={{color: '#666666'}}>Rental Potential:</span>
                      <span className="font-semibold capitalize" style={{color: '#000000'}}>
                        {marketData.investment_analysis.rental_potential}
                      </span>
                    </div>
                  )}
                  {marketData.investment_analysis.estimated_rental_income && (
                    <div className="flex justify-between">
                      <span style={{color: '#666666'}}>Est. Rental Income:</span>
                      <span className="font-semibold" style={{color: '#000000'}}>
                        ${marketData.investment_analysis.estimated_rental_income.toLocaleString()}/mo
                      </span>
                    </div>
                  )}
                  {marketData.investment_analysis.cap_rate && (
                    <div className="flex justify-between">
                      <span style={{color: '#666666'}}>Cap Rate:</span>
                      <span className="font-semibold" style={{color: '#000000'}}>
                        {marketData.investment_analysis.cap_rate}%
                      </span>
                    </div>
                  )}
                  {marketData.investment_analysis.roi_potential && (
                    <div className="flex justify-between">
                      <span style={{color: '#666666'}}>ROI Potential:</span>
                      <span className="font-semibold" style={{color: '#000000'}}>
                        {marketData.investment_analysis.roi_potential}
                      </span>
                    </div>
                  )}
                </div>
                {marketData.investment_analysis.opportunities?.length > 0 && (
                  <div className="mt-3 pt-3" style={{borderTop: '2px solid #F6F1EB'}}>
                    <p className="text-xs font-semibold mb-1" style={{color: '#000000'}}>Opportunities:</p>
                    <ul className="text-xs space-y-1" style={{color: '#666666'}}>
                      {marketData.investment_analysis.opportunities.map((opp, idx) => (
                        <li key={idx}>• {opp}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Market Trend */}
            {marketData.market_trend && (
              <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                <h3 className="text-xs font-bold uppercase mb-4" style={{color: '#666666', letterSpacing: '1px'}}>
                  Market Trend
                </h3>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  {marketData.market_trend.trend_direction && (
                    <div>
                      <p className="text-xs" style={{color: '#666666'}}>Direction</p>
                      <p className="font-semibold capitalize" style={{color: '#000000'}}>
                        {marketData.market_trend.trend_direction}
                      </p>
                    </div>
                  )}
                  {marketData.market_trend.buyer_demand && (
                    <div>
                      <p className="text-xs" style={{color: '#666666'}}>Buyer Demand</p>
                      <p className="font-semibold capitalize" style={{color: '#000000'}}>
                        {marketData.market_trend.buyer_demand}
                      </p>
                    </div>
                  )}
                  {marketData.market_trend.inventory_level && (
                    <div>
                      <p className="text-xs" style={{color: '#666666'}}>Inventory</p>
                      <p className="font-semibold capitalize" style={{color: '#000000'}}>
                        {marketData.market_trend.inventory_level}
                      </p>
                    </div>
                  )}
                  {marketData.market_trend.appreciation_rate && (
                    <div>
                      <p className="text-xs" style={{color: '#666666'}}>Appreciation</p>
                      <p className="font-semibold" style={{color: '#000000'}}>
                        {marketData.market_trend.appreciation_rate}%
                      </p>
                    </div>
                  )}
                </div>
                {marketData.market_trend.insights && (
                  <p className="text-xs mt-3 pt-3" style={{borderTop: '2px solid #F6F1EB', color: '#666666'}}>
                    {marketData.market_trend.insights}
                  </p>
                )}
              </div>
            )}

            {/* Neighborhood Insights */}
            {marketData.neighborhood_analysis && (
              <div className="rounded-lg p-6" style={{background: '#F6F1EB', border: '1px solid #E5E5E5'}}>
                <h3 className="text-xs font-bold uppercase mb-3" style={{color: '#666666', letterSpacing: '1px'}}>
                  Neighborhood Insights
                </h3>
                <div className="space-y-2">
                  {marketData.neighborhood_analysis.walkability_score && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm" style={{color: '#000000'}}>Walkability Score:</span>
                      <span className="text-lg font-black" style={{color: '#FF5959'}}>
                        {marketData.neighborhood_analysis.walkability_score}
                      </span>
                    </div>
                  )}
                  {marketData.neighborhood_analysis.transit_score && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm" style={{color: '#000000'}}>Transit Score:</span>
                      <span className="text-lg font-black" style={{color: '#FF5959'}}>
                        {marketData.neighborhood_analysis.transit_score}
                      </span>
                    </div>
                  )}
                  {marketData.neighborhood_analysis.median_home_value && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm" style={{color: '#000000'}}>Median Home Value:</span>
                      <span className="text-sm font-black" style={{color: '#000000'}}>
                        ${marketData.neighborhood_analysis.median_home_value.toLocaleString()}
                      </span>
                    </div>
                  )}
                  {marketData.neighborhood_analysis.median_household_income && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm" style={{color: '#000000'}}>Median Income:</span>
                      <span className="text-sm font-black" style={{color: '#000000'}}>
                        ${marketData.neighborhood_analysis.median_household_income.toLocaleString()}
                      </span>
                    </div>
                  )}
                  {marketData.neighborhood_analysis.population && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm" style={{color: '#000000'}}>Population:</span>
                      <span className="text-sm font-black" style={{color: '#000000'}}>
                        {marketData.neighborhood_analysis.population.toLocaleString()}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* RIGHT COLUMN - Tabbed Content (Marketing & Client Engagement) */}
          <div className="space-y-6">
            {/* Tab Navigation */}
            <div className="sticky top-0 z-40">
              <div className="flex space-x-2 p-1" style={{background: '#F6F1EB', borderRadius: '8px'}}>
                <button
                  onClick={() => setActiveTab('marketing')}
                  className="flex-1 px-4 py-3 font-bold uppercase text-xs transition-all"
                  style={{
                    background: activeTab === 'marketing' ? '#FF5959' : 'transparent',
                    color: activeTab === 'marketing' ? '#FFFFFF' : '#666666',
                    borderRadius: '6px',
                    letterSpacing: '1px'
                  }}
                  onMouseEnter={(e) => {
                    if (activeTab !== 'marketing') {
                      e.currentTarget.style.background = '#FFFFFF'
                      e.currentTarget.style.color = '#000000'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (activeTab !== 'marketing') {
                      e.currentTarget.style.background = 'transparent'
                      e.currentTarget.style.color = '#666666'
                    }
                  }}
                >
                  Marketing Content
                </button>
                <button
                  onClick={() => setActiveTab('analytics')}
                  className="flex-1 px-4 py-3 font-bold uppercase text-xs transition-all"
                  style={{
                    background: activeTab === 'analytics' ? '#FF5959' : 'transparent',
                    color: activeTab === 'analytics' ? '#FFFFFF' : '#666666',
                    borderRadius: '6px',
                    letterSpacing: '1px'
                  }}
                  onMouseEnter={(e) => {
                    if (activeTab !== 'analytics') {
                      e.currentTarget.style.background = '#FFFFFF'
                      e.currentTarget.style.color = '#000000'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (activeTab !== 'analytics') {
                      e.currentTarget.style.background = 'transparent'
                      e.currentTarget.style.color = '#666666'
                    }
                  }}
                >
                  Client Engagement
                </button>
              </div>
            </div>

            {/* Tab Content */}
            <div className="space-y-6">
              {activeTab === 'marketing' && (
                <div className="space-y-6">
                  {/* Marketing Content */}
                  {extracted.listing_copy ? (
                    <>
                      {/* Headline */}
                      <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                        <div className="flex items-center justify-between mb-3">
                          <h2 className="text-lg font-black uppercase flex items-center" style={{color: '#000000', letterSpacing: '1px'}}>
                            <FileText className="w-5 h-5 mr-2" style={{color: '#FF5959'}} />
                            Listing Headline
                          </h2>
                          <button
                            onClick={() => copyToClipboard(extracted.listing_copy.headline, 'Headline')}
                            className="p-2 transition"
                            style={{borderRadius: '4px', color: '#FF5959'}}
                            onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,89,89,0.1)'}
                            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                            title="Copy to clipboard"
                          >
                            <Copy className="w-4 h-4" />
                          </button>
                        </div>
                        <p className="text-xl font-bold" style={{color: '#000000'}}>
                          {extracted.listing_copy.headline}
                        </p>
                      </div>

                      {/* Description */}
                      <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                        <div className="flex items-center justify-between mb-3">
                          <h2 className="text-lg font-black uppercase" style={{color: '#000000', letterSpacing: '1px'}}>MLS Description</h2>
                          <button
                            onClick={() => copyToClipboard(extracted.listing_copy.description, 'Description')}
                            className="p-2 transition"
                            style={{borderRadius: '4px', color: '#FF5959'}}
                            onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,89,89,0.1)'}
                            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                            title="Copy to clipboard"
                          >
                            <Copy className="w-4 h-4" />
                          </button>
                        </div>
                        <p className="text-sm whitespace-pre-line leading-relaxed" style={{color: '#000000'}}>
                          {extracted.listing_copy.description}
                        </p>
                      </div>

                      {/* Highlights */}
                      {extracted.listing_copy.highlights?.length > 0 && (
                        <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                          <h2 className="text-lg font-black uppercase mb-3" style={{color: '#000000', letterSpacing: '1px'}}>Key Highlights</h2>
                          <ul className="space-y-2">
                            {extracted.listing_copy.highlights.map((highlight, idx) => (
                              <li key={idx} className="flex items-start text-sm">
                                <Star className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" style={{color: '#FF5959'}} />
                                <span style={{color: '#000000'}}>{highlight}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Social Media */}
                      {extracted.social_variants && (
                        <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                          <h2 className="text-lg font-black uppercase mb-4 flex items-center" style={{color: '#000000', letterSpacing: '1px'}}>
                            <Share2 className="w-5 h-5 mr-2" style={{color: '#FF5959'}} />
                            Social Media
                          </h2>
                          <div className="space-y-3">
                            {extracted.social_variants.instagram && (
                              <div className="rounded-lg p-4" style={{background: '#F6F1EB', border: '1px solid #E5E5E5'}}>
                                <div className="flex items-center justify-between mb-2">
                                  <span className="text-xs font-bold uppercase" style={{color: '#000000', letterSpacing: '1px'}}>Instagram</span>
                                  <button
                                    onClick={() => copyToClipboard(extracted.social_variants.instagram, 'Instagram caption')}
                                    className="p-1.5 transition-all"
                                    style={{color: '#FF5959', borderRadius: '4px'}}
                                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,89,89,0.1)'}
                                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                  >
                                    <Copy className="w-4 h-4" />
                                  </button>
                                </div>
                                <p className="text-sm leading-relaxed" style={{color: '#000000'}}>
                                  {extracted.social_variants.instagram}
                                </p>
                              </div>
                            )}
                            {extracted.social_variants.facebook && (
                              <div className="rounded-lg p-4" style={{background: '#F6F1EB', border: '1px solid #E5E5E5'}}>
                                <div className="flex items-center justify-between mb-2">
                                  <span className="text-xs font-bold uppercase" style={{color: '#000000', letterSpacing: '1px'}}>Facebook</span>
                                  <button
                                    onClick={() => copyToClipboard(extracted.social_variants.facebook, 'Facebook post')}
                                    className="p-1.5 transition-all"
                                    style={{color: '#FF5959', borderRadius: '4px'}}
                                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,89,89,0.1)'}
                                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                  >
                                    <Copy className="w-4 h-4" />
                                  </button>
                                </div>
                                <p className="text-sm leading-relaxed" style={{color: '#000000'}}>
                                  {extracted.social_variants.facebook}
                                </p>
                              </div>
                            )}
                            {extracted.social_variants.twitter && (
                              <div className="rounded-lg p-4" style={{background: '#F6F1EB', border: '1px solid #E5E5E5'}}>
                                <div className="flex items-center justify-between mb-2">
                                  <span className="text-xs font-bold uppercase" style={{color: '#000000', letterSpacing: '1px'}}>Twitter / X</span>
                                  <button
                                    onClick={() => copyToClipboard(extracted.social_variants.twitter, 'Tweet')}
                                    className="p-1.5 transition-all"
                                    style={{color: '#FF5959', borderRadius: '4px'}}
                                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,89,89,0.1)'}
                                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                  >
                                    <Copy className="w-4 h-4" />
                                  </button>
                                </div>
                                <p className="text-sm leading-relaxed" style={{color: '#000000'}}>
                                  {extracted.social_variants.twitter}
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* CTA & Email */}
                      <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                        <div className="space-y-4">
                          <div className="rounded-lg p-4" style={{background: '#F6F1EB', border: '1px solid #E5E5E5'}}>
                            <span className="text-xs font-bold uppercase block mb-2" style={{color: '#666666', letterSpacing: '1px'}}>Call to Action</span>
                            <p className="text-sm font-medium" style={{color: '#000000'}}>
                              {extracted.listing_copy.call_to_action}
                            </p>
                          </div>
                          {extracted.listing_copy.email_subject && (
                            <div className="rounded-lg p-4" style={{background: '#F6F1EB', border: '1px solid #E5E5E5'}}>
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-bold uppercase" style={{color: '#000000', letterSpacing: '1px'}}>Email Subject Line</span>
                                <button
                                  onClick={() => copyToClipboard(extracted.listing_copy.email_subject, 'Email subject')}
                                  className="p-1.5 transition-all"
                                  style={{color: '#FF5959', borderRadius: '4px'}}
                                  onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,89,89,0.1)'}
                                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                                >
                                  <Copy className="w-4 h-4" />
                                </button>
                              </div>
                              <p className="text-sm" style={{color: '#000000'}}>
                                {extracted.listing_copy.email_subject}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* SEO Keywords */}
                      {extracted.listing_copy.seo_keywords?.length > 0 && (
                        <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                          <h2 className="text-sm font-bold uppercase mb-3" style={{color: '#000000', letterSpacing: '1px'}}>SEO Keywords</h2>
                          <div className="flex flex-wrap gap-2">
                            {extracted.listing_copy.seo_keywords.map((keyword, idx) => (
                              <span key={idx} className="text-xs px-3 py-1.5 font-medium" style={{background: '#F6F1EB', color: '#000000', borderRadius: '4px', border: '1px solid #E5E5E5'}}>
                                {keyword}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="border border-gray-200 rounded-lg p-12 text-center">
                      <Loader className="w-12 h-12 text-orange-600 mx-auto mb-4 animate-spin" />
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Creating Marketing Content</h3>
                      <p className="text-sm text-gray-600 mb-4">Our AI is crafting compelling listing descriptions...</p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'analytics' && (
                <Analytics propertyId={id} />
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Floating Share Button - Sticky Side Box */}
      <button
        onClick={openShareModal}
        className="fixed text-white shadow-lg transition-all duration-200 z-40 flex flex-col items-center justify-center space-y-2"
        style={{
          background: '#FF5959',
          width: '80px',
          height: '100px',
          top: '50%',
          right: '0',
          transform: 'translateY(-50%)',
          borderTopLeftRadius: '12px',
          borderBottomLeftRadius: '12px',
          borderRight: 'none'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = '#E54545'
          e.currentTarget.style.width = '90px'
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = '#FF5959'
          e.currentTarget.style.width = '80px'
        }}
        title="Share Property"
      >
        <Share2 className="w-8 h-8" />
        <span className="text-xs font-black uppercase" style={{letterSpacing: '1px'}}>Share</span>
      </button>

      {/* Share Link Modal */}
      {showShareModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)'}}>
          <div className="bg-white max-w-lg w-full p-8" style={{borderRadius: '12px', boxShadow: '0 8px 24px rgba(0,0,0,0.2)', border: '2px solid #000000'}}>
            <div className="flex items-start justify-between mb-6">
              <div>
                <h3 className="text-2xl font-black uppercase mb-2" style={{color: '#000000', letterSpacing: '-1px'}}>Share <span style={{color: '#FF5959'}}>Property</span></h3>
                <p className="text-sm" style={{color: '#666666'}}>Generate a public link to share this property</p>
              </div>
              <button
                onClick={() => {
                  setShowShareModal(false)
                  setCopied(false)
                }}
                className="transition-colors p-1"
                style={{color: '#FF5959'}}
                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,89,89,0.1)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {generatingLink ? (
              <div className="text-center py-8">
                <Loader className="w-8 h-8 animate-spin mx-auto mb-4" style={{color: '#FF5959'}} />
                <p className="text-sm" style={{color: '#666666'}}>Generating shareable link...</p>
              </div>
            ) : shareableLink ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-bold uppercase mb-2" style={{color: '#000000', letterSpacing: '1px'}}>
                    Shareable Link
                  </label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={shareableLink.shareable_url}
                      readOnly
                      className="flex-1 px-4 py-2 text-sm focus:outline-none"
                      style={{border: '2px solid #000000', borderRadius: '4px', background: '#F6F1EB', color: '#000000'}}
                    />
                    <button
                      onClick={handleCopyLink}
                      className="px-4 py-2 transition-all flex items-center space-x-2 font-bold uppercase text-sm"
                      style={{
                        background: copied ? '#F0FDF4' : '#FF5959',
                        color: copied ? '#22C55E' : '#FFFFFF',
                        borderRadius: '4px',
                        letterSpacing: '1px'
                      }}
                      onMouseEnter={(e) => {if (!copied) {e.currentTarget.style.background = '#E54545'; e.currentTarget.style.transform = 'translateY(-1px)'}}}
                      onMouseLeave={(e) => {if (!copied) {e.currentTarget.style.background = '#FF5959'; e.currentTarget.style.transform = 'translateY(0)'}}}
                    >
                      {copied ? (
                        <>
                          <Check className="w-4 h-4" />
                          <span>Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

                <div className="rounded-lg p-4 space-y-2" style={{background: '#F6F1EB', border: '1px solid #E5E5E5'}}>
                  <div className="flex items-center justify-between text-sm">
                    <span style={{color: '#666666'}}>Expires:</span>
                    <span className="font-bold" style={{color: '#000000'}}>
                      {new Date(shareableLink.expires_at).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-xs" style={{color: '#666666'}}>
                    This link will remain active for 30 days. Anyone with this link can view the property details.
                  </p>
                </div>

                <div className="flex items-center justify-end space-x-3 pt-2">
                  <button
                    onClick={() => {
                      setShowShareModal(false)
                      setCopied(false)
                    }}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                  >
                    Close
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-sm text-gray-600">Failed to load shareable link.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default AgentTools


