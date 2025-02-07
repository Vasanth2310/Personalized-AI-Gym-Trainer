import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import HomeScreen from './components/HomeScreen';
import LoginScreen from './components/LoginScreen';
import CreateAccountScreen from './components/CreateAccountScreen';
import PricingScreen from './components/PricingScreen';
import Trainer from './components/Trainer';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false); // Track authentication

  useEffect(() => {
    // Check authentication status on mount (e.g., from localStorage)
    const token = localStorage.getItem('token'); // Or however you store your token
    setIsAuthenticated(!!token); // Set isAuthenticated based on token presence
  }, []);

  const handleLogin = (token) => {
    // Set authentication status and store the token (e.g., in localStorage)
    setIsAuthenticated(true);
    localStorage.setItem('token', token); // Or your preferred storage method
  };

  const handleLogout = () => {
    // Clear authentication status and remove the token
    setIsAuthenticated(false);
    localStorage.removeItem('token');
  };

  return (
    <Router>
      <div className="App">
        <main>
          <Routes>
            <Route path="/" element={<HomeScreen />} />
            <Route path="/login" element={<LoginScreen onLogin={handleLogin} />} /> {/* Pass handleLogin */}
            <Route path="/create-account" element={<CreateAccountScreen />} />
            <Route path="/pricing" element={<PricingScreen />} />
            {/* Protected route for Trainer */}
            <Route
              path="/trainer"
              element={isAuthenticated ? <Trainer onLogout={handleLogout} /> : <Navigate to="/login" />}
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;