import React, { useEffect, useRef, useState } from 'react'
import { Loader as GoogleMapsLoader } from '@googlemaps/js-api-loader'
import { MapPin, Loader, AlertCircle } from 'lucide-react'

const PropertyMap = ({ address, propertyData }) => {
  const mapRef = useRef(null)
  const [map, setMap] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [coordinates, setCoordinates] = useState(null)

  useEffect(() => {
    if (!address) {
      setError('No address provided')
      setLoading(false)
      return
    }

    initializeMap()
  }, [address])

  const initializeMap = async () => {
    try {
      setLoading(true)
      setError(null)

      // Get API key from environment
      const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY

      if (!apiKey) {
        throw new Error('Google Maps API key not configured')
      }

      // Initialize Google Maps loader
      const loader = new GoogleMapsLoader({
        apiKey: apiKey,
        version: 'weekly',
        libraries: ['places']  // Note: geocoding is NOT a library, it's accessed via google.maps.Geocoder
      })

      // Load Google Maps
      const google = await loader.load()

      // Geocode the address
      const geocoder = new google.maps.Geocoder()
      const geocodeResult = await geocoder.geocode({ address })

      if (geocodeResult.results.length === 0) {
        throw new Error('Address not found')
      }

      const location = geocodeResult.results[0].geometry.location
      const coords = {
        lat: location.lat(),
        lng: location.lng()
      }
      setCoordinates(coords)

      // Create map
      const mapInstance = new google.maps.Map(mapRef.current, {
        center: coords,
        zoom: 15,
        mapTypeControl: true,
        mapTypeControlOptions: {
          style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
          position: google.maps.ControlPosition.TOP_RIGHT,
          mapTypeIds: ['roadmap', 'satellite', 'hybrid']
        },
        streetViewControl: true,
        fullscreenControl: true,
        zoomControl: true,
        styles: [
          {
            featureType: 'poi',
            elementType: 'labels',
            stylers: [{ visibility: 'on' }]
          }
        ]
      })

      // Add property marker
      new google.maps.Marker({
        position: coords,
        map: mapInstance,
        title: address,
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          scale: 12,
          fillColor: '#10B981',
          fillOpacity: 1,
          strokeColor: '#FFFFFF',
          strokeWeight: 3
        },
        animation: google.maps.Animation.DROP
      })

      // Add info window
      const infoWindow = new google.maps.InfoWindow({
        content: `
          <div style="padding: 12px; font-family: system-ui;">
            <h3 style="margin: 0 0 8px 0; font-size: 14px; font-weight: 600; color: #111827;">
              ${address}
            </h3>
            ${propertyData.bedrooms || propertyData.bathrooms ? `
              <p style="margin: 0; font-size: 12px; color: #6B7280;">
                ${propertyData.bedrooms || '?'} bed • ${propertyData.bathrooms || '?'} bath
                ${propertyData.square_footage ? ` • ${propertyData.square_footage.toLocaleString()} sq ft` : ''}
              </p>
            ` : ''}
          </div>
        `
      })

      // Show info window on marker click
      const marker = new google.maps.Marker({
        position: coords,
        map: mapInstance,
        title: address
      })

      marker.addListener('click', () => {
        infoWindow.open(mapInstance, marker)
      })

      // Search for nearby amenities
      const placesService = new google.maps.places.PlacesService(mapInstance)
      
      // Search for schools
      placesService.nearbySearch(
        {
          location: coords,
          radius: 1600, // 1 mile
          type: 'school'
        },
        (results, status) => {
          if (status === google.maps.places.PlacesServiceStatus.OK && results) {
            results.slice(0, 5).forEach((place) => {
              new google.maps.Marker({
                position: place.geometry.location,
                map: mapInstance,
                title: place.name,
                icon: {
                  url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                  scaledSize: new google.maps.Size(32, 32)
                }
              })
            })
          }
        }
      )

      // Search for grocery stores
      placesService.nearbySearch(
        {
          location: coords,
          radius: 1600,
          type: 'supermarket'
        },
        (results, status) => {
          if (status === google.maps.places.PlacesServiceStatus.OK && results) {
            results.slice(0, 5).forEach((place) => {
              new google.maps.Marker({
                position: place.geometry.location,
                map: mapInstance,
                title: place.name,
                icon: {
                  url: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
                  scaledSize: new google.maps.Size(32, 32)
                }
              })
            })
          }
        }
      )

      setMap(mapInstance)
      setLoading(false)
    } catch (err) {
      console.error('Error initializing map:', err)
      setError(err.message || 'Failed to load map')
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-2 mb-4">
          <MapPin className="w-5 h-5 text-gray-900" />
          <h2 className="text-lg font-semibold text-gray-900">Location</h2>
        </div>
        <div className="flex flex-col items-center justify-center h-96 bg-gray-50 rounded-lg">
          <Loader className="w-8 h-8 animate-spin text-primary-600 mb-2" />
          <p className="text-sm text-gray-600">Loading map...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-2 mb-4">
          <MapPin className="w-5 h-5 text-gray-900" />
          <h2 className="text-lg font-semibold text-gray-900">Location</h2>
        </div>
        <div className="flex flex-col items-center justify-center h-96 bg-gray-50 rounded-lg">
          <AlertCircle className="w-8 h-8 text-red-600 mb-2" />
          <p className="text-sm text-gray-600">{error}</p>
          <p className="text-xs text-gray-500 mt-1">Google Maps API key may not be configured</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <MapPin className="w-5 h-5 text-gray-900" />
          <h2 className="text-lg font-semibold text-gray-900">Location</h2>
        </div>
        <div className="flex items-center space-x-2 text-xs text-gray-600">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span>Property</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span>Schools</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span>Stores</span>
          </div>
        </div>
      </div>
      
      <div
        ref={mapRef}
        className="w-full h-96 rounded-lg overflow-hidden border border-gray-200"
      />
      
      {coordinates && (
        <div className="mt-4 text-xs text-gray-500">
          <p>{address}</p>
          <p className="mt-1">
            Coordinates: {coordinates.lat.toFixed(6)}, {coordinates.lng.toFixed(6)}
          </p>
        </div>
      )}
    </div>
  )
}

export default PropertyMap
