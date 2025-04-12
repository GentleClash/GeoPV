import React from "react";
import sampleImage from '../assets/sample.png';

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

export default SampleImageGuide;