import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import axios from 'axios'
import {
  Home,
  MapPin,
  DollarSign,
  Square,
  Bed,
  Bath,
  Calendar,
  TrendingUp,
  AlertCircle,
  Loader,
  ExternalLink,
  CheckCircle,
  ZoomIn,
  ZoomOut,
  X,
  Maximize2,
  Building2
} from 'lucide-react'
import PropertyMap from '../components/PropertyMap'

const PublicReport = () => {
  const { token } = useParams()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [property, setProperty] = useState(null)
  const [tokenInfo, setTokenInfo] = useState(null)
  const [imageZoomed, setImageZoomed] = useState(false)
  const [zoomLevel, setZoomLevel] = useState(1)

  useEffect(() => {
    loadPropertyReport()
    logView()
  }, [token])

  const loadPropertyReport = async () => {
    try {
      const response = await axios.get(`/api/public/report/${token}`)
      setProperty(response.data.property)
      setTokenInfo(response.data.token_info)
      setLoading(false)
    } catch (err) {
      if (err.response?.status === 404) {
        setError('This property report link could not be found.')
      } else if (err.response?.status === 410) {
        setError('This property report link has expired.')
      } else {
        setError('Failed to load property report. Please try again later.')
      }
      setLoading(false)
    }
  }

  const logView = async () => {
    try {
      await axios.post(`/api/public/report/${token}/log_view`, {
        viewport_width: window.innerWidth,
        viewport_height: window.innerHeight,
        referrer: document.referrer
      })
    } catch (err) {
      // Silently fail - don't block page load
      console.warn('Failed to log view:', err)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-12 h-12 animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading property report...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full">
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to Load Report</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <p className="text-sm text-gray-500">
              If you believe this is an error, please contact the property agent who shared this link with you.
            </p>
          </div>
        </div>
      </div>
    )
  }

  const extractedData = property.extracted_data || {}
  const marketInsights = extractedData.market_insights || {}
  const priceEstimate = marketInsights.price_estimate || {}
  const investmentAnalysis = marketInsights.investment_analysis || {}
  const marketingContent = extractedData.marketing_content || {}
  const comparableProperties = marketInsights.comparable_properties || []
  
  const address = extractedData.address || property.address || 'Property Address'
  const price = priceEstimate.estimated_value || 0
  const sqft = extractedData.square_footage || 0
  const bedrooms = extractedData.bedrooms || 0
  const bathrooms = extractedData.bathrooms || 0
  const layoutType = extractedData.layout_type || ''
  const investmentScore = investmentAnalysis.investment_score || 0

  const handleZoomIn = () => {
    setZoomLevel(prev => Math.min(prev + 0.25, 3))
  }

  const handleZoomOut = () => {
    setZoomLevel(prev => Math.max(prev - 0.25, 1))
  }

  const handleImageClick = () => {
    setImageZoomed(true)
    setZoomLevel(1)
  }

  const closeZoom = () => {
    setImageZoomed(false)
    setZoomLevel(1)
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
                <h1 className="text-xl font-bold text-gray-900">Property Report</h1>
                <p className="text-sm text-gray-500">AI-Powered Market Analysis</p>
              </div>
            </div>
            {tokenInfo && (
              <div className="hidden md:flex items-center space-x-2 text-sm text-gray-600">
                <Calendar className="w-4 h-4" />
                <span>Expires {new Date(tokenInfo.expires_at).toLocaleDateString()}</span>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Property Header */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center space-x-2 text-gray-600 mb-2">
                <MapPin className="w-5 h-5" />
                <p className="text-lg">{address}</p>
              </div>
              {price > 0 && (
                <div className="flex items-center space-x-2">
                  <DollarSign className="w-6 h-6 text-green-600" />
                  <p className="text-3xl font-bold text-gray-900">
                    ${price.toLocaleString()}
                  </p>
                  {sqft > 0 && (
                    <span className="text-sm text-gray-500 ml-2">
                      (${Math.round(price / sqft)}/sq ft)
                    </span>
                  )}
                </div>
              )}
            </div>
            {investmentScore > 0 && (
              <div className="flex flex-col items-center bg-gradient-to-br from-green-50 to-green-100 px-4 py-3 rounded-lg">
                <div className="flex items-center space-x-1 mb-1">
                  <TrendingUp className="w-4 h-4 text-green-600" />
                  <span className="text-xs font-medium text-green-600">Investment Score</span>
                </div>
                <span className="text-2xl font-bold text-green-900">{investmentScore}</span>
                <span className="text-xs text-green-600">out of 100</span>
              </div>
            )}
          </div>

          {/* Key Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            {bedrooms > 0 && (
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Bed className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="text-sm text-gray-600">Bedrooms</p>
                  <p className="text-lg font-semibold text-gray-900">{bedrooms}</p>
                </div>
              </div>
            )}
            {bathrooms > 0 && (
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Bath className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="text-sm text-gray-600">Bathrooms</p>
                  <p className="text-lg font-semibold text-gray-900">{bathrooms}</p>
                </div>
              </div>
            )}
            {sqft > 0 && (
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Square className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="text-sm text-gray-600">Square Feet</p>
                  <p className="text-lg font-semibold text-gray-900">{sqft.toLocaleString()}</p>
                </div>
              </div>
            )}
            {layoutType && (
              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <Home className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="text-sm text-gray-600">Layout</p>
                  <p className="text-sm font-semibold text-gray-900 line-clamp-2">{layoutType}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Floor Plan with Zoom */}
        {property.floor_plan_url && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Floor Plan</h2>
              <button
                onClick={handleImageClick}
                className="flex items-center space-x-2 px-3 py-2 text-sm text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              >
                <Maximize2 className="w-4 h-4" />
                <span>View Full Size</span>
              </button>
            </div>
            <div className="rounded-lg overflow-hidden cursor-pointer hover:opacity-90 transition-opacity" onClick={handleImageClick}>
              <img
                src={property.floor_plan_url}
                alt="Floor Plan"
                className="w-full h-auto"
              />
            </div>
          </div>
        )}

        {/* Image Zoom Modal */}
        {imageZoomed && (
          <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4" onClick={closeZoom}>
            <button
              onClick={closeZoom}
              className="absolute top-4 right-4 p-2 bg-white rounded-full hover:bg-gray-100 transition-colors z-10"
            >
              <X className="w-6 h-6 text-gray-900" />
            </button>
            
            <div className="absolute top-4 left-4 flex space-x-2 z-10">
              <button
                onClick={(e) => { e.stopPropagation(); handleZoomIn(); }}
                className="p-2 bg-white rounded-full hover:bg-gray-100 transition-colors"
              >
                <ZoomIn className="w-6 h-6 text-gray-900" />
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); handleZoomOut(); }}
                className="p-2 bg-white rounded-full hover:bg-gray-100 transition-colors"
              >
                <ZoomOut className="w-6 h-6 text-gray-900" />
              </button>
              <div className="px-3 py-2 bg-white rounded-full text-sm font-medium text-gray-900">
                {Math.round(zoomLevel * 100)}%
              </div>
            </div>

            <div className="overflow-auto max-w-full max-h-full" onClick={(e) => e.stopPropagation()}>
              <img
                src={property.floor_plan_url}
                alt="Floor Plan - Full Size"
                style={{ transform: `scale(${zoomLevel})`, transition: 'transform 0.2s' }}
                className="max-w-none"
              />
            </div>
          </div>
        )}

        {/* Property Description */}
        {marketingContent.listing_description && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">About This Property</h2>
            <p className="text-gray-700 whitespace-pre-line leading-relaxed">
              {marketingContent.listing_description}
            </p>
          </div>
        )}

        {/* Key Features */}
        {extractedData.features && extractedData.features.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Key Features</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {extractedData.features.map((feature, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <span className="text-gray-700">{feature}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Comparable Properties */}
        {comparableProperties && comparableProperties.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <div className="flex items-center space-x-2 mb-4">
              <Building2 className="w-5 h-5 text-gray-900" />
              <h2 className="text-lg font-semibold text-gray-900">Comparable Properties</h2>
            </div>
            <p className="text-sm text-gray-600 mb-4">Similar properties sold recently in this area</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {comparableProperties.slice(0, 6).map((comp, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900 line-clamp-2">
                        {comp.address || comp.property_address || `Property ${index + 1}`}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {comp.distance_miles ? `${comp.distance_miles} mi away` : 'Nearby'}
                      </p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    {comp.sale_price && (
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-600">Sale Price</span>
                        <span className="text-sm font-semibold text-gray-900">
                          ${parseInt(comp.sale_price).toLocaleString()}
                        </span>
                      </div>
                    )}
                    
                    {comp.sale_date && (
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-600">Sold Date</span>
                        <span className="text-xs text-gray-700">
                          {new Date(comp.sale_date).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                      <div className="flex items-center space-x-3 text-xs text-gray-600">
                        {comp.bedrooms && (
                          <span className="flex items-center space-x-1">
                            <Bed className="w-3 h-3" />
                            <span>{comp.bedrooms}</span>
                          </span>
                        )}
                        {comp.bathrooms && (
                          <span className="flex items-center space-x-1">
                            <Bath className="w-3 h-3" />
                            <span>{comp.bathrooms}</span>
                          </span>
                        )}
                        {comp.square_feet && (
                          <span className="flex items-center space-x-1">
                            <Square className="w-3 h-3" />
                            <span>{parseInt(comp.square_feet).toLocaleString()}</span>
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Market Insights */}
        {marketInsights.market_overview && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Market Insights</h2>
            <p className="text-gray-700 whitespace-pre-line leading-relaxed">
              {marketInsights.market_overview}
            </p>
          </div>
        )}

        {/* Property Map */}
        {address && (
          <div className="mb-6">
            <PropertyMap
              address={address}
              propertyData={{
                bedrooms: bedrooms,
                bathrooms: bathrooms,
                square_footage: sqft
              }}
            />
          </div>
        )}

        {/* Footer */}
        <div className="mt-8 text-center py-6 border-t border-gray-200">
          <p className="text-sm text-gray-600 mb-2">
            This property report was generated using AI-powered market analysis
          </p>
          <p className="text-xs text-gray-500">
            Report expires on {tokenInfo && new Date(tokenInfo.expires_at).toLocaleDateString()}
          </p>
        </div>
      </main>
    </div>
  )
}

export default PublicReport
