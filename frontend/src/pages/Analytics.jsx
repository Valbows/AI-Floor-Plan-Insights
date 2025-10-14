/**
 * Analytics Dashboard Page
 * Displays regression model statistics, quality scores, and predictions
 */

import { useState, useEffect } from 'react';
import analyticsApi from '../services/analyticsApi';
import QualityScoreBadge from '../components/QualityScoreBadge';

const Analytics = () => {
  const [modelStats, setModelStats] = useState(null);
  const [sqftImpact, setSqftImpact] = useState(null);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [selectedModel, setSelectedModel] = useState('ridge');

  useEffect(() => {
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
          <div className="text-lg text-gray-600">Loading analytics...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Regression models, price predictions, and floor plan quality analysis
        </p>
      </div>

      {/* Model Training Section */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Regression Model</h2>
        
        <div className="flex items-center gap-4 mb-4">
          <label className="text-sm font-medium text-gray-700">Model Type:</label>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="ridge">Ridge Regression</option>
            <option value="linear">Linear Regression</option>
            <option value="random_forest">Random Forest</option>
          </select>
          
          <button
            onClick={handleTrainModel}
            disabled={training}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {training ? 'Training...' : 'Train Model'}
          </button>
        </div>

        {modelStats && (
          <div className="grid grid-cols-4 gap-4 mt-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">R² Score</p>
              <p className="text-2xl font-bold text-blue-600">
                {(modelStats.performance.r2_score * 100).toFixed(1)}%
              </p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">Properties Used</p>
              <p className="text-2xl font-bold text-green-600">
                {modelStats.properties_used}
              </p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">Mean Abs. Error</p>
              <p className="text-2xl font-bold text-purple-600">
                ${modelStats.performance.mae.toLocaleString()}
              </p>
            </div>
            <div className="bg-orange-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 capitalize">Model Type</p>
              <p className="text-2xl font-bold text-orange-600 capitalize">
                {modelStats.model_type}
              </p>
            </div>
          </div>
        )}

        {modelStats && modelStats.feature_importance && (
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-3">Feature Importance</h3>
            <div className="space-y-2">
              {Object.entries(modelStats.feature_importance)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 5)
                .map(([feature, importance]) => (
                  <div key={feature} className="flex items-center">
                    <span className="text-sm text-gray-700 w-32 capitalize">
                      {feature.replace(/_/g, ' ')}:
                    </span>
                    <div className="flex-1">
                      <div className="w-full bg-gray-200 rounded-full h-4">
                        <div
                          className="bg-blue-600 h-4 rounded-full"
                          style={{ width: `${importance * 100}%` }}
                        />
                      </div>
                    </div>
                    <span className="text-sm font-semibold text-gray-900 ml-3">
                      {(importance * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>

      {/* Square Footage Impact */}
      {sqftImpact && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Square Footage Impact</h2>
          
          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-sm text-gray-600 mb-2">Price Per Square Foot</p>
              <p className="text-3xl font-bold text-green-600">
                ${sqftImpact.price_per_sqft.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-2">Impact Per Square Foot</p>
              <p className="text-3xl font-bold text-blue-600">
                ${sqftImpact.impact_per_sqft.toFixed(2)}
              </p>
            </div>
          </div>

          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-3">Examples</h3>
            <div className="space-y-3">
              {sqftImpact.examples.map((example, idx) => (
                <div key={idx} className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
                  <span className="text-sm text-gray-700">{example.description}</span>
                  <span className="text-lg font-bold text-green-600">
                    +${example.price_impact.toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 text-sm text-gray-600">
            <p>Model: {sqftImpact.model_type} | Properties analyzed: {sqftImpact.properties_analyzed}</p>
          </div>
        </div>
      )}

      {/* Info Section */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">About Analytics</h3>
        <p className="text-blue-800">
          The analytics dashboard uses machine learning regression models to predict property prices
          based on floor plan measurements, room counts, amenities, and location factors. Train a model
          with at least 5 properties to see predictions and comparisons.
        </p>
      </div>
    </div>
  );
};

export default Analytics;
