import React from 'react'
import { X, ZoomIn, ZoomOut } from 'lucide-react'

const FloorPlanZoomModal = ({ 
  showFloorPlanModal,
  closeFloorPlanModal,
  imageUrl,
  zoomLevel,
  handleZoomIn,
  handleZoomOut
}) => {
  if (!showFloorPlanModal || !imageUrl) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4" onClick={closeFloorPlanModal}>
      <button
        onClick={closeFloorPlanModal}
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
          src={imageUrl}
          alt="Floor Plan - Full Size"
          style={{ transform: `scale(${zoomLevel})`, transition: 'transform 0.2s' }}
          className="max-w-none"
        />
      </div>
    </div>
  )
}

export default FloorPlanZoomModal

