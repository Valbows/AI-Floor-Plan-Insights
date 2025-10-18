import React from 'react'
import { Loader, CheckCircle, Upload, Eye, DollarSign, FileText } from 'lucide-react'

const ProgressOverlay = ({ 
  showProgressOverlay,
  analysisStep
}) => {
  if (!showProgressOverlay) return null

  const analysisSteps = [
    { icon: Upload, text: 'Uploading floor plan...', color: 'text-blue-600' },
    { icon: Eye, text: 'Analyzing layout and rooms...', color: 'text-purple-600' },
    { icon: DollarSign, text: 'Calculating market value...', color: 'text-green-600' },
    { icon: FileText, text: 'Generating listing content...', color: 'text-orange-600' }
  ]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)'}}>
      <div className="bg-white p-10 max-w-md w-full mx-4" style={{borderRadius: '12px', boxShadow: '0 8px 24px rgba(0,0,0,0.2)'}}>
        <div className="text-center mb-8">
          <Loader className="w-20 h-20 mx-auto mb-4 animate-spin" style={{color: '#FF5959'}} />
          <h3 className="text-3xl font-black uppercase mb-3" style={{color: '#000000', letterSpacing: '-1px'}}>Analyzing Your <span style={{color: '#FF5959'}}>Property</span></h3>
          <p className="text-base" style={{color: '#666666'}}>Please wait while our AI processes your floor plan...</p>
        </div>

        {/* Analysis Steps */}
        <div className="space-y-4">
          {analysisSteps.map((step, index) => {
            const StepIcon = step.icon
            const isActive = index === analysisStep
            const isCompleted = index < analysisStep
            
            return (
              <div 
                key={index}
                className="flex items-center space-x-3 p-4 transition-all"
                style={{
                  background: isActive ? '#FFF5F5' : isCompleted ? '#F0FDF4' : '#F6F1EB',
                  border: `2px solid ${isActive ? '#FF5959' : isCompleted ? '#22C55E' : '#E5E5E5'}`,
                  borderRadius: '8px',
                  opacity: isActive || isCompleted ? 1 : 0.5,
                  transform: isActive ? 'scale(1.02)' : 'scale(1)'
                }}
              >
                <div className={`flex-shrink-0 ${isActive ? 'animate-pulse' : ''}`}>
                  {isCompleted ? (
                    <CheckCircle className="w-6 h-6" style={{color: '#22C55E'}} />
                  ) : (
                    <StepIcon className="w-6 h-6" style={{color: isActive ? '#FF5959' : '#999999'}} />
                  )}
                </div>
                <p className="text-sm font-bold" style={{
                  color: isActive ? '#000000' : isCompleted ? '#22C55E' : '#999999'
                }}>
                  {step.text}
                </p>
              </div>
            )
          })}
        </div>

        <div className="mt-6">
          <div className="w-full rounded-full h-2" style={{background: '#E5E5E5'}}>
            <div 
              className="h-2 rounded-full transition-all duration-500"
              style={{ width: `${((analysisStep + 1) / analysisSteps.length) * 100}%`, background: '#FF5959' }}
            ></div>
          </div>
          <p className="text-xs font-bold mt-2 text-center uppercase" style={{color: '#666666', letterSpacing: '1px'}}>
            Step {analysisStep + 1} of {analysisSteps.length}
          </p>
        </div>
      </div>
    </div>
  )
}

export default ProgressOverlay

