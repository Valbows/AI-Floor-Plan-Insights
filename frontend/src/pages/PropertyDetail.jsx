import React, { useState, useEffect } from 'react'
import { Link, useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { 
  Home, ArrowLeft, Bed, Bath, Maximize, Clock, CheckCircle, XCircle, Loader,
  DollarSign, TrendingUp, Building2, Copy, Share2, Mail, MessageCircle,
  FileText, Star, AlertCircle, BarChart3, Info, LineChart, Megaphone, Check,
  Wifi, Tv, Wind, Coffee, Car, UtensilsCrossed, Dumbbell, Shield, Upload, Eye, Edit2, Save, X, Trash2, ZoomIn, ZoomOut, Maximize2, RefreshCw, Wrench, MapPin, ChevronDown, ChevronUp
} from 'lucide-react'
import axios from 'axios'
import Analytics from '../components/Analytics'
import FloorPlanAnalysisDetails from '../components/FloorPlanAnalysisDetails'
import ShareModal from '../components/modals/ShareModal'
import DeleteModal from '../components/modals/DeleteModal'
import FloorPlanZoomModal from '../components/modals/FloorPlanZoomModal'
import ProgressOverlay from '../components/modals/ProgressOverlay'
import PPSFComparisonChart from '../components/charts/PPSFComparisonChart'

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
  const [reEnriching, setReEnriching] = useState(false)
  
  // Edit states
  const [editMode, setEditMode] = useState(false) // Master edit mode toggle
  const [editingField, setEditingField] = useState(null) // 'headline', 'description', 'social_facebook', etc.
  const [editedContent, setEditedContent] = useState({})
  const [saving, setSaving] = useState(false)
  
  // Delete states
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  
  // Floor plan zoom states
  const [showFloorPlanModal, setShowFloorPlanModal] = useState(false)
  const [zoomLevel, setZoomLevel] = useState(1)
  const [deleting, setDeleting] = useState(false)
  
  // Share states
  const [showShareModal, setShowShareModal] = useState(false)
  const [shareableLink, setShareableLink] = useState(null)
  const [generatingLink, setGeneratingLink] = useState(false)
  const [copied, setCopied] = useState(false)

  // Features expand state
  const [showAllFeatures, setShowAllFeatures] = useState(false)
  
  // Property details collapse state
  const [showPropertyDetails, setShowPropertyDetails] = useState(true)
  
  // Property characteristics accordion state
  const [showPropertyCharacteristics, setShowPropertyCharacteristics] = useState(false)
  
  // Price animation state
  const [animatedPrice, setAnimatedPrice] = useState(0)

  // Hide marketing/analytics tabs and share button (now only in Agent Tools)
  const showMarketingAndAnalytics = false

  useEffect(() => {
    document.title = 'Property Details | FP AI'
    loadProperty()
  }, [id])

  // Animate price when property loads
  useEffect(() => {
    if (property?.extracted_data?.market_insights?.price_estimate?.estimated_value) {
      const targetPrice = property.extracted_data.market_insights.price_estimate.estimated_value
      const startPrice = targetPrice * 0.95 // Start from 95% of target (much higher!)
      const duration = 400 // 0.4 seconds (much faster!)
      const steps = 20 // Fewer steps for quicker animation
      const increment = (targetPrice - startPrice) / steps
      let currentStep = 0

      setAnimatedPrice(startPrice) // Set initial value

      const timer = setInterval(() => {
        currentStep++
        if (currentStep <= steps) {
          setAnimatedPrice(Math.floor(startPrice + (increment * currentStep)))
        } else {
          setAnimatedPrice(targetPrice)
          clearInterval(timer)
        }
      }, duration / steps)

      return () => clearInterval(timer)
    }
  }, [property?.extracted_data?.market_insights?.price_estimate?.estimated_value])

  // Progress overlay animation
  useEffect(() => {
    if (showProgressOverlay) {
      const interval = setInterval(() => {
        setAnalysisStep(prev => {
          if (prev < 3) {  // 4 steps (0-3)
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

  const loadProperty = async (retryCount = 0) => {
    try {
      const response = await axios.get(`/api/properties/${id}`)
      console.log('PropertyDetail - Full response:', response.data)
      console.log('PropertyDetail - Property:', response.data.property)
      console.log('PropertyDetail - Extracted data:', response.data.property?.extracted_data)
      setProperty(response.data.property)
      setLoading(false)
      setError('') // Clear any previous errors
    } catch (err) {
      // If property not found and we haven't retried yet, wait and try again
      // This handles the case where property is being created by Celery
      if (err.response?.status === 404 && retryCount < 3) {
        setTimeout(() => {
          loadProperty(retryCount + 1)
        }, 2000) // Wait 2 seconds before retry
      } else {
        setError(err.response?.data?.message || 'Failed to load property')
        setLoading(false)
      }
    }
  }

  const handleReEnrich = async () => {
    try {
      setReEnriching(true)
      await axios.post(`/api/properties/${id}/enrich`)
      // trigger immediate reload and let polling take over
      await loadProperty()
    } catch (err) {
      alert('Failed to re-run market insights. Please try again.')
    } finally {
      setReEnriching(false)
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      'processing': { icon: Loader, color: 'text-white', bg: '#666666', text: 'Processing' },
      'parsing_complete': { icon: Clock, color: 'text-white', bg: '#666666', text: 'Floor Plan Complete' },
      'enrichment_complete': { icon: BarChart3, color: 'text-white', bg: '#666666', text: 'Market Analysis Complete' },
      'complete': { icon: CheckCircle, color: 'text-white', bg: '#000000', text: 'All Complete' },
      'failed': { icon: XCircle, color: 'text-white', bg: '#FF5959', text: 'Failed' },
      'enrichment_failed': { icon: AlertCircle, color: 'text-white', bg: '#FF5959', text: 'Market Data Failed' },
    }
    const badge = badges[status] || badges['processing']
    const Icon = badge.icon
    
    return (
      <span className="inline-flex items-center px-4 py-2 text-xs font-black uppercase shadow-sm" style={{background: badge.bg, color: '#FFFFFF', borderRadius: '6px', letterSpacing: '1.5px'}}>
        <Icon className="w-4 h-4 mr-2" />
        {badge.text}
      </span>
    )
  }

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text)
    alert(`${label} copied to clipboard!`)
  }

  const handleZoomIn = () => {
    setZoomLevel(prev => Math.min(prev + 0.25, 3))
  }

  const handleZoomOut = () => {
    setZoomLevel(prev => Math.max(prev - 0.25, 1))
  }

  const openFloorPlanModal = () => {
    setShowFloorPlanModal(true)
    setZoomLevel(1)
  }

  const closeFloorPlanModal = () => {
    setShowFloorPlanModal(false)
    setZoomLevel(1)
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
    setShareableLink(null) // Clear previous link
    
    try {
      // Get token from localStorage
      const token = localStorage.getItem('token')
      
      if (!token) {
        alert('Authentication required. Please log in again.')
        setGeneratingLink(false)
        return
      }
      
      // First try to get existing link
      try {
        const response = await axios.get(`/api/properties/${id}/shareable-link`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
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
    } catch (err) {
      console.error('Error generating shareable link:', err)
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
      <div className="min-h-screen" style={{background: '#F6F1EB'}}>
        <div className="max-w-2xl mx-auto px-4 py-16 text-center">
          <XCircle className="w-16 h-16 mx-auto mb-4" style={{color: '#FF5959'}} />
          <h2 className="text-2xl font-black uppercase mb-2" style={{color: '#000000'}}>Error Loading Property</h2>
          <p className="mb-6" style={{color: '#666666'}}>{error}</p>
          <Link 
            to="/dashboard" 
            className="inline-flex items-center space-x-2 text-white px-8 py-4 font-bold uppercase tracking-wide transition-all"
            style={{background: '#FF5959', borderRadius: '4px'}}
            onMouseEnter={(e) => {e.currentTarget.style.background = '#E54545'; e.currentTarget.style.transform = 'translateY(-1px)'}}
            onMouseLeave={(e) => {e.currentTarget.style.background = '#FF5959'; e.currentTarget.style.transform = 'translateY(0)'}}
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  const extracted = property.extracted_data || {}

  return (
    <div className="min-h-screen relative" style={{background: '#F6F1EB'}}>
      {/* Progress Overlay */}
      <ProgressOverlay 
        showProgressOverlay={showProgressOverlay}
        analysisStep={analysisStep}
      />

      <main className="max-w-[1400px] mx-auto px-4 py-12">
        {/* Page Header with Actions */}
        <div className="mb-8 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link 
              to="/dashboard" 
              className="transition-all p-2 rounded-lg"
              style={{color: '#000000'}}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = '#FF5959'
                e.currentTarget.style.background = '#FFF5F5'
                e.currentTarget.style.transform = 'translateX(-2px)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = '#000000'
                e.currentTarget.style.background = 'transparent'
                e.currentTarget.style.transform = 'translateX(0)'
              }}
            >
              <ArrowLeft className="w-8 h-8" />
            </Link>
            <h1 className="text-5xl font-black uppercase tracking-tight" style={{color: '#000000', letterSpacing: '-2px', lineHeight: '0.95'}}>
              PROPERTY <span style={{color: '#FF5959'}}>DETAILS</span>
            </h1>
            {getStatusBadge(property.status)}
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => {
                setEditMode(!editMode)
                if (editMode) {
                  setEditingField(null)
                  setEditedContent({})
                }
              }}
              className="flex items-center space-x-2 px-5 py-2.5 transition-all font-bold uppercase text-sm"
              style={{
                background: editMode ? '#666666' : '#FF5959',
                color: '#FFFFFF',
                borderRadius: '4px',
                letterSpacing: '1px',
                boxShadow: editMode ? 'none' : '0 2px 8px rgba(255,89,89,0.3)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = editMode ? '#555555' : '#E54545'
                e.currentTarget.style.transform = 'translateY(-1px)'
                e.currentTarget.style.boxShadow = editMode ? 'none' : '0 4px 12px rgba(255,89,89,0.4)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = editMode ? '#666666' : '#FF5959'
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = editMode ? 'none' : '0 2px 8px rgba(255,89,89,0.3)'
              }}
              disabled={saving}
            >
              {editMode ? <X className="w-4 h-4" /> : <Edit2 className="w-4 h-4" />}
              <span>{editMode ? 'Cancel' : 'Edit'}</span>
            </button>
            <button
              onClick={() => setShowDeleteModal(true)}
              className="flex items-center space-x-2 px-4 py-2 transition-all font-bold uppercase text-sm"
              style={{background: 'transparent', color: editMode ? '#CCCCCC' : '#FF5959', border: `2px solid ${editMode ? '#CCCCCC' : '#FF5959'}`, borderRadius: '4px', letterSpacing: '1px', cursor: editMode ? 'not-allowed' : 'pointer'}}
              onMouseEnter={(e) => {if (!editMode) {e.currentTarget.style.background = '#FF5959'; e.currentTarget.style.color = '#FFFFFF'}}}
              onMouseLeave={(e) => {if (!editMode) {e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#FF5959'}}}
              disabled={editMode}
            >
              <Trash2 className="w-4 h-4" />
              <span>Delete</span>
            </button>
            {editMode && editingField && (
              <button
                onClick={() => saveEdit(editingField)}
                disabled={saving}
                className="flex items-center space-x-2 px-4 py-2 text-white transition-all font-bold uppercase text-sm"
                style={{background: saving ? '#CCCCCC' : '#22C55E', borderRadius: '4px', letterSpacing: '1px', cursor: saving ? 'not-allowed' : 'pointer'}}
                onMouseEnter={(e) => {if (!saving) e.currentTarget.style.background = '#16A34A'}}
                onMouseLeave={(e) => {if (!saving) e.currentTarget.style.background = '#22C55E'}}
              >
                <Save className="w-4 h-4" />
                <span>{saving ? 'Saving...' : 'Save Changes'}</span>
              </button>
            )}
          </div>
        </div>

        {/* MAIN CONTENT GRID - 3 Columns */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* COLUMNS 1 & 2 - Left Content Area */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* KEY METRICS ROW - Top Stats (4 columns in a row) */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Metric Card: Address */}
              <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                <div className="flex items-center gap-2 mb-2">
                  <MapPin className="w-5 h-5" style={{color: '#666666'}} />
                  <h3 className="text-xs font-bold uppercase tracking-wider" style={{color: '#666666'}}>Address</h3>
              </div>
                <p className="text-lg font-bold leading-tight" style={{color: '#000000'}}>
                  {extracted.address || property.address || 'Not specified'}
                </p>
                </div>

              {/* Metric Card: Bed & Bath */}
              <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                <div className="flex items-center gap-2 mb-2">
                  <Home className="w-5 h-5" style={{color: '#666666'}} />
                  <h3 className="text-xs font-bold uppercase tracking-wider" style={{color: '#666666'}}>Bed & Bath</h3>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1">
                    <Bed className="w-4 h-4" style={{color: '#666666'}} />
                    <span className="text-2xl font-black" style={{color: '#000000'}}>{extracted.bedrooms || '—'}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Bath className="w-4 h-4" style={{color: '#666666'}} />
                    <span className="text-2xl font-black" style={{color: '#000000'}}>{extracted.bathrooms || '—'}</span>
                  </div>
                </div>
            </div>

              {/* Metric Card: Square Footage */}
              <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                <div className="flex items-center gap-2 mb-2">
                  <Maximize className="w-5 h-5" style={{color: '#666666'}} />
                  <h3 className="text-xs font-bold uppercase tracking-wider" style={{color: '#666666'}}>Square Feet</h3>
                </div>
                <p className="text-2xl font-black" style={{color: '#000000'}}>
                  {extracted.square_footage ? extracted.square_footage.toLocaleString() : '—'}
                </p>
              </div>

              {/* Metric Card: Price Estimate */}
              <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="w-5 h-5" style={{color: '#666666'}} />
                  <h3 className="text-xs font-bold uppercase tracking-wider" style={{color: '#666666'}}>Est. Price</h3>
                </div>
                <p 
                  className="text-2xl font-black" 
                  style={{color: '#FF5959'}}
                >
                  {extracted.market_insights?.price_estimate?.estimated_value
                    ? `$${animatedPrice.toLocaleString()}`
                    : '—'}
                </p>
              </div>
            </div>

            {/* 2-COLUMN LAYOUT for Property Details and Market Insights */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* COLUMN 1 - Property Details */}
          <div className="flex flex-col gap-6">
            {/* Property Details Section */}
            <div className="flex flex-col gap-4 flex-1">

            {/* PROPERTY VALUATION - Combined Analysis */}
            {extracted.square_footage > 0 && extracted.market_insights?.price_estimate?.estimated_value && (
              (() => {
                const price = extracted.market_insights.price_estimate.estimated_value
                const sqft = extracted.square_footage
                const ppsf = Math.round(price / sqft)
                const priceEstimate = extracted.market_insights.price_estimate
                
                // Calculate market average from comparable properties
                let marketAvgPPSF = 1200 // Default fallback
                const comparables = extracted.market_insights.comparable_properties || []
                
                if (comparables.length > 0) {
                  // Calculate average PPSF from comps that have both price and sqft
                  const validComps = comparables.filter(comp => 
                    comp.last_sale_price && comp.square_feet && comp.square_feet > 0
                  )
                  
                  if (validComps.length > 0) {
                    const totalPPSF = validComps.reduce((sum, comp) => 
                      sum + (comp.last_sale_price / comp.square_feet), 0
                    )
                    marketAvgPPSF = Math.round(totalPPSF / validComps.length)
                  }
                }
                
                const diff = ppsf - marketAvgPPSF
                const percentDiff = Math.round((diff / marketAvgPPSF) * 100)
                const isAboveMarket = diff > 0
                const compCount = comparables.length
                
                return (
                  <div className="rounded-lg p-6 flex flex-col flex-1" style={{background: '#FFFFFF', border: '3px solid #FF5959'}}>
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <DollarSign className="w-5 h-5" style={{color: '#FF5959'}} />
                        <h3 className="text-sm font-black uppercase tracking-wider" style={{color: '#000000', letterSpacing: '1.5px'}}>
                          Property Valuation
                        </h3>
                  </div>
                      
                      {/* Confidence Badge */}
                      <span className="px-3 py-1 text-xs font-bold uppercase" style={{
                        background: priceEstimate?.confidence === 'high' ? '#22C55E' : priceEstimate?.confidence === 'medium' ? '#666666' : '#CCCCCC',
                        color: '#FFFFFF',
                        borderRadius: '4px',
                        letterSpacing: '1px'
                      }}>
                        {priceEstimate?.confidence || 'low'} confidence
                      </span>
              </div>
                    
                    <div className="space-y-4">
                      {/* Main Price Display */}
                      <div className="rounded-lg p-4" style={{background: '#FFF5F5', border: '2px solid #FFE5E5'}}>
                        <div className="flex items-baseline gap-2 mb-2">
                          <span className="text-4xl font-black" style={{color: '#FF5959'}}>
                            ${price.toLocaleString()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                          Range: ${(priceEstimate?.value_range_low || 0).toLocaleString()} - ${(priceEstimate?.value_range_high || 0).toLocaleString()}
                        </p>
                        <div className="flex items-center gap-4">
                          <span className="text-lg font-bold" style={{color: '#FF5959'}}>
                            ${ppsf.toLocaleString()}/sqft
                          </span>
                          <span className="text-sm" style={{color: '#666666'}}>
                            ({sqft.toLocaleString()} sq ft)
                          </span>
                        </div>
            </div>

                      {/* Market Comparison */}
                      <div className="grid grid-cols-2 gap-3">
                        <div className="rounded-lg p-3" style={{background: '#F6F1EB'}}>
                          <p className="text-xs font-medium mb-1" style={{color: '#666666'}}>
                            Market Avg {compCount > 0 && `(${compCount} comps)`}
                          </p>
                          <p className="text-lg font-bold" style={{color: '#000000'}}>
                            ${marketAvgPPSF.toLocaleString()}/sqft
                          </p>
              </div>
                        <div className="rounded-lg p-3" style={{
                          background: isAboveMarket ? '#F0FDF4' : '#FEF2F2',
                          border: `1px solid ${isAboveMarket ? '#86EFAC' : '#FECACA'}`
                        }}>
                          <p className="text-xs font-medium mb-1" style={{color: '#666666'}}>
                            Market Position
                          </p>
                          <p className="text-sm font-bold" style={{color: isAboveMarket ? '#16A34A' : '#DC2626'}}>
                            {isAboveMarket ? '▲' : '▼'} {Math.abs(percentDiff)}% {isAboveMarket ? 'Above' : 'Below'}
                          </p>
                </div>
                </div>
                      
                      {/* Data Source Tooltip */}
                      <div className="flex items-center justify-center pt-3 border-t border-gray-200">
                        <div className="group relative">
                          <button className="flex items-center gap-2 text-xs font-medium transition-colors px-3 py-1.5 rounded-lg hover:bg-gray-50" style={{color: '#666666'}}>
                            <Info className="w-4 h-4" />
                            <span>Valuation Details</span>
                          </button>
                          <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-80 p-4 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50"
                               style={{background: '#000000', border: '2px solid #FF5959'}}>
                            <div className="space-y-3 text-xs" style={{color: '#FFFFFF'}}>
                              <p>
                                💡 <span className="font-semibold">Source:</span> {priceEstimate?.reasoning || 'Multi-source valuation from Zillow, Redfin, and StreetEasy estimates'}
                              </p>
                              <p>
                                📊 <span className="font-semibold">PPSF Insight:</span> Higher price per square foot typically correlates with better layouts and larger living spaces
                                {compCount > 0 && ` • Based on ${compCount} comparable sales`}
                              </p>
                </div>
                            {/* Arrow */}
                            <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0" 
                                 style={{borderLeft: '8px solid transparent', borderRight: '8px solid transparent', borderTop: '8px solid #FF5959'}}>
              </div>
            </div>
              </div>
                </div>
              </div>
            </div>
                )
              })()
            )}

            {/* Market Trend */}
            {extracted.market_insights?.market_trend && (
              <div className="rounded-lg p-6 flex flex-col flex-1" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                <h2 className="text-lg font-black uppercase mb-4 flex items-center" style={{color: '#000000', letterSpacing: '1px'}}>
                  <TrendingUp className="w-5 h-5 mr-2" style={{color: '#FF5959'}} />
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
            )}

            {/* Investment Analysis */}
            {extracted.market_insights?.investment_analysis && (
              <div className="rounded-lg p-6 flex flex-col flex-1" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                <h2 className="text-lg font-black uppercase mb-4 flex items-center" style={{color: '#000000', letterSpacing: '1px'}}>
                  <Building2 className="w-5 h-5 mr-2" style={{color: '#FF5959'}} />
                  Investment Analysis
                </h2>
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-medium" style={{color: '#666666'}}>Investment Score</span>
                    <span className="text-3xl font-black" style={{color: '#000000'}}>
                      {extracted.market_insights.investment_analysis?.investment_score || 0}<span className="text-lg" style={{color: '#666666'}}>/100</span>
                    </span>
                      </div>
                  <div className="w-full rounded-full h-3" style={{background: '#E5E5E5'}}>
                    <div 
                      className="h-3 rounded-full transition-all" 
                      style={{ width: `${extracted.market_insights.investment_analysis?.investment_score || 0}%`, background: '#FF5959' }}
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
            )}

            </div>
          </div>

          {/* COLUMN 2 - Market Insights */}
          <div className="space-y-6">
            {/* Tab Navigation - HIDDEN since only showing Market Insights */}
            {false && (
            <div className="sticky top-0 z-40 pb-4" style={{background: '#F6F1EB'}}>
              <div className="flex space-x-2 p-1" style={{background: '#F6F1EB', borderRadius: '8px'}}>
              <button
                onClick={() => setActiveTab('market')}
                className="flex-1 px-4 py-3 font-bold uppercase text-xs transition-all"
                style={{
                  background: activeTab === 'market' ? '#FF5959' : 'transparent',
                  color: activeTab === 'market' ? '#FFFFFF' : '#666666',
                  borderRadius: '6px',
                  letterSpacing: '1px'
                }}
                onMouseEnter={(e) => {
                  if (activeTab !== 'market') {
                    e.currentTarget.style.background = '#FFFFFF'
                    e.currentTarget.style.color = '#000000'
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeTab !== 'market') {
                    e.currentTarget.style.background = 'transparent'
                    e.currentTarget.style.color = '#666666'
                  }
                }}
              >
                Market Insights
              </button>
                {showMarketingAndAnalytics && (
                <>
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
                Analytics
              </button>
                </>
              )}
              </div>
            </div>
            )}

            {/* Tab Content */}
            <div className="space-y-6">
            {activeTab === 'market' && (
              <div className="space-y-6">
                {/* Market Insights (Agent #2) */}
                {extracted.market_insights ? (
                  <>


                    {/* Comparable Properties Analysis - Combined Chart + Details */}
                    {extracted.market_insights.comparable_properties?.length > 0 && (
                    <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                        <h2 className="text-lg font-black uppercase mb-6 flex items-center" style={{color: '#000000', letterSpacing: '1px'}}>
                          <BarChart3 className="w-5 h-5 mr-2" style={{color: '#FF5959'}} />
                          Comparable Properties Analysis
                      </h2>
                        
                        {/* PPSF Comparison Chart */}
                        <div className="mb-6">
                          <PPSFComparisonChart 
                            property={property} 
                            comparables={extracted.market_insights.comparable_properties || []}
                          />
                        </div>
                        
                        {/* Divider */}
                        <div className="border-t border-gray-200 mb-6"></div>
                        
                        {/* Property Details - Collapsible */}
                        <div>
                          <div className="flex items-center justify-between gap-6 mb-4">
                        <div className="flex-1">
                              <h3 className="text-sm font-bold uppercase mb-2" style={{color: '#666666', letterSpacing: '1px'}}>
                                Property Details
                              </h3>
                              <p className="text-sm text-gray-600">
                                {extracted.market_insights.comparable_properties.length} similar properties found nearby
                          </p>
                        </div>
                            <button
                              onClick={() => setShowPropertyDetails(!showPropertyDetails)}
                              className="flex items-center gap-2 px-4 py-2.5 text-xs font-bold uppercase transition-all rounded-lg flex-shrink-0"
                              style={{
                                background: showPropertyDetails ? '#000000' : 'transparent',
                                color: showPropertyDetails ? '#FFFFFF' : '#000000',
                                border: '2px solid #000000',
                                letterSpacing: '1px'
                              }}
                              onMouseEnter={(e) => {
                                if (!showPropertyDetails) {
                                  e.currentTarget.style.background = '#000000'
                                  e.currentTarget.style.color = '#FFFFFF'
                                }
                              }}
                              onMouseLeave={(e) => {
                                if (!showPropertyDetails) {
                                  e.currentTarget.style.background = 'transparent'
                                  e.currentTarget.style.color = '#000000'
                                }
                              }}
                            >
                              <span>{showPropertyDetails ? 'Hide Details' : 'Show Details'}</span>
                              {showPropertyDetails ? (
                                <ChevronUp className="w-4 h-4" />
                              ) : (
                                <ChevronDown className="w-4 h-4" />
                              )}
                            </button>
                    </div>

                          {/* Collapsible Content */}
                          {showPropertyDetails && (
                            <div className="space-y-3 mt-4">
                              {extracted.market_insights.comparable_properties.slice(0, 5).map((comp, idx) => (
                                <div key={idx} className="p-4 rounded-lg transition-all" style={{background: '#F6F1EB', border: '1px solid #E5E5E5'}}>
                                  <p className="font-semibold text-gray-900 mb-1">{comp.address}</p>
                                  <div className="flex items-center gap-4 text-sm text-gray-600">
                                    <span className="flex items-center gap-1">
                                      <Bed className="w-3 h-3" />
                                      {comp.bedrooms}BR
                          </span>
                                    <span className="flex items-center gap-1">
                                      <Bath className="w-3 h-3" />
                                      {comp.bathrooms}BA
                          </span>
                                    <span className="flex items-center gap-1">
                                      <Maximize className="w-3 h-3" />
                                      {comp.square_feet?.toLocaleString()} sqft
                            </span>
                          </div>
                                  <div className="flex items-center justify-between mt-2">
                                    <span className="font-semibold text-green-600">
                                      Sold: ${comp.last_sale_price?.toLocaleString()}
                                    </span>
                                    <span className="text-sm text-gray-500">
                                      {comp.distance_miles} mi away
                            </span>
                          </div>
                      </div>
                              ))}
                        </div>
                      )}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <>
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
                  </>
                )}
              </div>
            )}

            {showMarketingAndAnalytics && activeTab === 'marketing' && (
              <div className="space-y-6">
                {/* Listing Copy (Agent #3) */}
                {extracted.listing_copy ? (
                  <>
                    {/* Headline */}
                    <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                      <div className="flex items-center justify-between mb-3">
                        <h2 className="text-lg font-black uppercase flex items-center" style={{color: '#000000', letterSpacing: '1px'}}>
                          <FileText className="w-5 h-5 mr-2" style={{color: '#FF5959'}} />
                          Listing Headline
                        </h2>
                        <div className="flex items-center space-x-2">
                          {editMode && (editingField === 'headline' ? (
                            <>
                              <button
                                onClick={() => saveEdit('headline')}
                                disabled={saving}
                                className="p-2 text-white transition flex items-center space-x-1"
                                style={{background: saving ? '#CCCCCC' : '#22C55E', borderRadius: '4px'}}
                              >
                                <Save className="w-4 h-4" />
                                <span className="text-xs font-bold">Save</span>
                              </button>
                              <button
                                onClick={cancelEditing}
                                className="p-2 text-white transition"
                                style={{background: '#666666', borderRadius: '4px'}}
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </>
                          ) : (
                            <button
                              onClick={() => startEditing('headline', extracted.listing_copy.headline)}
                              className="p-2 transition"
                              style={{borderRadius: '4px', color: '#FF5959'}}
                              onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,89,89,0.1)'}
                              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                              title="Edit headline"
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                          ))}
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
                      </div>
                      {editMode ? (
                        <input
                          type="text"
                          value={editingField === 'headline' ? editedContent.headline : (extracted.listing_copy.headline || '')}
                          onChange={(e) => {
                            setEditingField('headline')
                            setEditedContent({ ...editedContent, headline: e.target.value })
                          }}
                          className="w-full text-xl font-bold bg-white px-4 py-2 focus:outline-none"
                          style={{border: '2px solid #FF5959', borderRadius: '4px', color: '#000000'}}
                          placeholder="Enter listing headline"
                        />
                      ) : (
                        <p className="text-xl font-bold" style={{color: '#000000'}}>
                          {extracted.listing_copy.headline}
                        </p>
                      )}
                    </div>

                    {/* Description */}
                    <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                      <div className="flex items-center justify-between mb-3">
                        <h2 className="text-lg font-black uppercase" style={{color: '#000000', letterSpacing: '1px'}}>MLS Description</h2>
                        <div className="flex items-center space-x-2">
                          {editMode && (editingField === 'description' ? (
                            <>
                              <button
                                onClick={() => saveEdit('description')}
                                disabled={saving}
                                className="p-2 text-white transition flex items-center space-x-1"
                                style={{background: saving ? '#CCCCCC' : '#22C55E', borderRadius: '4px'}}
                              >
                                <Save className="w-4 h-4" />
                                <span className="text-xs font-bold">Save</span>
                              </button>
                              <button
                                onClick={cancelEditing}
                                className="p-2 text-white transition"
                                style={{background: '#666666', borderRadius: '4px'}}
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </>
                          ) : (
                            <button
                              onClick={() => startEditing('description', extracted.listing_copy.description)}
                              className="p-2 transition"
                              style={{borderRadius: '4px', color: '#FF5959'}}
                              onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,89,89,0.1)'}
                              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                              title="Edit description"
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                          ))}
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
                      </div>
                      {editMode ? (
                        <textarea
                          value={editingField === 'description' ? editedContent.description : (extracted.listing_copy.description || '')}
                          onChange={(e) => {
                            setEditingField('description')
                            setEditedContent({ ...editedContent, description: e.target.value })
                          }}
                          className="w-full text-sm bg-white px-4 py-3 focus:outline-none min-h-[200px]"
                          style={{border: '2px solid #FF5959', borderRadius: '4px', color: '#000000'}}
                          placeholder="Enter MLS description"
                        />
                      ) : (
                        <p className="text-sm whitespace-pre-line leading-relaxed" style={{color: '#000000'}}>
                          {extracted.listing_copy.description}
                        </p>
                      )}
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
                                  title="Copy to clipboard"
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
                                  title="Copy to clipboard"
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
                                  title="Copy to clipboard"
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
                                title="Copy to clipboard">
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

            {showMarketingAndAnalytics && activeTab === 'analytics' && (
              <Analytics propertyId={id} />
            )}
            </div>
          </div>
          
          </div> {/* End 2-column layout */}
          </div> {/* End left content area (lg:col-span-2) */}

          {/* COLUMN 3 - Floor Plan (Sticky) */}
          <div className="space-y-6">
            <div className="sticky top-4 space-y-4">
              {/* Data Sources + Re-run Button */}
              <div className="flex items-center justify-between rounded-lg p-3" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-black uppercase" style={{color: '#000000', letterSpacing: '1px'}}>Data Sources Used:</span>
                  {/* Build pills from extracted.data_sources if available */}
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
                  className="flex items-center space-x-2 px-4 py-2 text-xs font-bold uppercase whitespace-nowrap"
                  style={{border: '2px solid #000000', borderRadius: '6px', color: reEnriching ? '#666666' : '#000000', background: '#FFFFFF', cursor: reEnriching ? 'not-allowed' : 'pointer'}}
                  onMouseEnter={(e) => { if (!reEnriching) { e.currentTarget.style.background = '#000000'; e.currentTarget.style.color = '#FFFFFF' } }}
                  onMouseLeave={(e) => { if (!reEnriching) { e.currentTarget.style.background = '#FFFFFF'; e.currentTarget.style.color = '#000000' } }}
                >
                  {reEnriching ? <Loader className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
                  <span>{reEnriching ? 'Refreshing...' : 'Refresh Data'}</span>
                    </button>
                </div>

              {/* Floor Plan Card */}
              <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-black uppercase tracking-wider" style={{color: '#000000', letterSpacing: '1.5px'}}>Floor Plan</h3>
                  {property.image_url && (
                  <button
                      onClick={openFloorPlanModal}
                      className="flex items-center space-x-2 px-3 py-2 text-xs font-bold uppercase transition-all"
                      style={{color: '#FF5959', background: 'transparent', border: '2px solid #FF5959', borderRadius: '4px'}}
                      onMouseEnter={(e) => {e.currentTarget.style.background = '#FF5959'; e.currentTarget.style.color = '#FFFFFF'}}
                      onMouseLeave={(e) => {e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#FF5959'}}
                    >
                      <Maximize2 className="w-4 h-4" />
                      <span>Full Size</span>
                  </button>
                  )}
                </div>
                {property.image_url ? (
                  <div 
                    className="cursor-pointer hover:opacity-90 transition-opacity rounded-lg overflow-hidden"
                    onClick={openFloorPlanModal}
                    style={{background: '#F6F1EB'}}
                  >
                    <img 
                      src={property.image_url} 
                      alt="Floor Plan" 
                      className="w-full rounded-lg"
                    />
              </div>
            ) : (
                  <div className="rounded-lg h-96 flex items-center justify-center" style={{background: '#F6F1EB'}}>
                    <Home className="w-16 h-16" style={{color: '#CCCCCC'}} />
              </div>
            )}
          </div>

              {/* ATTOM Data (Property, AVM, Parcel, Area) - Inside Floor Plan Container */}
              {extracted.attom && (
                <div className="rounded-lg p-6 space-y-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
                  <h2 className="text-lg font-black uppercase" style={{color: '#000000', letterSpacing: '1px'}}>Property & Market Data</h2>
                  
                  {/* Property Characteristics - Only show if there's actual data */}
                  {extracted.attom.property && (() => {
                    const hasData = extracted.attom.property.property_type || 
                                   extracted.attom.property.year_built || 
                                   extracted.attom.property.bedrooms !== undefined || 
                                   extracted.attom.property.bathrooms !== undefined || 
                                   extracted.attom.property.square_feet || 
                                   extracted.attom.property.last_sale_date
                    
                    return hasData ? (
                    <div 
                      className="cursor-pointer transition-all duration-200 hover:shadow-sm" 
                      style={{
                        border: `1px solid ${showPropertyCharacteristics ? '#FF5959' : '#E5E5E5'}`,
                        borderRadius: '8px',
                        padding: '16px',
                        background: '#FAFAFA'
                      }}
                      onClick={() => setShowPropertyCharacteristics(!showPropertyCharacteristics)}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'translateY(-1px)'
                        e.currentTarget.style.boxShadow = '0 4px 12px -2px rgba(0, 0, 0, 0.1)'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'translateY(0)'
                        e.currentTarget.style.boxShadow = 'none'
                      }}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-xs font-bold uppercase flex items-center gap-2" style={{color: '#666666', letterSpacing: '1px'}}>
                          Property Characteristics
                          <span className="text-xs font-normal" style={{color: '#999999'}}>
                            {showPropertyCharacteristics ? '(Click to collapse)' : '(Click to expand)'}
                          </span>
                        </h3>
                        <div className="flex items-center gap-2 pointer-events-none">
                          <span className="text-xs font-medium" style={{color: '#666666'}}>
                            {showPropertyCharacteristics ? 'Expanded' : 'Collapsed'}
                          </span>
                          {showPropertyCharacteristics ? (
                            <ChevronUp className="w-4 h-4" style={{color: '#FF5959'}} />
                          ) : (
                            <ChevronDown className="w-4 h-4" style={{color: '#666666'}} />
                          )}
                        </div>
                      </div>
                      
                      {showPropertyCharacteristics && (
                        <div className="grid grid-cols-2 gap-3 text-sm" onClick={(e) => e.stopPropagation()}>
                          <div><p className="text-gray-600">Type</p><p className="font-semibold text-gray-900">{extracted.attom.property.property_type || '—'}</p></div>
                          <div><p className="text-gray-600">Year Built</p><p className="font-semibold text-gray-900">{extracted.attom.property.year_built || '—'}</p></div>
                          <div><p className="text-gray-600">Beds</p><p className="font-semibold text-gray-900">{extracted.attom.property.bedrooms ?? '—'}</p></div>
                          <div><p className="text-gray-600">Baths</p><p className="font-semibold text-gray-900">{extracted.attom.property.bathrooms ?? '—'}</p></div>
                          <div><p className="text-gray-600">Sq Ft</p><p className="font-semibold text-gray-900">{extracted.attom.property.square_feet?.toLocaleString?.() || extracted.attom.property.square_feet || '—'}</p></div>
                          <div><p className="text-gray-600">Last Sale</p><p className="font-semibold text-gray-900">{extracted.attom.property.last_sale_date || '—'}{extracted.attom.property.last_sale_price ? ` • $${Number(extracted.attom.property.last_sale_price).toLocaleString()}` : ''}</p></div>
                        </div>
                      )}
                    </div>
                    ) : null
                  })()}

                  {/* AVM */}
                  {extracted.attom.avm && (
                    <div>
                      <h3 className="text-xs font-bold uppercase mb-2" style={{color: '#666666', letterSpacing: '1px'}}>ATTOM AVM</h3>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div><p className="text-gray-600">Estimated Value</p><p className="font-semibold text-gray-900">${Number(extracted.attom.avm.estimated_value || 0).toLocaleString()}</p></div>
                        <div><p className="text-gray-600">Confidence</p><p className="font-semibold text-gray-900">{extracted.attom.avm.confidence_score ? `${extracted.attom.avm.confidence_score}%` : '—'}</p></div>
                        <div><p className="text-gray-600">Range</p><p className="font-semibold text-gray-900">${Number(extracted.attom.avm.value_range_low || 0).toLocaleString()} - ${Number(extracted.attom.avm.value_range_high || 0).toLocaleString()}</p></div>
                        <div><p className="text-gray-600">As of</p><p className="font-semibold text-gray-900">{extracted.attom.avm.as_of_date || '—'}</p></div>
                      </div>
                    </div>
                  )}

                  {/* Parcel Summary */}
                  {extracted.attom.parcel && (
                    <div>
                      <h3 className="text-xs font-bold uppercase mb-2" style={{color: '#666666', letterSpacing: '1px'}}>Public Records</h3>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div><p className="text-gray-600">APN</p><p className="font-semibold text-gray-900">{extracted.attom.parcel.apn || '—'}</p></div>
                        <div><p className="text-gray-600">FIPS</p><p className="font-semibold text-gray-900">{extracted.attom.parcel.fips || '—'}</p></div>
                        <div><p className="text-gray-600">Lot Size (acres)</p><p className="font-semibold text-gray-900">{extracted.attom.parcel.lot_size_acres ?? '—'}</p></div>
                        <div><p className="text-gray-600">Lot Size (sqft)</p><p className="font-semibold text-gray-900">{extracted.attom.parcel.lot_size_sqft?.toLocaleString?.() || extracted.attom.parcel.lot_size_sqft || '—'}</p></div>
                        <div><p className="text-gray-600">Zoning</p><p className="font-semibold text-gray-900">{extracted.attom.parcel.zoning || '—'}</p></div>
                        <div><p className="text-gray-600">Use</p><p className="font-semibold text-gray-900">{extracted.attom.parcel.county_use || '—'}</p></div>
                      </div>
                    </div>
                  )}

                  {/* Area / Demographics */}
                  {extracted.attom.area_stats && (
                    <div>
                      <h3 className="text-xs font-bold uppercase mb-2" style={{color: '#666666', letterSpacing: '1px'}}>Area</h3>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div><p className="text-gray-600">Median Home Value</p><p className="font-semibold text-gray-900">${Number(extracted.attom.area_stats.median_home_value || 0).toLocaleString()}</p></div>
                        <div><p className="text-gray-600">Median Household Income</p><p className="font-semibold text-gray-900">${Number(extracted.attom.area_stats.median_household_income || 0).toLocaleString()}</p></div>
                        <div><p className="text-gray-600">Population</p><p className="font-semibold text-gray-900">{Number(extracted.attom.area_stats.population || 0).toLocaleString()}</p></div>
                      </div>
                    </div>
                  )}
                </div>
              )}
        </div>
                </div>

          {/* ROOM-BY-ROOM MEASUREMENTS - Spans All 3 Columns (Full Width) */}
          <div className="lg:col-span-3">
            <div className="mt-6">
              <h3 className="text-xs font-bold uppercase mb-4" style={{color: '#666666', letterSpacing: '1px'}}>
                AI Analysis - Floor Plan Details
                </h3>
              <FloorPlanAnalysisDetails 
                extractedData={extracted} 
                showAllFeatures={showAllFeatures}
                setShowAllFeatures={setShowAllFeatures}
              />
              </div>
            </div>
            </div>
      </main>
      
      {/* Modals */}
      <ShareModal 
        showShareModal={showShareModal}
        setShowShareModal={setShowShareModal}
        generatingLink={generatingLink}
        shareableLink={shareableLink}
        copied={copied}
        handleCopyLink={handleCopyLink}
        setCopied={setCopied}
      />
      
      <DeleteModal 
        showDeleteModal={showDeleteModal}
        setShowDeleteModal={setShowDeleteModal}
        deleting={deleting}
        handleDelete={handleDelete}
      />
      
      {/* Share Button - only visible when showMarketingAndAnalytics is true */}
      {showMarketingAndAnalytics && (
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
      )}

      {/* Floor Plan Zoom Modal */}
      <FloorPlanZoomModal 
        showFloorPlanModal={showFloorPlanModal}
        closeFloorPlanModal={closeFloorPlanModal}
        imageUrl={property.image_url}
        zoomLevel={zoomLevel}
        handleZoomIn={handleZoomIn}
        handleZoomOut={handleZoomOut}
      />
    </div>
  )
}
export default PropertyDetail
