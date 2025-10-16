/**
 * Floor Plan Analysis Details Component
 * Shows room-by-room breakdown with dimensions and OCR/Vision comparison
 */

import React from 'react';
import { Ruler, Eye, Maximize2, CheckCircle, AlertCircle } from 'lucide-react';

const FloorPlanAnalysisDetails = ({ extractedData }) => {
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

  return (
    <div className="space-y-6">
      {/* Analysis Method Info */}
      <div className="rounded-lg p-4" style={{background: '#F6F1EB', border: '1px solid #E5E5E5'}}>
        <div className="flex items-start gap-3">
          <Eye className="w-4 h-4 mt-0.5" style={{color: '#FF5959'}} />
          <div className="flex-1">
            <h3 className="text-xs font-bold uppercase mb-2" style={{color: '#666666', letterSpacing: '1px'}}>Analysis Method</h3>
            <div className="text-sm space-y-1" style={{color: '#000000'}}>
              <p>✅ <span className="font-medium">Google Gemini Vision</span>: Room identification and layout</p>
              {usedOCR && (
                <p>✅ <span className="font-medium">OCR ({ocrMethod})</span>: Dimension extraction and validation</p>
              )}
              {!usedOCR && (
                <p>⚠️ <span className="font-medium">OCR</span>: Not used (no dimensions found or failed)</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Overall Metrics */}
      <div className="rounded-lg p-4" style={{background: '#F6F1EB', border: '1px solid #E5E5E5'}}>
        <h3 className="text-xs font-bold uppercase mb-4 flex items-center gap-2" style={{color: '#666666', letterSpacing: '1px'}}>
          <Maximize2 className="w-4 h-4" />
          Overall Property Metrics
        </h3>
        <div className="grid grid-cols-3 gap-3">
          <div className="rounded-lg p-3" style={{background: '#FFFFFF'}}>
            <p className="text-xs font-medium mb-1" style={{color: '#666666'}}>Total Rooms Identified</p>
            <p className="text-2xl font-bold" style={{color: '#000000'}}>{rooms.length}</p>
          </div>
          <div className="rounded-lg p-3" style={{background: '#FFFFFF'}}>
            <p className="text-xs font-medium mb-1" style={{color: '#666666'}}>Total Square Footage</p>
            <p className="text-2xl font-bold" style={{color: '#000000'}}>{square_footage?.toLocaleString() || 'N/A'}</p>
          </div>
          <div className="rounded-lg p-3" style={{background: '#FFFFFF'}}>
            <p className="text-xs font-medium mb-1" style={{color: '#666666'}}>Rooms with Dimensions</p>
            <p className="text-2xl font-bold" style={{color: '#000000'}}>
              {rooms.filter(r => r.dimensions).length}
            </p>
          </div>
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
                      <span className="font-medium capitalize text-sm" style={{color: '#000000'}}>
                        {room.type || 'Unknown Room'}
                      </span>
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
