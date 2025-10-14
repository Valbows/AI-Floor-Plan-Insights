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
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Eye className="w-5 h-5 text-blue-600 mt-0.5" />
          <div className="flex-1">
            <h3 className="font-semibold text-blue-900 mb-1">Analysis Method</h3>
            <div className="text-sm text-blue-800 space-y-1">
              <p>✅ <strong>Google Gemini Vision</strong>: Room identification and layout</p>
              {usedOCR && (
                <p>✅ <strong>OCR ({ocrMethod})</strong>: Dimension extraction and validation</p>
              )}
              {!usedOCR && (
                <p>⚠️ <strong>OCR</strong>: Not used (no dimensions found or failed)</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Overall Metrics */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Maximize2 className="w-5 h-5" />
          Overall Property Metrics
        </h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Total Rooms Identified</p>
            <p className="text-2xl font-bold text-gray-900">{rooms.length}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Total Square Footage</p>
            <p className="text-2xl font-bold text-gray-900">{square_footage?.toLocaleString() || 'N/A'}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Rooms with Dimensions</p>
            <p className="text-2xl font-bold text-gray-900">
              {rooms.filter(r => r.dimensions).length}
            </p>
          </div>
        </div>
      </div>

      {/* Room-by-Room Breakdown */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Ruler className="w-5 h-5" />
          Room-by-Room Measurements
        </h3>

        {rooms.length === 0 ? (
          <p className="text-gray-500">No rooms identified</p>
        ) : (
          <div className="space-y-3">
            {rooms.map((room, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900 capitalize">
                      {room.type || 'Unknown Room'}
                    </span>
                    {room.dimensions && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded-full">
                        <Ruler className="w-3 h-3" />
                        {room.dimensions}
                      </span>
                    )}
                  </div>
                  {room.features && room.features.length > 0 && (
                    <div className="mt-1 flex flex-wrap gap-1">
                      {room.features.map((feature, idx) => (
                        <span
                          key={idx}
                          className="text-xs text-gray-600 bg-gray-200 px-2 py-0.5 rounded"
                        >
                          {feature}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div>
                  {room.dimensions ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-gray-400" title="No dimensions found" />
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Analysis Notes */}
      {notes && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h4 className="font-semibold text-yellow-900 mb-2">Analysis Notes</h4>
          <p className="text-sm text-yellow-800">{notes}</p>
        </div>
      )}
    </div>
  );
};

export default FloorPlanAnalysisDetails;
