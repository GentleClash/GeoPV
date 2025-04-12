import React from "react";

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

export default RooftopDetails;