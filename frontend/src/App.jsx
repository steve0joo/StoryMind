import './App.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import SearchResults from './pages/SearchResults'
import BookDetail from './pages/BookDetail'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/search" element={<SearchResults />} />
        <Route path="/book/:bookId" element={<BookDetail />} />
      </Routes>
    </Router>
  )
}

export default App
