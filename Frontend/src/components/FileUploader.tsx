import { Upload } from "lucide-react";
import React from "react";

// File Upload Component
const FileUploader = ({ onFileSelect, selectedFile }) => (
  <div className="mb-4 p-6 border border-blue-100 rounded-lg bg-blue-50">
    <div className="flex items-center gap-3 mb-4">
      <Upload size={24} className="text-blue-600" />
      <h3 className="text-lg font-semibold text-blue-800 ">Upload an Image</h3>
    </div>
    
    <input
      type="file"
      onChange={onFileSelect}
      accept="image/*"
      className="block w-full text-sm text-slate-500
        file:mr-4 file:py-2 file:px-4
        file:rounded-full file:border-0
        file:text-sm file:font-semibold
        file:bg-blue-100 file:text-blue-700
        hover:file:bg-blue-200"
    />
    {selectedFile && (
      <div className="mt-3 p-3 bg-white rounded-lg border border-blue-100">
        <p className="text-sm text-blue-700 font-medium">
          Selected file: {selectedFile.name}
        </p>
      </div>
    )}
  </div>
);

export default FileUploader;
