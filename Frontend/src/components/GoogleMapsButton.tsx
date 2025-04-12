import React from "react";
import { Map, Search, Camera } from 'lucide-react';
import axios from "axios";
import { useState } from "react";
// Google Maps Button Component with City Search
const GoogleMapsButton = () => {
  const [cityName, setCityName] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState('');

  const handleCityChange = (e) => {
    setCityName(e.target.value);
    setSearchError('');
  };

  const openGoogleMapsWithCity = async () => {
    if (!cityName.trim()) {
      setSearchError('Please enter a city name');
      return;
    }

    setIsSearching(true);
    setSearchError('');

    try {
      // Using Nominatim OpenStreetMap API for geocoding (free and no API key required)
      const response = await axios.get(`https://nominatim.openstreetmap.org/search`, {
        params: {
          q: cityName,
          format: 'json',
          limit: 1
        },
        headers: {
          'Accept-Language': 'en-US,en;q=0.9',
          'User-Agent': 'GeoPV-Solar-Analyzer'
        }
      });

      if (response.data && response.data.length > 0) {
        const { lat, lon } = response.data[0];
        // Open Google Maps in a new tab with the specified coordinates and zoom level
        window.open(
          `https://www.google.com/maps/@${lat},${lon},115m/data=!3m1!1e3`,
          '_blank'
        );
      } else {
        setSearchError(`Location "${cityName}" not found. Please try another search term.`);
      }
    } catch (error) {
      console.error("Error finding city coordinates:", error);
      setSearchError('Error finding location. Please try again.');
    } finally {
      setIsSearching(false);
    }
  };

  const openGoogleMapsCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          window.open(
            `https://www.google.com/maps/@${latitude},${longitude},115m/data=!3m1!1e3`,
            '_blank'
          );
        },
        (error) => {
          console.error("Geolocation error:", error);
          setSearchError('Unable to get your location. Please try searching for a city instead.');
        }
      );
    } else {
      setSearchError('Geolocation is not supported by your browser. Please search for a city instead.');
    }
  };

  return (
    <div className="mb-6 p-6 border border-green-100 rounded-lg bg-green-50">
      <div className="flex items-center gap-3 mb-4">
        <Map size={24} className="text-green-600" />
        <h3 className="text-lg font-semibold text-green-800">Find Location on Google Maps</h3>
      </div>
      
      <div className="flex flex-col space-y-4">
        {/* City search input and button */}
        <div className="flex flex-col sm:flex-row gap-2">
          <div className="relative flex-grow">
            <input
              type="text"
              value={cityName}
              onChange={handleCityChange}
              placeholder="Enter city name (e.g. Mumbai, Delhi)"
              className="w-full px-4 py-2 border border-green-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
            />
            {searchError && (
              <p className="text-red-500 text-xs mt-1">{searchError}</p>
            )}
          </div>
          
          <button
            onClick={openGoogleMapsWithCity}
            disabled={isSearching}
            className="flex items-center justify-center gap-2 py-2 px-4 bg-green-600 text-white rounded-lg 
              hover:bg-green-700 transition-colors disabled:bg-green-400 cursor-pointer"
          >
            {isSearching ? (
              <span className="animate-pulse">Searching...</span>
            ) : (
              <>
                <Search size={18} />
                <span>Search City</span>
              </>
            )}
          </button>
        </div>
        
        {/* Current location button */}
        <div className="text-center">
          <button
            onClick={openGoogleMapsCurrentLocation}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium cursor-pointer"
          >
            Or use my current location
          </button>
        </div>
      </div>
      
      <div className="mt-4 p-3 bg-white rounded-lg border border-green-100">
        <div className="flex items-center gap-2">
          <Camera size={16} className="text-green-600" />
          <p className="text-sm text-green-700">
            Google Maps will open at the 115m zoom level. Take a screenshot of the area you want to analyze.
          </p>
        </div>
      </div>
    </div>
  );
};

export default GoogleMapsButton;