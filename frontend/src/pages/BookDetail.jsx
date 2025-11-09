import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getBook, getBookCharacters, generateImage } from '../api/client';

function BookDetail() {
  const { bookId } = useParams();
  const navigate = useNavigate();
  const [book, setBook] = useState(null);
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generatingImages, setGeneratingImages] = useState({}); // Track which characters are generating
  const [imageErrors, setImageErrors] = useState({}); // Track image generation errors

  useEffect(() => {
    loadBookData();
  }, [bookId]);

  const loadBookData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch book and characters in parallel
      const [bookData, charactersData] = await Promise.all([
        getBook(bookId),
        getBookCharacters(bookId),
      ]);
      setBook(bookData);
      setCharacters(charactersData.characters || []);
    } catch (err) {
      console.error('Error loading book:', err);
      setError('Failed to load book details. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateImage = async (character, style = 'photorealistic portrait, detailed, high quality', aspectRatio = '1:1') => {
    const characterId = character.id;

    // Mark as generating
    setGeneratingImages(prev => ({ ...prev, [characterId]: true }));
    setImageErrors(prev => ({ ...prev, [characterId]: null }));

    try {
      const result = await generateImage(characterId, style, aspectRatio);

      // Update character with new image
      setCharacters(prev =>
        prev.map(char =>
          char.id === characterId
            ? { ...char, image_url: result.image_url, image_generated_at: new Date().toISOString() }
            : char
        )
      );
    } catch (err) {
      console.error('Error generating image:', err);
      const errorMsg = err.response?.data?.error || 'Failed to generate image. Please try again.';
      setImageErrors(prev => ({ ...prev, [characterId]: errorMsg }));
    } finally {
      setGeneratingImages(prev => ({ ...prev, [characterId]: false }));
    }
  };

  const handleDownloadImage = (imageUrl, characterName) => {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `${characterName.replace(/\s+/g, '_')}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center">
        <div className="flex flex-col items-center">
          <div className="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
          <p className="mt-4 text-gray-600">Loading book details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center px-4">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md text-center">
          <svg className="w-16 h-16 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p className="text-gray-800 font-semibold mb-4">{error}</p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={loadBookData}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Try Again
            </button>
            <button
              onClick={() => navigate('/search')}
              className="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Back to Search
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <button
            onClick={() => navigate('/search')}
            className="text-indigo-600 hover:text-indigo-700 font-semibold flex items-center gap-2 mb-4"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Search
          </button>

          {book && (
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">{book.title}</h1>
              <p className="text-xl text-gray-600 mb-3">{book.author}</p>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  <span>{characters.length} characters</span>
                </div>
                {book.uploaded_at && (
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span>Uploaded {new Date(book.uploaded_at).toLocaleDateString()}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Characters */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Characters</h2>

        {characters.length === 0 ? (
          <div className="bg-white rounded-xl shadow-md p-12 text-center border border-gray-200">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <p className="text-gray-600 text-lg">No characters found for this book</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {characters.map((character) => (
              <div key={character.id} className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
                <div className="p-6">
                  {/* Character Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-gray-900 mb-1">{character.name}</h3>
                      {character.role && (
                        <span className="inline-block px-3 py-1 bg-indigo-100 text-indigo-700 text-sm font-medium rounded-full">
                          {character.role}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Character Description */}
                  {character.canonical_description && (
                    <div className="mb-4">
                      <p className="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap">
                        {character.canonical_description}
                      </p>
                    </div>
                  )}

                  {/* Generated Image */}
                  {character.image_url && (
                    <div className="mb-4">
                      <img
                        src={character.image_url}
                        alt={character.name}
                        className="w-full rounded-lg shadow-md"
                      />
                      <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                        {character.image_generated_at && (
                          <span>Generated {new Date(character.image_generated_at).toLocaleString()}</span>
                        )}
                        <button
                          onClick={() => handleDownloadImage(character.image_url, character.name)}
                          className="text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                          </svg>
                          Download
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Generate Image Button */}
                  <div>
                    {generatingImages[character.id] ? (
                      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                        <div className="flex items-center gap-3">
                          <div className="w-5 h-5 border-2 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
                          <div className="flex-1">
                            <p className="text-indigo-900 font-medium">Generating image...</p>
                            <p className="text-indigo-700 text-sm">This may take 15-60 seconds</p>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <button
                        onClick={() => handleGenerateImage(character)}
                        className="w-full px-4 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-2"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        {character.image_url ? 'Regenerate Image' : 'Generate Image'}
                      </button>
                    )}

                    {/* Error Message */}
                    {imageErrors[character.id] && (
                      <div className="mt-2 bg-red-50 border border-red-200 rounded-lg p-3">
                        <p className="text-red-800 text-sm">{imageErrors[character.id]}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default BookDetail;
