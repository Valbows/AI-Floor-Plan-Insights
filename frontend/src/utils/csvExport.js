/**
 * CSV Export Utility for Property Data
 * Matches Andrew's BK Sales Tracker format with added room dimensions
 */

import { extractNeighborhood } from './neighborhoodUtils';

export const exportPropertiesToCSV = (properties) => {
  if (!properties || properties.length === 0) {
    alert('No properties to export');
    return;
  }

  // CSV Headers matching Andrew's workflow + room dimensions
  const headers = [
    'Address',
    'Date Added',
    'Estimated Price',
    'Neighborhood',
    'Square Feet',
    'Price Per Sq Ft',
    'Unit Type',
    'Bedrooms',
    'Bathrooms',
    'Layout Type',
    'Kitchen Size',
    'Living Room Size',
    'Bedroom Size',
    'Bathroom Size',
    'Status',
    'Investment Score'
  ];

  // Helper to format room dimensions
  const formatRoomSize = (rooms, roomType) => {
    if (!rooms || !Array.isArray(rooms)) return '';
    
    const room = rooms.find(r => 
      r.room_type?.toLowerCase().includes(roomType.toLowerCase())
    );
    
    if (!room || !room.dimensions) return '';
    
    // Format: "10' x 12'"
    const dim = room.dimensions;
    if (dim.length && dim.width) {
      return `${dim.length}" x ${dim.width}"`;
    } else if (dim.dimensions_text) {
      return dim.dimensions_text;
    }
    
    return '';
  };

  // Convert properties to CSV rows
  const rows = properties.map(property => {
    const extracted = property.extracted_data || {};
    const marketData = extracted.market_insights || {};
    const address = extracted.address || property.address || '';
    const price = marketData.price_estimate?.estimated_value || 0;
    const sqft = extracted.square_footage || 0;
    const ppsf = sqft > 0 && price > 0 ? Math.round(price / sqft) : 0;
    const bedrooms = extracted.bedrooms || 0;
    const bathrooms = extracted.bathrooms || 0;
    
    // Determine unit type
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
      unitType = `${bedrooms}-Bedroom`;
    }
    
    const neighborhood = extractNeighborhood(address);
    const dateAdded = new Date(property.created_at).toLocaleDateString('en-US');
    const investmentScore = marketData.investment_analysis?.investment_score || '';
    
    // Get room dimensions
    const rooms = extracted.room_details || [];
    const kitchenSize = formatRoomSize(rooms, 'kitchen');
    const livingRoomSize = formatRoomSize(rooms, 'living');
    const bedroomSize = formatRoomSize(rooms, 'bedroom');
    const bathroomSize = formatRoomSize(rooms, 'bath');
    
    return [
      address,
      dateAdded,
      price > 0 ? `$${price.toLocaleString()}` : '',
      neighborhood,
      sqft > 0 ? sqft.toLocaleString() : '',
      ppsf > 0 ? `$${ppsf}` : '',
      unitType,
      bedrooms || '',
      bathrooms || '',
      extracted.layout_type || '',
      kitchenSize,
      livingRoomSize,
      bedroomSize,
      bathroomSize,
      property.status,
      investmentScore
    ];
  });

  // Create CSV content
  const csvContent = [
    headers.join(','),
    ...rows.map(row => 
      row.map(cell => {
        // Escape cells with commas, quotes, or newlines
        const cellStr = String(cell || '');
        if (cellStr.includes(',') || cellStr.includes('"') || cellStr.includes('\n')) {
          return `"${cellStr.replace(/"/g, '""')}"`;
        }
        return cellStr;
      }).join(',')
    )
  ].join('\n');

  // Create download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  const timestamp = new Date().toISOString().split('T')[0];
  const filename = `property-export-${timestamp}.csv`;
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  return true;
};

// Export selected properties (for future bulk selection feature)
export const exportSelectedProperties = (properties, selectedIds) => {
  const selectedProperties = properties.filter(p => selectedIds.has(p.id));
  return exportPropertiesToCSV(selectedProperties);
};

// Export building data (for building-grouped exports)
export const exportBuildingProperties = (buildingAddress, properties) => {
  const filename = `${buildingAddress.replace(/[^a-z0-9]/gi, '_')}-${new Date().toISOString().split('T')[0]}.csv`;
  // Use same export logic but with custom filename
  exportPropertiesToCSV(properties);
};

