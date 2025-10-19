import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const PPSFComparisonChart = ({ property, comparables }) => {
  // Prepare data for chart
  const prepareChartData = () => {
    const data = []
    
    // Add current property
    if (property.extracted_data?.square_footage && property.market_insights?.price_estimate?.estimated_value) {
      const price = property.market_insights.price_estimate.estimated_value
      const sqft = property.extracted_data.square_footage
      const ppsf = Math.round(price / sqft)
      
      data.push({
        name: 'Your Property',
        ppsf: ppsf,
        isSubject: true,
        address: property.extracted_data.address || 'Your Property'
      })
    }
    
    // Add comparable properties
    if (comparables && comparables.length > 0) {
      comparables.forEach((comp, index) => {
        if (comp.last_sale_price && comp.square_feet && comp.square_feet > 0) {
          const ppsf = Math.round(comp.last_sale_price / comp.square_feet)
          data.push({
            name: `Comp ${index + 1}`,
            ppsf: ppsf,
            isSubject: false,
            address: comp.address || `Comparable ${index + 1}`
          })
        }
      })
    }
    
    return data
  }
  
  const chartData = prepareChartData()
  
  if (chartData.length === 0) {
    return (
      <div className="rounded-lg p-6" style={{background: '#F6F1EB', border: '1px solid #E5E5E5'}}>
        <p className="text-sm text-center" style={{color: '#666666'}}>
          No comparable data available for chart
        </p>
      </div>
    )
  }
  
  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="rounded-lg p-3 shadow-lg" style={{background: '#000000', border: '2px solid #FF5959'}}>
          <p className="text-xs font-bold mb-1" style={{color: '#FF5959'}}>
            {data.name}
          </p>
          <p className="text-sm font-bold" style={{color: '#FFFFFF'}}>
            ${data.ppsf.toLocaleString()}/sqft
          </p>
          <p className="text-xs mt-1" style={{color: '#CCCCCC'}}>
            {data.address}
          </p>
        </div>
      )
    }
    return null
  }
  
  return (
    <div className="rounded-lg p-6" style={{background: '#FFFFFF', border: '2px solid #000000'}}>
      <div className="mb-4">
        <h3 className="text-sm font-black uppercase tracking-wider mb-1" style={{color: '#000000', letterSpacing: '1.5px'}}>
          Price Per Square Foot Comparison
        </h3>
        <p className="text-xs" style={{color: '#666666'}}>
          Your property vs {chartData.length - 1} comparable sales
        </p>
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" />
          <XAxis 
            dataKey="name" 
            angle={-45}
            textAnchor="end"
            height={80}
            tick={{ fill: '#666666', fontSize: 12 }}
          />
          <YAxis 
            tick={{ fill: '#666666', fontSize: 12 }}
            label={{ 
              value: 'Price per Sq Ft ($)', 
              angle: -90, 
              position: 'insideLeft',
              style: { fill: '#666666', fontSize: 12 }
            }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="ppsf" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.isSubject ? '#FF5959' : '#CCCCCC'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      
      {/* Legend */}
      <div className="flex items-center justify-center gap-4 mt-4 pt-4" style={{borderTop: '1px solid #E5E5E5'}}>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{background: '#FF5959'}}></div>
          <span className="text-xs" style={{color: '#666666'}}>Your Property</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{background: '#CCCCCC'}}></div>
          <span className="text-xs" style={{color: '#666666'}}>Comparable Sales</span>
        </div>
      </div>
    </div>
  )
}

export default PPSFComparisonChart

