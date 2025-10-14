/**
 * Quality Score Badge Component
 * Displays floor plan quality score with color coding
 */

import { useEffect, useState } from 'react';
import analyticsApi from '../services/analyticsApi';

const QualityScoreBadge = ({ propertyId, detailed = false }) => {
  const [qualityData, setQualityData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!propertyId) return;

    const fetchQualityScore = async () => {
      try {
        setLoading(true);
        const data = await analyticsApi.getQualityScore(propertyId);
        setQualityData(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch quality score:', err);
        setError(err.response?.data?.message || 'Failed to load quality score');
      } finally {
        setLoading(false);
      }
    };

    fetchQualityScore();
  }, [propertyId]);

  if (loading) {
    return (
      <div className="inline-flex items-center px-3 py-1 rounded-full bg-gray-100 text-gray-600">
        <span className="text-sm">Loading...</span>
      </div>
    );
  }

  if (error || !qualityData) {
    return null;
  }

  const colorClasses = {
    green: 'bg-green-100 text-green-800 border-green-300',
    blue: 'bg-blue-100 text-blue-800 border-blue-300',
    yellow: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    red: 'bg-red-100 text-red-800 border-red-300'
  };

  const colorClass = colorClasses[qualityData.color] || colorClasses.gray;

  if (!detailed) {
    // Compact badge view
    return (
      <div className={`inline-flex items-center px-3 py-1 rounded-full border ${colorClass}`}>
        <span className="font-semibold mr-2">Quality:</span>
        <span className="text-lg font-bold">{qualityData.quality_score}</span>
        <span className="ml-2 text-sm capitalize">({qualityData.quality_level})</span>
      </div>
    );
  }

  // Detailed view with breakdown
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Floor Plan Quality</h3>
        <div className={`px-3 py-1 rounded-full border ${colorClass}`}>
          <span className="text-2xl font-bold">{qualityData.quality_score}</span>
          <span className="text-sm ml-2 capitalize">({qualityData.quality_level})</span>
        </div>
      </div>

      {/* Quality Breakdown */}
      <div className="space-y-3 mb-4">
        {Object.entries(qualityData.breakdown).map(([key, value]) => (
          <div key={key}>
            <div className="flex justify-between text-sm mb-1">
              <span className="capitalize">{key}</span>
              <span className="font-semibold">{value}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${value >= 80 ? 'bg-green-500' : value >= 60 ? 'bg-blue-500' : value >= 40 ? 'bg-yellow-500' : 'bg-red-500'}`}
                style={{ width: `${value}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Metadata */}
      <div className="border-t pt-3 text-sm text-gray-600">
        <p>Rooms Measured: {qualityData.metadata.rooms_measured}</p>
        <p>Total: {qualityData.metadata.total_square_feet.toLocaleString()} sq ft</p>
        <p className="capitalize">Method: {qualityData.metadata.measurement_method.replace(/_/g, ' ')}</p>
      </div>

      {/* Recommendations */}
      {qualityData.recommendations && qualityData.recommendations.length > 0 && (
        <div className="mt-4 bg-blue-50 rounded p-3">
          <p className="text-sm font-semibold mb-2">Recommendations:</p>
          <ul className="text-sm space-y-1">
            {qualityData.recommendations.map((rec, idx) => (
              <li key={idx} className="text-gray-700">• {rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default QualityScoreBadge;
