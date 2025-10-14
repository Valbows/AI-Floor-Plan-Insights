/**
 * Analytics API Service
 * Handles all API calls to the analytics endpoints
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5001';

// Create axios instance with default config
const api = axios.create({
  baseURL: `${API_BASE}/api/analytics`,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const analyticsApi = {
  /**
   * Train regression model
   * @param {string} modelType - 'ridge', 'linear', or 'random_forest'
   * @param {number} minProperties - Minimum properties required
   */
  trainModel: async (modelType = 'ridge', minProperties = 5) => {
    const response = await api.post('/model/train', {
      model_type: modelType,
      min_properties: minProperties
    });
    return response.data;
  },

  /**
   * Predict price for a property
   * @param {string} propertyId - Property UUID
   * @param {boolean} trainModel - Whether to auto-train if model not ready
   */
  predictPrice: async (propertyId, trainModel = true) => {
    const response = await api.get(`/predict/${propertyId}`, {
      params: { train_model: trainModel }
    });
    return response.data;
  },

  /**
   * Compare two properties
   * @param {string} propertyAId - First property UUID
   * @param {string} propertyBId - Second property UUID
   */
  compareProperties: async (propertyAId, propertyBId) => {
    const response = await api.post('/compare', {
      property_a_id: propertyAId,
      property_b_id: propertyBId,
      train_model: false
    });
    return response.data;
  },

  /**
   * Get square footage impact
   * @param {number} sqftChange - Square footage change to calculate
   */
  getSqftImpact: async (sqftChange = 100) => {
    const response = await api.get('/sqft-impact', {
      params: { sqft_change: sqftChange, train_model: true }
    });
    return response.data;
  },

  /**
   * Get floor plan quality score
   * @param {string} propertyId - Property UUID
   */
  getQualityScore: async (propertyId) => {
    const response = await api.get(`/quality-score/${propertyId}`);
    return response.data;
  },

  /**
   * Get comprehensive analytics (quality + prediction)
   * @param {string} propertyId - Property UUID
   */
  getPropertyAnalytics: async (propertyId) => {
    const response = await api.get(`/property-analytics/${propertyId}`);
    return response.data;
  }
};

export default analyticsApi;
