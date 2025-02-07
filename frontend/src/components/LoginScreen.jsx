import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginScreen.css';

const LoginScreen = ({ onLogin }) => {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null); // Clear previous errors

        try {
            const response = await fetch('/login', { // Your backend login endpoint
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded', // Important for form data
                },
                body: `username=${email}&password=${password}`, // URL-encoded form data
            });

            if (response.ok) {
                const data = await response.json();
                onLogin(data.access_token); // Call onLogin with the received token
                navigate('/trainer'); // Redirect to trainer page
            } else {
                const errorData = await response.json();
                setError(errorData.detail || "Invalid email or password"); // Set error message
            }
        } catch (err) {
            console.error("Login Error:", err);
            setError("An error occurred during login. Please try again later.");
        }
    };

    return (
        <div className="login-container">
            <h2>Login</h2>
            {error && <p className="error-message">{error}</p>} {/* Display error message */}
            <form onSubmit={handleSubmit}>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <button type="submit">Login</button>
                <p>
                    Don't have an account? <a href="/create-account">Create Account</a>
                </p>
            </form>
        </div>
    );
};

export default LoginScreen;