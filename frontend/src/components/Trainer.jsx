import React, { useState, useEffect, useRef } from 'react';
import './Trainer.css'; // Import your CSS file
import logo from '/assets/ai-trainer.png'; // Import your logo
import { useNavigate } from 'react-router-dom';

const Trainer = ({ onLogout }) => {
    const navigate = useNavigate();
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [selectedExercise, setSelectedExercise] = useState(null);
    const [isCameraActive, setIsCameraActive] = useState(false);
    const [reps, setReps] = useState(0);
    const [timeTaken, setTimeTaken] = useState(0);
    const [feedback, setFeedback] = useState([]);
    const [processedImage, setProcessedImage] = useState(null);
    const [sessionId, setSessionId] = useState(null);
    const videoRef = useRef(null);
    const [token, setToken] = useState(localStorage.getItem('token'));


    const exercises = {
        "Abs": ["Crunches", "Situps", "Plank", "Mountain Climber", "Side Bridges"],
        "Arms": ["Curls", "Bench Press", "Skull Crushers", "Overhead Extensions", "Shoulder Press"],
        "Chest": ["Pushups", "Inclined Dumbell Press"],
        "Legs": ["Squats", "Wall Sit", "Dips"]
    };

    useEffect(() => {
        if (!token) {
            navigate('/login'); // Redirect if no token
            return;
        }
    }, [token, navigate]);

    const handleLogoutClick = () => {
        onLogout();
        navigate('/login');
    };

    const toggleDropdown = () => {
        setIsDropdownOpen(!isDropdownOpen);
    };

    const handleExerciseSelect = (exercise) => {
        setSelectedExercise(exercise);
        setReps(0);
        setTimeTaken(0);
        setFeedback([]);
    };

    const handleCameraToggle = async () => {
        setIsCameraActive(!isCameraActive);

        if (!isCameraActive && selectedExercise) {
            try {
                const startResponse = await fetch('/start_session', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ exercise: selectedExercise }),
                });

                if (!startResponse.ok) {
                    const errorData = await startResponse.json();
                    throw new Error(errorData.detail || "Failed to start session");
                }

                const startData = await startResponse.json();
                setSessionId(startData.session_id);

                const constraints = { video: true };
                const stream = await navigator.mediaDevices.getUserMedia(constraints);
                videoRef.current.srcObject = stream;
                videoRef.current.onloadedmetadata = () => {
                    videoRef.current.play();
                    processVideo();
                };
            } catch (error) {
                console.error("Error starting session or camera:", error);
            }
        } else {
            try {
                if (sessionId) {
                    const stopResponse = await fetch('/stop_session', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({ session_id: sessionId }),
                    });

                    if (!stopResponse.ok) {
                        const errorData = await stopResponse.json();
                        throw new Error(errorData.detail || "Failed to stop session");
                    }
                }

                setSessionId(null);
                if (videoRef.current && videoRef.current.srcObject) {
                    videoRef.current.srcObject.getTracks().forEach(track => track.stop());
                    videoRef.current.srcObject = null;
                }
            } catch (error) {
                console.error("Error stopping session:", error);
            }
        }
    };

    const processVideo = async () => {
        if (!isCameraActive || !videoRef.current || !sessionId || !token) return;

        const canvas = document.createElement('canvas');
        canvas.width = videoRef.current.videoWidth;
        canvas.height = videoRef.current.videoHeight;
        canvas.getContext('2d').drawImage(videoRef.current, 0, 0);
        const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));

        const formData = new FormData();
        formData.append('file', blob, 'frame.jpg');
        formData.append('session_id', sessionId);

        try {
            const response = await fetch('/process_frame', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to process frame");
            }

            const data = await response.json();
            setReps(data.rep_count);
            setTimeTaken(data.duration);
            setFeedback(data.feedback);
            setProcessedImage(`data:image/jpeg;base64,${data.processed_image}`);
            processVideo();
        } catch (error) {
            console.error("Error processing frame:", error);
        }
    };

    return (
        <div className="trainer-container">
            <header className="trainer-header">
                <div className="trainer-logo-container">
                    <img src={logo} alt="FitAI Logo" className="trainer-logo" />
                </div>
                <div className="trainer-user-profile" onClick={toggleDropdown}>
                    <div className="profile-icon"></div>
                    {isDropdownOpen && (
                        <div className="dropdown-menu">
                            <a href="/profile">Profile</a>
                            <a href="/settings">Settings</a>
                            <button onClick={handleLogoutClick} className="logout-button">Logout</button> {/* Logout Button */}
                        </div>
                    )}
                </div>
            </header>

            <main className="trainer-main-content">
                <div className="trainer-webcam-area">
                    <video ref={videoRef} autoPlay muted className="webcam-feed" style={{ display: processedImage ? 'none' : 'block' }} />
                    {processedImage && <img src={processedImage} alt="Processed Frame" />}
                </div>

                <div className="trainer-controls">
                    <div className="exercise-selection">
                        {Object.keys(exercises).map(category => (
                            <div key={category}>
                                <h3>{category}</h3>
                                {exercises[category].map(exercise => (
                                    <button
                                        key={exercise}
                                        onClick={() => handleExerciseSelect(exercise)}
                                        className={selectedExercise === exercise ? 'selected' : ''}
                                    >
                                        {exercise}
                                    </button>
                                ))}
                            </div>
                        ))}
                    </div>

                    <button onClick={handleCameraToggle} disabled={!selectedExercise}>
                        {isCameraActive ? "Stop" : "Start"}
                    </button>

                    <div className="exercise-stats">
                        <p>Reps: {reps}</p>
                        <p>Time: {timeTaken}s</p>
                    </div>

                    <div className="feedback-area">
                        {feedback.map((f, index) => <p key={index}>{f}</p>)}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Trainer;