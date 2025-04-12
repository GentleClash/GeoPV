import React, { useState, useEffect } from 'react';
import axios from 'axios';
import FileUploader from './FileUploader';
import GoogleMapsButton from './GoogleMapsButton';
import SampleImageGuide from './SampleImageGuide';
import RooftopSummary from './RooftopSummary';
import RooftopDetails from './RooftopDetails';
import LoadingSpinner from './LoadingSpinner';
import JobProgress from './JobProgress';
import ErrorDisplay from './ErrorDisplay';
import OptionsSection from './OptionsSection';
import FullScreenImageModal from './FullScreen';



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
  const [imagePreview, setImagePreview] = useState(null);

  useEffect(() => {
    // Add event listener for messages from the map window
    const handleMessage = (event) => {
      // Check if the message is from our map window
      if (event.data && event.data.type === 'SATELLITE_IMAGE_CAPTURED') {
        // Create a file object from the image path
        fetch(event.data.imagePath)
          .then(response => response.blob())
          .then(blob => {
            const file = new File([blob], "satellite_capture.png", { type: "image/png" });
            setSelectedFile(file);
            setAnalysisResult(null);
            setError(null);
            setJobId(null);
            setJobStatus(null);
            // Optionally auto-start the analysis
            // handleUpload();
            const previewURL = URL.createObjectURL(blob);
            setImagePreview(previewURL);
          }
          )
          .catch(err => {
            console.error("Error fetching captured image:", err);
            setError("Failed to load captured image");
          });
      }
    };

    window.addEventListener("message", handleMessage);

    // Clean up the event listener on component unmount
    return () => {
      window.removeEventListener("message", handleMessage);
    };
  }, []);


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
        {imagePreview && (
          <div className="image-preview">
            <p>Preview:</p>
            <img src={imagePreview} alt="Satellite Preview" style={{ maxWidth: '100%', height: 'auto' }} />
          </div>
        )}

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