import { useState } from 'react'
import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <h1 className="text-3xl font-bold text-gray-900">
            StoryMind
          </h1>
          <p className="text-gray-600">AI-Powered Character Visualization</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 px-4">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-semibold mb-4">Welcome to StoryMind</h2>
          <p className="text-gray-700">
            Upload a book and generate consistent, text-accurate character visualizations.
          </p>
          <p className="text-sm text-gray-500 mt-4">
            Frontend setup complete. Install dependencies with: <code className="bg-gray-100 px-2 py-1 rounded">npm install</code>
          </p>
        </div>
      </main>
    </div>
  )
}

export default App
