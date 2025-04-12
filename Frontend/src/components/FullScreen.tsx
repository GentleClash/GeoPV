import React from "react";
import { X } from 'lucide-react';

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


export default FullScreenImageModal;