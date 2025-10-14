# Analytics API Documentation

**Base URL**: `http://localhost:5001/api/analytics`  
**Authentication**: All endpoints require JWT token in `Authorization: Bearer <token>` header

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/model/train` | Train regression model on property data |
| GET | `/predict/<property_id>` | Predict price for a specific property |
| POST | `/compare` | Compare two properties side-by-side |
| GET | `/sqft-impact` | Calculate $/sqft impact with examples |
| GET | `/quality-score/<property_id>` | Get Floor Plan Quality Score (0-100) |
| GET | `/property-analytics/<property_id>` | Get all analytics for a property in one call |

---

## 1. Train Regression Model

**Endpoint**: `POST /api/analytics/model/train`

**Description**: Train a machine learning model on existing property data. Required before predictions.

### Request Body
```json
{
  "model_type": "ridge",  // Options: "ridge", "linear", "random_forest"
  "min_properties": 5     // Minimum properties required (default: 10)
}
```

### Response (200 OK)
```json
{
  "message": "Model trained successfully",
  "model_type": "ridge",
  "properties_used": 25,
  "performance": {
    "r2_score": 0.85,
    "mae": 15000.50,
    "rmse": 20000.75,
    "cv_scores_mean": 0.82,
    "cv_scores_std": 0.05
  },
  "feature_importance": {
    "total_sqft": 0.45,
    "bedrooms": 0.20,
    "bathrooms": 0.15,
    "has_garage": 0.10,
    "avg_room_sqft": 0.10
  },
  "trained_at": "2025-10-13T22:30:00Z"
}
```

### Error Responses
```json
// 400 - Insufficient Data
{
  "error": "Insufficient data",
  "message": "Need at least 5 properties with measurements and prices"
}

// 400 - Invalid Model Type
{
  "error": "Invalid model_type",
  "message": "model_type must be 'ridge', 'linear', or 'random_forest'"
}
```

---

## 2. Predict Property Price

**Endpoint**: `GET /api/analytics/predict/<property_id>`

**Description**: Get AI-powered price prediction for a property based on its features.

### Query Parameters
- `train_model` (optional): Set to `true` to train model if not already trained

### Request Example
```bash
GET /api/analytics/predict/123e4567-e89b-12d3-a456-426614174000?train_model=true
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response (200 OK)
```json
{
  "property_id": "123e4567-e89b-12d3-a456-426614174000",
  "predicted_price": 450000.00,
  "confidence": "high",  // "high", "medium", "low"
  "price_range": {
    "low": 425000.00,
    "high": 475000.00
  },
  "features": {
    "total_sqft": 2000,
    "bedrooms": 3,
    "bathrooms": 2.0,
    "room_count": 8,
    "avg_room_sqft": 250.0,
    "largest_room_sqft": 400.0,
    "has_garage": true,
    "has_fireplace": false,
    "has_balcony": true,
    "has_closets": true,
    "num_doors": 15,
    "num_windows": 20
  },
  "model_type": "ridge",
  "model_performance": {
    "r2_score": 0.85,
    "mae": 15000.50
  }
}
```

### Error Responses
```json
// 404 - Property Not Found
{
  "error": "Property not found",
  "message": "Property with ID 123... not found or unauthorized"
}

// 400 - Model Not Trained
{
  "error": "Model not trained",
  "message": "No trained model available. Set train_model=true to train first"
}

// 400 - Missing Measurements
{
  "error": "Missing measurements",
  "message": "Property has no floor plan measurements"
}
```

---

## 3. Compare Properties

**Endpoint**: `POST /api/analytics/compare`

**Description**: Compare two properties side-by-side with detailed breakdown of differences.

### Request Body
```json
{
  "property_a_id": "123e4567-e89b-12d3-a456-426614174000",
  "property_b_id": "987fcdeb-51a2-43c7-9d5e-123456789abc",
  "train_model": false  // Optional: train model if needed
}
```

### Response (200 OK)
```json
{
  "property_a": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "predicted_price": 450000.00,
    "features": {
      "total_sqft": 2000,
      "bedrooms": 3,
      "bathrooms": 2.0,
      "has_garage": true,
      "has_fireplace": false
    }
  },
  "property_b": {
    "id": "987fcdeb-51a2-43c7-9d5e-123456789abc",
    "predicted_price": 425000.00,
    "features": {
      "total_sqft": 1800,
      "bedrooms": 3,
      "bathrooms": 1.5,
      "has_garage": true,
      "has_fireplace": true
    }
  },
  "comparison": {
    "price_difference": 25000.00,
    "sqft_difference": 200,
    "feature_differences": {
      "bathrooms": 0.5,
      "has_fireplace": true
    },
    "price_impact": {
      "sqft_impact": 15000.00,
      "bathroom_impact": 8000.00,
      "fireplace_impact": 2000.00,
      "total_difference": 25000.00,
      "price_per_sqft_diff": 12.50
    }
  },
  "summary": "Property A is $25,000 more expensive. Main differences: +200 sqft (+$15,000), +0.5 bathrooms (+$8,000). Property B has fireplace (+$2,000 value)."
}
```

### Error Responses
```json
// 400 - Same Property
{
  "error": "Invalid comparison",
  "message": "Cannot compare property to itself"
}

// 404 - Property Not Found
{
  "error": "Property not found",
  "message": "One or both properties not found"
}
```

---

## 4. Square Footage Impact

**Endpoint**: `GET /api/analytics/sqft-impact`

**Description**: Calculate how much each additional square foot adds to property value.

### Query Parameters
- `train_model` (optional): Set to `true` to train model if needed
- `sqft_change` (optional): Number of sqft to calculate (default: 100)

### Request Example
```bash
GET /api/analytics/sqft-impact?train_model=true&sqft_change=100
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response (200 OK)
```json
{
  "price_per_sqft": 150.50,
  "impact_per_sqft": 75.25,
  "examples": [
    {
      "sqft_change": 100,
      "price_impact": 7525.00,
      "description": "Adding 100 sq ft increases value by $7,525"
    },
    {
      "sqft_change": 200,
      "price_impact": 15050.00,
      "description": "Adding 200 sq ft increases value by $15,050"
    },
    {
      "sqft_change": 500,
      "price_impact": 37625.00,
      "description": "Adding 500 sq ft increases value by $37,625"
    }
  ],
  "model_type": "ridge",
  "properties_analyzed": 25
}
```

### Error Responses
```json
// 400 - Model Not Trained
{
  "error": "Model not trained",
  "message": "Model not trained. Set train_model=true to train first"
}
```

---

## 5. Floor Plan Quality Score

**Endpoint**: `GET /api/analytics/quality-score/<property_id>`

**Description**: Calculate a comprehensive quality score (0-100) for floor plan measurements.

### Request Example
```bash
GET /api/analytics/quality-score/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response (200 OK)
```json
{
  "property_id": "123e4567-e89b-12d3-a456-426614174000",
  "quality_score": 85,
  "quality_level": "excellent",  // "excellent", "good", "fair", "poor"
  "color": "green",  // "green", "blue", "yellow", "red"
  "breakdown": {
    "completeness": 90,  // All rooms measured
    "accuracy": 85,      // Measurement precision
    "clarity": 80,       // Image quality
    "consistency": 85    // Data consistency
  },
  "metadata": {
    "rooms_measured": 8,
    "total_square_feet": 2000,
    "measurement_method": "ai_estimation",
    "confidence": 0.92
  },
  "recommendations": [
    "Floor plan quality is excellent - no improvements needed"
  ]
}
```

### Error Responses
```json
// 404 - Property Not Found
{
  "error": "Property not found",
  "message": "Property with ID 123... not found or unauthorized"
}

// 400 - No Measurements
{
  "error": "No measurements",
  "message": "Property has no floor plan measurements"
}
```

---

## 6. Comprehensive Property Analytics

**Endpoint**: `GET /api/analytics/property-analytics/<property_id>`

**Description**: Get all analytics data for a property in a single API call. Combines quality score and price prediction.

### Request Example
```bash
GET /api/analytics/property-analytics/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response (200 OK)
```json
{
  "property_id": "123e4567-e89b-12d3-a456-426614174000",
  "quality_score": {
    "quality_score": 85,
    "quality_level": "excellent",
    "color": "green",
    "breakdown": {
      "completeness": 90,
      "accuracy": 85,
      "clarity": 80,
      "consistency": 85
    },
    "metadata": {
      "rooms_measured": 8,
      "total_square_feet": 2000
    },
    "recommendations": [
      "Floor plan quality is excellent - no improvements needed"
    ]
  },
  "price_prediction": {
    "predicted_price": 450000.00,
    "confidence": "high",
    "price_range": {
      "low": 425000.00,
      "high": 475000.00
    },
    "features": {
      "total_sqft": 2000,
      "bedrooms": 3,
      "bathrooms": 2.0
    }
  },
  "timestamp": "2025-10-13T22:30:00Z"
}
```

### Error Responses
```json
// 500 - Analytics Retrieval Failed
{
  "error": "Analytics retrieval failed",
  "message": "Error details..."
}
```

**Note**: This endpoint automatically trains the model if needed, making it very convenient for frontend use.

---

## Authentication

### Get JWT Token

1. **Register** (if needed):
```bash
POST /auth/register
Content-Type: application/json

{
  "email": "agent@example.com",
  "password": "SecurePass123!",
  "full_name": "Real Estate Agent"
}
```

2. **Login**:
```bash
POST /auth/login
Content-Type: application/json

{
  "email": "agent@example.com",
  "password": "SecurePass123!"
}
```

Response:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-uuid",
    "email": "agent@example.com",
    "full_name": "Real Estate Agent"
  }
}
```

3. **Use Token** in all analytics requests:
```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Error Codes Summary

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input or model not trained |
| 401 | Unauthorized - Missing or invalid JWT token |
| 404 | Not Found - Property doesn't exist or unauthorized |
| 500 | Internal Server Error - Unexpected error occurred |

---

## Frontend Integration Examples

### React Example

```typescript
// api/analytics.ts
import axios from 'axios';

const API_BASE = 'http://localhost:5001/api/analytics';

const getAuthHeaders = () => ({
  'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`,
  'Content-Type': 'application/json'
});

export const trainModel = async (modelType: string = 'ridge') => {
  const response = await axios.post(
    `${API_BASE}/model/train`,
    { model_type: modelType, min_properties: 5 },
    { headers: getAuthHeaders() }
  );
  return response.data;
};

export const predictPrice = async (propertyId: string) => {
  const response = await axios.get(
    `${API_BASE}/predict/${propertyId}`,
    { 
      headers: getAuthHeaders(),
      params: { train_model: true }
    }
  );
  return response.data;
};

export const compareProperties = async (propertyAId: string, propertyBId: string) => {
  const response = await axios.post(
    `${API_BASE}/compare`,
    { 
      property_a_id: propertyAId,
      property_b_id: propertyBId,
      train_model: false
    },
    { headers: getAuthHeaders() }
  );
  return response.data;
};

export const getSqftImpact = async (sqftChange: number = 100) => {
  const response = await axios.get(
    `${API_BASE}/sqft-impact`,
    { 
      headers: getAuthHeaders(),
      params: { sqft_change: sqftChange }
    }
  );
  return response.data;
};
```

### Usage in Component

```typescript
// components/Analytics.tsx
import { useState, useEffect } from 'react';
import { trainModel, predictPrice, compareProperties } from '../api/analytics';

export const AnalyticsDashboard = () => {
  const [modelStats, setModelStats] = useState(null);
  const [prediction, setPrediction] = useState(null);

  useEffect(() => {
    // Train model on component mount
    trainModel('ridge').then(setModelStats);
  }, []);

  const handlePredict = async (propertyId: string) => {
    const result = await predictPrice(propertyId);
    setPrediction(result);
  };

  return (
    <div>
      <h1>Analytics Dashboard</h1>
      {modelStats && (
        <div>
          <h2>Model Performance</h2>
          <p>R² Score: {modelStats.performance.r2_score}</p>
          <p>Properties Used: {modelStats.properties_used}</p>
        </div>
      )}
      {/* Add your UI here */}
    </div>
  );
};
```

---

## Testing with cURL

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}' \
  | jq -r '.token')

# 2. Train Model
curl -X POST http://localhost:5001/api/analytics/model/train \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model_type":"ridge","min_properties":5}' \
  | jq .

# 3. Predict Price
curl -X GET "http://localhost:5001/api/analytics/predict/PROPERTY_ID?train_model=true" \
  -H "Authorization: Bearer $TOKEN" \
  | jq .

# 4. Compare Properties
curl -X POST http://localhost:5001/api/analytics/compare \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "property_a_id":"PROPERTY_A_ID",
    "property_b_id":"PROPERTY_B_ID"
  }' \
  | jq .

# 5. Get SQFT Impact
curl -X GET "http://localhost:5001/api/analytics/sqft-impact?sqft_change=200" \
  -H "Authorization: Bearer $TOKEN" \
  | jq .
```

---

## Notes for Frontend Developer

1. **Authentication Required**: All endpoints require JWT token from `/auth/login`
2. **Train Model First**: Call `/model/train` before using prediction endpoints
3. **Auto-Training**: Use `train_model=true` parameter to auto-train if needed
4. **Error Handling**: Always handle 400, 401, 404, 500 status codes
5. **CORS**: Backend configured for `http://localhost:3000` origin
6. **Rate Limiting**: Consider implementing request throttling for model training
7. **Caching**: Consider caching predictions for frequently accessed properties

---

## Support

For questions or issues, refer to:
- `backend/app/routes/analytics.py` - Implementation
- `backend/tests/integration/test_analytics_api.py` - Test examples
- `log.md` - Phase 4 documentation
