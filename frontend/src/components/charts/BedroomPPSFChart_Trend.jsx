import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Scatter, ComposedChart } from 'recharts';
import { Moon } from 'lucide-react';

const BedroomPPSFChart_Trend = ({ properties }) => {
  if (!properties || properties.length === 0) {
    return null;
  }

  const chartData = [];
  
  properties.forEach(property => {
    const extracted = property.extracted_data || {};
    const rooms = extracted.rooms || [];
    const marketData = extracted.market_insights || {};
    const price = marketData.price_estimate?.estimated_value || 0;
    const sqft = extracted.square_footage || 0;
    const ppsf = sqft > 0 && price > 0 ? Math.round(price / sqft) : 0;

    if (ppsf === 0 || rooms.length === 0) return;

    // Find bedroom (prioritize primary/master bedroom)
    const bedroom = rooms.find(r => {
      const roomType = (r.type || r.room_type || '').toLowerCase();
      return roomType && (
        roomType.includes('bedroom') ||
        roomType.includes('bed') ||
        roomType.includes('br') ||
        roomType.includes('master') ||
        roomType.includes('primary')
      );
    });

    if (!bedroom) return;

    const dimensionsStr = bedroom.dimensions || '';
    if (!dimensionsStr || 
        dimensionsStr.toLowerCase().includes('irregular') ||
        dimensionsStr.toLowerCase().includes('n/a') ||
        dimensionsStr.toLowerCase().includes('varies')) return;

    const match = dimensionsStr.match(/(\d+)['\-].*?\s*x\s*(\d+)['\-]/i);
    if (!match) return;

    const length = parseInt(match[1]);
    const width = parseInt(match[2]);
    const roomSize = length * width;

    if (roomSize > 0 && roomSize < 800) { // Bedrooms typically smaller than living rooms
      chartData.push({
        size: Math.round(roomSize),
        ppsf: ppsf,
        address: extracted.address || property.address
      });
    }
  });

  if (chartData.length === 0) {
    return null;
  }

  const sortedData = chartData.sort((a, b) => a.size - b.size);
  const avgPPSF = Math.round(sortedData.reduce((sum, item) => sum + item.ppsf, 0) / sortedData.length);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="p-3 rounded-lg shadow-xl" style={{background: '#FFFFFF', border: '3px solid #000000'}}>
          <p className="text-xs font-bold mb-2" style={{color: '#000000'}}>
            {data.address?.substring(0, 30)}...
          </p>
          <div className="space-y-1 text-xs">
            <p><span className="font-semibold">Size:</span> {data.size} sq ft</p>
            <p><span className="font-semibold" style={{color: '#6366F1'}}>PPSF: ${data.ppsf.toLocaleString()}</span></p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="rounded-lg p-6" style={{border: '3px solid #6366F1', background: 'transparent'}}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Moon className="w-5 h-5" style={{color: '#6366F1'}} />
          <div>
            <h3 className="text-sm font-black uppercase tracking-wider" style={{color: '#000000', letterSpacing: '1.5px'}}>
              Trend Analysis
            </h3>
          </div>
        </div>
        <div className="px-3 py-1.5 rounded-lg" style={{background: '#FFFFFF', border: '2px solid #6366F1'}}>
          <p className="text-xs font-bold" style={{color: '#6366F1'}}>${avgPPSF} avg</p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={sortedData} margin={{ top: 10, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" />
          <XAxis 
            dataKey="size" 
            label={{ value: 'Size (sq ft)', position: 'bottom', offset: -5, style: { fill: '#666666', fontSize: 12 } }}
            tick={{ fill: '#666666', fontSize: 11 }}
          />
          <YAxis 
            label={{ value: 'PPSF', angle: -90, position: 'insideLeft', style: { fill: '#666666', fontSize: 12 } }}
            tick={{ fill: '#666666', fontSize: 11 }}
            tickFormatter={(value) => `$${value}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line 
            type="monotone" 
            dataKey="ppsf" 
            stroke="#6366F1" 
            strokeWidth={3}
            dot={{ fill: '#6366F1', stroke: '#000000', strokeWidth: 2, r: 5 }}
            activeDot={{ r: 7, stroke: '#6366F1', strokeWidth: 3 }}
          />
        </ComposedChart>
      </ResponsiveContainer>

      <div className="grid grid-cols-3 gap-2 mt-4">
        <div className="p-2 rounded text-center" style={{background: '#F6F1EB'}}>
          <p className="text-xs font-bold mb-1" style={{color: '#666666'}}>Min</p>
          <p className="text-sm font-black" style={{color: '#000000'}}>
            {Math.min(...sortedData.map(d => d.size))} sf
          </p>
        </div>
        <div className="p-2 rounded text-center" style={{background: '#FFFFFF', border: '1px solid #6366F1'}}>
          <p className="text-xs font-bold mb-1" style={{color: '#6366F1'}}>Total</p>
          <p className="text-sm font-black" style={{color: '#6366F1'}}>
            {sortedData.length}
          </p>
        </div>
        <div className="p-2 rounded text-center" style={{background: '#F6F1EB'}}>
          <p className="text-xs font-bold mb-1" style={{color: '#666666'}}>Max</p>
          <p className="text-sm font-black" style={{color: '#000000'}}>
            {Math.max(...sortedData.map(d => d.size))} sf
          </p>
        </div>
      </div>
    </div>
  );
};

export default BedroomPPSFChart_Trend;

