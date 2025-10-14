# Frontend Integration Guide - Analytics API

**For**: Frontend Developer  
**Backend Ready**: ✅ All endpoints tested and working  
**Authentication**: JWT Token (obtain via `/auth/login`)

---

## Quick Start

### 1. Install Dependencies

```bash
npm install axios
# or
yarn add axios
```

### 2. Copy Type Definitions

Copy `analytics-api.types.ts` to your project:
```bash
cp backend/docs/analytics-api.types.ts frontend/src/types/
```

### 3. Create API Client

**`src/api/analytics.ts`**:
```typescript
import axios from 'axios';
import type {
  TrainModelResponse,
  PredictPriceResponse,
  ComparePropertiesResponse,
  SqftImpactResponse,
  QualityScoreResponse,
  PropertyAnalyticsResponse
} from '../types/analytics-api.types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const analyticsApi = {
  // Train model
  trainModel: (modelType: 'ridge' | 'linear' | 'random_forest' = 'ridge') =>
    api.post<TrainModelResponse>('/api/analytics/model/train', {
      model_type: modelType,
      min_properties: 5
    }),

  // Predict price
  predictPrice: (propertyId: string, trainModel = true) =>
    api.get<PredictPriceResponse>(`/api/analytics/predict/${propertyId}`, {
      params: { train_model: trainModel }
    }),

  // Compare properties
  compareProperties: (propertyAId: string, propertyBId: string) =>
    api.post<ComparePropertiesResponse>('/api/analytics/compare', {
      property_a_id: propertyAId,
      property_b_id: propertyBId,
      train_model: false
    }),

  // Get sqft impact
  getSqftImpact: (sqftChange = 100) =>
    api.get<SqftImpactResponse>('/api/analytics/sqft-impact', {
      params: { sqft_change: sqftChange }
    }),

  // Get quality score
  getQualityScore: (propertyId: string) =>
    api.get<QualityScoreResponse>(`/api/analytics/quality-score/${propertyId}`),

  // Get all analytics (quality + prediction)
  getPropertyAnalytics: (propertyId: string) =>
    api.get<PropertyAnalyticsResponse>(`/api/analytics/property-analytics/${propertyId}`)
};
```

---

## Component Examples

### Analytics Dashboard

```typescript
// pages/analytics.tsx
import { useState, useEffect } from 'react';
import { analyticsApi } from '../api/analytics';
import type { TrainModelResponse } from '../types/analytics-api.types';

export default function AnalyticsDashboard() {
  const [modelStats, setModelStats] = useState<TrainModelResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Train model on page load
    analyticsApi.trainModel('ridge')
      .then(response => setModelStats(response.data))
      .catch(error => console.error('Training failed:', error))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Training model...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Analytics Dashboard</h1>
      
      {modelStats && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-3">Model Performance</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-gray-600">R² Score</p>
              <p className="text-2xl font-bold">{(modelStats.performance.r2_score * 100).toFixed(1)}%</p>
            </div>
            <div>
              <p className="text-gray-600">Properties Used</p>
              <p className="text-2xl font-bold">{modelStats.properties_used}</p>
            </div>
            <div>
              <p className="text-gray-600">Mean Absolute Error</p>
              <p className="text-2xl font-bold">${modelStats.performance.mae.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-gray-600">Model Type</p>
              <p className="text-2xl font-bold capitalize">{modelStats.model_type}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

### Property Price Prediction Card

```typescript
// components/PricePredictionCard.tsx
import { useState, useEffect } from 'react';
import { analyticsApi } from '../api/analytics';
import type { PredictPriceResponse } from '../types/analytics-api.types';

interface Props {
  propertyId: string;
}

export function PricePredictionCard({ propertyId }: Props) {
  const [prediction, setPrediction] = useState<PredictPriceResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsApi.predictPrice(propertyId, true)
      .then(response => setPrediction(response.data))
      .catch(error => console.error('Prediction failed:', error))
      .finally(() => setLoading(false));
  }, [propertyId]);

  if (loading) return <div>Loading prediction...</div>;
  if (!prediction) return <div>No prediction available</div>;

  const confidenceColor = {
    high: 'text-green-600',
    medium: 'text-yellow-600',
    low: 'text-red-600'
  }[prediction.confidence];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Price Prediction</h3>
      
      <div className="mb-4">
        <p className="text-3xl font-bold">
          ${prediction.predicted_price.toLocaleString()}
        </p>
        <p className={`text-sm ${confidenceColor} capitalize`}>
          {prediction.confidence} confidence
        </p>
      </div>

      <div className="text-sm text-gray-600 mb-4">
        <p>Range: ${prediction.price_range.low.toLocaleString()} - ${prediction.price_range.high.toLocaleString()}</p>
      </div>

      <div className="border-t pt-4">
        <p className="text-sm font-semibold mb-2">Property Features:</p>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>• {prediction.features.total_sqft} sq ft</li>
          <li>• {prediction.features.bedrooms} bed / {prediction.features.bathrooms} bath</li>
          <li>• {prediction.features.room_count} rooms</li>
          {prediction.features.has_garage && <li>• Garage included</li>}
          {prediction.features.has_fireplace && <li>• Fireplace</li>}
        </ul>
      </div>
    </div>
  );
}
```

### Property Comparison View

```typescript
// components/PropertyComparison.tsx
import { useState } from 'react';
import { analyticsApi } from '../api/analytics';
import type { ComparePropertiesResponse } from '../types/analytics-api.types';

interface Props {
  propertyAId: string;
  propertyBId: string;
}

export function PropertyComparison({ propertyAId, propertyBId }: Props) {
  const [comparison, setComparison] = useState<ComparePropertiesResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleCompare = async () => {
    setLoading(true);
    try {
      const response = await analyticsApi.compareProperties(propertyAId, propertyBId);
      setComparison(response.data);
    } catch (error) {
      console.error('Comparison failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <button
        onClick={handleCompare}
        disabled={loading}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
      >
        {loading ? 'Comparing...' : 'Compare Properties'}
      </button>

      {comparison && (
        <div className="grid grid-cols-2 gap-6">
          {/* Property A */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-3">Property A</h3>
            <p className="text-2xl font-bold mb-2">
              ${comparison.property_a.predicted_price.toLocaleString()}
            </p>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>• {comparison.property_a.features.total_sqft} sq ft</li>
              <li>• {comparison.property_a.features.bedrooms} bed / {comparison.property_a.features.bathrooms} bath</li>
            </ul>
          </div>

          {/* Property B */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-3">Property B</h3>
            <p className="text-2xl font-bold mb-2">
              ${comparison.property_b.predicted_price.toLocaleString()}
            </p>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>• {comparison.property_b.features.total_sqft} sq ft</li>
              <li>• {comparison.property_b.features.bedrooms} bed / {comparison.property_b.features.bathrooms} bath</li>
            </ul>
          </div>

          {/* Comparison Summary */}
          <div className="col-span-2 bg-blue-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-3">Analysis</h3>
            <p className="text-gray-700 mb-4">{comparison.summary}</p>
            
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Price Difference</p>
                <p className="font-bold text-lg">
                  ${Math.abs(comparison.comparison.price_difference).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-gray-600">Size Difference</p>
                <p className="font-bold text-lg">
                  {Math.abs(comparison.comparison.sqft_difference)} sq ft
                </p>
              </div>
              <div>
                <p className="text-gray-600">Price/Sqft Diff</p>
                <p className="font-bold text-lg">
                  ${comparison.comparison.price_impact.price_per_sqft_diff.toFixed(2)}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

### Quality Score Badge

```typescript
// components/QualityScoreBadge.tsx
import { useState, useEffect } from 'react';
import { analyticsApi } from '../api/analytics';
import type { QualityScoreResponse } from '../types/analytics-api.types';

interface Props {
  propertyId: string;
}

export function QualityScoreBadge({ propertyId }: Props) {
  const [qualityData, setQualityData] = useState<QualityScoreResponse | null>(null);

  useEffect(() => {
    analyticsApi.getQualityScore(propertyId)
      .then(response => setQualityData(response.data))
      .catch(error => console.error('Quality score fetch failed:', error));
  }, [propertyId]);

  if (!qualityData) return null;

  const colorClasses = {
    green: 'bg-green-100 text-green-800 border-green-300',
    blue: 'bg-blue-100 text-blue-800 border-blue-300',
    yellow: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    red: 'bg-red-100 text-red-800 border-red-300'
  };

  return (
    <div className={`inline-flex items-center px-3 py-1 rounded-full border ${colorClasses[qualityData.color]}`}>
      <span className="font-semibold mr-2">Quality Score:</span>
      <span className="text-lg font-bold">{qualityData.quality_score}</span>
      <span className="ml-2 text-sm capitalize">({qualityData.quality_level})</span>
    </div>
  );
}
```

---

## Authentication Flow

```typescript
// api/auth.ts
import axios from 'axios';
import type { LoginRequest, RegisterRequest, AuthResponse } from '../types/analytics-api.types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';

export const authApi = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await axios.post<AuthResponse>(`${API_BASE}/auth/login`, credentials);
    localStorage.setItem('jwt_token', response.data.token);
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await axios.post<AuthResponse>(`${API_BASE}/auth/register`, data);
    localStorage.setItem('jwt_token', response.data.token);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('jwt_token');
  }
};
```

---

## Error Handling

```typescript
// utils/errorHandler.ts
import { AxiosError } from 'axios';
import type { ApiError } from '../types/analytics-api.types';

export function handleApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const apiError = error.response?.data as ApiError;
    return apiError?.message || 'An unexpected error occurred';
  }
  return 'Network error - please try again';
}

// Usage in component:
try {
  const response = await analyticsApi.predictPrice(propertyId);
  setPrediction(response.data);
} catch (error) {
  const errorMessage = handleApiError(error);
  toast.error(errorMessage);
}
```

---

## Environment Variables

**`.env.local`**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:5001
```

**Production**:
```bash
NEXT_PUBLIC_API_URL=https://your-backend-api.com
```

---

## Testing Backend Endpoints

Use this script to verify all endpoints are working:

```bash
# Save as test-api.sh
#!/bin/bash

BASE_URL="http://localhost:5001"

# Login
TOKEN=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}' \
  | jq -r '.token')

echo "Token: $TOKEN"

# Train model
echo "\n=== Training Model ==="
curl -s -X POST $BASE_URL/api/analytics/model/train \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model_type":"ridge"}' | jq .

# Get quality score (replace PROPERTY_ID)
echo "\n=== Quality Score ==="
curl -s $BASE_URL/api/analytics/quality-score/PROPERTY_ID \
  -H "Authorization: Bearer $TOKEN" | jq .

# Get comprehensive analytics
echo "\n=== Property Analytics ==="
curl -s $BASE_URL/api/analytics/property-analytics/PROPERTY_ID \
  -H "Authorization: Bearer $TOKEN" | jq .
```

---

## API Response Caching (Optional)

```typescript
// utils/cache.ts
const cache = new Map<string, { data: any; timestamp: number }>();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export function getCached<T>(key: string): T | null {
  const cached = cache.get(key);
  if (!cached) return null;
  
  if (Date.now() - cached.timestamp > CACHE_DURATION) {
    cache.delete(key);
    return null;
  }
  
  return cached.data as T;
}

export function setCache<T>(key: string, data: T): void {
  cache.set(key, { data, timestamp: Date.now() });
}

// Usage:
const cacheKey = `prediction-${propertyId}`;
const cached = getCached<PredictPriceResponse>(cacheKey);
if (cached) return cached;

const response = await analyticsApi.predictPrice(propertyId);
setCache(cacheKey, response.data);
```

---

## Summary for Frontend Developer

**What You Need**:
1. ✅ Copy `analytics-api.types.ts` to your project
2. ✅ Create `api/analytics.ts` client (provided above)
3. ✅ Set `NEXT_PUBLIC_API_URL` environment variable
4. ✅ Implement authentication flow
5. ✅ Use provided component examples

**All Backend Endpoints Working**:
- ✅ `/api/analytics/model/train` - Train model
- ✅ `/api/analytics/predict/<id>` - Predict price
- ✅ `/api/analytics/compare` - Compare properties
- ✅ `/api/analytics/sqft-impact` - SQFT calculator
- ✅ `/api/analytics/quality-score/<id>` - Quality score
- ✅ `/api/analytics/property-analytics/<id>` - All-in-one

**Documentation**:
- Full API docs: `backend/docs/ANALYTICS_API.md`
- Type definitions: `backend/docs/analytics-api.types.ts`
- This guide: `backend/docs/FRONTEND_INTEGRATION.md`

**Questions?** Check `log.md` Phase 4 section for implementation details.
