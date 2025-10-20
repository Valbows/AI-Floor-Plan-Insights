/**
 * Floor Plan Analysis Details Component
 * Shows room-by-room breakdown with dimensions and OCR/Vision comparison
 */

import React from 'react';
import { Ruler, Eye, Maximize2, CheckCircle, AlertCircle, Bed, Bath, UtensilsCrossed, Home, Maximize, ArrowUpDown, Shirt, Archive, Briefcase, Armchair, Trash2, DoorOpen, TreePine, Info } from 'lucide-react';

const FloorPlanAnalysisDetails = ({ extractedData, showAllFeatures, setShowAllFeatures }) => {
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

  return (
    <div className="space-y-6">
      {/* Property Overview - Combined Section */}
      <div className="rounded-lg p-6" style={{background: '#F6F1EB', border: '1px solid #E5E5E5'}}>
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xs font-bold uppercase flex items-center gap-2" style={{color: '#666666', letterSpacing: '1px'}}>
            <Maximize2 className="w-4 h-4" />
            Property Overview
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
        
        {/* Metrics Grid */}
        <div className="grid grid-cols-3 gap-3 mb-6">
          <div className="rounded-lg p-3" style={{background: '#FFFFFF'}}>
            <p className="text-xs font-medium mb-1" style={{color: '#666666'}}>Total Rooms</p>
            <p className="text-2xl font-bold" style={{color: '#000000'}}>{rooms.length}</p>
          </div>
          <div className="rounded-lg p-3" style={{background: '#FFFFFF'}}>
            <p className="text-xs font-medium mb-1" style={{color: '#666666'}}>Square Footage</p>
            <p className="text-2xl font-bold" style={{color: '#000000'}}>{square_footage?.toLocaleString() || 'N/A'}</p>
          </div>
          <div className="rounded-lg p-3" style={{background: '#FFFFFF'}}>
            <p className="text-xs font-medium mb-1" style={{color: '#666666'}}>With Dimensions</p>
            <p className="text-2xl font-bold" style={{color: '#000000'}}>
              {rooms.filter(r => r.dimensions).length}
            </p>
          </div>
        </div>

        {/* Layout Type & Features Side by Side */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Layout Type */}
          {extractedData.layout_type && (
            <div className="rounded-lg p-4" style={{background: '#FFFFFF'}}>
              <h4 className="text-xs font-bold uppercase mb-2" style={{color: '#666666', letterSpacing: '1px'}}>Layout Type</h4>
              <p className="text-sm leading-relaxed" style={{color: '#000000'}}>{extractedData.layout_type}</p>
            </div>
          )}

          {/* Features */}
          {extractedData.features && extractedData.features.length > 0 && (
            <div className="rounded-lg p-4" style={{background: '#FFFFFF'}}>
              <h4 className="text-xs font-bold uppercase mb-2" style={{color: '#666666', letterSpacing: '1px'}}>Key Features</h4>
              <ul className="space-y-1">
                {extractedData.features.slice(0, showAllFeatures ? extractedData.features.length : 4).map((feature, index) => (
                  <li key={index} className="flex items-start text-sm">
                    <span className="mr-2 mt-0.5" style={{color: '#FF5959'}}>•</span>
                    <span style={{color: '#000000'}}>{feature}</span>
                  </li>
                ))}
                {extractedData.features.length > 4 && !showAllFeatures && (
                  <li>
                    <button
                      onClick={() => setShowAllFeatures(true)}
                      className="text-xs font-medium transition-all hover:underline cursor-pointer"
                      style={{color: '#FF5959'}}
                      onMouseEnter={(e) => e.currentTarget.style.color = '#E54545'}
                      onMouseLeave={(e) => e.currentTarget.style.color = '#FF5959'}
                    >
                      +{extractedData.features.length - 4} more features
                    </button>
                  </li>
                )}
                {showAllFeatures && extractedData.features.length > 4 && (
                  <li>
                    <button
                      onClick={() => setShowAllFeatures(false)}
                      className="text-xs font-medium transition-all hover:underline cursor-pointer"
                      style={{color: '#666666'}}
                      onMouseEnter={(e) => e.currentTarget.style.color = '#000000'}
                      onMouseLeave={(e) => e.currentTarget.style.color = '#666666'}
                    >
                      Show less
                    </button>
                  </li>
                )}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Room-by-Room Breakdown */}
      <div className="rounded-lg p-4" style={{background: '#F6F1EB', border: '1px solid #E5E5E5'}}>
        <h3 className="text-xs font-bold uppercase mb-4 flex items-center gap-2" style={{color: '#666666', letterSpacing: '1px'}}>
          <Ruler className="w-4 h-4" />
          Room-by-Room Measurements
        </h3>

        {rooms.length === 0 ? (
          <p className="text-sm" style={{color: '#666666'}}>No rooms identified</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full" style={{borderCollapse: 'separate', borderSpacing: '0 4px'}}>
              <thead>
                <tr>
                  <th className="text-left text-xs font-bold uppercase px-3 py-2" style={{color: '#666666', letterSpacing: '1px', background: 'transparent'}}>
                    Room
                  </th>
                  <th className="text-center text-xs font-bold uppercase px-3 py-2" style={{color: '#666666', letterSpacing: '1px', background: 'transparent'}}>
                    Dimensions
                  </th>
                  <th className="text-left text-xs font-bold uppercase px-3 py-2" style={{color: '#666666', letterSpacing: '1px', background: 'transparent'}}>
                    Features
                  </th>
                  <th className="text-center text-xs font-bold uppercase px-3 py-2" style={{color: '#666666', letterSpacing: '1px', background: 'transparent', width: '60px'}}>
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {rooms.map((room, index) => (
                  <tr
                    key={index}
                    className="transition-colors"
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
                    <td className="px-3 py-3" style={{borderTop: '1px solid #E5E5E5', borderBottom: '1px solid #E5E5E5'}}>
                      {room.features && room.features.length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {room.features.slice(0, 3).map((feature, idx) => (
                            <span
                              key={idx}
                              className="text-xs px-2 py-0.5 rounded"
                              style={{color: '#666666', background: '#F6F1EB'}}
                            >
                              {feature}
                            </span>
                          ))}
                          {room.features.length > 3 && (
                            <span className="text-xs font-medium" style={{color: '#666666'}}>
                              +{room.features.length - 3}
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-xs" style={{color: '#CCCCCC'}}>—</span>
                      )}
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
