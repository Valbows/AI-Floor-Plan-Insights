import React from 'react';
import { Grid3x3, TrendingUp } from 'lucide-react';

const BedroomPPSFChart_Grid = ({ properties }) => {
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

    if (roomSize > 0 && roomSize < 800) {
      chartData.push({
        size: Math.round(roomSize),
        ppsf: ppsf,
        address: extracted.address || property.address,
        dimensions: `${length}' x ${width}'`
      });
    }
  });

  if (chartData.length === 0) {
    return null;
  }

  const sortedData = chartData.sort((a, b) => b.ppsf - a.ppsf);
  const avgPPSF = Math.round(sortedData.reduce((sum, item) => sum + item.ppsf, 0) / sortedData.length);
  const avgSize = Math.round(sortedData.reduce((sum, item) => sum + item.size, 0) / sortedData.length);

  return (
    <div className="rounded-lg" style={{border: '3px solid #000000', background: 'transparent'}}>
      <div className="p-4 pb-3 rounded-t-lg" style={{background: '#6366F1'}}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Grid3x3 className="w-5 h-5" style={{color: '#FFFFFF'}} />
            <h3 className="text-sm font-black uppercase tracking-wider" style={{color: '#FFFFFF', letterSpacing: '1.5px'}}>
              Property Details
            </h3>
          </div>
          <p className="text-xs" style={{color: '#E0E7FF'}}>
            {sortedData.length} Properties
          </p>
        </div>
      </div>

        <div className="p-4">
          {/* Property Cards Grid */}
          <div className="space-y-2 overflow-y-auto" style={{ maxHeight: '340px' }}>
          <div className="grid grid-cols-12 gap-2 px-3 pb-2" style={{borderBottom: '2px solid #E5E5E5'}}>
            <div className="col-span-1 text-xs font-bold" style={{color: '#666666'}}>#</div>
            <div className="col-span-5 text-xs font-bold" style={{color: '#666666'}}>ADDRESS</div>
            <div className="col-span-2 text-xs font-bold text-center" style={{color: '#666666'}}>DIM</div>
            <div className="col-span-2 text-xs font-bold text-center" style={{color: '#666666'}}>SIZE</div>
            <div className="col-span-2 text-xs font-bold text-right" style={{color: '#666666'}}>PPSF</div>
          </div>

          {sortedData.map((property, index) => {
            const isAboveAvg = property.ppsf >= avgPPSF;
            return (
              <div 
                key={index}
                className="grid grid-cols-12 gap-2 p-2.5 rounded-lg transition-all hover:shadow-md"
                style={{
                  background: isAboveAvg ? '#F0FDF4' : '#FAFAFA',
                  border: `2px solid ${isAboveAvg ? '#22C55E' : '#E5E5E5'}`
                }}
              >
                <div className="col-span-1 flex items-center">
                  <div className="w-5 h-5 rounded-full flex items-center justify-center font-bold text-xs" 
                       style={{background: isAboveAvg ? '#22C55E' : '#CCCCCC', color: '#FFFFFF'}}>
                    {index + 1}
                  </div>
                </div>
                <div className="col-span-5 flex items-center">
                  <p className="text-xs font-semibold truncate" style={{color: '#000000'}}>
                    {property.address?.substring(0, 30)}...
                  </p>
                </div>
                <div className="col-span-2 flex items-center justify-center">
                  <span className="text-xs font-bold px-2 py-0.5 rounded" style={{background: '#FFFFFF', color: '#666666', border: '1px solid #E5E5E5'}}>
                    {property.dimensions}
                  </span>
                </div>
                <div className="col-span-2 flex items-center justify-center">
                  <p className="text-xs font-bold" style={{color: '#000000'}}>
                    {property.size} sf
                  </p>
                </div>
                <div className="col-span-2 flex items-center justify-end">
                  <p className="text-sm font-black" style={{color: isAboveAvg ? '#22C55E' : '#000000'}}>
                    ${property.ppsf.toLocaleString()}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Compact Legend */}
        <div className="mt-4 p-2.5 rounded-lg" style={{background: '#F6F1EB'}}>
          <div className="flex items-center justify-center gap-4 text-xs">
            <div className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full" style={{background: '#22C55E'}}></div>
              <span style={{color: '#666666'}}>Above Avg</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full" style={{background: '#CCCCCC'}}></div>
              <span style={{color: '#666666'}}>Below Avg</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BedroomPPSFChart_Grid;

