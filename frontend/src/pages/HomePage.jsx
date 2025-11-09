import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, BookOpen, Sparkles, Upload } from 'lucide-react';
import { uploadBook } from '../api/client';

function HomePage() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    } else {
      navigate('/search');
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadError(null);

    try {
      const result = await uploadBook(file);
      // Navigate to the book detail page after successful upload
      navigate(`/book/${result.book_id}`);
    } catch (err) {
      console.error('Upload error:', err);

      // Determine specific error message
      let errorMessage = 'Failed to upload book. Please try again.';

      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        errorMessage = 'Upload timed out. The file might be too large or the server is not responding.';
      } else if (err.code === 'ERR_NETWORK' || err.message?.includes('Network Error')) {
        errorMessage = 'Cannot connect to server. Make sure the backend is running on http://localhost:5001';
      } else if (err.response) {
        // Server responded with error
        errorMessage = err.response.data?.message || err.response.data?.error || `Server error: ${err.response.status}`;
      }

      setUploadError(errorMessage);
    } finally {
      setUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Decorative background elements - Books pattern */}
        <div className="absolute inset-0 overflow-hidden opacity-40">
          {/* Book shapes scattered in background */}
          <div className="absolute top-20 left-10 w-32 h-40 bg-gradient-to-br from-indigo-400 to-indigo-600 rounded-r-lg transform rotate-12 blur-sm"></div>
          <div className="absolute top-40 right-20 w-24 h-36 bg-gradient-to-br from-purple-400 to-purple-600 rounded-r-lg transform -rotate-6 blur-sm"></div>
          <div className="absolute bottom-32 left-1/4 w-28 h-42 bg-gradient-to-br from-pink-400 to-pink-600 rounded-r-lg transform rotate-[-15deg] blur-sm"></div>
          <div className="absolute top-1/3 right-1/3 w-20 h-32 bg-gradient-to-br from-blue-400 to-blue-600 rounded-r-lg transform rotate-45 blur-sm"></div>
          <div className="absolute bottom-20 right-1/4 w-26 h-38 bg-gradient-to-br from-violet-400 to-violet-600 rounded-r-lg transform -rotate-12 blur-sm"></div>
          <div className="absolute top-60 left-1/3 w-22 h-34 bg-gradient-to-br from-fuchsia-400 to-fuchsia-600 rounded-r-lg transform rotate-20 blur-sm"></div>

          {/* Book spines */}
          <div className="absolute top-10 right-10 w-6 h-40 bg-gradient-to-b from-amber-500 to-amber-700 rounded-sm transform rotate-3 blur-[2px]"></div>
          <div className="absolute bottom-40 left-20 w-5 h-36 bg-gradient-to-b from-emerald-500 to-emerald-700 rounded-sm transform -rotate-6 blur-[2px]"></div>
          <div className="absolute top-1/2 right-1/4 w-6 h-42 bg-gradient-to-b from-rose-500 to-rose-700 rounded-sm transform rotate-[-8deg] blur-[2px]"></div>
          <div className="absolute bottom-10 right-40 w-5 h-38 bg-gradient-to-b from-cyan-500 to-cyan-700 rounded-sm transform rotate-12 blur-[2px]"></div>

          {/* Floating pages/papers */}
          <div className="absolute top-32 left-1/2 w-16 h-20 bg-white/60 rounded transform rotate-[-25deg] blur-[3px] shadow-lg"></div>
          <div className="absolute bottom-1/3 right-1/3 w-14 h-18 bg-white/50 rounded transform rotate-15 blur-[3px] shadow-lg"></div>
          <div className="absolute top-2/3 left-1/4 w-12 h-16 bg-white/55 rounded transform rotate-30 blur-[3px] shadow-lg"></div>

          {/* Animated blob overlays for depth */}
          <div className="absolute -top-40 -right-40 w-96 h-96 bg-purple-300/30 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
          <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-indigo-300/30 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
          <div className="absolute top-40 left-40 w-96 h-96 bg-pink-300/30 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-4000"></div>
        </div>

        {/* Content */}
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24">
          {/* Header */}
          <div className="text-center mb-16">
            <div className="flex items-center justify-center mb-6">
              <div className="relative">
                <BookOpen className="w-16 h-16 text-indigo-600" />
                <Sparkles className="w-8 h-8 text-purple-500 absolute -top-2 -right-2 animate-pulse" />
              </div>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 tracking-tight">
              Story<span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Mind</span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto mb-4">
              AI-Powered Character Visualization from Literary Works
            </p>

            <p className="text-md text-gray-500 max-w-2xl mx-auto">
              Transform your favorite book characters into consistent, text-accurate visual representations using advanced AI technology
            </p>
          </div>

          {/* Search Bar */}
          <div className="max-w-3xl mx-auto mb-12">
            <form onSubmit={handleSearch}>
              <div className={`relative transition-all duration-300 ${isSearchFocused ? 'transform scale-105' : ''}`}>
                <div className={`absolute inset-0 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl blur-lg opacity-0 transition-opacity duration-300 ${isSearchFocused ? 'opacity-30' : ''}`}></div>

                <div className="relative bg-white rounded-2xl shadow-2xl overflow-hidden">
                  <div className="flex items-center px-6 py-5">
                    <Search className={`w-6 h-6 mr-4 transition-colors duration-300 ${isSearchFocused ? 'text-indigo-600' : 'text-gray-400'}`} />

                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onFocus={() => setIsSearchFocused(true)}
                      onBlur={() => setIsSearchFocused(false)}
                      placeholder="Search for a book title..."
                      className="flex-1 text-lg outline-none text-gray-900 placeholder-gray-400"
                    />

                    <button
                      type="submit"
                      className="ml-4 px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                    >
                      Search
                    </button>
                  </div>
                </div>
              </div>
            </form>

            {/* Upload Button */}
            <div className="mt-6 flex justify-end">
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.epub,.txt"
                onChange={handleFileChange}
                className="hidden"
              />
              <button
                onClick={handleUploadClick}
                disabled={uploading}
                className="px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-xl hover:from-purple-700 hover:to-pink-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {uploading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="w-5 h-5" />
                    Upload Book
                  </>
                )}
              </button>
            </div>

            {/* Upload Error Message */}
            {uploadError && (
              <div className="mt-4 bg-red-50 border border-red-200 rounded-xl p-4">
                <p className="text-red-800 text-sm">{uploadError}</p>
              </div>
            )}
          </div>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto mt-20">
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-shadow duration-300">
              <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Text-Accurate</h3>
              <p className="text-gray-600">
                Characters are visualized based on precise descriptions from the original text
              </p>
            </div>

            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-shadow duration-300">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Consistent Design</h3>
              <p className="text-gray-600">
                Same character, same appearance every time with deterministic generation
              </p>
            </div>

            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-shadow duration-300">
              <div className="w-12 h-12 bg-pink-100 rounded-xl flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-pink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">AI-Powered</h3>
              <p className="text-gray-600">
                Powered by Gemini 2.0 & Imagen 3 for high-fidelity generation
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
