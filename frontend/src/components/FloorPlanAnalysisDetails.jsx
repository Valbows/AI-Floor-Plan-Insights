/**
 * Floor Plan Analysis Details Component
 * Shows room-by-room breakdown with dimensions and OCR/Vision comparison
 */

import React, { useState } from 'react';
import { Ruler, Eye, Maximize2, CheckCircle, AlertCircle, Bed, Bath, UtensilsCrossed, Home, Maximize, ArrowUpDown, Shirt, Archive, Briefcase, Armchair, Trash2, DoorOpen, TreePine, Info, Star, ChevronDown, ChevronUp } from 'lucide-react';

const FloorPlanAnalysisDetails = ({ extractedData, showAllFeatures, setShowAllFeatures }) => {
  const [expandedRows, setExpandedRows] = useState(new Set())
  const [expandAll, setExpandAll] = useState(false)
  const [isTableExpanded, setIsTableExpanded] = useState(false)
  
  const toggleRowExpanded = (index) => {
    const newExpanded = new Set(expandedRows)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedRows(newExpanded)
  }
  
  const toggleExpandAll = () => {
    setExpandAll(!expandAll)
  }
  
  const toggleTableExpanded = () => {
    setIsTableExpanded(!isTableExpanded)
  }
  if (!extractedData) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-500">No floor plan analysis data available</p>
      </div>
    );
  }

  const { rooms = [], square_footage, notes } = extractedData;

  // Check if OCR was used (from notes field)
  const ocrMethod = notes?.includes('OCR:') ? notes.split('OCR:')[1]?.trim() : 'none';
  const usedOCR = ocrMethod !== 'none' && ocrMethod !== 'failed';

  // Helper function to get icon based on room type with specific icons for each room
  const getRoomIcon = (type) => {
    const lowerType = type.toLowerCase()
    
    // Priority order: most specific rooms first
    if (lowerType.includes('bedroom') || lowerType.includes('bed')) return <Bed className="w-4 h-4" />
    if (lowerType.includes('bathroom') || lowerType.includes('bath')) return <Bath className="w-4 h-4" />
    if (lowerType.includes('kitchen')) return <UtensilsCrossed className="w-4 h-4" />
    if (lowerType.includes('living') || lowerType.includes('dining')) return <Home className="w-4 h-4" />
    if (lowerType.includes('stairs') || lowerType.includes('stair')) return <ArrowUpDown className="w-4 h-4" />
    if (lowerType.includes('closet') || lowerType.includes('walk-in')) return <Shirt className="w-4 h-4" />
    
    // New specific room icons
    if (lowerType.includes('pantry')) return <Archive className="w-4 h-4" />
    if (lowerType.includes('office')) return <Briefcase className="w-4 h-4" />
    if (lowerType.includes('den')) return <Armchair className="w-4 h-4" />
    if (lowerType.includes('trash') || lowerType.includes('garbage')) return <Trash2 className="w-4 h-4" />
    if (lowerType.includes('entryway') || lowerType.includes('foyer') || lowerType.includes('entry')) return <DoorOpen className="w-4 h-4" />
    if (lowerType.includes('balcony')) return <TreePine className="w-4 h-4" />
    
    // General room types
    if (lowerType.includes('corridor') || lowerType.includes('elevator') || lowerType.includes('lobby')) return <Maximize className="w-4 h-4" />
    
    return <Maximize className="w-4 h-4" />
  }

  // Helper function to get key features for a specific room based on property features
  const getRoomKeyFeatures = (roomType) => {
    const lowerRoomType = roomType.toLowerCase()
    const propertyFeatures = extractedData.features || []
    const keyFeatures = []

    propertyFeatures.forEach(feature => {
      const lowerFeature = feature.toLowerCase()
      
      // Map features to specific room types
      if (lowerRoomType.includes('bedroom') || lowerRoomType.includes('bed')) {
        if (lowerFeature.includes('walk-in closet') || lowerFeature.includes('walk in closet')) {
          keyFeatures.push('Premium Storage')
        }
        if (lowerFeature.includes('skylights') || lowerFeature.includes('skylight')) {
          keyFeatures.push('Natural Light')
        }
        if (lowerFeature.includes('dormer') || lowerFeature.includes('window')) {
          keyFeatures.push('Architectural Detail')
        }
      }
      
      if (lowerRoomType.includes('stairs') || lowerRoomType.includes('stair')) {
        if (lowerFeature.includes('lower level') || lowerFeature.includes('stairs to')) {
          keyFeatures.push('Multi-Level Access')
        }
      }
      
      if (lowerRoomType.includes('closet')) {
        if (lowerFeature.includes('linen') || lowerFeature.includes('walk-in')) {
          keyFeatures.push('Storage Feature')
        }
      }
      
      if (lowerRoomType.includes('balcony')) {
        if (lowerFeature.includes('outdoor') || lowerFeature.includes('balcony')) {
          keyFeatures.push('Outdoor Space')
        }
      }
      
      // General features that could apply to any room
      if (lowerFeature.includes('skylights') && (lowerRoomType.includes('living') || lowerRoomType.includes('dining'))) {
        keyFeatures.push('Natural Light')
      }
    })

    return keyFeatures
  }

  return (
    <div className="space-y-6">

      {/* Room-by-Room Breakdown */}
      <div 
        className="rounded-lg p-6 cursor-pointer transition-all duration-200 hover:shadow-lg" 
        style={{
          background: '#FFFFFF', 
          border: `2px solid ${isTableExpanded ? '#FF5959' : '#000000'}`,
          transform: 'translateY(0)',
        }}
        onClick={toggleTableExpanded}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-2px)'
          e.currentTarget.style.boxShadow = '0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)'
          e.currentTarget.style.boxShadow = 'none'
        }}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <h3 className="text-xs font-bold uppercase flex items-center gap-2" style={{color: '#666666', letterSpacing: '1px'}}>
              <Ruler className="w-4 h-4" />
              Room-by-Room Measurements
              {/* Visual indicator that it's clickable */}
              <span className="text-xs font-normal" style={{color: '#999999'}}>
                {isTableExpanded ? '(Click to collapse)' : '(Click to expand)'}
              </span>
            </h3>
            
            {/* Analysis Method Tooltip */}
            <div className="group relative">
              <Info 
                className="w-4 h-4 cursor-help transition-colors" 
                style={{color: '#666666'}}
                onMouseEnter={(e) => e.currentTarget.style.color = '#FF5959'}
                onMouseLeave={(e) => e.currentTarget.style.color = '#666666'}
                onClick={(e) => e.stopPropagation()} // Prevent container click
              />
              <div className="absolute left-0 top-6 w-72 p-4 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50"
                   style={{background: '#000000', border: '2px solid #FF5959'}}>
                <div className="flex items-center gap-2 mb-3">
                  <Eye className="w-4 h-4" style={{color: '#FF5959'}} />
                  <p className="text-xs font-bold uppercase" style={{color: '#FF5959', letterSpacing: '1px'}}>Analysis Method</p>
                </div>
                <div className="space-y-2 text-xs" style={{color: '#FFFFFF'}}>
                  <p>✅ <span className="font-semibold">Google Gemini Vision:</span> Room identification and layout analysis</p>
                  {usedOCR && (
                    <p>✅ <span className="font-semibold">OCR ({ocrMethod}):</span> Dimension extraction and validation</p>
                  )}
                  {!usedOCR && (
                    <p>⚠️ <span className="font-semibold">OCR:</span> Not used (no dimensions found or failed)</p>
                  )}
                </div>
              </div>
            </div>
          </div>
          
          {/* Expand/Collapse Indicator - Now just visual, not clickable */}
          <div className="flex items-center gap-2 pointer-events-none">
            <span className="text-xs font-medium" style={{color: '#666666'}}>
              {isTableExpanded ? 'Expanded' : 'Collapsed'}
            </span>
            {isTableExpanded ? (
              <ChevronUp className="w-5 h-5" style={{color: '#FF5959'}} />
            ) : (
              <ChevronDown className="w-5 h-5" style={{color: '#666666'}} />
            )}
          </div>
        </div>

        {rooms.length === 0 ? (
          <p className="text-sm" style={{color: '#666666'}}>No rooms identified</p>
        ) : isTableExpanded ? (
          <div className="overflow-x-auto" onClick={(e) => e.stopPropagation()}>
            <table className="w-full" style={{borderCollapse: 'separate', borderSpacing: '0'}}>
              <thead>
                <tr style={{background: '#000000'}}>
                  <th className="text-left text-xs font-black uppercase px-4 py-4 border-b-2" style={{color: '#FFFFFF', letterSpacing: '1.5px', borderColor: '#000000', width: '35%'}}>
                    Room
                  </th>
                  <th className="text-center text-xs font-black uppercase px-4 py-4 border-b-2" style={{color: '#FFFFFF', letterSpacing: '1.5px', borderColor: '#000000', width: '30%'}}>
                    Dimensions
                  </th>
                  <th className="text-left text-xs font-black uppercase px-4 py-4 border-b-2" style={{color: '#FFFFFF', letterSpacing: '1.5px', borderColor: '#000000', width: '25%'}}>
                    <div className="flex items-center justify-between">
                      <span>Features</span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          toggleExpandAll()
                        }}
                        className="text-xs px-3 py-1.5 rounded font-bold uppercase transition-all"
                        style={{
                          background: expandAll ? '#FF5959' : '#FFFFFF',
                          color: expandAll ? '#FFFFFF' : '#000000',
                          border: '1px solid #FFFFFF',
                          letterSpacing: '1px'
                        }}
                        onMouseEnter={(e) => {
                          if (!expandAll) {
                            e.currentTarget.style.background = '#FF5959'
                            e.currentTarget.style.color = '#FFFFFF'
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (!expandAll) {
                            e.currentTarget.style.background = '#FFFFFF'
                            e.currentTarget.style.color = '#000000'
                          }
                        }}
                        title={expandAll ? 'Collapse all features' : 'Expand all features'}
                      >
                        {expandAll ? 'Collapse' : 'Expand All'}
                      </button>
                    </div>
                  </th>
                  <th className="text-center text-xs font-black uppercase px-4 py-4 border-b-2" style={{color: '#FFFFFF', letterSpacing: '1.5px', borderColor: '#000000', width: '10%'}}>
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {rooms.map((room, index) => (
                  <tr
                    key={index}
                    className="transition-colors relative"
                    style={{
                      background: index % 2 === 0 ? '#FFFFFF' : '#F6F1EB',
                      borderBottom: '1px solid #E5E5E5'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#FFF5F5'}
                    onMouseLeave={(e) => e.currentTarget.style.background = index % 2 === 0 ? '#FFFFFF' : '#F6F1EB'}
                  >
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-8 h-8 rounded-lg" style={{background: '#FFF5F5', color: '#FF5959'}}>
                          {getRoomIcon(room.type || 'Unknown Room')}
                        </div>
                        <span className="font-black text-sm uppercase tracking-wide" style={{color: '#000000', letterSpacing: '0.5px'}}>
                          {room.type || 'Unknown Room'}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-4 text-center">
                      {room.dimensions ? (
                        <span className="inline-flex items-center gap-2 px-4 py-2 text-sm font-bold rounded" style={{background: '#F6F1EB', color: '#000000', border: '2px solid #000000'}}>
                          <Ruler className="w-4 h-4" />
                          {room.dimensions}
                        </span>
                      ) : (
                        <span className="text-xs font-medium" style={{color: '#CCCCCC'}}>—</span>
                      )}
                    </td>
                    <td className="px-4 py-4">
                      {(() => {
                        const roomFeatures = room.features || []
                        const keyFeatures = getRoomKeyFeatures(room.type || 'Unknown Room')
                        const allFeatures = [...roomFeatures]
                        
                        // Add key features that aren't already in room features
                        keyFeatures.forEach(keyFeature => {
                          if (!roomFeatures.some(rf => rf.toLowerCase().includes(keyFeature.toLowerCase().split(' ')[0]))) {
                            allFeatures.push(keyFeature)
                          }
                        })
                        
                        if (allFeatures.length === 0) {
                          return <span className="text-xs font-medium" style={{color: '#CCCCCC'}}>—</span>
                        }
                        
                        const isExpanded = expandAll || expandedRows.has(index)
                        
                        // Sort features: premium first
                        const sortedFeatures = allFeatures.sort((a, b) => {
                          const aIsKey = keyFeatures.some(kf => 
                            a.toLowerCase().includes(kf.toLowerCase().split(' ')[0]) ||
                            kf.toLowerCase().includes(a.toLowerCase().split(' ')[0])
                          )
                          const bIsKey = keyFeatures.some(kf => 
                            b.toLowerCase().includes(kf.toLowerCase().split(' ')[0]) ||
                            kf.toLowerCase().includes(b.toLowerCase().split(' ')[0])
                          )
                          return bIsKey - aIsKey
                        })
                        
                        // When expanded, show all features inline
                        if (isExpanded) {
                          return (
                            <div className="space-y-2">
                              {sortedFeatures.map((feature, idx) => {
                                const isKey = keyFeatures.some(kf => 
                                  feature.toLowerCase().includes(kf.toLowerCase().split(' ')[0]) ||
                                  kf.toLowerCase().includes(feature.toLowerCase().split(' ')[0])
                                )
                                return (
                                  <div
                                    key={idx}
                                    className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-lg mr-2 mb-1"
                                    style={{
                                      background: isKey ? '#FEF3C7' : '#F3F4F6',
                                      color: isKey ? '#92400E' : '#374151',
                                      border: isKey ? '1px solid #FDE68A' : '1px solid #E5E7EB'
                                    }}
                                  >
                                    {isKey && <Star className="w-3 h-3" style={{color: '#F59E0B'}} fill="#F59E0B" />}
                                    <span>{feature}</span>
                                  </div>
                                )
                              })}
                            </div>
                          )
                        }
                        
                        // When collapsed, show only primary feature
                        const primaryFeature = sortedFeatures[0]
                        const isKeyFeature = keyFeatures.some(kf => 
                          primaryFeature.toLowerCase().includes(kf.toLowerCase().split(' ')[0]) ||
                          kf.toLowerCase().includes(primaryFeature.toLowerCase().split(' ')[0])
                        )
                        
                        return (
                          <div className="flex items-center gap-2">
                            {/* Primary feature badge */}
                            <div
                              className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-lg flex-1 min-w-0"
                              style={{
                                background: isKeyFeature ? '#FEF3C7' : '#F3F4F6',
                                color: isKeyFeature ? '#92400E' : '#374151',
                                border: isKeyFeature ? '1px solid #FDE68A' : '1px solid #E5E7EB'
                              }}
                            >
                              {isKeyFeature && <Star className="w-3 h-3 flex-shrink-0" style={{color: '#F59E0B'}} fill="#F59E0B" />}
                              <span className="truncate">{primaryFeature}</span>
                            </div>
                            
                            {/* Expand button if more features exist */}
                            {allFeatures.length > 1 && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  toggleRowExpanded(index)
                                }}
                                className="text-xs px-2 py-1 rounded-lg font-medium transition-colors flex-shrink-0"
                                style={{
                                  background: '#F3F4F6',
                                  color: '#6B7280',
                                  border: '1px solid #E5E7EB'
                                }}
                                onMouseEnter={(e) => {
                                  e.currentTarget.style.background = '#E5E7EB'
                                }}
                                onMouseLeave={(e) => {
                                  e.currentTarget.style.background = '#F3F4F6'
                                }}
                                title={`View all ${allFeatures.length} features`}
                              >
                                +{allFeatures.length - 1}
                              </button>
                            )}
                          </div>
                        )
                      })()}
                    </td>
                    
                    <td className="px-4 py-4 text-center">
                      {room.dimensions ? (
                        <div className="inline-flex items-center justify-center w-8 h-8 rounded-lg" style={{background: '#DCFCE7', color: '#16A34A'}}>
                          <CheckCircle className="w-4 h-4" />
                        </div>
                      ) : (
                        <div className="inline-flex items-center justify-center w-8 h-8 rounded-lg" style={{background: '#FEF2F2', color: '#DC2626'}}>
                          <AlertCircle className="w-4 h-4" />
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
              
              {/* Summary Footer */}
              <tfoot>
                <tr style={{background: '#F6F1EB'}}>
                  <td colSpan="4" className="px-4 py-6">
                    <div className="grid grid-cols-3 gap-6">
                      <div className="text-center">
                        <p className="text-xs font-black uppercase mb-2" style={{color: '#666666', letterSpacing: '1.5px'}}>TOTAL ROOMS</p>
                        <p className="text-3xl font-black" style={{color: '#000000'}}>{rooms.length}</p>
                      </div>
                      <div className="text-center border-x border-gray-300">
                        <p className="text-xs font-black uppercase mb-2" style={{color: '#666666', letterSpacing: '1.5px'}}>SQUARE FOOTAGE</p>
                        <p className="text-3xl font-black" style={{color: '#FF5959'}}>{square_footage?.toLocaleString() || 'N/A'}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs font-black uppercase mb-2" style={{color: '#666666', letterSpacing: '1.5px'}}>WITH DIMENSIONS</p>
                        <p className="text-3xl font-black" style={{color: '#000000'}}>
                          {rooms.filter(r => r.dimensions).length}
                        </p>
                      </div>
                    </div>
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        ) : (
          /* Collapsed Summary View */
          <div className="border-t-2 border-gray-300 pt-6 mt-4">
            <div className="grid grid-cols-3 gap-6">
              <div className="text-center">
                <p className="text-xs font-black uppercase mb-2" style={{color: '#666666', letterSpacing: '1.5px'}}>TOTAL ROOMS</p>
                <p className="text-4xl font-black" style={{color: '#000000'}}>{rooms.length}</p>
              </div>
              <div className="text-center border-x-2 border-gray-300">
                <p className="text-xs font-black uppercase mb-2" style={{color: '#666666', letterSpacing: '1.5px'}}>SQUARE FOOTAGE</p>
                <p className="text-4xl font-black" style={{color: '#FF5959'}}>{square_footage?.toLocaleString() || 'N/A'}</p>
              </div>
              <div className="text-center">
                <p className="text-xs font-black uppercase mb-2" style={{color: '#666666', letterSpacing: '1.5px'}}>WITH DIMENSIONS</p>
                <p className="text-4xl font-black" style={{color: '#000000'}}>
                  {rooms.filter(r => r.dimensions).length}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Analysis Notes */}
      {notes && (
        <div className="rounded-lg p-4" style={{background: '#FFF5F5', border: '1px solid #FFE5E5'}}>
          <h4 className="text-xs font-bold uppercase mb-2" style={{color: '#FF5959', letterSpacing: '1px'}}>Analysis Notes</h4>
          <p className="text-sm" style={{color: '#000000'}}>{notes}</p>
        </div>
      )}
    </div>
  );
};

export default FloorPlanAnalysisDetails;
