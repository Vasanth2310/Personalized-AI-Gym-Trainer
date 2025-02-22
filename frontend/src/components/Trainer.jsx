import React, { useState, useEffect, useRef, useCallback } from 'react'; 
import './Trainer.css';
import logo from '/assets/ai-trainer.png';
import { useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS } from 'chart.js/auto';

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
    const [stream, setStream] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [error, setError] = useState(null);
    const [dailyData, setDailyData] = useState(null);
    const [weeklyData, setWeeklyData] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const processVideoTimeoutRef = useRef(null);
    //const processingIntervalRef = useRef(null);

    const exercises = {
        "Abs": ["Crunches", "Situps", "Plank", "Mountain Climber", "Side Bridges"],
        "Arms": ["Curls", "Bench Press", "Skull Crushers", "Overhead Extensions", "Shoulder Press"],
        "Chest": ["Pushups", "Inclined Dumbell Press"],
        "Legs": ["Squats", "Wall Sit", "Dips"]
    };

    const refreshAccessToken = useCallback(async () => {
        try {
            const refreshResponse = await fetch('YOUR_REFRESH_TOKEN_ENDPOINT', { // Replace with your actual endpoint
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` // Assuming you send the current token in the refresh request
                },
                // Include any necessary data for token refresh (e.g., refresh token)
                body: JSON.stringify({ refresh_token: localStorage.getItem('refreshToken') }) // Example
            });

            if (!refreshResponse.ok) {
                console.error("Token refresh failed:", refreshResponse.status);
                localStorage.removeItem('token'); // Clear invalid token
                setToken(null);
                navigate('/login'); // Redirect to login
                return false; // Indicate refresh failure
            }

            const data = await refreshResponse.json();
            localStorage.setItem('token', data.access_token);
            setToken(data.access_token);
            return true; // Indicate refresh success

        } catch (error) {
            console.error("Error refreshing token:", error);
            localStorage.removeItem('token');
            setToken(null);
            navigate('/login');
            return false;
        }
    }, [navigate, token]);

    useEffect(() => {
        if (!token) {
            navigate('/login');
            return;
        }

        // Get sessionId from localStorage *after* token is verified
        const storedSessionId = localStorage.getItem('sessionId');
        if (storedSessionId) {
            setSessionId(storedSessionId);
        }

    }, [token, navigate]);

    const fetchExerciseData = useCallback(async (timePeriod) => {
        if (!sessionId) {
            console.error("Session ID is not available. Cannot fetch data.");
            return;
        }

        const url = `http://localhost:8000/exercise_data?session_id=${sessionId}&time_period=${timePeriod}`;

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Failed to fetch ${timePeriod} data: ${response.status} - ${errorText}`);
            }

            const data = await response.json();
            if (timePeriod === 'daily') {
                setDailyData(formatChartData(data));
            } else if (timePeriod === 'weekly') {
                setWeeklyData(formatChartData(data));
            }
        } catch (error) {
            console.error(`Error fetching ${timePeriod} data:`, error);
            setError(error.message);// Set the error message
        }
    }, [sessionId, token]);

    const formatChartData = (data) => {
        if (!data || data.length === 0) { // Check for undefined as well
            return null;
        }

        const labels = data.map(item => item.date || item.day); // Directly use the date
        const repCounts = data.map(item => item.rep_count);

        return {
            labels,
            datasets: [
                {
                    label: 'Reps',
                    data: repCounts,
                    fill: false,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.4,
                },
            ],
        };
    };

    const handleLogoutClick = () => {
        onLogout();
        navigate('/login');
    };

    const toggleDropdown = () => {
        setIsDropdownOpen(!isDropdownOpen);
    };

    const processVideo = useCallback(async () => {
        console.log("processVideo() called!");
        if (!isCameraActive || !videoRef.current || !sessionId || !token || isProcessing || !stream) {
            return;
        }

        if (videoRef.current.videoWidth === 0 || videoRef.current.videoHeight === 0) {
            console.log("Video dimensions not available yet. Retrying...");
            //setTimeout(processVideo, 500);
            return;
        }

        setIsProcessing(true);

        const canvas = document.createElement('canvas');
        canvas.width = videoRef.current.videoWidth;
        canvas.height = videoRef.current.videoHeight;
        canvas.getContext('2d').drawImage(videoRef.current, 0, 0);

        const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));

        const formData = new FormData();
        formData.append('file', blob, 'frame.jpg');
        formData.append('session_id', sessionId);

        try {
            const url = `http://localhost:8000/process_frame?session_id=${sessionId}`;

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData,
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error("Server Error:", response.status, errorText);
                throw new Error(`Failed to process frame: ${response.status} - ${errorText}`);
            }

            const data = await response.json();
            console.log("📸 API Response:", data);
            setReps(data.rep_count);
            setTimeTaken(data.duration);
            setFeedback(Array.isArray(data.feedback) ? data.feedback : ["Unexpected feedback format"]);
            setProcessedImage(`data:image/jpeg;base64,${data.processed_image}`);

            if (sessionId && data.rep_count) {
                fetchExerciseData('daily');
                fetchExerciseData('weekly');
            }

        } catch (error) {
            console.error("Error processing frame:", error);
            setError(error.message);
        } finally {
            setIsProcessing(false);
        }
    }, [isCameraActive, sessionId, token, isProcessing, stream, fetchExerciseData]);

    useEffect(() => {
        let currentVideoRef = videoRef.current;

        const startCameraAndProcess = async () => {
            if (isCameraActive && selectedExercise && currentVideoRef && !currentVideoRef.srcObject && sessionId && !stream) {
                try {
                    const constraints = { video: true };
                    const newStream = await navigator.mediaDevices.getUserMedia(constraints);
                    currentVideoRef.srcObject = newStream;
                    setStream(newStream);

                    processVideoTimeoutRef.current = setTimeout(processVideo, 1000);

                } catch (error) {
                    console.error("Error starting camera:", error);
                    setError(error.message);
                    setIsCameraActive(false);
                    if (currentVideoRef && currentVideoRef.srcObject) {
                        currentVideoRef.srcObject.getTracks().forEach(track => track.stop());
                        currentVideoRef.srcObject = null;
                    }
                }
            } else if (!isCameraActive && stream) {
                const tracks = stream.getTracks();
                tracks.forEach(track => track.stop());
                currentVideoRef.srcObject = null;
                setStream(null);
                setIsProcessing(false);
                clearTimeout(processVideoTimeoutRef.current);
                //clearInterval(processingIntervalRef.current);
            } else if (isCameraActive && selectedExercise && currentVideoRef && sessionId && stream && !isProcessing) {
                processVideoTimeoutRef.current = setTimeout(processVideo, 1000);
            }
        };

        startCameraAndProcess();

        return () => {
            if (stream) {
                const tracks = stream.getTracks();
                tracks.forEach(track => track.stop());
                currentVideoRef.srcObject = null;
                setStream(null);
                setIsProcessing(false);
                clearTimeout(processVideoTimeoutRef.current);
                //clearInterval(processingIntervalRef.current);
            }
        };
    }, [isCameraActive, selectedExercise, sessionId, processVideo, stream, isProcessing]);

    const handleCameraToggle = useCallback(async () => {
        setIsCameraActive(prevIsCameraActive => !prevIsCameraActive);
        setError(null);

        if (!isCameraActive && selectedExercise && !sessionId) {
            try {
                const startResponse = await fetch('http://localhost:8000/start_session', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ exercise: selectedExercise }),
                });

                if (startResponse.status === 401) {
                    const refreshed = await refreshAccessToken();
                    if (refreshed) {
                        return handleCameraToggle();
                    } else {
                        return;
                    }
                } else if (!startResponse.ok) {
                    const errorText = await startResponse.text();
                    console.error("Server Error:", startResponse.status, errorText);
                    throw new Error(`Failed to start session: ${startResponse.status} - ${errorText}`);
                }
    
                const startData = await startResponse.json();
                setSessionId(startData.session_id);
                localStorage.setItem('sessionId', startData.session_id);
                //processVideo();              
    
            } catch (error) {
                console.error("Error starting session or camera:", error);
                setError(error.message);
                setIsCameraActive(false);
                if (videoRef.current && videoRef.current.srcObject) {
                    videoRef.current.srcObject.getTracks().forEach(track => track.stop());
                    videoRef.current.srcObject = null;
                }
            }
        } else if (!isCameraActive && selectedExercise && sessionId) {
            processVideo();
        } else if (isCameraActive) { // Just stop video processing, don't stop the session.
            if (videoRef.current && videoRef.current.srcObject) {
                videoRef.current.srcObject.getTracks().forEach(track => track.stop());
                videoRef.current.srcObject = null;
            }
        }
    }, [selectedExercise, sessionId, token, isCameraActive, processVideo, refreshAccessToken]);


    const handleExerciseSelect = (exercise) => {
        setSelectedExercise(exercise);
        setSessionId(null);
        localStorage.removeItem('sessionId');
        setReps(0);
        setTimeTaken(0);
        setFeedback([]);
        setError(null);
        setDailyData(null);
        setWeeklyData(null);
        setIsCameraActive(false);
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            videoRef.current.srcObject = null;
            setStream(null);
        }
    };

    return (
        <div className="trainer-container">
            <div className="trainer-header">
                <div className="trainer-logo-container">
                    <img src={logo} alt="AI Trainer Logo" className="trainer-logo" />
                </div>
                <div className="trainer-user-profile" onClick={toggleDropdown}>
                    <div className="profile-icon"></div>
                    {isDropdownOpen && (
                        <div className="dropdown-menu">
                            <button onClick={handleLogoutClick} className="logout-button">Logout</button>
                        </div>
                    )}
                </div>
            </div>
            <div className="trainer-main-content">
                <div className="trainer-webcam-area">
                    <video className="webcam-feed" ref={videoRef} autoPlay muted></video>
                    {processedImage && <img src={processedImage} alt="Processed Frame" className="processed-image" />}
                </div>
                <div className="trainer-controls">
                    <div className="exercise-selection">
                        <h3>Select Exercise</h3>
                        {Object.keys(exercises).map(category => (
                            <div key={category}>
                                <h4>{category}</h4>
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
                        {isCameraActive ? 'Stop' : 'Start'}
                    </button>
                    <div className="exercise-stats">
                        <p>Reps: {reps}</p>
                        <p>Time Taken: {timeTaken} seconds</p>
                    </div>
                </div>
            </div>
            <div className="feedback-area">
                <div className="feedback-card">
                    <h3>Feedback</h3>
                    {feedback.map((f, index) => <p key={index}>{f}</p>)}
                    {error && <p className="error-message">{error}</p>}
                </div>
                <div className="chart-area">
                    {dailyData && (
                        <div className="chart-container">
                            <h3>Daily Exercise Analysis</h3>
                            <Line data={dailyData} />
                        </div>
                    )}

                    {weeklyData && (
                        <div className="chart-container">
                            <h3>Weekly Exercise Analysis</h3>
                            <Line data={weeklyData} />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

Trainer.propTypes = {
    onLogout: PropTypes.func.isRequired,
};

export default Trainer;