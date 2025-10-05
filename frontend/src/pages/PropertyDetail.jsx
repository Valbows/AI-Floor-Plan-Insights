import React, { useState, useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import { 
  Home, ArrowLeft, Bed, Bath, Maximize, Clock, CheckCircle, XCircle, Loader,
  DollarSign, TrendingUp, Building2, Copy, Share2, Mail, MessageCircle,
  FileText, Star, AlertCircle, BarChart3, Edit3, Save, X
} from 'lucide-react'
import axios from 'axios'

const PropertyDetail = () => {
  const { id } = useParams()
  const [property, setProperty] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [editedListingCopy, setEditedListingCopy] = useState(null)
  const [saving, setSaving] = useState(false)
  const [copySuccess, setCopySuccess] = useState('')

  useEffect(() => {
    loadProperty()
  }, [id])

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
    setCopySuccess(label)
    setTimeout(() => setCopySuccess(''), 2000)
  }

  const handleEdit = () => {
    setEditedListingCopy({
      ...property.listing_copy,
      headline: property.listing_copy?.headline || '',
      description: property.listing_copy?.description || ''
    })
    setIsEditing(true)
  }

  const handleCancel = () => {
    setIsEditing(false)
    setEditedListingCopy(null)
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      const response = await axios.put(`/api/properties/${id}`, {
        listing_copy: editedListingCopy
      })
      
      setProperty(response.data.property)
      setIsEditing(false)
      setEditedListingCopy(null)
      setCopySuccess('Listing updated successfully!')
      setTimeout(() => setCopySuccess(''), 3000)
    } catch (err) {
      alert(err.response?.data?.message || 'Failed to update listing')
    } finally {
      setSaving(false)
    }
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

      {/* Toast Notification */}
      {copySuccess && (
        <div className="fixed top-4 right-4 z-50 animate-fade-in">
          <div className="bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center space-x-2">
            <CheckCircle className="w-5 h-5" />
            <span className="font-medium">{copySuccess} copied!</span>
          </div>
        </div>
      )}

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* LEFT COLUMN - Floor Plan Image */}
          <div className="lg:col-span-1">
            <div className="card sticky top-4">
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
          </div>

          {/* MIDDLE COLUMN - Property Information */}
          <div className="lg:col-span-1 space-y-6">
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

          </div>

          {/* RIGHT COLUMN - Market Insights & Listing Copy */}
          <div className="lg:col-span-1 space-y-6">
            {/* Market Insights (Agent #2) */}
            {extracted.market_insights && (
              <>
                {/* Price Estimate */}
                <div className="card bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
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
                <div className="card">
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
                <div className="card">
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
                  <div className="card">
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
            )}

            {/* Listing Copy (Agent #3) */}
            {extracted.listing_copy && (
              <>
                {/* Edit/Save/Cancel Buttons */}
                <div className="flex justify-end space-x-2 mb-4">
                  {!isEditing ? (
                    <button
                      onClick={handleEdit}
                      className="btn-secondary flex items-center space-x-2"
                    >
                      <Edit3 className="w-4 h-4" />
                      <span>Edit Listing</span>
                    </button>
                  ) : (
                    <>
                      <button
                        onClick={handleCancel}
                        className="btn-secondary flex items-center space-x-2"
                        disabled={saving}
                      >
                        <X className="w-4 h-4" />
                        <span>Cancel</span>
                      </button>
                      <button
                        onClick={handleSave}
                        className="btn-primary flex items-center space-x-2"
                        disabled={saving}
                      >
                        {saving ? (
                          <Loader className="w-4 h-4 animate-spin" />
                        ) : (
                          <Save className="w-4 h-4" />
                        )}
                        <span>{saving ? 'Saving...' : 'Save Changes'}</span>
                      </button>
                    </>
                  )}
                </div>

                {/* Headline */}
                <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
                  <div className="flex items-center justify-between mb-3">
                    <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                      <FileText className="w-5 h-5 mr-2 text-blue-600" />
                      Listing Headline
                    </h2>
                    {!isEditing && (
                      <button
                        onClick={() => copyToClipboard(extracted.listing_copy.headline, 'Headline')}
                        className="p-2 hover:bg-blue-100 rounded-lg transition"
                      >
                        <Copy className="w-4 h-4 text-blue-600" />
                      </button>
                    )}
                  </div>
                  {isEditing ? (
                    <textarea
                      value={editedListingCopy?.headline || ''}
                      onChange={(e) => setEditedListingCopy({...editedListingCopy, headline: e.target.value})}
                      className="w-full p-3 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg font-bold text-blue-900 bg-white"
                      rows="2"
                      placeholder="Enter listing headline..."
                    />
                  ) : (
                    <p className="text-xl font-bold text-blue-900">
                      {extracted.listing_copy.headline}
                    </p>
                  )}
                </div>

                {/* Description */}
                <div className="card">
                  <div className="flex items-center justify-between mb-3">
                    <h2 className="text-lg font-semibold text-gray-900">MLS Description</h2>
                    {!isEditing && (
                      <button
                        onClick={() => copyToClipboard(extracted.listing_copy.description, 'Description')}
                        className="p-2 hover:bg-gray-100 rounded-lg transition"
                      >
                        <Copy className="w-4 h-4 text-gray-600" />
                      </button>
                    )}
                  </div>
                  {isEditing ? (
                    <textarea
                      value={editedListingCopy?.description || ''}
                      onChange={(e) => setEditedListingCopy({...editedListingCopy, description: e.target.value})}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm text-gray-700 leading-relaxed"
                      rows="8"
                      placeholder="Enter property description..."
                    />
                  ) : (
                    <p className="text-sm text-gray-700 whitespace-pre-line leading-relaxed">
                      {extracted.listing_copy.description}
                    </p>
                  )}
                </div>

                {/* Highlights */}
                {extracted.listing_copy.highlights?.length > 0 && (
                  <div className="card">
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
                  <div className="card">
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
                              className="text-xs text-indigo-600 hover:text-indigo-700 flex items-center"
                            >
                              <Copy className="w-3 h-3 mr-1" /> Copy
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
                              className="text-xs text-indigo-600 hover:text-indigo-700 flex items-center"
                            >
                              <Copy className="w-3 h-3 mr-1" /> Copy
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
                              className="text-xs text-indigo-600 hover:text-indigo-700 flex items-center"
                            >
                              <Copy className="w-3 h-3 mr-1" /> Copy
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
                <div className="card">
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
                            className="text-xs text-indigo-600 hover:text-indigo-700 flex items-center">
                            <Copy className="w-3 h-3 mr-1" /> Copy
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
                  <div className="card">
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
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
export default PropertyDetail
