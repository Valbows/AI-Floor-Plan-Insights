import React from 'react'
import { X, Loader, Copy, Check } from 'lucide-react'

const ShareModal = ({ 
  showShareModal, 
  setShowShareModal,
  generatingLink,
  shareableLink,
  copied,
  handleCopyLink,
  setCopied
}) => {
  if (!showShareModal) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)'}}>
      <div className="bg-white max-w-lg w-full p-8" style={{borderRadius: '12px', boxShadow: '0 8px 24px rgba(0,0,0,0.2)', border: '2px solid #000000'}}>
        <div className="flex items-start justify-between mb-6">
          <div>
            <h3 className="text-2xl font-black uppercase mb-2" style={{color: '#000000', letterSpacing: '-1px'}}>Share <span style={{color: '#FF5959'}}>Property</span></h3>
            <p className="text-sm" style={{color: '#666666'}}>Generate a public link to share this property</p>
          </div>
          <button
            onClick={() => {
              setShowShareModal(false)
              setCopied(false)
            }}
            className="transition-colors p-1"
            style={{color: '#FF5959'}}
            onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,89,89,0.1)'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {generatingLink ? (
          <div className="text-center py-8">
            <Loader className="w-8 h-8 animate-spin mx-auto mb-4" style={{color: '#FF5959'}} />
            <p className="text-sm" style={{color: '#666666'}}>Generating shareable link...</p>
          </div>
        ) : shareableLink ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-bold uppercase mb-2" style={{color: '#000000', letterSpacing: '1px'}}>
                Shareable Link
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={shareableLink.shareable_url}
                  readOnly
                  className="flex-1 px-4 py-2 text-sm focus:outline-none"
                  style={{border: '2px solid #000000', borderRadius: '4px', background: '#F6F1EB', color: '#000000'}}
                />
                <button
                  onClick={handleCopyLink}
                  className="px-4 py-2 transition-all flex items-center space-x-2 font-bold uppercase text-sm"
                  style={{
                    background: copied ? '#F0FDF4' : '#FF5959',
                    color: copied ? '#22C55E' : '#FFFFFF',
                    borderRadius: '4px',
                    letterSpacing: '1px'
                  }}
                  onMouseEnter={(e) => {if (!copied) {e.currentTarget.style.background = '#E54545'; e.currentTarget.style.transform = 'translateY(-1px)'}}}
                  onMouseLeave={(e) => {if (!copied) {e.currentTarget.style.background = '#FF5959'; e.currentTarget.style.transform = 'translateY(0)'}}}
                >
                  {copied ? (
                    <>
                      <Check className="w-4 h-4" />
                      <span>Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            <div className="rounded-lg p-4 space-y-2" style={{background: '#F6F1EB', border: '1px solid #E5E5E5'}}>
              <div className="flex items-center justify-between text-sm">
                <span style={{color: '#666666'}}>Expires:</span>
                <span className="font-bold" style={{color: '#000000'}}>
                  {new Date(shareableLink.expires_at).toLocaleDateString()}
                </span>
              </div>
              <p className="text-xs" style={{color: '#666666'}}>
                This link will remain active for 30 days. Anyone with this link can view the property details.
              </p>
            </div>

            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                onClick={() => {
                  setShowShareModal(false)
                  setCopied(false)
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-sm text-gray-600">Failed to load shareable link.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ShareModal

