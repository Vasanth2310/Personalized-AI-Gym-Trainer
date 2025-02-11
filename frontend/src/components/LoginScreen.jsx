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
            const response = await fetch('http://localhost:8000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username: email, password }),
            });

            if (response.ok) {
                const text = await response.text();
                const data = text ? JSON.parse(text) : {};

                if (data.access_token) {
                    localStorage.setItem('token', data.access_token);
                    onLogin(data.access_token);
                    navigate('/trainer');
                } else {
                    setError("Login successful, but no token received.");
                }
            } else {
                const errorText = await response.text();
                try {
                    const errorData = JSON.parse(errorText);

                    // *** KEY CHANGE HERE ***
                    const errorMessage = typeof errorData.detail === 'string' ? 
                                          errorData.detail : // Use detail if it's a string
                                          (errorData.detail?.message || errorData.detail?.msg || errorData.detail?.detail || "Invalid email or password"); // Fallback, including detail

                    setError(errorMessage);

                } catch (parseError) {  // Catch JSON parsing errors
                    setError(errorText || "Invalid email or password");
                }
            }
        } catch (err) {
            console.error("Login Error:", err);
            setError("An error occurred during login. Please try again later.");
        }
    };

    return (
        <div className="login-container">
            <h2>Login</h2>
            {error && <p className="error-message">{error}</p>}
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