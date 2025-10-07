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
  CheckCircle
} from 'lucide-react'

const PublicReport = () => {
  const { token } = useParams()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [property, setProperty] = useState(null)
  const [tokenInfo, setTokenInfo] = useState(null)

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
  
  const address = extractedData.address || property.address || 'Property Address'
  const price = priceEstimate.estimated_value || 0
  const sqft = extractedData.square_footage || 0
  const bedrooms = extractedData.bedrooms || 0
  const bathrooms = extractedData.bathrooms || 0
  const layoutType = extractedData.layout_type || ''
  const investmentScore = investmentAnalysis.investment_score || 0

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

        {/* Floor Plan */}
        {property.floor_plan_url && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Floor Plan</h2>
            <div className="rounded-lg overflow-hidden">
              <img
                src={property.floor_plan_url}
                alt="Floor Plan"
                className="w-full h-auto"
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

        {/* Market Insights */}
        {marketInsights.market_overview && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Market Insights</h2>
            <p className="text-gray-700 whitespace-pre-line leading-relaxed">
              {marketInsights.market_overview}
            </p>
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
