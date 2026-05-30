import { useState } from 'react';

export const ResumeUpload = () => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      setFile(files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    
    // Simulate upload
    setTimeout(() => {
      setUploading(false);
      alert('Resume uploaded successfully!');
    }, 2000);
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Your Resume</h1>
      <p className="text-gray-600 mb-8">
        Upload your resume to get personalized feedback and start your interview preparation
      </p>

      {/* Upload Area */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
          dragActive ? 'border-red-600 bg-red-50' : 'border-gray-300 bg-gray-50'
        }`}
      >
        <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>

        {!file ? (
          <>
            <h2 className="text-xl font-bold text-gray-900 mb-2">Drag and drop your resume</h2>
            <p className="text-gray-600 mb-4">or</p>
            <label className="cursor-pointer">
              <span className="px-6 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition inline-block">
                Browse Files
              </span>
              <input
                type="file"
                onChange={handleChange}
                accept=".pdf,.doc,.docx"
                className="hidden"
              />
            </label>
            <p className="text-sm text-gray-500 mt-4">Supported formats: PDF, DOC, DOCX (Max 10 MB)</p>
          </>
        ) : (
          <>
            <svg className="w-16 h-16 mx-auto mb-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-xl font-bold text-gray-900 mb-2">File Selected</h2>
            <p className="text-gray-600 mb-4">{file.name}</p>
            <button
              onClick={() => setFile(null)}
              className="text-red-600 hover:text-red-700 font-medium"
            >
              Choose Different File
            </button>
          </>
        )}
      </div>

      {/* Upload Button */}
      {file && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="w-full mt-6 py-3 bg-red-600 text-white font-bold rounded-lg hover:bg-red-700 disabled:opacity-50 transition"
        >
          {uploading ? 'Uploading...' : 'Upload Resume'}
        </button>
      )}
    </div>
  );
};
