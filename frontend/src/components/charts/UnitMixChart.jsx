import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const UnitMixChart = ({ properties }) => {
  if (!properties || properties.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg border-2 border-gray-200">
        <h3 className="text-lg font-bold mb-4" style={{color: '#000000'}}>Unit Mix Overview</h3>
        <p className="text-gray-500">No property data available</p>
      </div>
    );
  }

  // Count unit types by bedroom count (include all properties with bedroom data)
  const unitCounts = properties.reduce((acc, property) => {
    const bedrooms = property.extracted_data?.bedrooms;
    
    // Skip if no bedroom data extracted yet
    if (bedrooms === undefined || bedrooms === null) {
      return acc;
    }
    
    let unitType = '';
    
    if (bedrooms === 0) {
      unitType = 'Studio';
    } else if (bedrooms === 1) {
      unitType = '1-Bedroom';
    } else if (bedrooms === 2) {
      unitType = '2-Bedroom';
    } else if (bedrooms === 3) {
      unitType = '3-Bedroom';
    } else if (bedrooms >= 4) {
      unitType = '4+ Bedroom';
    }
    
    acc[unitType] = (acc[unitType] || 0) + 1;
    return acc;
  }, {});

  // Convert to chart data format
  const chartData = Object.entries(unitCounts)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => {
      // Sort by bedroom count
      const order = ['Studio', '1-Bedroom', '2-Bedroom', '3-Bedroom', '4+ Bedroom'];
      return order.indexOf(a.name) - order.indexOf(b.name);
    });

  if (chartData.length === 0) {
    const analyzingCount = properties.filter(p => p.status !== 'complete' && p.status !== 'failed').length;
    return (
      <div className="bg-white p-6 rounded-lg border-2 border-gray-200">
        <h3 className="text-lg font-bold mb-4" style={{color: '#000000'}}>Unit Mix Overview</h3>
        <p className="text-gray-500">
          {analyzingCount > 0 
            ? `Waiting for ${analyzingCount} ${analyzingCount === 1 ? 'property' : 'properties'} to finish analyzing...`
            : 'No unit type data available yet'
          }
        </p>
      </div>
    );
  }
  
  // Count properties still analyzing
  const analyzingCount = properties.filter(p => 
    !p.extracted_data?.bedrooms && (p.status === 'processing' || p.status === 'parsing_complete' || p.status === 'enrichment_complete')
  ).length;

  // Colors for different unit types
  const COLORS = {
    'Studio': '#FF5959',
    '1-Bedroom': '#000000',
    '2-Bedroom': '#666666',
    '3-Bedroom': '#999999',
    '4+ Bedroom': '#CCCCCC'
  };

  const total = chartData.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="p-6 rounded-lg" style={{border: '3px solid #000000', background: 'transparent'}}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-black uppercase tracking-wider" style={{color: '#000000', letterSpacing: '1.5px'}}>
          Unit Mix Analysis
        </h3>
        <div className="flex items-center gap-2">
          {analyzingCount > 0 && (
            <div className="text-xs font-bold px-3 py-1 rounded" style={{background: '#FFFFFF', color: '#FF5959', border: '1px solid #FF5959'}}>
              +{analyzingCount} analyzing
            </div>
          )}
          <div className="text-xs font-bold px-3 py-1 rounded" style={{background: '#FFFFFF', color: '#666666'}}>
            {total} {total === 1 ? 'Unit' : 'Units'}
          </div>
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={90}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#CCCCCC'} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value, name, props) => [
              `${value} units (${((value / total) * 100).toFixed(1)}%)`,
              props.payload.name
            ]}
          />
        </PieChart>
      </ResponsiveContainer>

      {/* Legend with counts */}
      <div className="mt-4 grid grid-cols-2 gap-3">
        {chartData.map((item) => (
          <div key={item.name} className="flex items-center justify-between p-3 rounded" style={{background: '#FFFFFF'}}>
            <div className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full flex-shrink-0" 
                style={{background: COLORS[item.name]}}
              />
              <span className="text-xs font-bold" style={{color: '#000000'}}>{item.name}</span>
            </div>
            <span className="text-sm font-black" style={{color: '#FF5959'}}>{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default UnitMixChart;

