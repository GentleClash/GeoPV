import React from "react";

// Error Display Component
const ErrorDisplay = ({ message }) => (
    <div className="mt-4 p-4 bg-red-100 text-red-800 rounded-lg border border-red-200">
        <div className="flex items-center gap-2">
            <div className="w-5 h-5 flex items-center justify-center rounded-full bg-red-200 text-red-800 font-bold text-xs">!</div>
            <p>{message}</p>
        </div>
    </div>
);

export default ErrorDisplay;