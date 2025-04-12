import React from "react";

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

export default OptionsSection;