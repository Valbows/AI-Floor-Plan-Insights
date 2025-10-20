/**
 * Floor Plan Analysis Details Component
 * Shows room-by-room breakdown with dimensions and OCR/Vision comparison
 */

import React, { useState } from 'react';
import { Ruler, Eye, Maximize2, CheckCircle, AlertCircle, Bed, Bath, UtensilsCrossed, Home, Maximize, ArrowUpDown, Shirt, Archive, Briefcase, Armchair, Trash2, DoorOpen, TreePine, Info, Star } from 'lucide-react';

const FloorPlanAnalysisDetails = ({ extractedData, showAllFeatures, setShowAllFeatures }) => {
  const [expandedRows, setExpandedRows] = useState(new Set())
  const [expandAll, setExpandAll] = useState(false)
  
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
      <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xs font-bold uppercase flex items-center gap-2" style={{color: '#666666', letterSpacing: '1px'}}>
            <Ruler className="w-4 h-4" />
            Room-by-Room Measurements
          </h3>
          
          {/* Analysis Method Tooltip */}
          <div className="group relative">
            <Info 
              className="w-4 h-4 cursor-help transition-colors" 
              style={{color: '#666666'}}
              onMouseEnter={(e) => e.currentTarget.style.color = '#FF5959'}
              onMouseLeave={(e) => e.currentTarget.style.color = '#666666'}
            />
            <div className="absolute right-0 top-6 w-72 p-4 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50"
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

        {rooms.length === 0 ? (
          <p className="text-sm" style={{color: '#666666'}}>No rooms identified</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full" style={{borderCollapse: 'separate', borderSpacing: '0 4px'}}>
              <thead>
                <tr>
                  <th className="text-left text-xs font-bold uppercase px-3 py-2" style={{color: '#666666', letterSpacing: '1px', background: 'transparent', width: '35%'}}>
                    Room
                  </th>
                  <th className="text-center text-xs font-bold uppercase px-3 py-2" style={{color: '#666666', letterSpacing: '1px', background: 'transparent', width: '30%'}}>
                    Dimensions
                  </th>
                  <th className="text-left text-xs font-bold uppercase px-3 py-2" style={{color: '#666666', letterSpacing: '1px', background: 'transparent', width: '25%'}}>
                    <div className="flex items-center justify-between">
                      <span>Features</span>
                      <button
                        onClick={toggleExpandAll}
                        className="text-xs px-2 py-1 rounded hover:bg-gray-100 transition-colors normal-case"
                        style={{color: '#999999', fontWeight: '500', letterSpacing: 'normal'}}
                        title={expandAll ? 'Collapse all features' : 'Expand all features'}
                      >
                        {expandAll ? 'Collapse All' : 'Expand All'}
                      </button>
                    </div>
                  </th>
                  <th className="text-center text-xs font-bold uppercase px-3 py-2" style={{color: '#666666', letterSpacing: '1px', background: 'transparent', width: '10%'}}>
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {rooms.map((room, index) => (
                  <tr
                    key={index}
                    className="transition-colors relative"
                    style={{background: '#FFFFFF'}}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#FFF5F5'}
                    onMouseLeave={(e) => e.currentTarget.style.background = '#FFFFFF'}
                  >
                    <td className="px-3 py-3 rounded-l-lg" style={{borderLeft: '1px solid #E5E5E5', borderTop: '1px solid #E5E5E5', borderBottom: '1px solid #E5E5E5'}}>
                      <div className="flex items-center gap-2">
                        <div className="flex items-center justify-center" style={{color: '#FF5959'}}>
                          {getRoomIcon(room.type || 'Unknown Room')}
                        </div>
                        <span className="font-medium capitalize text-sm" style={{color: '#000000'}}>
                          {room.type || 'Unknown Room'}
                        </span>
                      </div>
                    </td>
                    <td className="px-3 py-3 text-center" style={{borderTop: '1px solid #E5E5E5', borderBottom: '1px solid #E5E5E5'}}>
                      {room.dimensions ? (
                        <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded" style={{background: '#FFF5F5', color: '#FF5959'}}>
                          <Ruler className="w-3 h-3" />
                          {room.dimensions}
                        </span>
                      ) : (
                        <span className="text-xs" style={{color: '#CCCCCC'}}>—</span>
                      )}
                    </td>
                    <td className="px-3 py-2" style={{borderTop: '1px solid #E5E5E5', borderBottom: '1px solid #E5E5E5'}}>
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
                          return <span className="text-xs" style={{color: '#CCCCCC'}}>—</span>
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
                            <div className="space-y-1">
                              {sortedFeatures.map((feature, idx) => {
                                const isKey = keyFeatures.some(kf => 
                                  feature.toLowerCase().includes(kf.toLowerCase().split(' ')[0]) ||
                                  kf.toLowerCase().includes(feature.toLowerCase().split(' ')[0])
                                )
                                return (
                                  <div
                                    key={idx}
                                    className="text-xs px-2 py-0.5 rounded flex items-center gap-1"
                                    style={{
                                      color: '#666666', 
                                      background: isKey ? '#FFF5F5' : '#F6F1EB',
                                      border: isKey ? '1px solid #FFE5E5' : 'none'
                                    }}
                                  >
                                    {isKey && <Star className="w-2.5 h-2.5 flex-shrink-0" style={{color: '#FFD700'}} fill="#FFD700" />}
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
                              className="text-xs px-2 py-0.5 rounded flex items-center gap-1 flex-1 min-w-0"
                              style={{
                                color: '#666666', 
                                background: isKeyFeature ? '#FFF5F5' : '#F6F1EB',
                                border: isKeyFeature ? '1px solid #FFE5E5' : 'none'
                              }}
                            >
                              {isKeyFeature && <Star className="w-2.5 h-2.5 flex-shrink-0" style={{color: '#FFD700'}} fill="#FFD700" />}
                              <span className="truncate">{primaryFeature}</span>
                            </div>
                            
                            {/* Expand button if more features exist */}
                            {allFeatures.length > 1 && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  toggleRowExpanded(index)
                                }}
                                className="text-xs px-1.5 py-0.5 rounded hover:bg-gray-200 transition-colors flex-shrink-0"
                                style={{color: '#999999', fontWeight: '500'}}
                                title={`View all ${allFeatures.length} features`}
                              >
                                +{allFeatures.length - 1}
                              </button>
                            )}
                          </div>
                        )
                      })()}
                    </td>
                    
                    <td className="px-3 py-3 text-center rounded-r-lg" style={{borderRight: '1px solid #E5E5E5', borderTop: '1px solid #E5E5E5', borderBottom: '1px solid #E5E5E5'}}>
                      {room.dimensions ? (
                        <CheckCircle className="w-4 h-4 inline-block" style={{color: '#22C55E'}} />
                      ) : (
                        <AlertCircle className="w-4 h-4 inline-block" style={{color: '#CCCCCC'}} title="No dimensions found" />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
              
              {/* Summary Footer */}
              <tfoot>
                <tr>
                  <td colSpan="4" className="px-3 py-4">
                    <div className="border-t border-gray-200 pt-4">
                      <div className="grid grid-cols-3 gap-4">
                        <div className="text-center">
                          <p className="text-xs font-medium mb-1" style={{color: '#666666'}}>TOTAL ROOMS</p>
                          <p className="text-lg font-bold" style={{color: '#000000'}}>{rooms.length}</p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs font-medium mb-1" style={{color: '#666666'}}>SQUARE FOOTAGE</p>
                          <p className="text-lg font-bold" style={{color: '#000000'}}>{square_footage?.toLocaleString() || 'N/A'}</p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs font-medium mb-1" style={{color: '#666666'}}>WITH DIMENSIONS</p>
                          <p className="text-lg font-bold" style={{color: '#000000'}}>
                            {rooms.filter(r => r.dimensions).length}
                          </p>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              </tfoot>
            </table>
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
