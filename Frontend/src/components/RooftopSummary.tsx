import React from "react";

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

export default RooftopSummary;