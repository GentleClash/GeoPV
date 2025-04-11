import React, { useState } from 'react';
import axios from 'axios';
import { X } from 'lucide-react';
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
  <div className="mb-4">
    <input
      type="file"
      onChange={onFileSelect}
      accept="image/*"
      className="block w-full text-sm text-slate-500
        file:mr-4 file:py-2 file:px-4
        file:rounded-full file:border-0
        file:text-sm file:font-semibold
        file:bg-blue-50 file:text-blue-700
        hover:file:bg-blue-100"
    />
    {selectedFile && (
      <p className="mt-2 text-sm text-gray-500">
        Selected file: {selectedFile.name}
      </p>
    )}
  </div>
);

// Sample Image Guide Component
const SampleImageGuide = () => (
  <div className="mt-6 p-4 border border-blue-200 rounded-lg bg-blue-50">
    <h3 className="font-bold mb-2 text-blue-800">Image Example</h3>
    <div className="flex flex-col items-center">
      <img
        src={sampleImage}
        alt="Sample satellite rooftop image"
        className="w-full max-w-sm rounded-lg shadow-md mb-2"
      />
      <p className="text-sm text-blue-700 font-medium text-center">
        For best results, upload an aerial image with approximately 115 meters of zoom level as shown.
      </p>
    </div>
  </div>
);

// Rooftop Summary Component
const RooftopSummary = ({ analysis }) => (
  <div className="bg-blue-50 p-4 rounded-lg">
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
  <div className="max-h-64 overflow-y-auto bg-gray-50 p-4 rounded-lg">
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
          <p>Potential Panels: {rooftop.potential_panel_count}</p>
          <p>CO2 Saved: {rooftop.co2_saved_kg_per_year.toFixed(2)} kg/year</p>
        </div>
      </div>
    ))}
  </div>
);

// Loading Spinner Component
const LoadingSpinner = () => (
  <div className="text-center py-6">
    <div className="animate-spin inline-block w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
    <p className="mt-2 text-blue-600">Analyzing image...</p>
  </div>
);

// Error Display Component
const ErrorDisplay = ({ message }) => (
  <div className="mt-4 p-4 bg-red-100 text-red-800 rounded-lg">
    {message}
  </div>
);

// Main Solar Rooftop Detector Component
const SolarRooftopDetector = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fullScreenImage, setFullScreenImage] = useState(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setAnalysisResult(null);
    setError(null);
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

    try {
      const response = await axios.post('http://localhost:5000/detect_rooftops', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // Fetch the result image
      const imageResponse = await axios.get('http://localhost:5000/get_result_image', {
        responseType: 'blob'
      });

      // Fetch the report
      const reportResponse = await axios.get('http://localhost:5000/get_report', {
        responseType: 'text'
      });

      setAnalysisResult({
        analysis: response.data.analysis,
        imageUrl: URL.createObjectURL(imageResponse.data),
        report: reportResponse.data
      });
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred during upload');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageClick = () => {
    if (analysisResult?.imageUrl) {
      setFullScreenImage(analysisResult.imageUrl);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white shadow-lg rounded-lg">
      <h1 className="text-center mb-4">
        <div className="text-3xl font-bold text-blue-600 font-mono underline">
          GeoPV
        </div>
        <div className="text-lg text-blue-500 font-light">
          A Solar Rooftop Potential Analyzer
        </div>
      </h1>
      <FileUploader
        onFileSelect={handleFileSelect}
        selectedFile={selectedFile}
      />

      <button
        onClick={handleUpload}
        disabled={!selectedFile || isLoading}
        className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg 
          hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? 'Analyzing...' : 'Detect Solar Potential'}
      </button>

      {error && <ErrorDisplay message={error} />}
      {isLoading && <LoadingSpinner />}

      {/* Show sample image guide only when no file is selected and not analyzing */}
      {!selectedFile && !isLoading && !analysisResult && (
        <SampleImageGuide />
      )}

      {analysisResult && (
        <div className="mt-6 space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <RooftopSummary analysis={analysisResult.analysis} />
              <RooftopDetails rooftops={analysisResult.analysis.rooftops} />
            </div>

            <div>
              <h3 className="font-bold mb-2 text-blue-800">Rooftop Detection Visualization</h3>
              <img
                src={analysisResult.imageUrl}
                alt="Rooftop Detection Result"
                className="w-full rounded-lg shadow-md cursor-zoom-in hover:opacity-90 transition-opacity"
                onClick={handleImageClick}
              />
            </div>
          </div>

          <div>
            <h3 className="font-bold mb-2 text-blue-800">Detailed Report</h3>
            <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto max-h-64 overflow-y-auto">
              {analysisResult.report}
            </pre>
          </div>
        </div>
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