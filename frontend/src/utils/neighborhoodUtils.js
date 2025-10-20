/**
 * Neighborhood Utilities
 * Extract and manage Brooklyn neighborhoods
 */

// Common Brooklyn neighborhoods (matches Andrew's BK Sales Tracker)
export const BROOKLYN_NEIGHBORHOODS = [
  'Williamsburg',
  'Gowanus',
  'Park Slope',
  'Brooklyn Heights',
  'DUMBO',
  'Carroll Gardens',
  'Red Hook',
  'Greenpoint',
  'Bushwick',
  'Bedford-Stuyvesant',
  'Crown Heights',
  'Prospect Heights',
  'Fort Greene',
  'Clinton Hill',
  'Cobble Hill',
  'Boerum Hill',
  'Sunset Park',
  'Bay Ridge',
  'Kensington',
  'Windsor Terrace',
  'Prospect Lefferts Gardens',
  'Flatbush',
  'Marine Park',
  'Dyker Heights',
  'Borough Park'
].sort();

/**
 * Extract neighborhood from address string
 * @param {string} address - Full property address
 * @returns {string} - Neighborhood name or 'Other'
 */
export const extractNeighborhood = (address) => {
  if (!address) return 'Other';
  
  const addressUpper = address.toUpperCase();
  
  // First: Check for exact neighborhood matches (Williamsburg, Gowanus, etc.)
  for (const hood of BROOKLYN_NEIGHBORHOODS) {
    if (addressUpper.includes(hood.toUpperCase())) {
      return hood;
    }
  }
  
  // Second: Try to extract from address parts (flexible parsing)
  const parts = address.split(',').map(p => p.trim());
  
  // Pattern 1: "123 Main St, Williamsburg, Brooklyn, NY" (4+ parts)
  if (parts.length >= 4) {
    const potentialHood = parts[1]; // Second part often neighborhood
    const match = BROOKLYN_NEIGHBORHOODS.find(hood => 
      hood.toUpperCase() === potentialHood.toUpperCase()
    );
    if (match) return match;
  }
  
  // Pattern 2: "123 Main St, Brooklyn, NY" - Use "Brooklyn" as neighborhood
  if (parts.length >= 2) {
    // Check if any part matches a known neighborhood
    for (let i = 1; i < parts.length - 1; i++) {
      const part = parts[i].trim();
      const match = BROOKLYN_NEIGHBORHOODS.find(hood => 
        hood.toUpperCase() === part.toUpperCase()
      );
      if (match) return match;
    }
    
    // If no specific neighborhood found, check for borough/city name
    const cityPart = parts[parts.length - 2].trim();
    if (cityPart.length > 2 && cityPart.length < 30) {
      // Accept Brooklyn, Manhattan, Queens, etc. as valid neighborhoods
      if (!['NY', 'NEW YORK', 'USA'].includes(cityPart.toUpperCase())) {
        return cityPart;
      }
    }
  }
  
  return 'Other';
};

/**
 * Get all unique neighborhoods from properties
 * @param {Array} properties - Array of property objects
 * @returns {Array} - Sorted array of unique neighborhoods
 */
export const getUniqueNeighborhoods = (properties) => {
  const neighborhoods = new Set();
  
  properties.forEach(property => {
    const extractedData = property.extracted_data || {};
    const address = extractedData.address || property.address || '';
    const hood = extractNeighborhood(address);
    neighborhoods.add(hood);
  });
  
  return Array.from(neighborhoods).sort();
};

/**
 * Group properties by neighborhood
 * @param {Array} properties - Array of property objects
 * @returns {Object} - Object with neighborhood keys and property arrays
 */
export const groupPropertiesByNeighborhood = (properties) => {
  const grouped = {};
  
  properties.forEach(property => {
    const extractedData = property.extracted_data || {};
    const address = extractedData.address || property.address || '';
    const neighborhood = extractNeighborhood(address);
    
    if (!grouped[neighborhood]) {
      grouped[neighborhood] = [];
    }
    
    grouped[neighborhood].push(property);
  });
  
  return grouped;
};

