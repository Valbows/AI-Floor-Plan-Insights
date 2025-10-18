import React from 'react'
import { AlertCircle, Loader, Trash2 } from 'lucide-react'

const DeleteModal = ({ 
  showDeleteModal, 
  setShowDeleteModal,
  deleting,
  handleDelete
}) => {
  if (!showDeleteModal) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
        <div className="flex items-start mb-4">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
              <AlertCircle className="w-6 h-6 text-red-600" />
            </div>
          </div>
          <div className="ml-4 flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              Delete Property?
            </h3>
            <p className="text-sm text-gray-600">
              Are you sure you want to delete this property? This action cannot be undone. 
              All property data, floor plans, and analysis will be permanently removed.
            </p>
          </div>
        </div>
        
        <div className="flex items-center justify-end space-x-3 mt-6">
          <button
            onClick={() => setShowDeleteModal(false)}
            disabled={deleting}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors disabled:opacity-50 flex items-center space-x-2"
          >
            {deleting ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                <span>Deleting...</span>
              </>
            ) : (
              <>
                <Trash2 className="w-4 h-4" />
                <span>Delete Property</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default DeleteModal

