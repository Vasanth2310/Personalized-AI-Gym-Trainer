import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';  // Import useNavigate
import './CreateAccountScreen.css';

const CreateAccountScreen = () => {
    const navigate = useNavigate(); // Initialize useNavigate
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null); // State for error messages
    const [successMessage, setSuccessMessage] = useState(null); // State for success message

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null); // Clear previous errors
        setSuccessMessage(null); // Clear previous success messages

        try {
            const response = await fetch('/register', { // Your backend registration endpoint
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: email, // Assuming email is used as username
                    password: password,
                    // Add other fields if needed (e.g., name)
                }),
            });

            if (response.ok) {
                const data = await response.json();
                setSuccessMessage(data.message || "Account created successfully!");
                // Optionally redirect after successful registration:
                setTimeout(() => navigate('/login'), 2000); // Redirect after 2 seconds
            } else {
                const errorData = await response.json();
                setError(errorData.detail || "Error creating account. Please try again.");
            }
        } catch (err) {
            console.error("Registration Error:", err);
            setError("An error occurred during registration. Please try again later.");
        }
    };

    return (
        <div className="create-account-container">
            <h2>Create Account</h2>
            {error && <p className="error-message">{error}</p>} {/* Display error message */}
            {successMessage && <p className="success-message">{successMessage}</p>} {/* Display success message */}
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                />
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
                <button type="submit">Create Account</button>
                <p>Already have an account? <a href="/login">Login</a></p>
            </form>
        </div>
    );
};

export default CreateAccountScreen;