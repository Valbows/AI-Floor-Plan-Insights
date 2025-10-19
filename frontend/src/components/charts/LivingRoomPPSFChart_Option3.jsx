import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Scatter, ComposedChart } from 'recharts';
import { Activity } from 'lucide-react';

const LivingRoomPPSFChart_Option3 = ({ properties }) => {
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

    const livingRoom = rooms.find(r => {
      const roomType = (r.type || r.room_type || '').toLowerCase();
      return roomType && (
        roomType.includes('living') ||
        roomType.includes('l.r.') ||
        roomType.includes('lr') ||
        roomType.includes('living/dining')
      );
    });

    if (!livingRoom) return;

    const dimensionsStr = livingRoom.dimensions || '';
    if (!dimensionsStr || 
        dimensionsStr.toLowerCase().includes('irregular') ||
        dimensionsStr.toLowerCase().includes('n/a')) return;

    const match = dimensionsStr.match(/(\d+)['\-].*?\s*x\s*(\d+)['\-]/i);
    if (!match) return;

    const length = parseInt(match[1]);
    const width = parseInt(match[2]);
    const roomSize = length * width;

    if (roomSize > 0 && roomSize < 1000) {
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
            <p><span className="font-semibold" style={{color: '#FF5959'}}>PPSF: ${data.ppsf.toLocaleString()}</span></p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg p-6" style={{border: '3px solid #FF5959'}}>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Activity className="w-6 h-6" style={{color: '#FF5959'}} />
          <div>
            <h3 className="text-base font-black uppercase tracking-wider" style={{color: '#000000', letterSpacing: '1.5px'}}>
              Living Room Trend Analysis
            </h3>
            <p className="text-xs mt-1" style={{color: '#666666'}}>
              Price Per Square Foot by Living Room Size
            </p>
          </div>
        </div>
        <div className="px-4 py-2 rounded-lg" style={{background: '#FFF5F5', border: '2px solid #FF5959'}}>
          <p className="text-xs font-bold uppercase" style={{color: '#666666'}}>Avg PPSF</p>
          <p className="text-xl font-black" style={{color: '#FF5959'}}>${avgPPSF}</p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={350}>
        <ComposedChart data={sortedData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" />
          <XAxis 
            dataKey="size" 
            label={{ value: 'Living Room Size (sq ft)', position: 'bottom', offset: -5, style: { fill: '#000000', fontWeight: 'bold' } }}
            tick={{ fill: '#666666' }}
          />
          <YAxis 
            label={{ value: 'Price Per Sq Ft ($)', angle: -90, position: 'insideLeft', style: { fill: '#000000', fontWeight: 'bold' } }}
            tick={{ fill: '#666666' }}
            tickFormatter={(value) => `$${value}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line 
            type="monotone" 
            dataKey="ppsf" 
            stroke="#FF5959" 
            strokeWidth={3}
            dot={{ fill: '#FF5959', stroke: '#000000', strokeWidth: 2, r: 6 }}
            activeDot={{ r: 8, stroke: '#FF5959', strokeWidth: 3 }}
          />
        </ComposedChart>
      </ResponsiveContainer>

      <div className="grid grid-cols-3 gap-4 mt-6">
        <div className="p-3 rounded-lg text-center" style={{background: '#F6F1EB'}}>
          <p className="text-xs font-bold uppercase mb-1" style={{color: '#666666'}}>Min Size</p>
          <p className="text-lg font-black" style={{color: '#000000'}}>
            {Math.min(...sortedData.map(d => d.size))} sf
          </p>
        </div>
        <div className="p-3 rounded-lg text-center" style={{background: '#FFF5F5', border: '2px solid #FF5959'}}>
          <p className="text-xs font-bold uppercase mb-1" style={{color: '#FF5959'}}>Properties</p>
          <p className="text-lg font-black" style={{color: '#FF5959'}}>
            {sortedData.length}
          </p>
        </div>
        <div className="p-3 rounded-lg text-center" style={{background: '#F6F1EB'}}>
          <p className="text-xs font-bold uppercase mb-1" style={{color: '#666666'}}>Max Size</p>
          <p className="text-lg font-black" style={{color: '#000000'}}>
            {Math.max(...sortedData.map(d => d.size))} sf
          </p>
        </div>
      </div>
    </div>
  );
};

export default LivingRoomPPSFChart_Option3;

