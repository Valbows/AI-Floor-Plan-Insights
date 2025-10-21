import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { BarChart3, Loader, Check, X, MapPin, ChevronDown, SlidersHorizontal, Search, Building2 } from 'lucide-react'
import axios from 'axios'
import UnitMixChart from '../components/charts/UnitMixChart'
import LivingRoomPPSFChart_Option3 from '../components/charts/LivingRoomPPSFChart_Option3'
import LivingRoomPPSFChart_Option4 from '../components/charts/LivingRoomPPSFChart_Option4'
import BedroomPPSFChart_Trend from '../components/charts/BedroomPPSFChart_Trend'
import BedroomPPSFChart_Grid from '../components/charts/BedroomPPSFChart_Grid'
import { getUniqueNeighborhoods, extractNeighborhood } from '../utils/neighborhoodUtils'

const DataStudio = () => {
  const [properties, setProperties] = useState([])
  const [loading, setLoading] = useState(true)
  const [neighborhoodFilter, setNeighborhoodFilter] = useState('all')
  const [bedroomFilter, setBedroomFilter] = useState('all')
  const [sqftMin, setSqftMin] = useState('')
  const [sqftMax, setSqftMax] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [buildingFilter, setBuildingFilter] = useState('all')
  const navigate = useNavigate()

  useEffect(() => {
    document.title = 'Data Studio | FloorIQ'
    fetchProperties()
  }, [])

  const fetchProperties = async () => {
    try {
      const response = await axios.get('/api/properties')
      const allProps = response.data.properties || []
      setProperties(allProps)
    } catch (error) {
      console.error('Failed to fetch properties:', error)
    } finally {
      setLoading(false)
    }
  }

  // Get available neighborhoods
  const availableNeighborhoods = getUniqueNeighborhoods(properties)

  // Get unique bedroom counts
  const uniqueBedrooms = [...new Set(properties
    .map(p => p.extracted_data?.bedrooms)
    .filter(b => b != null)
  )].sort((a, b) => a - b)

  // Get unique buildings (base address without unit number)
  const getBaseAddress = (fullAddress) => {
    if (!fullAddress) return 'Unknown'
    // Remove common unit indicators: #, Unit, Apt, Suite, etc.
    return fullAddress
      .replace(/#.*$/i, '')
      .replace(/,?\s*(unit|apt|suite|apartment|floor|fl)\s*\w+/gi, '')
      .trim()
  }

  const uniqueBuildings = [...new Set(properties
    .map(p => {
      const address = p.extracted_data?.address || p.address || ''
      return getBaseAddress(address)
    })
    .filter(addr => addr && addr !== 'Unknown')
  )].sort()

  // Count units per building
  const buildingsWithCounts = uniqueBuildings.map(building => {
    const count = properties.filter(p => {
      const address = p.extracted_data?.address || p.address || ''
      return getBaseAddress(address) === building
    }).length
    return { building, count }
  }).filter(b => b.count > 1) // Only show buildings with multiple units

  // Advanced filtering logic
  const filteredProperties = properties.filter(property => {
    const extracted = property.extracted_data || {}
    const address = extracted.address || property.address || ''
    
    // Search filter
    if (searchTerm && !address.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false
    }
    
    // Neighborhood filter
    if (neighborhoodFilter !== 'all') {
      const neighborhood = extractNeighborhood(address)
      if (neighborhood !== neighborhoodFilter) return false
    }

    // Building filter
    if (buildingFilter !== 'all') {
      const baseAddress = getBaseAddress(address)
      if (baseAddress !== buildingFilter) return false
    }
    
    // Bedroom filter
    if (bedroomFilter !== 'all') {
      if (bedroomFilter === '0') {
        // Studio (0 bedrooms)
        if (extracted.bedrooms !== 0) return false
      } else if (bedroomFilter === '4+') {
        // 4+ bedrooms
        if (!extracted.bedrooms || extracted.bedrooms < 4) return false
      } else {
        // Exact match
        if (extracted.bedrooms !== parseInt(bedroomFilter)) return false
      }
    }
    
    // Square footage filter
    const sqft = extracted.square_footage || 0
    if (sqftMin && sqft < parseInt(sqftMin)) return false
    if (sqftMax && sqft > parseInt(sqftMax)) return false
    
    return true
  })

  const clearFilters = () => {
    setSearchTerm('')
    setNeighborhoodFilter('all')
    setBedroomFilter('all')
    setBuildingFilter('all')
    setSqftMin('')
    setSqftMax('')
  }

  const hasActiveFilters = searchTerm || neighborhoodFilter !== 'all' || bedroomFilter !== 'all' || buildingFilter !== 'all' || sqftMin || sqftMax

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader className="w-8 h-8 animate-spin" style={{color: '#FF5959'}} />
      </div>
    )
  }

  return (
    <div className="min-h-screen" style={{background: '#F6F1EB'}}>
      <div className="max-w-[1400px] mx-auto px-4 py-16">
        {/* Hero Header - Matching MY PROPERTIES style */}
        <div className="text-center mb-16">
          <h1 className="text-6xl font-black uppercase tracking-tight mb-8" style={{color: '#000000', letterSpacing: '-2px', lineHeight: '0.95'}}>
            DATA <span style={{color: '#FF5959'}}><span style={{borderBottom: '6px solid #FF5959'}}>STU</span>DIO</span>
          </h1>
          <p className="text-lg font-medium" style={{color: '#666666'}}>
            Interactive analysis of your property portfolio
          </p>
        </div>

        {/* Advanced Filter Panel */}
        {properties.length > 0 && (
          <div className="mb-8">
            <div className="rounded-lg border-2 p-6" style={{borderColor: '#000000', background: 'transparent'}}>
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-black uppercase mb-1" style={{color: '#000000'}}>
                    Comp Set Filters
                  </h3>
                  <p className="text-sm" style={{color: '#666666'}}>
                    Narrow down your comparison set from {properties.length} total properties
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2 text-sm font-bold" style={{color: hasActiveFilters ? '#FF5959' : '#666666'}}>
                    <SlidersHorizontal className="w-4 h-4" />
                    <span>{filteredProperties.length} properties selected</span>
                  </div>
                  {hasActiveFilters && (
                    <button
                      onClick={clearFilters}
                      className="px-4 py-2 font-bold uppercase tracking-wide transition-all text-xs flex items-center gap-2"
                      style={{
                        background: 'transparent',
                        color: '#FF5959',
                        border: '2px solid #FF5959',
                        borderRadius: '4px'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = '#FFF5F5'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = 'transparent'
                      }}
                    >
                      <X className="w-3 h-3" />
                      Clear All
                    </button>
                  )}
                </div>
              </div>

            <div className="space-y-4">
              {/* First Row: Search + Building (if multi-unit buildings exist) */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Search */}
                <div className="relative min-w-0">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5" style={{color: '#666666'}} />
                  <input
                    type="text"
                    placeholder="Search by address..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border-2 focus:outline-none font-semibold transition-all"
                    style={{
                      borderColor: searchTerm ? '#FF5959' : '#000000',
                      borderRadius: '4px',
                      background: searchTerm ? '#FFF5F5' : '#FFFFFF',
                      color: '#000000',
                      fontSize: '14px'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#FF5959';
                      e.target.style.boxShadow = '0 0 0 2px rgba(255,89,89,0.2)';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = searchTerm ? '#FF5959' : '#000000';
                      e.target.style.boxShadow = 'none';
                    }}
                  />
                </div>

                {/* Building Filter (only show if there are multi-unit buildings) */}
                {buildingsWithCounts.length > 0 && (
                  <div className="relative min-w-0">
                    <Building2 className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 pointer-events-none" style={{color: '#666666', zIndex: 10}} />
                    <select
                      value={buildingFilter}
                      onChange={(e) => setBuildingFilter(e.target.value)}
                      className="w-full pl-10 pr-10 py-3 border-2 focus:outline-none appearance-none cursor-pointer font-semibold transition-all relative"
                      style={{
                        borderColor: buildingFilter !== 'all' ? '#FF5959' : '#000000',
                        borderRadius: '4px',
                        background: buildingFilter !== 'all' ? '#FFF5F5' : '#FFFFFF',
                        color: '#000000',
                        fontSize: '14px'
                      }}
                      onFocus={(e) => {
                        e.target.style.borderColor = '#FF5959';
                        e.target.style.boxShadow = '0 0 0 2px rgba(255,89,89,0.2)';
                      }}
                      onBlur={(e) => {
                        e.target.style.borderColor = buildingFilter !== 'all' ? '#FF5959' : '#000000';
                        e.target.style.boxShadow = 'none';
                      }}
                    >
                      <option value="all">All Buildings</option>
                      {buildingsWithCounts.map(({ building, count }) => (
                        <option key={building} value={building}>
                          {building} ({count} units)
                        </option>
                      ))}
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 pointer-events-none" style={{color: '#000000', zIndex: 10}} />
                  </div>
                )}
              </div>

              {/* Second Row: Neighborhood + Bedrooms + Square Footage */}
              <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
                {/* Neighborhood Filter */}
                <div className="md:col-span-4 relative min-w-0">
                  <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 pointer-events-none" style={{color: '#666666', zIndex: 10}} />
                  <select
                    value={neighborhoodFilter}
                    onChange={(e) => setNeighborhoodFilter(e.target.value)}
                    className="w-full pl-10 pr-10 py-3 border-2 focus:outline-none appearance-none cursor-pointer font-semibold transition-all relative"
                    style={{
                      borderColor: neighborhoodFilter !== 'all' ? '#FF5959' : '#000000',
                      borderRadius: '4px',
                      background: neighborhoodFilter !== 'all' ? '#FFF5F5' : '#FFFFFF',
                      color: '#000000',
                      fontSize: '14px'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#FF5959';
                      e.target.style.boxShadow = '0 0 0 2px rgba(255,89,89,0.2)';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = neighborhoodFilter !== 'all' ? '#FF5959' : '#000000';
                      e.target.style.boxShadow = 'none';
                    }}
                  >
                    <option value="all">All Neighborhoods</option>
                    {availableNeighborhoods.map(hood => {
                      const count = properties.filter(p => {
                        const address = p.extracted_data?.address || p.address || '';
                        return extractNeighborhood(address) === hood;
                      }).length;
                      return (
                        <option key={hood} value={hood}>
                          {hood} ({count})
                        </option>
                      );
                    })}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 pointer-events-none" style={{color: '#000000', zIndex: 10}} />
                </div>

                {/* Bedroom Filter */}
                <div className="md:col-span-3 relative min-w-0">
                  <select
                    value={bedroomFilter}
                    onChange={(e) => setBedroomFilter(e.target.value)}
                    className="w-full pl-4 pr-10 py-3 border-2 focus:outline-none appearance-none cursor-pointer font-semibold transition-all relative"
                    style={{
                      borderColor: bedroomFilter !== 'all' ? '#FF5959' : '#000000',
                      borderRadius: '4px',
                      background: bedroomFilter !== 'all' ? '#FFF5F5' : '#FFFFFF',
                      color: '#000000',
                      fontSize: '14px'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#FF5959';
                      e.target.style.boxShadow = '0 0 0 2px rgba(255,89,89,0.2)';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = bedroomFilter !== 'all' ? '#FF5959' : '#000000';
                      e.target.style.boxShadow = 'none';
                    }}
                  >
                    <option value="all">All Beds</option>
                    <option value="0">Studio</option>
                    <option value="1">1 Bed</option>
                    <option value="2">2 Beds</option>
                    <option value="3">3 Beds</option>
                    <option value="4+">4+ Beds</option>
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 pointer-events-none" style={{color: '#000000', zIndex: 10}} />
                </div>

                {/* Square Footage Range */}
                <div className="md:col-span-5 flex gap-2 items-center min-w-0">
                  <input
                    type="number"
                    placeholder="Min"
                    value={sqftMin}
                    onChange={(e) => setSqftMin(e.target.value)}
                    className="flex-1 min-w-0 px-3 py-3 border-2 focus:outline-none font-semibold transition-all"
                    style={{
                      borderColor: sqftMin ? '#FF5959' : '#000000',
                      borderRadius: '4px',
                      background: sqftMin ? '#FFF5F5' : '#FFFFFF',
                      color: '#000000',
                      fontSize: '14px',
                      MozAppearance: 'textfield',
                      WebkitAppearance: 'none',
                      appearance: 'textfield'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#FF5959';
                      e.target.style.boxShadow = '0 0 0 2px rgba(255,89,89,0.2)';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = sqftMin ? '#FF5959' : '#000000';
                      e.target.style.boxShadow = 'none';
                    }}
                  />
                  <span className="text-sm font-bold flex-shrink-0" style={{color: '#666666'}}>—</span>
                  <input
                    type="number"
                    placeholder="Max"
                    value={sqftMax}
                    onChange={(e) => setSqftMax(e.target.value)}
                    className="flex-1 min-w-0 px-3 py-3 border-2 focus:outline-none font-semibold transition-all"
                    style={{
                      borderColor: sqftMax ? '#FF5959' : '#000000',
                      borderRadius: '4px',
                      background: sqftMax ? '#FFF5F5' : '#FFFFFF',
                      color: '#000000',
                      fontSize: '14px',
                      MozAppearance: 'textfield',
                      WebkitAppearance: 'none',
                      appearance: 'textfield'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#FF5959';
                      e.target.style.boxShadow = '0 0 0 2px rgba(255,89,89,0.2)';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = sqftMax ? '#FF5959' : '#000000';
                      e.target.style.boxShadow = 'none';
                    }}
                  />
                  <span className="text-xs font-bold flex-shrink-0 pl-1" style={{color: '#999999'}}>sqft</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts */}
      {filteredProperties.length > 0 ? (
        <div className="space-y-12">
          {/* Section 1: Portfolio Overview */}
          <div>
            <div className="mb-6">
              <h2 className="text-2xl font-black uppercase tracking-tight mb-2" style={{color: '#000000', letterSpacing: '1px'}}>
                Portfolio Overview
              </h2>
              <div className="w-16 h-1" style={{background: '#FF5959'}}></div>
              <p className="text-sm mt-2" style={{color: '#666666'}}>
                Distribution of unit types across your properties
              </p>
            </div>
            <UnitMixChart properties={filteredProperties} />
          </div>

          {/* Divider */}
          <div className="border-t-2" style={{borderColor: '#E5E5E5'}}></div>

          {/* Section 2: Living Room Analysis */}
          <div>
            <div className="mb-6">
              <h2 className="text-2xl font-black uppercase tracking-tight mb-2" style={{color: '#FF5959', letterSpacing: '1px'}}>
                Living Room Analysis
              </h2>
              <div className="w-16 h-1" style={{background: '#FF5959'}}></div>
              <p className="text-sm mt-2" style={{color: '#666666'}}>
                Correlation between living room dimensions and price per square foot
              </p>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Trend Chart */}
              <div>
                <LivingRoomPPSFChart_Option3 properties={filteredProperties} />
              </div>

              {/* Comparison Table */}
              <div>
                <LivingRoomPPSFChart_Option4 properties={filteredProperties} />
              </div>
            </div>
          </div>

          {/* Divider */}
          <div className="border-t-2" style={{borderColor: '#E5E5E5'}}></div>

          {/* Section 3: Bedroom Analysis */}
          <div>
            <div className="mb-6">
              <h2 className="text-2xl font-black uppercase tracking-tight mb-2" style={{color: '#6366F1', letterSpacing: '1px'}}>
                Bedroom Analysis
              </h2>
              <div className="w-16 h-1" style={{background: '#6366F1'}}></div>
              <p className="text-sm mt-2" style={{color: '#666666'}}>
                Correlation between bedroom dimensions and price per square foot
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Trend Chart */}
              <div>
                <BedroomPPSFChart_Trend properties={filteredProperties} />
              </div>

              {/* Comparison Table */}
              <div>
                <BedroomPPSFChart_Grid properties={filteredProperties} />
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg p-12 text-center" style={{border: '3px solid #E5E5E5'}}>
          <BarChart3 className="w-16 h-16 mx-auto mb-4" style={{color: '#CCCCCC'}} />
          <h3 className="text-xl font-black uppercase mb-2" style={{color: '#000000'}}>
            No Data Yet
          </h3>
          <p className="text-sm mb-6" style={{color: '#666666'}}>
            Upload properties with floor plans to see interactive analysis
          </p>
          <button
            onClick={() => navigate('/properties/new')}
            className="px-6 py-3 rounded-lg font-black uppercase text-white transition-all"
            style={{background: '#FF5959', border: '3px solid #000000'}}
            onMouseEnter={(e) => e.currentTarget.style.background = '#000000'}
            onMouseLeave={(e) => e.currentTarget.style.background = '#FF5959'}
          >
            Add Property
          </button>
        </div>
        )}
      </div>
    </div>
  )
}

export default DataStudio

