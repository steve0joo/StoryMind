import axios from 'axios';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      console.error('Network Error:', error.message);
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// API methods
export const searchBooks = async (query) => {
  // Backend doesn't have search endpoint - get all books and filter client-side
  const response = await apiClient.get('/books');
  const allBooks = response.data.books || [];

  if (!query || !query.trim()) {
    return { books: allBooks };
  }

  // Filter by title (case-insensitive)
  const queryLower = query.toLowerCase();
  const filtered = allBooks.filter(book =>
    book.title.toLowerCase().includes(queryLower)
  );

  return { books: filtered };
};

export const getBook = async (bookId) => {
  const response = await apiClient.get(`/books/${bookId}`);
  return response.data;
};

export const getBookCharacters = async (bookId) => {
  const response = await apiClient.get(`/books/${bookId}/characters`);
  return response.data;
};

// Global consistent style for all character images
const CONSISTENT_STYLE = 'realistic portrait, photorealistic, highly detailed, professional photography, studio lighting, neutral background';

export const generateImage = async (characterId, style, aspectRatio) => {
  const response = await apiClient.post(`/characters/${characterId}/generate-image`, {
    style: style || CONSISTENT_STYLE,
    aspect_ratio: aspectRatio || '1:1'
  });
  return response.data;
};

export const deleteBook = async (bookId) => {
  const response = await apiClient.delete(`/books/${bookId}`);
  return response.data;
};

export const uploadBook = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('/books/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 600000, // 10 minutes for book processing (analyzing entire book takes longer)
  });

  return response.data;
};

export default apiClient;
