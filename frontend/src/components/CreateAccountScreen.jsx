import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';  // Use Link for navigation
import './CreateAccountScreen.css';

const CreateAccountScreen = () => {
    const navigate = useNavigate(); 
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccessMessage(null);

        try {
            const response = await fetch('http://localhost:8000/register', { // Adjust URL as needed
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: email,  // Email used as username
                    password: password,
                    name: name  // Include the missing name field
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccessMessage(data.message || "Account created successfully!");
                setTimeout(() => navigate('/login'), 2000);
            } else {
                setError(data.detail || "Error creating account. Please try again.");
            }
        } catch (err) {
            console.error("Registration Error:", err);
            setError("An unexpected error occurred. Please try again later.");
        }
    };

    return (
        <div className="create-account-container">
            <h2>Create Account</h2>
            {error && <p className="error-message">{error}</p>}
            {successMessage && <p className="success-message">{successMessage}</p>}
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
                <p>Already have an account? <Link to="/login">Login</Link></p> 
            </form>
        </div>
    );
};

export default CreateAccountScreen;
