import React, { useState, useEffect } from 'react'
import { Link, useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { 
  Home, ArrowLeft, Bed, Bath, Maximize, Clock, CheckCircle, XCircle, Loader,
  DollarSign, TrendingUp, Building2, Copy, Share2, Mail, MessageCircle,
  FileText, Star, AlertCircle, BarChart3, Info, LineChart, Megaphone, Check,
  Wifi, Tv, Wind, Coffee, Car, UtensilsCrossed, Dumbbell, Shield, Upload, Eye, Edit2, Save, X, Trash2
} from 'lucide-react'
import axios from 'axios'
import Chatbot from '../components/Chatbot'
import Analytics from '../components/Analytics'

const PropertyDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const [property, setProperty] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('market')
  const [showProgressOverlay, setShowProgressOverlay] = useState(searchParams.get('showProgress') === 'true')
  const [analysisStep, setAnalysisStep] = useState(0)
  
  // Edit states
  const [editMode, setEditMode] = useState(false) // Master edit mode toggle
  const [editingField, setEditingField] = useState(null) // 'headline', 'description', 'social_facebook', etc.
  const [editedContent, setEditedContent] = useState({})
  const [saving, setSaving] = useState(false)
  
  // Delete states
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deleting, setDeleting] = useState(false)
  
  // Share states
  const [showShareModal, setShowShareModal] = useState(false)
  const [shareableLink, setShareableLink] = useState(null)
  const [generatingLink, setGeneratingLink] = useState(false)
  const [copied, setCopied] = useState(false)

  const analysisSteps = [
    { icon: Upload, text: 'Uploading floor plan...', color: 'text-blue-600' },
    { icon: Eye, text: 'Analyzing layout and rooms...', color: 'text-purple-600' },
    { icon: DollarSign, text: 'Calculating market value...', color: 'text-green-600' },
    { icon: FileText, text: 'Generating listing content...', color: 'text-orange-600' }
  ]

  useEffect(() => {
    loadProperty()
  }, [id])

  // Progress overlay animation
  useEffect(() => {
    if (showProgressOverlay) {
      const interval = setInterval(() => {
        setAnalysisStep(prev => {
          if (prev < analysisSteps.length - 1) {
            return prev + 1
          }
          // Keep cycling through steps while processing
          return 0
        })
      }, 3000) // 3 seconds per step
      
      return () => clearInterval(interval)
    }
  }, [showProgressOverlay])

  // Hide overlay when property analysis is complete
  useEffect(() => {
    if (showProgressOverlay && property?.status === 'complete') {
      // Wait a moment to show completion, then hide overlay
      setTimeout(() => {
        setShowProgressOverlay(false)
        setSearchParams({}) // Remove query param
      }, 1500)
    }
  }, [property?.status, showProgressOverlay])

  // Separate effect for polling
  useEffect(() => {
    // Poll while any processing is happening
    if (property?.status && !['complete', 'failed', 'enrichment_failed', 'listing_failed'].includes(property.status)) {
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
      'parsing_complete': { icon: Clock, color: 'bg-blue-100 text-blue-800', text: 'Floor Plan Complete' },
      'enrichment_complete': { icon: BarChart3, color: 'bg-purple-100 text-purple-800', text: 'Market Analysis Complete' },
      'complete': { icon: CheckCircle, color: 'bg-green-100 text-green-800', text: 'All Complete' },
      'failed': { icon: XCircle, color: 'bg-red-100 text-red-800', text: 'Failed' },
      'enrichment_failed': { icon: AlertCircle, color: 'bg-orange-100 text-orange-800', text: 'Market Data Failed' },
      'listing_failed': { icon: AlertCircle, color: 'bg-orange-100 text-orange-800', text: 'Listing Failed' }
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

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text)
    alert(`${label} copied to clipboard!`)
  }

  const startEditing = (field, currentValue) => {
    setEditingField(field)
    setEditedContent({ ...editedContent, [field]: currentValue })
  }

  const cancelEditing = () => {
    setEditingField(null)
    setEditedContent({})
  }

  const saveEdit = async (field) => {
    setSaving(true)
    try {
      // Determine if it's a property detail or listing copy field
      const isPropertyDetail = ['address', 'square_footage', 'bedrooms', 'bathrooms', 'layout_type'].includes(field)
      
      if (isPropertyDetail) {
        // Update extracted_data in the backend
        await axios.patch(`/api/properties/${id}/details`, {
          [field]: editedContent[field]
        })
        
        // Update local state
        setProperty(prev => ({
          ...prev,
          extracted_data: {
            ...prev.extracted_data,
            [field]: editedContent[field]
          }
        }))
      } else {
        // Update listing_copy in the backend
        await axios.patch(`/api/properties/${id}/listing`, {
          [field]: editedContent[field]
        })
        
        // Update local state
        setProperty(prev => ({
          ...prev,
          listing_copy: {
            ...prev.listing_copy,
            [field]: editedContent[field]
          }
        }))
      }
      
      setEditingField(null)
      alert('Changes saved successfully!')
    } catch (err) {
      alert('Failed to save changes. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    setDeleting(true)
    try {
      await axios.delete(`/api/properties/${id}`)
      // Redirect to dashboard after successful deletion
      navigate('/dashboard')
    } catch (err) {
      alert('Failed to delete property. Please try again.')
      setDeleting(false)
      setShowDeleteModal(false)
    }
  }

  const handleGenerateLink = async () => {
    setGeneratingLink(true)
    try {
      // First try to get existing link
      try {
        const response = await axios.get(`/api/properties/${id}/shareable-link`)
        setShareableLink(response.data)
      } catch (err) {
        // If no link exists, generate new one
        if (err.response?.status === 404) {
          const response = await axios.post(`/api/properties/${id}/generate-link`)
          setShareableLink(response.data)
        } else {
          throw err
        }
      }
    } catch (err) {
      alert('Failed to generate shareable link. Please try again.')
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
    // Load existing link when modal opens
    await handleGenerateLink()
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
    <div className="min-h-screen bg-white relative">
      {/* Progress Overlay */}
      {showProgressOverlay && (
        <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4">
            <div className="text-center mb-8">
              <Loader className="w-16 h-16 text-blue-600 mx-auto mb-4 animate-spin" />
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Analyzing Your Property</h3>
              <p className="text-gray-600">Please wait while our AI processes your floor plan...</p>
            </div>

            {/* Analysis Steps */}
            <div className="space-y-4">
              {analysisSteps.map((step, index) => {
                const StepIcon = step.icon
                const isActive = index === analysisStep
                const isCompleted = index < analysisStep
                
                return (
                  <div 
                    key={index}
                    className={`flex items-center space-x-3 p-4 rounded-lg transition-all ${
                      isActive ? 'bg-blue-50 border-2 border-blue-200 scale-105' : 
                      isCompleted ? 'bg-green-50 border-2 border-green-200' : 
                      'bg-gray-50 border-2 border-gray-200 opacity-50'
                    }`}
                  >
                    <div className={`flex-shrink-0 ${isActive ? 'animate-pulse' : ''}`}>
                      {isCompleted ? (
                        <CheckCircle className="w-6 h-6 text-green-600" />
                      ) : (
                        <StepIcon className={`w-6 h-6 ${isActive ? step.color : 'text-gray-400'}`} />
                      )}
                    </div>
                    <p className={`text-sm font-medium ${
                      isActive ? 'text-gray-900' : 
                      isCompleted ? 'text-green-700' : 
                      'text-gray-500'
                    }`}>
                      {step.text}
                    </p>
                  </div>
                )
              })}
            </div>

            <div className="mt-6">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${((analysisStep + 1) / analysisSteps.length) * 100}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-2 text-center">
                Step {analysisStep + 1} of {analysisSteps.length}
              </p>
            </div>
          </div>
        </div>
      )}

      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Link to="/dashboard" className="text-gray-400 hover:text-gray-900 transition-colors">
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <h1 className="text-lg font-medium text-gray-900">Property Details</h1>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => {
                    setEditMode(!editMode)
                    if (editMode) {
                      setEditingField(null)
                      setEditedContent({})
                    }
                  }}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    editMode 
                      ? 'bg-gray-500 text-white hover:bg-gray-600' 
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {editMode ? <X className="w-4 h-4" /> : <Edit2 className="w-4 h-4" />}
                  <span className="text-sm font-medium">{editMode ? 'Cancel' : 'Edit Property'}</span>
                </button>
                <button
                  onClick={openShareModal}
                  className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-green-600 text-white hover:bg-green-700 transition-colors"
                  disabled={editMode}
                >
                  <Share2 className="w-4 h-4" />
                  <span className="text-sm font-medium">Share</span>
                </button>
                <button
                  onClick={() => setShowDeleteModal(true)}
                  className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 transition-colors"
                  disabled={editMode}
                >
                  <Trash2 className="w-4 h-4" />
                  <span className="text-sm font-medium">Delete</span>
                </button>
                {editMode && editingField && (
                  <button
                    onClick={() => saveEdit(editingField)}
                    disabled={saving}
                    className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white hover:bg-green-700 rounded-lg transition-colors disabled:opacity-50"
                  >
                    <Save className="w-4 h-4" />
                    <span className="text-sm font-medium">{saving ? 'Saving...' : 'Save Changes'}</span>
                  </button>
                )}
              </div>
            </div>
            {getStatusBadge(property.status)}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* LEFT COLUMN - Floor Plan + Property Details (Scrollable) */}
          <div className="space-y-4">
            {/* Floor Plan Image */}
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              {property.image_url ? (
                <img 
                  src={property.image_url} 
                  alt="Floor Plan" 
                  className="w-full rounded-lg"
                />
              ) : (
                <div className="bg-white rounded-lg h-96 flex items-center justify-center">
                  <Home className="w-16 h-16 text-gray-300" />
                </div>
              )}
            </div>

            {/* Property Details Section */}
            <div className="space-y-4">
            {/* Address */}
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Address</h3>
                {editMode && (editingField === 'address' ? (
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => saveEdit('address')}
                      disabled={saving}
                      className="p-1 bg-green-600 text-white hover:bg-green-700 rounded transition text-xs flex items-center space-x-1"
                    >
                      <Save className="w-3 h-3" />
                      <span>Save</span>
                    </button>
                    <button
                      onClick={cancelEditing}
                      className="p-1 bg-gray-500 text-white hover:bg-gray-600 rounded transition"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => startEditing('address', extracted.address || '')}
                    className="p-1 hover:bg-gray-100 rounded transition"
                    title="Edit address"
                  >
                    <Edit2 className="w-3 h-3 text-gray-600" />
                  </button>
                ))}
              </div>
              {editMode ? (
                <input
                  type="text"
                  value={editingField === 'address' ? editedContent.address : (extracted.address || '')}
                  onChange={(e) => {
                    setEditingField('address')
                    setEditedContent({ ...editedContent, address: e.target.value })
                  }}
                  className="w-full text-sm text-gray-900 bg-white border-2 border-blue-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter property address"
                />
              ) : (
                <p className="text-sm text-gray-900">
                  {extracted.address || 'Not specified'}
                </p>
              )}
            </div>

            {/* Key Stats - Metrics Card */}
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-semibold text-blue-900 uppercase tracking-wider">Property Metrics</h3>
                {editMode && <Edit2 className="w-4 h-4 text-blue-700" />}
              </div>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-blue-900">Square Footage:</span>
                  {editMode ? (
                    <input
                      type="number"
                      value={editingField === 'square_footage' ? editedContent.square_footage : (extracted.square_footage || 0)}
                      onChange={(e) => {
                        setEditingField('square_footage')
                        setEditedContent({ ...editedContent, square_footage: parseInt(e.target.value) || 0 })
                      }}
                      className="w-32 text-lg font-bold text-blue-900 bg-white border-2 border-blue-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 text-right"
                      placeholder="0"
                    />
                  ) : (
                    <span className="text-lg font-bold text-blue-900">{extracted.square_footage || 0} sq ft</span>
                  )}
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-blue-900">Bedrooms:</span>
                  {editMode ? (
                    <input
                      type="number"
                      value={editingField === 'bedrooms' ? editedContent.bedrooms : (extracted.bedrooms || 0)}
                      onChange={(e) => {
                        setEditingField('bedrooms')
                        setEditedContent({ ...editedContent, bedrooms: parseInt(e.target.value) || 0 })
                      }}
                      className="w-20 text-lg font-bold text-blue-900 bg-white border-2 border-blue-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 text-right"
                      placeholder="0"
                    />
                  ) : (
                    <span className="text-lg font-bold text-blue-900">{extracted.bedrooms || 0}</span>
                  )}
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-blue-900">Bathrooms:</span>
                  {editMode ? (
                    <input
                      type="number"
                      step="0.5"
                      value={editingField === 'bathrooms' ? editedContent.bathrooms : (extracted.bathrooms || 0)}
                      onChange={(e) => {
                        setEditingField('bathrooms')
                        setEditedContent({ ...editedContent, bathrooms: parseFloat(e.target.value) || 0 })
                      }}
                      className="w-20 text-lg font-bold text-blue-900 bg-white border-2 border-blue-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 text-right"
                      placeholder="0"
                    />
                  ) : (
                    <span className="text-lg font-bold text-blue-900">{extracted.bathrooms || 0}</span>
                  )}
                </div>
              </div>
            </div>

            {/* Layout Type */}
            {extracted.layout_type && (
              <div>
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Layout Type</h3>
                <p className="text-sm text-gray-900">{extracted.layout_type}</p>
              </div>
            )}

            {/* Features */}
            {extracted.features && extracted.features.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Features</h3>
                <ul className="space-y-1">
                  {extracted.features.slice(0, 6).map((feature, index) => (
                    <li key={index} className="flex items-start text-xs text-gray-700">
                      <span className="text-gray-400 mr-2">•</span>
                      <span>{feature}</span>
                    </li>
                  ))}
                  {extracted.features.length > 6 && (
                    <li className="text-xs text-gray-500 italic">+{extracted.features.length - 6} more</li>
                  )}
                </ul>
              </div>
            )}

            {/* Room Facilities - Icon Grid */}
            {extracted.rooms && extracted.rooms.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Room Facilities</h3>
                <div className="grid grid-cols-4 gap-2">
                  {extracted.rooms.slice(0, 8).map((room, index) => (
                    <div key={index} className="flex flex-col items-center text-center p-2 hover:bg-gray-50 rounded transition-colors">
                      <div className="w-8 h-8 mb-1 text-gray-400">
                        {room.type.toLowerCase().includes('bed') && <Bed className="w-full h-full" />}
                        {room.type.toLowerCase().includes('bath') && <Bath className="w-full h-full" />}
                        {room.type.toLowerCase().includes('living') && <Home className="w-full h-full" />}
                        {room.type.toLowerCase().includes('kitchen') && <UtensilsCrossed className="w-full h-full" />}
                        {!['bed', 'bath', 'living', 'kitchen'].some(t => room.type.toLowerCase().includes(t)) && <Maximize className="w-full h-full" />}
                      </div>
                      <p className="text-xs text-gray-600 truncate w-full">{room.type}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* AI Notes */}
            {extracted.notes && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                <h3 className="text-xs font-semibold text-amber-900 uppercase tracking-wider mb-1">AI Analysis</h3>
                <p className="text-xs text-amber-900 leading-relaxed">{extracted.notes}</p>
              </div>
            )}
            </div>
          </div>

          {/* RIGHT COLUMN - Tabbed Content (Market & Marketing) - Sticky */}
          <div className="lg:sticky lg:top-4 lg:self-start space-y-6" style={{maxHeight: 'calc(100vh - 2rem)', overflowY: 'auto'}}>
            {/* Tab Navigation */}
            <div className="border-b border-gray-200">
              <div className="flex space-x-8">
                <button
                  onClick={() => setActiveTab('market')}
                  className={`pb-3 font-medium text-sm transition-colors border-b-2 ${
                    activeTab === 'market'
                      ? 'border-gray-900 text-gray-900'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Market Insights
                </button>
                <button
                  onClick={() => setActiveTab('marketing')}
                  className={`pb-3 font-medium text-sm transition-colors border-b-2 ${
                    activeTab === 'marketing'
                      ? 'border-gray-900 text-gray-900'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Marketing Content
                </button>
                <button
                  onClick={() => setActiveTab('analytics')}
                  className={`pb-3 font-medium text-sm transition-colors border-b-2 ${
                    activeTab === 'analytics'
                      ? 'border-gray-900 text-gray-900'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Analytics
                </button>
              </div>
            </div>

            {activeTab === 'market' && (
              <div className="space-y-6">
                {/* Market Insights (Agent #2) */}
                {extracted.market_insights ? (
                  <>
                    {/* Price Estimate */}
                    <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                          <DollarSign className="w-5 h-5 mr-2 text-green-600" />
                          Price Estimate
                        </h2>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          extracted.market_insights.price_estimate?.confidence === 'high' ? 'bg-green-200 text-green-800' :
                          extracted.market_insights.price_estimate?.confidence === 'medium' ? 'bg-yellow-200 text-yellow-800' :
                          'bg-gray-200 text-gray-800'
                        }`}>
                          {extracted.market_insights.price_estimate?.confidence || 'low'} confidence
                        </span>
                      </div>
                      <p className="text-3xl font-bold text-green-700 mb-2">
                        ${(extracted.market_insights.price_estimate?.estimated_value || 0).toLocaleString()}
                      </p>
                      <p className="text-sm text-gray-600 mb-3">
                        Range: ${(extracted.market_insights.price_estimate?.value_range_low || 0).toLocaleString()} - 
                        ${(extracted.market_insights.price_estimate?.value_range_high || 0).toLocaleString()}
                      </p>
                      <p className="text-xs text-gray-600 italic">
                        {extracted.market_insights.price_estimate?.reasoning}
                      </p>
                    </div>

                    {/* Market Trend */}
                    <div className="border border-gray-200 rounded-lg p-6">
                      <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
                        Market Trend
                      </h2>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <p className="text-gray-600">Direction</p>
                          <p className="font-semibold text-gray-900 capitalize">
                            {extracted.market_insights.market_trend?.trend_direction || 'Unknown'}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-600">Buyer Demand</p>
                          <p className="font-semibold text-gray-900 capitalize">
                            {extracted.market_insights.market_trend?.buyer_demand || 'Unknown'}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-600">Inventory</p>
                          <p className="font-semibold text-gray-900 capitalize">
                            {extracted.market_insights.market_trend?.inventory_level || 'Unknown'}
                          </p>
                        </div>
                        {extracted.market_insights.market_trend?.appreciation_rate && (
                          <div>
                            <p className="text-gray-600">Appreciation</p>
                            <p className="font-semibold text-gray-900">
                              {extracted.market_insights.market_trend.appreciation_rate}%
                            </p>
                          </div>
                        )}
                      </div>
                      {extracted.market_insights.market_trend?.insights && (
                        <p className="text-xs text-gray-600 mt-3 pt-3 border-t">
                          {extracted.market_insights.market_trend.insights}
                        </p>
                      )}
                    </div>

                    {/* Investment Analysis */}
                    <div className="border border-gray-200 rounded-lg p-6">
                      <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <Building2 className="w-5 h-5 mr-2 text-purple-600" />
                        Investment Analysis
                      </h2>
                      <div className="mb-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-gray-600">Investment Score</span>
                          <span className="text-lg font-bold text-purple-700">
                            {extracted.market_insights.investment_analysis?.investment_score || 0}/100
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-purple-600 h-2 rounded-full" 
                            style={{ width: `${extracted.market_insights.investment_analysis?.investment_score || 0}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Rental Potential:</span>
                          <span className="font-semibold text-gray-900 capitalize">
                            {extracted.market_insights.investment_analysis?.rental_potential || 'N/A'}
                          </span>
                        </div>
                        {extracted.market_insights.investment_analysis?.estimated_rental_income && (
                          <div className="flex justify-between">
                            <span className="text-gray-600">Est. Rental Income:</span>
                            <span className="font-semibold text-gray-900">
                              ${extracted.market_insights.investment_analysis.estimated_rental_income.toLocaleString()}/mo
                            </span>
                          </div>
                        )}
                        {extracted.market_insights.investment_analysis?.cap_rate && (
                          <div className="flex justify-between">
                            <span className="text-gray-600">Cap Rate:</span>
                            <span className="font-semibold text-gray-900">
                              {extracted.market_insights.investment_analysis.cap_rate}%
                            </span>
                          </div>
                        )}
                      </div>
                      {extracted.market_insights.investment_analysis?.opportunities?.length > 0 && (
                        <div className="mt-3 pt-3 border-t">
                          <p className="text-xs font-semibold text-gray-700 mb-1">Opportunities:</p>
                          <ul className="text-xs text-gray-600 space-y-1">
                            {extracted.market_insights.investment_analysis.opportunities.map((opp, idx) => (
                              <li key={idx}>• {opp}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>

                    {/* Comparable Properties */}
                    {extracted.market_insights.comparable_properties?.length > 0 && (
                      <div className="border border-gray-200 rounded-lg p-6">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">Comparable Properties</h2>
                        <p className="text-sm text-gray-600 mb-3">
                          {extracted.market_insights.comparable_properties.length} similar properties found nearby
                        </p>
                        <div className="space-y-2">
                          {extracted.market_insights.comparable_properties.slice(0, 3).map((comp, idx) => (
                            <div key={idx} className="text-xs p-2 bg-gray-50 rounded">
                              <p className="font-medium text-gray-900">{comp.address}</p>
                              <p className="text-gray-600">
                                {comp.bedrooms}BR / {comp.bathrooms}BA • {comp.square_feet?.toLocaleString()} sqft
                              </p>
                              <p className="text-gray-600">
                                Sold: ${comp.last_sale_price?.toLocaleString()} • {comp.distance_miles} mi away
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="border border-gray-200 rounded-lg p-12 text-center">
                    <Loader className="w-12 h-12 text-blue-600 mx-auto mb-4 animate-spin" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Analyzing Market Data</h3>
                    <p className="text-sm text-gray-600 mb-4">Our AI is gathering comparable properties and calculating market value...</p>
                    <div className="max-w-md mx-auto">
                      <div className="flex items-center space-x-2 text-xs text-gray-500">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        <span>Floor plan analysis complete</span>
                      </div>
                      <div className="flex items-center space-x-2 text-xs text-blue-600 mt-2">
                        <Loader className="w-4 h-4 animate-spin" />
                        <span>Processing market insights...</span>
                      </div>
                    </div>
                    <p className="text-xs text-gray-400 mt-4">This usually takes 1-2 minutes</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'marketing' && (
              <div className="space-y-6">
                {/* Listing Copy (Agent #3) */}
                {extracted.listing_copy ? (
                  <>
                    {/* Headline */}
                    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-3">
                        <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                          <FileText className="w-5 h-5 mr-2 text-blue-600" />
                          Listing Headline
                        </h2>
                        <div className="flex items-center space-x-2">
                          {editMode && (editingField === 'headline' ? (
                            <>
                              <button
                                onClick={() => saveEdit('headline')}
                                disabled={saving}
                                className="p-2 bg-green-600 text-white hover:bg-green-700 rounded-lg transition flex items-center space-x-1"
                              >
                                <Save className="w-4 h-4" />
                                <span className="text-xs">Save</span>
                              </button>
                              <button
                                onClick={cancelEditing}
                                className="p-2 bg-gray-500 text-white hover:bg-gray-600 rounded-lg transition"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </>
                          ) : (
                            <button
                              onClick={() => startEditing('headline', extracted.listing_copy.headline)}
                              className="p-2 hover:bg-blue-100 rounded-lg transition"
                              title="Edit headline"
                            >
                              <Edit2 className="w-4 h-4 text-blue-600" />
                            </button>
                          ))}
                          <button
                            onClick={() => copyToClipboard(extracted.listing_copy.headline, 'Headline')}
                            className="p-2 hover:bg-blue-100 rounded-lg transition"
                            title="Copy to clipboard"
                          >
                            <Copy className="w-4 h-4 text-blue-600" />
                          </button>
                        </div>
                      </div>
                      {editMode ? (
                        <input
                          type="text"
                          value={editingField === 'headline' ? editedContent.headline : (extracted.listing_copy.headline || '')}
                          onChange={(e) => {
                            setEditingField('headline')
                            setEditedContent({ ...editedContent, headline: e.target.value })
                          }}
                          className="w-full text-xl font-bold text-blue-900 bg-white border-2 border-blue-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="Enter listing headline"
                        />
                      ) : (
                        <p className="text-xl font-bold text-blue-900">
                          {extracted.listing_copy.headline}
                        </p>
                      )}
                    </div>

                    {/* Description */}
                    <div className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-3">
                        <h2 className="text-lg font-semibold text-gray-900">MLS Description</h2>
                        <div className="flex items-center space-x-2">
                          {editMode && (editingField === 'description' ? (
                            <>
                              <button
                                onClick={() => saveEdit('description')}
                                disabled={saving}
                                className="p-2 bg-green-600 text-white hover:bg-green-700 rounded-lg transition flex items-center space-x-1"
                              >
                                <Save className="w-4 h-4" />
                                <span className="text-xs">Save</span>
                              </button>
                              <button
                                onClick={cancelEditing}
                                className="p-2 bg-gray-500 text-white hover:bg-gray-600 rounded-lg transition"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </>
                          ) : (
                            <button
                              onClick={() => startEditing('description', extracted.listing_copy.description)}
                              className="p-2 hover:bg-gray-100 rounded-lg transition"
                              title="Edit description"
                            >
                              <Edit2 className="w-4 h-4 text-gray-600" />
                            </button>
                          ))}
                          <button
                            onClick={() => copyToClipboard(extracted.listing_copy.description, 'Description')}
                            className="p-2 hover:bg-gray-100 rounded-lg transition"
                            title="Copy to clipboard"
                          >
                            <Copy className="w-4 h-4 text-gray-600" />
                          </button>
                        </div>
                      </div>
                      {editMode ? (
                        <textarea
                          value={editingField === 'description' ? editedContent.description : (extracted.listing_copy.description || '')}
                          onChange={(e) => {
                            setEditingField('description')
                            setEditedContent({ ...editedContent, description: e.target.value })
                          }}
                          className="w-full text-sm text-gray-700 bg-white border-2 border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-gray-500 min-h-[200px]"
                          placeholder="Enter MLS description"
                        />
                      ) : (
                        <p className="text-sm text-gray-700 whitespace-pre-line leading-relaxed">
                          {extracted.listing_copy.description}
                        </p>
                      )}
                    </div>

                    {/* Highlights */}
                    {extracted.listing_copy.highlights?.length > 0 && (
                      <div className="border border-gray-200 rounded-lg p-6">
                        <h2 className="text-lg font-semibold text-gray-900 mb-3">Key Highlights</h2>
                        <ul className="space-y-2">
                          {extracted.listing_copy.highlights.map((highlight, idx) => (
                            <li key={idx} className="flex items-start text-sm">
                              <Star className="w-4 h-4 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" />
                              <span className="text-gray-700">{highlight}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Social Media */}
                    {extracted.social_variants && (
                      <div className="border border-gray-200 rounded-lg p-6">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                          <Share2 className="w-5 h-5 mr-2 text-indigo-600" />
                          Social Media
                        </h2>
                        <div className="space-y-3">
                          {extracted.social_variants.instagram && (
                            <div>
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-xs font-semibold text-gray-700">Instagram</span>
                                <button
                                  onClick={() => copyToClipboard(extracted.social_variants.instagram, 'Instagram caption')}
                                  className="p-1 text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 rounded transition-colors"
                                  title="Copy to clipboard"
                                >
                                  <Copy className="w-4 h-4" />
                                </button>
                              </div>
                              <p className="text-xs text-gray-600 bg-gray-50 p-2 rounded">
                                {extracted.social_variants.instagram}
                              </p>
                            </div>
                          )}
                          {extracted.social_variants.facebook && (
                            <div>
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-xs font-semibold text-gray-700">Facebook</span>
                                <button
                                  onClick={() => copyToClipboard(extracted.social_variants.facebook, 'Facebook post')}
                                  className="p-1 text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 rounded transition-colors"
                                  title="Copy to clipboard"
                                >
                                  <Copy className="w-4 h-4" />
                                </button>
                              </div>
                              <p className="text-xs text-gray-600 bg-gray-50 p-2 rounded">
                                {extracted.social_variants.facebook}
                              </p>
                            </div>
                          )}
                          {extracted.social_variants.twitter && (
                            <div>
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-xs font-semibold text-gray-700">Twitter / X</span>
                                <button
                                  onClick={() => copyToClipboard(extracted.social_variants.twitter, 'Tweet')}
                                  className="p-1 text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 rounded transition-colors"
                                  title="Copy to clipboard"
                                >
                                  <Copy className="w-4 h-4" />
                                </button>
                              </div>
                              <p className="text-xs text-gray-600 bg-gray-50 p-2 rounded">
                                {extracted.social_variants.twitter}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* CTA & Email */}
                    <div className="border border-gray-200 rounded-lg p-6">
                      <div className="space-y-3">
                        <div>
                          <span className="text-xs font-semibold text-gray-700">Call to Action</span>
                          <p className="text-sm text-gray-900 font-medium mt-1">
                            {extracted.listing_copy.call_to_action}
                          </p>
                        </div>
                        {extracted.listing_copy.email_subject && (
                          <div className="pt-3 border-t">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-xs font-semibold text-gray-700">Email Subject Line</span>
                              <button
                                onClick={() => copyToClipboard(extracted.listing_copy.email_subject, 'Email subject')}
                                className="p-1 text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 rounded transition-colors"
                                title="Copy to clipboard">
                                <Copy className="w-4 h-4" />
                              </button>
                            </div>
                            <p className="text-sm text-gray-900">
                              {extracted.listing_copy.email_subject}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* SEO Keywords */}
                    {extracted.listing_copy.seo_keywords?.length > 0 && (
                      <div className="border border-gray-200 rounded-lg p-6">
                        <h2 className="text-sm font-semibold text-gray-900 mb-2">SEO Keywords</h2>
                        <div className="flex flex-wrap gap-1">
                          {extracted.listing_copy.seo_keywords.map((keyword, idx) => (
                            <span key={idx} className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">
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
                    <p className="text-sm text-gray-600 mb-4">Our AI is crafting compelling listing descriptions and social media posts...</p>
                    <div className="max-w-md mx-auto">
                      <div className="flex items-center space-x-2 text-xs text-gray-500">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        <span>Floor plan analysis complete</span>
                      </div>
                      <div className="flex items-center space-x-2 text-xs text-orange-600 mt-2">
                        <Loader className="w-4 h-4 animate-spin" />
                        <span>Generating marketing content...</span>
                      </div>
                    </div>
                    <p className="text-xs text-gray-400 mt-4">This usually takes 30-60 seconds</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'analytics' && (
              <Analytics propertyId={id} />
            )}
          </div>
        </div>
      </main>
      
      {/* Share Link Modal */}
      {showShareModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6">
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <Share2 className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Share Property</h3>
                  <p className="text-sm text-gray-600">Generate a public link to share this property</p>
                </div>
              </div>
              <button
                onClick={() => {
                  setShowShareModal(false)
                  setCopied(false)
                }}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {generatingLink ? (
              <div className="text-center py-8">
                <Loader className="w-8 h-8 animate-spin text-green-600 mx-auto mb-4" />
                <p className="text-sm text-gray-600">Generating shareable link...</p>
              </div>
            ) : shareableLink ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Shareable Link
                  </label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={shareableLink.shareable_url}
                      readOnly
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                    <button
                      onClick={handleCopyLink}
                      className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-2 ${
                        copied
                          ? 'bg-green-100 text-green-700'
                          : 'bg-green-600 text-white hover:bg-green-700'
                      }`}
                    >
                      {copied ? (
                        <>
                          <Check className="w-4 h-4" />
                          <span className="text-sm font-medium">Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4" />
                          <span className="text-sm font-medium">Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Expires:</span>
                    <span className="font-medium text-gray-900">
                      {new Date(shareableLink.expires_at).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">
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
      
      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
            <div className="flex items-start mb-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                  <AlertCircle className="w-6 h-6 text-red-600" />
                </div>
              </div>
              <div className="ml-4 flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  Delete Property?
                </h3>
                <p className="text-sm text-gray-600">
                  Are you sure you want to delete this property? This action cannot be undone. 
                  All property data, floor plans, and analysis will be permanently removed.
                </p>
              </div>
            </div>
            
            <div className="flex items-center justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowDeleteModal(false)}
                disabled={deleting}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors disabled:opacity-50 flex items-center space-x-2"
              >
                {deleting ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin" />
                    <span>Deleting...</span>
                  </>
                ) : (
                  <>
                    <Trash2 className="w-4 h-4" />
                    <span>Delete Property</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Chatbot */}
      <Chatbot />
    </div>
  )
}
export default PropertyDetail
