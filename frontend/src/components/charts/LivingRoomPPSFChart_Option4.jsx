import React from 'react';
import { Grid3x3, TrendingUp } from 'lucide-react';

const LivingRoomPPSFChart_Option4 = ({ properties }) => {
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
    <div className="bg-white rounded-lg" style={{border: '3px solid #000000'}}>
      <div className="p-6 pb-4" style={{background: '#000000'}}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg" style={{background: '#FF5959'}}>
              <Grid3x3 className="w-6 h-6" style={{color: '#FFFFFF'}} />
            </div>
            <div>
              <h3 className="text-base font-black uppercase tracking-wider" style={{color: '#FFFFFF', letterSpacing: '1.5px'}}>
                Property Comparison Grid
              </h3>
              <p className="text-xs mt-1" style={{color: '#CCCCCC'}}>
                Living Room Size vs PPSF • {sortedData.length} Properties
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* Stats Bar */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="p-4 rounded-lg" style={{background: '#FFF5F5', border: '2px solid #FF5959'}}>
            <p className="text-xs font-bold uppercase mb-1" style={{color: '#666666'}}>Portfolio Average</p>
            <p className="text-2xl font-black" style={{color: '#FF5959'}}>${avgPPSF}/sqft</p>
            <p className="text-xs mt-1" style={{color: '#666666'}}>Avg Living Room: {avgSize} sq ft</p>
          </div>
          <div className="p-4 rounded-lg" style={{background: '#F6F1EB', border: '2px solid #E5E5E5'}}>
            <p className="text-xs font-bold uppercase mb-1" style={{color: '#666666'}}>Price Range</p>
            <p className="text-2xl font-black" style={{color: '#000000'}}>
              ${Math.min(...sortedData.map(d => d.ppsf))} - ${Math.max(...sortedData.map(d => d.ppsf))}
            </p>
            <p className="text-xs mt-1" style={{color: '#666666'}}>Per Square Foot</p>
          </div>
        </div>

        {/* Property Cards Grid */}
        <div className="space-y-3">
          <div className="grid grid-cols-12 gap-2 px-3 pb-2" style={{borderBottom: '2px solid #E5E5E5'}}>
            <div className="col-span-1 text-xs font-bold" style={{color: '#666666'}}>#</div>
            <div className="col-span-5 text-xs font-bold" style={{color: '#666666'}}>ADDRESS</div>
            <div className="col-span-2 text-xs font-bold text-center" style={{color: '#666666'}}>LIVING ROOM</div>
            <div className="col-span-2 text-xs font-bold text-center" style={{color: '#666666'}}>SIZE</div>
            <div className="col-span-2 text-xs font-bold text-right" style={{color: '#666666'}}>PPSF</div>
          </div>

          {sortedData.map((property, index) => {
            const isAboveAvg = property.ppsf >= avgPPSF;
            return (
              <div 
                key={index}
                className="grid grid-cols-12 gap-2 p-3 rounded-lg transition-all hover:shadow-md"
                style={{
                  background: isAboveAvg ? '#F0FDF4' : '#FFFFFF',
                  border: `2px solid ${isAboveAvg ? '#22C55E' : '#E5E5E5'}`
                }}
              >
                <div className="col-span-1 flex items-center">
                  <div className="w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs" 
                       style={{background: isAboveAvg ? '#22C55E' : '#CCCCCC', color: '#FFFFFF'}}>
                    {index + 1}
                  </div>
                </div>
                <div className="col-span-5 flex items-center">
                  <p className="text-sm font-semibold truncate" style={{color: '#000000'}}>
                    {property.address?.substring(0, 35)}...
                  </p>
                </div>
                <div className="col-span-2 flex items-center justify-center">
                  <span className="text-xs font-bold px-2 py-1 rounded" style={{background: '#F6F1EB', color: '#666666'}}>
                    {property.dimensions}
                  </span>
                </div>
                <div className="col-span-2 flex items-center justify-center">
                  <p className="text-sm font-bold" style={{color: '#000000'}}>
                    {property.size} sq ft
                  </p>
                </div>
                <div className="col-span-2 flex items-center justify-end">
                  <p className="text-lg font-black" style={{color: isAboveAvg ? '#22C55E' : '#000000'}}>
                    ${property.ppsf.toLocaleString()}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Legend */}
        <div className="mt-6 p-4 rounded-lg" style={{background: '#F6F1EB'}}>
          <div className="flex items-center justify-center gap-6 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{background: '#22C55E'}}></div>
              <span style={{color: '#666666'}}>Above Average PPSF</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{background: '#CCCCCC'}}></div>
              <span style={{color: '#666666'}}>Below Average PPSF</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LivingRoomPPSFChart_Option4;

