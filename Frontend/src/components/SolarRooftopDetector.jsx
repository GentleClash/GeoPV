import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Map, Search, Upload, Camera } from 'lucide-react';
import sampleImage from '../assets/sample.png'

const FullScreenImageModal = ({ imageUrl, onClose }) => {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-80 p-4"
      onClick={onClose}
    >
      <div
        className="relative w-1/2 aspect-auto bg-white p-4 rounded-lg shadow-2xl flex items-center justify-center"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-600 hover:text-gray-800 z-60"
        >
          <X size={24} />
        </button>
        <img
          src={imageUrl}
          alt="Rooftop Detection Visualization"
          className="max-w-full max-h-full object-contain"
        />
      </div>
    </div>
  );
};

// File Upload Component
const FileUploader = ({ onFileSelect, selectedFile }) => (
  <div className="mb-4 p-6 border border-blue-100 rounded-lg bg-blue-50">
    <div className="flex items-center gap-3 mb-4">
      <Upload size={24} className="text-blue-600" />
      <h3 className="text-lg font-semibold text-blue-800 ">Upload an Image</h3>
    </div>
    
    <input
      type="file"
      onChange={onFileSelect}
      accept="image/*"
      className="block w-full text-sm text-slate-500
        file:mr-4 file:py-2 file:px-4
        file:rounded-full file:border-0
        file:text-sm file:font-semibold
        file:bg-blue-100 file:text-blue-700
        hover:file:bg-blue-200"
    />
    {selectedFile && (
      <div className="mt-3 p-3 bg-white rounded-lg border border-blue-100">
        <p className="text-sm text-blue-700 font-medium">
          Selected file: {selectedFile.name}
        </p>
      </div>
    )}
  </div>
);

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

// Sample Image Guide Component
const SampleImageGuide = () => (
  <div className="mt-6 p-6 border border-gray-200 rounded-lg bg-gray-50">
    <div className="flex items-center gap-3 mb-3">
      <h3 className="font-semibold text-gray-700">Image Requirements</h3>
    </div>
    <div className="flex flex-col items-center">
      <img
        src={sampleImage}
        alt="Sample satellite rooftop image"
        className="w-full max-w-sm rounded-lg shadow-md mb-3"
      />
      <p className="text-sm text-gray-600 font-medium text-center">
        For best results, upload an aerial image with approximately 115 meters of zoom level as shown above.
      </p>
    </div>
  </div>
);

// Rooftop Summary Component
const RooftopSummary = ({ analysis }) => (
  <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
    <h3 className="font-bold mb-2 text-blue-800">Solar Potential Overview</h3>
    <div className="space-y-2">
      <p>
        <span className="font-medium">Total Rooftop Coverage:</span>{' '}
        {analysis.total_coverage_percentage.toFixed(2)}%
      </p>
      <p>
        <span className="font-medium">Total Energy Potential:</span>{' '}
        {analysis.total_energy_potential.toFixed(2)} kWh/year
      </p>
    </div>
  </div>
);

// Individual Rooftop Details Component
const RooftopDetails = ({ rooftops }) => (
  <div className="max-h-64 overflow-y-auto bg-white p-4 rounded-lg border border-gray-200">
    <h3 className="font-bold mb-3 text-blue-800">Individual Rooftop Details</h3>
    {rooftops.map((rooftop) => (
      <div
        key={rooftop.id}
        className="mb-3 pb-3 border-b border-gray-200 last:border-b-0"
      >
        <h4 className="font-semibold text-blue-700">Rooftop {rooftop.id}</h4>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <p>Coverage: {rooftop.percentage.toFixed(2)}%</p>
          <p>Area: {rooftop.area_m2.toFixed(2)} m²</p>
          <p>Energy Potential: {rooftop.energy_potential_kwh_per_year.toFixed(2)} kWh/year</p>
        </div>
      </div>
    ))}
  </div>
);

// Loading Spinner Component
const LoadingSpinner = ({ message }) => (
  <div className="text-center py-6">
    <div className="animate-spin inline-block w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
    <p className="mt-2 text-blue-600">{message || 'Analyzing image...'}</p>
  </div>
);

// Job Progress Component
const JobProgress = ({ status, position }) => {
  let statusMessage = "Processing image...";
  
  if (position !== undefined) {
    statusMessage = `Processing image... (Position in queue: ${position})`;
  }
  
  return (
    <div className="mt-4 p-4 bg-blue-50 text-blue-800 rounded-lg border border-blue-200">
      <div className="flex flex-col items-center gap-2">
        <LoadingSpinner message={statusMessage} />
        <div className="w-full bg-blue-200 rounded-full h-2.5">
          <div className="bg-blue-600 h-2.5 rounded-full animate-pulse w-3/4"></div>
        </div>
        <p className="text-sm text-blue-600">This may take up to a minute depending on image complexity</p>
      </div>
    </div>
  );
};

// Error Display Component
const ErrorDisplay = ({ message }) => (
  <div className="mt-4 p-4 bg-red-100 text-red-800 rounded-lg border border-red-200">
    <div className="flex items-center gap-2">
      <div className="w-5 h-5 flex items-center justify-center rounded-full bg-red-200 text-red-800 font-bold text-xs">!</div>
      <p>{message}</p>
    </div>
  </div>
);

// Options Section Component
const OptionsSection = ({ children, title, icon }) => (
  <div className="mb-8 border-b border-gray-200 pb-6">
    <div className="flex items-center gap-2 mb-4">
      {icon}
      <h2 className="text-xl font-bold text-gray-800">{title}</h2>
    </div>
    {children}
  </div>
);

// Main Solar Rooftop Detector Component
const SolarRooftopDetector = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fullScreenImage, setFullScreenImage] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [pollingInterval, setPollingInterval] = useState(null);

  // Function to check job status
  const checkJobStatus = async (id) => {
    try {
      const response = await axios.get(`http://localhost:5000/job_status/${id}`);
      const statusData = response.data;
      
      setJobStatus(statusData);
      
      // If job completed, fetch results
      if (statusData.status === 'completed') {
        clearInterval(pollingInterval);
        setPollingInterval(null);
        
        // Get image as blob
        const imageResponse = await axios.get(`http://localhost:5000/get_result_image/${id}`, {
          responseType: 'blob'
        });
        
        // Get report as text
        const reportResponse = await axios.get(`http://localhost:5000/get_report/${id}`, {
          responseType: 'text'
        });
        
        setAnalysisResult({
          analysis: statusData,  // The analysis data is now included in the status response
          imageUrl: URL.createObjectURL(imageResponse.data),
          report: reportResponse.data
        });
        
        setIsLoading(false);
      } 
      // If job failed, show error
      else if (statusData.status === 'failed' || statusData.status === 'error') {
        clearInterval(pollingInterval);
        setPollingInterval(null);
        setError(statusData.error || 'Analysis failed');
        setIsLoading(false);
      }
      // Otherwise continue polling
    } catch (err) {
      console.error("Error checking job status:", err);
      setError("Error checking job status. Please try again.");
      clearInterval(pollingInterval);
      setPollingInterval(null);
      setIsLoading(false);
    }
  };

  // Clean up polling on component unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setAnalysisResult(null);
    setError(null);
    setJobId(null);
    setJobStatus(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }

    const formData = new FormData();
    formData.append('image', selectedFile);

    setIsLoading(true);
    setError(null);
    setJobId(null);
    setJobStatus(null);

    try {
      // Submit job
      const response = await axios.post('http://localhost:5000/detect_rooftops', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // Get job ID from response
      const id = response.data.job_id;
      setJobId(id);
      
      // Start polling for job status
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
      
      const interval = setInterval(() => {
        checkJobStatus(id);
      }, 2000); // Poll every 2 seconds
      
      setPollingInterval(interval);
      
      // Also check immediately
      checkJobStatus(id);
      
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred during upload');
      console.error(err);
      setIsLoading(false);
    }
  };

  const handleImageClick = () => {
    if (analysisResult?.imageUrl) {
      setFullScreenImage(analysisResult.imageUrl);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white shadow-xl rounded-lg">
      <div className="bg-gradient-to-r from-blue-600 to-green-600 -mx-6 -mt-6 px-6 py-5 rounded-t-lg mb-8">
        <h1 className="text-center">
          <div className="text-3xl font-bold text-white font-mono">
            GeoPV
          </div>
          <div className="text-lg text-white font-light">
            A solar potential analyzer for Indian rooftops.
          </div>
        </h1>
      </div>

      {/* Step 1: Get an Image */}
      <OptionsSection 
        title="Get an Image" 
        icon={<div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold">1</div>}
      >
        <p className="mb-4 text-gray-600">Choose one of these options to get a satellite image for analysis:</p>
        
        {/* Google Maps Button with City Search */}
        <GoogleMapsButton />
        
        <div className="text-center my-4">
          <div className="inline-block px-4 py-1 rounded-full bg-gray-100 text-gray-600 text-sm font-medium">
            OR
          </div>
        </div>
        
        {/* File Upload Component */}
        <FileUploader
          onFileSelect={handleFileSelect}
          selectedFile={selectedFile}
        />

        {/* Show sample image guide only when no file is selected and not analyzing */}
        {!selectedFile && !isLoading && !analysisResult && (
          <SampleImageGuide />
        )}
      </OptionsSection>

      {/* Step 2: Run Analysis */}
      <OptionsSection 
        title="Run Analysis" 
        icon={<div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold">2</div>}
      >
        <button
          onClick={handleUpload}
          disabled={!selectedFile || isLoading}
          className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg text-lg font-medium
            hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors cursor-pointer"
        >
          {isLoading ? 'Analyzing...' : 'Detect Solar Potential'}
        </button>

        {error && <ErrorDisplay message={error} />}
        
        {/* Show job progress when job is processing */}
        {isLoading && jobStatus && jobStatus.status === 'processing' && (
          <JobProgress 
            status={jobStatus.status} 
            position={jobStatus.position_in_queue} 
          />
        )}
        
        {/* Show simple loading spinner when initiating job */}
        {isLoading && (!jobStatus || !jobId) && (
          <LoadingSpinner message="Submitting job..." />
        )}
      </OptionsSection>

      {/* Step 3: View Results */}
      {analysisResult && (
        <OptionsSection 
          title="View Results" 
          icon={<div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold">3</div>}
        >
          <div className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <RooftopSummary analysis={analysisResult.analysis} />
                <RooftopDetails rooftops={analysisResult.analysis.rooftops} />
              </div>

              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <h3 className="font-bold mb-2 text-blue-800">Rooftop Detection Visualization</h3>
                <img
                  src={analysisResult.imageUrl}
                  alt="Rooftop Detection Result"
                  className="w-full rounded-lg shadow-md cursor-zoom-in hover:opacity-90 transition-opacity"
                  onClick={handleImageClick}
                />
                <p className="text-xs text-gray-500 mt-2 text-center">Click image to enlarge</p>
              </div>
            </div>

            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <h3 className="font-bold mb-2 text-blue-800">Detailed Report</h3>
              <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto max-h-64 overflow-y-auto border border-gray-200">
                {analysisResult.report}
              </pre>
            </div>
          </div>
        </OptionsSection>
      )}
      
      {/* Full Screen Image Modal */}
      {fullScreenImage && (
        <FullScreenImageModal
          imageUrl={fullScreenImage}
          onClose={() => setFullScreenImage(null)}
        />
      )}
    </div>
  );
};

export default SolarRooftopDetector;