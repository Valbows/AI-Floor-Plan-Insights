/**
 * TypeScript Type Definitions for Analytics API
 * 
 * Use these types in your frontend React/Next.js application
 * for type-safe API integration
 */

// ============================================================================
// BASE TYPES
// ============================================================================

export interface PropertyFeatures {
  total_sqft: number;
  bedrooms: number;
  bathrooms: number;
  room_count: number;
  avg_room_sqft: number;
  largest_room_sqft: number;
  has_garage: boolean;
  has_fireplace: boolean;
  has_balcony: boolean;
  has_closets: boolean;
  num_doors: number;
  num_windows: number;
}

export interface ModelPerformance {
  r2_score: number;
  mae: number;
  rmse: number;
  cv_scores_mean: number;
  cv_scores_std: number;
}

export interface FeatureImportance {
  total_sqft: number;
  bedrooms: number;
  bathrooms: number;
  has_garage: number;
  avg_room_sqft: number;
  [key: string]: number;
}

// ============================================================================
// RESPONSE TYPES
// ============================================================================

export interface TrainModelResponse {
  message: string;
  model_type: 'ridge' | 'linear' | 'random_forest';
  properties_used: number;
  performance: ModelPerformance;
  feature_importance: FeatureImportance;
  trained_at: string;
}

export interface PredictPriceResponse {
  property_id: string;
  predicted_price: number;
  confidence: 'high' | 'medium' | 'low';
  price_range: {
    low: number;
    high: number;
  };
  features: PropertyFeatures;
  model_type: string;
  model_performance: {
    r2_score: number;
    mae: number;
  };
}

export interface ComparePropertiesResponse {
  property_a: {
    id: string;
    predicted_price: number;
    features: PropertyFeatures;
  };
  property_b: {
    id: string;
    predicted_price: number;
    features: PropertyFeatures;
  };
  comparison: {
    price_difference: number;
    sqft_difference: number;
    feature_differences: {
      [key: string]: number | boolean;
    };
    price_impact: {
      sqft_impact: number;
      bathroom_impact?: number;
      bedroom_impact?: number;
      garage_impact?: number;
      fireplace_impact?: number;
      total_difference: number;
      price_per_sqft_diff: number;
    };
  };
  summary: string;
}

export interface SqftImpactResponse {
  price_per_sqft: number;
  impact_per_sqft: number;
  examples: Array<{
    sqft_change: number;
    price_impact: number;
    description: string;
  }>;
  model_type: string;
  properties_analyzed: number;
}

export interface QualityScoreResponse {
  property_id: string;
  quality_score: number;
  quality_level: 'excellent' | 'good' | 'fair' | 'poor';
  color: 'green' | 'blue' | 'yellow' | 'red';
  breakdown: {
    completeness: number;
    accuracy: number;
    clarity: number;
    consistency: number;
  };
  metadata: {
    rooms_measured: number;
    total_square_feet: number;
    measurement_method: string;
    confidence: number;
  };
  recommendations: string[];
}

export interface PropertyAnalyticsResponse {
  property_id: string;
  quality_score: QualityScoreResponse;
  price_prediction: PredictPriceResponse;
  timestamp: string;
}

export interface ApiError {
  error: string;
  message: string;
}

// ============================================================================
// REQUEST TYPES
// ============================================================================

export interface TrainModelRequest {
  model_type?: 'ridge' | 'linear' | 'random_forest';
  min_properties?: number;
}

export interface ComparePropertiesRequest {
  property_a_id: string;
  property_b_id: string;
  train_model?: boolean;
}

export interface PredictPriceParams {
  train_model?: boolean;
}

export interface SqftImpactParams {
  train_model?: boolean;
  sqft_change?: number;
}

// ============================================================================
// AUTH TYPES
// ============================================================================

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  token: string;
  user: {
    id: string;
    email: string;
    full_name: string;
  };
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export type ApiResponse<T> = {
  data: T;
  status: number;
} | {
  error: ApiError;
  status: number;
};

// Helper type for async API calls
export type AsyncApiCall<T> = () => Promise<ApiResponse<T>>;

// ============================================================================
// EXAMPLE USAGE IN REACT
// ============================================================================

/*
import { useState, useEffect } from 'react';
import type { TrainModelResponse, PredictPriceResponse } from './analytics-api.types';

export function useAnalytics() {
  const [model, setModel] = useState<TrainModelResponse | null>(null);
  const [loading, setLoading] = useState(false);
  
  const trainModel = async (modelType: 'ridge' | 'linear' | 'random_forest') => {
    setLoading(true);
    try {
      const response = await fetch('/api/analytics/model/train', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ model_type: modelType })
      });
      
      const data: TrainModelResponse = await response.json();
      setModel(data);
    } catch (error) {
      console.error('Training failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return { model, trainModel, loading };
}
*/
