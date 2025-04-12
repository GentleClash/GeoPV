import React from "react";
// Loading Spinner Component
const LoadingSpinner = ({ message }) => (
    <div className="text-center py-6">
        <div className="animate-spin inline-block w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
        <p className="mt-2 text-blue-600">{message || 'Analyzing image...'}</p>
    </div>
);

export default LoadingSpinner;  