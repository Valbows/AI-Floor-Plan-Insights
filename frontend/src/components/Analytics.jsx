import React, { useState, useEffect } from 'react'
import { BarChart3, Download, Eye, Users, Calendar, TrendingUp } from 'lucide-react'
import axios from 'axios'

const Analytics = ({ propertyId }) => {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadAnalytics()
  }, [propertyId])

  const loadAnalytics = async () => {
    try {
      const response = await axios.get(`/api/properties/${propertyId}/analytics`)
      setAnalytics(response.data)
      setLoading(false)
    } catch (err) {
      setError('Failed to load analytics')
      setLoading(false)
    }
  }

  const exportToCSV = () => {
    if (!analytics || !analytics.views) return
    
    // Create CSV content
    const headers = ['Date', 'Time', 'User Agent', 'IP Address']
    const rows = analytics.views.map(view => [
      new Date(view.viewed_at).toLocaleDateString(),
      new Date(view.viewed_at).toLocaleTimeString(),
      view.user_agent || 'Unknown',
      view.ip_address || 'Unknown'
    ])
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n')
    
    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `property-${propertyId}-analytics.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="h-48 bg-gray-200 rounded"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card">
        <div className="text-center py-12">
          <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Analytics Not Available</h3>
          <p className="text-sm text-gray-600">{error}</p>
        </div>
      </div>
    )
  }

  const totalViews = analytics?.view_count || 0
  const uniqueViewers = analytics?.unique_viewers || 0
  const views = analytics?.views || []

  // Group views by date for chart
  const viewsByDate = views.reduce((acc, view) => {
    const date = new Date(view.viewed_at).toLocaleDateString()
    acc[date] = (acc[date] || 0) + 1
    return acc
  }, {})

  const chartData = Object.entries(viewsByDate).slice(-7) // Last 7 days

  // Calculate max views for chart scaling
  const maxViews = Math.max(...Object.values(viewsByDate), 1)

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-xs font-bold uppercase mb-2 whitespace-nowrap" style={{color: '#666666', letterSpacing: '1px'}}>Total Views</p>
              <p className="text-4xl font-black" style={{color: '#000000'}}>{totalViews}</p>
            </div>
            <div className="w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0" style={{background: '#F6F1EB'}}>
              <Eye className="w-7 h-7" style={{color: '#FF5959'}} />
            </div>
          </div>
        </div>

        <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-xs font-bold uppercase mb-2 whitespace-nowrap" style={{color: '#666666', letterSpacing: '1px'}}>Unique Viewers</p>
              <p className="text-4xl font-black" style={{color: '#000000'}}>{uniqueViewers}</p>
            </div>
            <div className="w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0" style={{background: '#F6F1EB'}}>
              <Users className="w-7 h-7" style={{color: '#FF5959'}} />
            </div>
          </div>
        </div>

        <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-xs font-bold uppercase mb-2 whitespace-nowrap" style={{color: '#666666', letterSpacing: '1px'}}>Avg. per Day</p>
              <p className="text-4xl font-black" style={{color: '#000000'}}>
                {chartData.length > 0 ? Math.round(totalViews / chartData.length) : 0}
              </p>
            </div>
            <div className="w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0" style={{background: '#F6F1EB'}}>
              <TrendingUp className="w-7 h-7" style={{color: '#FF5959'}} />
            </div>
          </div>
        </div>
      </div>

      {/* Views Chart */}
      <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-black uppercase flex items-center" style={{color: '#000000', letterSpacing: '1px'}}>
            <BarChart3 className="w-5 h-5 mr-2" style={{color: '#FF5959'}} />
            Views Over Time (Last 7 Days)
          </h3>
          <button
            onClick={exportToCSV}
            className="flex items-center space-x-2 px-4 py-2 text-sm font-bold uppercase transition-all"
            style={{background: views.length === 0 ? '#CCCCCC' : 'transparent', color: views.length === 0 ? '#666666' : '#000000', border: `2px solid ${views.length === 0 ? '#CCCCCC' : '#000000'}`, borderRadius: '4px', letterSpacing: '1px', cursor: views.length === 0 ? 'not-allowed' : 'pointer'}}
            onMouseEnter={(e) => {if (views.length > 0) {e.currentTarget.style.background = '#000000'; e.currentTarget.style.color = '#FFFFFF'}}}
            onMouseLeave={(e) => {if (views.length > 0) {e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#000000'}}}
            disabled={views.length === 0}
          >
            <Download className="w-4 h-4" />
            <span>Export CSV</span>
          </button>
        </div>

        {chartData.length > 0 ? (
          <div className="space-y-3">
            {chartData.map(([date, count]) => (
              <div key={date} className="flex items-center space-x-3">
                <div className="w-24 text-sm text-gray-600 flex items-center">
                  <Calendar className="w-3 h-3 mr-1" />
                  {new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </div>
                <div className="flex-1 rounded-full h-8 overflow-hidden" style={{background: '#E5E5E5'}}>
                  <div
                    className="h-full flex items-center justify-end pr-3 transition-all duration-500"
                    style={{ width: `${(count / maxViews) * 100}%`, minWidth: '40px', background: '#FF5959' }}
                  >
                    <span className="text-sm font-bold text-white">{count}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p>No views yet. Share this property to start tracking analytics.</p>
          </div>
        )}
      </div>

      {/* Recent Views Table */}
      {views.length > 0 && (
        <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
          <h3 className="text-lg font-black uppercase mb-4" style={{color: '#000000', letterSpacing: '1px'}}>Recent Views</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr style={{borderBottom: '2px solid #E5E5E5'}}>
                  <th className="text-left py-3 px-4 text-xs font-bold uppercase" style={{color: '#666666', letterSpacing: '1px'}}>Date & Time</th>
                  <th className="text-left py-3 px-4 text-xs font-bold uppercase" style={{color: '#666666', letterSpacing: '1px'}}>Browser</th>
                  <th className="text-left py-3 px-4 text-xs font-bold uppercase" style={{color: '#666666', letterSpacing: '1px'}}>Location</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {views.slice(0, 10).map((view, index) => {
                  const browserMatch = view.user_agent?.match(/(Chrome|Firefox|Safari|Edge|Opera)/i)
                  const browser = browserMatch ? browserMatch[1] : 'Unknown'
                  
                  return (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="py-3 px-4 text-sm text-gray-900">
                        {new Date(view.viewed_at).toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">{browser}</td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        {view.ip_address || 'Unknown'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          {views.length > 10 && (
            <div className="mt-4 text-center">
              <p className="text-sm text-gray-500">
                Showing 10 of {views.length} total views
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Analytics
