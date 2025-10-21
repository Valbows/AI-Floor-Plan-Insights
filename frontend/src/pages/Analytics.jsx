/**
 * Analytics Dashboard Page
 * Predict property prices based on floor plan analysis
 */

import { useState, useEffect } from 'react';
import { DollarSign, TrendingUp, Lightbulb, Zap, Calculator } from 'lucide-react';
import analyticsApi from '../services/analyticsApi';
import QualityScoreBadge from '../components/QualityScoreBadge';

const Analytics = () => {
  const [modelStats, setModelStats] = useState(null);
  const [sqftImpact, setSqftImpact] = useState(null);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [selectedModel, setSelectedModel] = useState('ridge');

  useEffect(() => {
    // Set page title
    document.title = 'Price Predictor | FloorIQ';
    
    // Try to load model stats and sqft impact on mount
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      // Try to get sqft impact (will auto-train if needed)
      const impact = await analyticsApi.getSqftImpact(100);
      setSqftImpact(impact);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTrainModel = async () => {
    try {
      setTraining(true);
      const result = await analyticsApi.trainModel(selectedModel, 5);
      setModelStats(result);
      // Reload sqft impact after training
      const impact = await analyticsApi.getSqftImpact(100);
      setSqftImpact(impact);
      alert('Model trained successfully!');
    } catch (err) {
      console.error('Training failed:', err);
      alert(err.response?.data?.message || 'Training failed');
    } finally {
      setTraining(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg" style={{color: '#666666'}}>Loading your price predictor...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 py-16">
      {/* Hero Header - Matching MY PROPERTIES style */}
      <div className="text-center mb-16">
        <h1 className="text-6xl font-black uppercase tracking-tight mb-8" style={{color: '#000000', letterSpacing: '-2px', lineHeight: '0.95'}}>
          AI PRICE <span style={{color: '#FF5959'}}><span style={{borderBottom: '6px solid #FF5959'}}>PRED</span>ICTOR</span>
        </h1>
        <p className="text-lg font-medium mb-2" style={{color: '#666666'}}>
          Test floor plans before construction • Predict pricing • Maximize ROI
        </p>
        <p className="text-sm" style={{color: '#999999'}}>
          For developers: Upload 20+ comparable units → Train AI → Get instant pricing for new designs
        </p>
      </div>

      {/* How It Works - More Visual */}
      <div className="bg-white rounded-lg p-6 mb-6" style={{border: '3px solid #000000'}}>
        <div className="flex items-center gap-2 mb-6">
          <Lightbulb className="w-6 h-6" style={{color: '#FF5959'}} />
          <h2 className="text-xl font-black uppercase tracking-wider">How It Works</h2>
        </div>
        
        <div className="grid grid-cols-4 gap-3">
          <div className="text-center p-4 rounded-lg" style={{background: '#FFF5F5', border: '2px solid #FF5959'}}>
            <div className="w-16 h-16 rounded-full flex items-center justify-center text-3xl font-black mb-3 mx-auto" 
                 style={{background: '#FF5959', color: '#FFFFFF'}}>
              1
            </div>
            <p className="text-sm font-bold mb-2">Upload Comps</p>
            <p className="text-xs" style={{color: '#666666'}}>20+ existing units with prices</p>
          </div>
          
          <div className="text-center p-4 rounded-lg" style={{background: '#F6F1EB', border: '2px solid #E5E5E5'}}>
            <div className="w-16 h-16 rounded-full flex items-center justify-center text-3xl font-black mb-3 mx-auto" 
                 style={{background: '#000000', color: '#FFFFFF'}}>
              2
            </div>
            <p className="text-sm font-bold mb-2">Train AI</p>
            <p className="text-xs" style={{color: '#666666'}}>AI learns pricing patterns</p>
          </div>
          
          <div className="text-center p-4 rounded-lg" style={{background: '#F6F1EB', border: '2px solid #E5E5E5'}}>
            <div className="w-16 h-16 rounded-full flex items-center justify-center text-3xl font-black mb-3 mx-auto" 
                 style={{background: '#000000', color: '#FFFFFF'}}>
              3
            </div>
            <p className="text-sm font-bold mb-2">Upload New Design</p>
            <p className="text-xs" style={{color: '#666666'}}>Your floor plan (no price)</p>
          </div>
          
          <div className="text-center p-4 rounded-lg" style={{background: '#F0FDF4', border: '2px solid #22C55E'}}>
            <div className="w-16 h-16 rounded-full flex items-center justify-center text-3xl font-black mb-3 mx-auto" 
                 style={{background: '#22C55E', color: '#FFFFFF'}}>
              ✓
            </div>
            <p className="text-sm font-bold mb-2">Get Price</p>
            <p className="text-xs" style={{color: '#666666'}}>Instant PPSF prediction</p>
          </div>
        </div>
      </div>

      {/* Train Model Section - Simplified */}
      <div className="bg-white rounded-lg p-6 mb-6" style={{border: '3px solid #FF5959'}}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-black uppercase tracking-wider mb-2">Train Your Predictor</h2>
            <p className="text-sm" style={{color: '#666666'}}>
              AI will analyze your uploaded properties to learn pricing patterns
            </p>
          </div>
          
          <button
            onClick={handleTrainModel}
            disabled={training}
            className="px-8 py-4 rounded-lg font-black uppercase tracking-wider text-white transition-all"
            style={{
              background: training ? '#CCCCCC' : '#FF5959',
              border: '3px solid #000000',
              cursor: training ? 'not-allowed' : 'pointer',
              fontSize: '16px'
            }}
            onMouseEnter={(e) => !training && (e.currentTarget.style.background = '#000000')}
            onMouseLeave={(e) => !training && (e.currentTarget.style.background = '#FF5959')}
          >
            {training ? '⏳ Training...' : '🚀 Train Now'}
          </button>
        </div>
        
        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 rounded-lg" style={{background: '#FFF5F5', border: '2px solid #FFE5E5'}}>
            <p className="text-xs font-bold uppercase mb-1" style={{color: '#999999'}}>Algorithm</p>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full px-3 py-2 rounded font-bold text-sm"
              style={{border: '2px solid #E5E5E5', background: '#FFFFFF', color: '#000000'}}
            >
              <option value="ridge">Smart (Recommended)</option>
              <option value="linear">Simple</option>
              <option value="random_forest">Advanced</option>
            </select>
          </div>
          
          <div className="p-4 rounded-lg text-center" style={{background: '#F6F1EB', border: '2px solid #E5E5E5'}}>
            <p className="text-xs font-bold uppercase mb-1" style={{color: '#999999'}}>Min. Properties</p>
            <p className="text-3xl font-black" style={{color: '#000000'}}>20+</p>
          </div>
          
          <div className="p-4 rounded-lg text-center" style={{background: '#F6F1EB', border: '2px solid #E5E5E5'}}>
            <p className="text-xs font-bold uppercase mb-1" style={{color: '#999999'}}>Training Time</p>
            <p className="text-3xl font-black" style={{color: '#000000'}}>~30s</p>
          </div>
        </div>

        {modelStats && (
          <div className="mt-6">
            <div className="p-4 rounded-lg mb-4" style={{background: '#F0FDF4', border: '2px solid #22C55E'}}>
              <p className="text-lg font-black" style={{color: '#16A34A'}}>
                ✅ Training Complete!
              </p>
            </div>
            
            <div className="grid grid-cols-4 gap-4">
              <div className="rounded-lg p-6 text-center" style={{background: '#FFF5F5', border: '3px solid #FF5959'}}>
                <p className="text-xs font-bold uppercase mb-2" style={{color: '#999999'}}>Accuracy</p>
                <p className="text-5xl font-black mb-2" style={{color: '#FF5959'}}>
                  {(modelStats.performance.r2_score * 100).toFixed(0)}%
                </p>
                <p className="text-xs" style={{color: '#999999'}}>AI confidence score</p>
              </div>
              <div className="rounded-lg p-6 text-center" style={{background: '#F6F1EB', border: '2px solid #E5E5E5'}}>
                <p className="text-xs font-bold uppercase mb-2" style={{color: '#999999'}}>Trained On</p>
                <p className="text-5xl font-black mb-2" style={{color: '#000000'}}>
                  {modelStats.properties_used}
                </p>
                <p className="text-xs" style={{color: '#999999'}}>properties analyzed</p>
              </div>
              <div className="rounded-lg p-6 text-center" style={{background: '#F6F1EB', border: '2px solid #E5E5E5'}}>
                <p className="text-xs font-bold uppercase mb-2" style={{color: '#999999'}}>Avg Error</p>
                <p className="text-5xl font-black mb-2" style={{color: '#000000'}}>
                  ±${Math.round(modelStats.performance.mae / 1000)}k
                </p>
                <p className="text-xs" style={{color: '#999999'}}>typical variance</p>
              </div>
              <div className="rounded-lg p-6 text-center" style={{background: '#F0FDF4', border: '2px solid #22C55E'}}>
                <p className="text-xs font-bold uppercase mb-2" style={{color: '#999999'}}>Status</p>
                <p className="text-3xl font-black mb-2" style={{color: '#22C55E'}}>
                  READY
                </p>
                <p className="text-xs" style={{color: '#999999'}}>upload new plans</p>
              </div>
            </div>
          </div>
        )}

        {modelStats && modelStats.feature_importance && (
          <div className="mt-6 p-6 rounded-lg" style={{background: '#000000', border: '3px solid #FF5959'}}>
            <h3 className="text-lg font-black uppercase tracking-wider mb-4" style={{color: '#FFFFFF'}}>
              💡 What Drives Pricing?
            </h3>
            <div className="space-y-3">
              {Object.entries(modelStats.feature_importance)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 5)
                .map(([feature, importance], index) => (
                  <div key={feature} className="flex items-center gap-3">
                    <span className="text-2xl font-black w-8" style={{color: '#FF5959'}}>
                      {index + 1}
                    </span>
                    <span className="text-sm font-bold w-32 capitalize" style={{color: '#FFFFFF'}}>
                      {feature.replace(/_/g, ' ')}
                    </span>
                    <div className="flex-1">
                      <div className="w-full rounded-full h-3" style={{background: '#333333'}}>
                        <div
                          className="h-3 rounded-full transition-all"
                          style={{ width: `${importance * 100}%`, background: '#FF5959' }}
                        />
                      </div>
                    </div>
                    <span className="text-sm font-black w-16 text-right" style={{color: '#FFFFFF'}}>
                      {(importance * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>

      {/* Square Footage Impact - Simplified */}
      {sqftImpact && (
        <div className="bg-white rounded-lg p-6 mb-6" style={{border: '3px solid #000000'}}>
          <h2 className="text-2xl font-black uppercase tracking-wider mb-6">💰 Size = Value Calculator</h2>
          
          <div className="grid grid-cols-2 gap-6">
            <div className="p-8 rounded-lg text-center" style={{background: '#F0FDF4', border: '3px solid #22C55E'}}>
              <p className="text-xs font-bold uppercase mb-3" style={{color: '#999999'}}>Average PPSF</p>
              <p className="text-6xl font-black mb-3" style={{color: '#22C55E'}}>
                ${Number(sqftImpact?.price_per_sqft ?? 0).toFixed(0)}
              </p>
              <p className="text-sm font-bold" style={{color: '#666666'}}>Per Square Foot</p>
            </div>
            <div className="p-8 rounded-lg text-center" style={{background: '#FFF5F5', border: '3px solid #FF5959'}}>
              <p className="text-xs font-bold uppercase mb-3" style={{color: '#999999'}}>Value Per Extra Sq Ft</p>
              <p className="text-6xl font-black mb-3" style={{color: '#FF5959'}}>
                ${Number(sqftImpact?.impact_per_sqft ?? sqftImpact?.price_per_sqft ?? 0).toFixed(0)}
              </p>
              <p className="text-sm font-bold" style={{color: '#666666'}}>Added Property Value</p>
            </div>
          </div>

          <div className="mt-6 space-y-3">
            {(Array.isArray(sqftImpact?.examples) ? sqftImpact.examples : []).map((example, idx) => (
              <div key={idx} className="flex items-center justify-between p-4 rounded-lg" 
                   style={{background: '#F6F1EB', border: '2px solid #E5E5E5'}}>
                <span className="text-sm font-bold" style={{color: '#000000'}}>
                  {example.description}
                </span>
                <span className="text-3xl font-black" style={{color: '#22C55E'}}>
                  +${example.price_impact.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Simple Status Bar with Tooltip */}
      <div className="bg-white rounded-lg p-6" style={{border: '3px solid #000000'}}>
        <div className="flex items-center justify-between">
          {/* Left: Status */}
          <div className="flex items-center gap-4">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center text-3xl`} 
                 style={{background: modelStats ? '#22C55E' : '#CCCCCC'}}>
              {modelStats ? '✓' : '○'}
            </div>
            <div>
              <p className="text-xs font-bold uppercase" style={{color: '#999999'}}>Model Status</p>
              <p className="text-2xl font-black" style={{color: '#000000'}}>
                {modelStats ? 'Ready to Predict' : 'Not Trained'}
              </p>
              {modelStats && (
                <p className="text-xs" style={{color: '#666666'}}>
                  {modelStats.properties_used} properties • {(modelStats.performance.r2_score * 100).toFixed(0)}% accuracy
                </p>
              )}
            </div>
          </div>
          
          {/* Right: Quick Stats + Tooltip */}
          <div className="flex items-center gap-4">
            <div className="flex gap-3">
              <div className="text-center">
                <p className="text-3xl font-black" style={{color: '#000000'}}>~60s</p>
                <p className="text-xs font-bold uppercase" style={{color: '#999999'}}>Per Test</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-black" style={{color: '#000000'}}>∞</p>
                <p className="text-xs font-bold uppercase" style={{color: '#999999'}}>Tests</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-black" style={{color: '#000000'}}>20+</p>
                <p className="text-xs font-bold uppercase" style={{color: '#999999'}}>Min Props</p>
              </div>
            </div>
            
            {/* Info Tooltip */}
            <div className="group relative">
              <div className="w-12 h-12 rounded-full flex items-center justify-center cursor-help transition-all"
                   style={{background: '#F6F1EB', border: '2px solid #E5E5E5'}}>
                <Lightbulb className="w-6 h-6" style={{color: '#666666'}} />
              </div>
              
              {/* Tooltip Content */}
              <div className="absolute right-0 bottom-full mb-3 w-96 p-6 rounded-lg shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50"
                   style={{background: '#000000', border: '3px solid #FF5959'}}>
                <p className="text-sm font-black uppercase mb-4" style={{color: '#FF5959'}}>
                  How to Use
                </p>
                
                <div className="space-y-3 text-xs" style={{color: '#FFFFFF'}}>
                  <div className="flex gap-2">
                    <span className="font-black" style={{color: '#FF5959'}}>1.</span>
                    <div>
                      <p className="font-bold">Upload 20+ Properties</p>
                      <p style={{color: '#CCCCCC'}}>Floor plans + sale prices</p>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <span className="font-black" style={{color: '#FF5959'}}>2.</span>
                    <div>
                      <p className="font-bold">Train AI</p>
                      <p style={{color: '#CCCCCC'}}>Click button above (~30s)</p>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <span className="font-black" style={{color: '#FF5959'}}>3.</span>
                    <div>
                      <p className="font-bold">Upload New Floor Plans</p>
                      <p style={{color: '#CCCCCC'}}>Get instant price predictions</p>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <span className="font-black" style={{color: '#22C55E'}}>✓</span>
                    <div>
                      <p className="font-bold">Compare Options</p>
                      <p style={{color: '#CCCCCC'}}>Test unlimited variations</p>
                    </div>
                  </div>
                </div>
                
                <div className="mt-4 pt-4" style={{borderTop: '1px solid #333333'}}>
                  <p className="text-xs font-bold mb-1" style={{color: '#FF5959'}}>Real Example</p>
                  <p className="text-xs" style={{color: '#CCCCCC'}}>
                    Andrew tested 10 layouts for Gowanus project → Found 280 sq ft living rooms = best PPSF
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;

