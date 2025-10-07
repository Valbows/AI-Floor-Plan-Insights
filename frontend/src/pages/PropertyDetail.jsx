import React, { useState, useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import { 
  Home, ArrowLeft, Bed, Bath, Maximize, Clock, CheckCircle, XCircle, Loader,
  DollarSign, TrendingUp, Building2, Copy, Share2, Mail, MessageCircle,
  FileText, Star, AlertCircle, BarChart3, Info, LineChart, Megaphone, Check,
  Wifi, Tv, Wind, Coffee, Car, UtensilsCrossed, Dumbbell, Shield
} from 'lucide-react'
import axios from 'axios'

const PropertyDetail = () => {
  const { id } = useParams()
  const [property, setProperty] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('market')

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
    alert(`${label} copied to clipboard!`)
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
    <div className="min-h-screen bg-white">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Link to="/dashboard" className="text-gray-400 hover:text-gray-900 transition-colors">
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <h1 className="text-lg font-medium text-gray-900">Property Details</h1>
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
            <div>
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Address</h3>
              <p className="text-sm text-gray-900">
                {extracted.address || 'Not specified'}
              </p>
            </div>

            {/* Key Stats - Metrics Card */}
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
              <h3 className="text-xs font-semibold text-blue-900 uppercase tracking-wider mb-2">Property Metrics</h3>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-blue-900">Square Footage:</span>
                  <span className="text-lg font-bold text-blue-900">{extracted.square_footage || 0} sq ft</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-blue-900">Bedrooms:</span>
                  <span className="text-lg font-bold text-blue-900">{extracted.bedrooms || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-blue-900">Bathrooms:</span>
                  <span className="text-lg font-bold text-blue-900">{extracted.bathrooms || 0}</span>
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
                    <BarChart3 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-sm text-gray-500">Market insights are being analyzed...</p>
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
                        <button
                          onClick={() => copyToClipboard(extracted.listing_copy.headline, 'Headline')}
                          className="p-2 hover:bg-blue-100 rounded-lg transition"
                        >
                          <Copy className="w-4 h-4 text-blue-600" />
                        </button>
                      </div>
                      <p className="text-xl font-bold text-blue-900">
                        {extracted.listing_copy.headline}
                      </p>
                    </div>

                    {/* Description */}
                    <div className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-3">
                        <h2 className="text-lg font-semibold text-gray-900">MLS Description</h2>
                        <button
                          onClick={() => copyToClipboard(extracted.listing_copy.description, 'Description')}
                          className="p-2 hover:bg-gray-100 rounded-lg transition"
                        >
                          <Copy className="w-4 h-4 text-gray-600" />
                        </button>
                      </div>
                      <p className="text-sm text-gray-700 whitespace-pre-line leading-relaxed">
                        {extracted.listing_copy.description}
                      </p>
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
                    <Megaphone className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-sm text-gray-500">Marketing content is being generated...</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
export default PropertyDetail
