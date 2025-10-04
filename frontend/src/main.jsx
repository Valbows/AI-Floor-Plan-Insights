import React from 'react'
import ReactDOM from 'react-dom/client'
import axios from 'axios'
import App from './App'
import './index.css'

// Configure axios baseURL for backend API
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:5000'
axios.defaults.headers.common['Content-Type'] = 'application/json'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
