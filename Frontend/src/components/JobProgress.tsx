import React from "react";
import LoadingSpinner from "./LoadingSpinner";

// Job Progress Component
const JobProgress = ({ status, position }) => {
    let statusMessage = "Processing image...";

    if (position !== undefined) {
        if (position == null) {
            position = 0;
        }
        else {
            position += 1;
        }

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

export default JobProgress;