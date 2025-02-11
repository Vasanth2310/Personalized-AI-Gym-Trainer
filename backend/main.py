import cv2
import numpy as np
import base64
import json
import os
import time
import datetime
import mediapipe as mp
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from uuid import uuid4
from exercise_analysis import feedback_and_count

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Configuration (Best practice: use environment variables for sensitive info)
SECRET_KEY = os.environ.get("SECRET_KEY") or "YOUR_VERY_STRONG_SECRET_KEY_HERE"  # Replace with a strong secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATA_FILE = "session_data.json"

origins = [
    "http://localhost:5173"  # Replace with your frontend URL
]

def process_image(frame_bgr):
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    frame_with_landmarks_bgr = frame_bgr.copy()
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame_with_landmarks_bgr, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
        )
    return frame_with_landmarks_bgr, results

# Initialize FastAPI app
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Adjust as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Data structures (replace with database in production)
SESSIONS = {}
USERS = {}

# Load session data from file
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        try:
            session_data = json.load(f)
        except json.JSONDecodeError:
            session_data = []  # Handle empty or corrupted JSON file
else:
    session_data = []


# Helper functions

def save_session_data(session_record):
    session_data.append(session_record)  # Append the new record
    with open(DATA_FILE, "w") as f:
        json.dump(session_data, f, indent=2)  # Save all data, not just append


def hash_password(password: str):
    return password_context.hash(password)


def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username not in USERS:
            raise HTTPException(status_code=401, detail="Invalid token or user not found")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid")


# Pydantic models (for data validation)

class UserCreate(BaseModel):
    username: str
    password: str
    name: str

class UserLogin(BaseModel):
    username: str
    password: str

class StartSessionRequest(BaseModel):
    exercise: str

class StartSessionResponse(BaseModel):
    session_id: str

class StopSessionRequest(BaseModel):
    session_id: str

class ProcessFrameResponse(BaseModel):
    rep_count: int
    duration: float
    feedback: list
    processed_image: str


# API endpoints

@app.post("/register")
def register_user(user: UserCreate):
    if user.username in USERS:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = hash_password(user.password)
    USERS[user.username] = hashed_password
    return {"message": "User registered successfully"}

@app.post("/login")
def login_user(user: UserLogin):
    stored_password = USERS.get(user.username)
    if not stored_password or not verify_password(user.password, stored_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/start_session", response_model=StartSessionResponse)
def start_exercise_session(request: StartSessionRequest, username: str = Depends(get_current_user)):
    session_id = str(uuid4())
    SESSIONS[session_id] = {
        "exercise": request.exercise,
        "start_time": time.time(),
        "counter": {"count": 0, "state": False, "stage": "down"},
        "rep_history": [],  # Initialize rep history
        "user": username  # Store the username with the session
    }
    return StartSessionResponse(session_id=session_id)

@app.post("/process_frame", response_model=ProcessFrameResponse)
async def process_exercise_frame(session_id: str, file: UploadFile = File(...), username: str = Depends(get_current_user)):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found.")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame_bgr is None:
        print("❌ Decoding Error. Check image format or transmission.")
        print(f"Numpy array type: {type(nparr)}")
        print(f"Numpy array shape: {nparr.shape}")
        raise HTTPException(status_code=400, detail="Decoding failed. Check image format or transmission.")

    print(f"✅ Decoded frame shape: {frame_bgr.shape}")

    counter = SESSIONS[session_id]["counter"]
    start_time = SESSIONS[session_id]["start_time"]
    exercise = SESSIONS[session_id]["exercise"]

    frame_with_landmarks, results = process_image(frame_bgr)

    if results.pose_landmarks:
        print("✅ Landmarks Detected!")
        landmarks = {i: lm for i, lm in enumerate(results.pose_landmarks.landmark)}
        feedback, rep_count, duration = feedback_and_count(exercise, landmarks, counter, start_time)

        SESSIONS[session_id]["rep_history"].append({
            "timestamp": datetime.datetime.now().isoformat(),
            "exercise": exercise,
            "rep_count": rep_count,
            "feedback": feedback,
        })
    else:
        print("❌ No Landmarks Detected!")
        print(results)
        feedback = ["No person detected. Ensure you are within the camera's view."]
        rep_count = counter["count"]
        duration = time.time() - start_time
        frame_with_landmarks = frame_bgr  # Return original frame

    success, buffer = cv2.imencode('.jpg', frame_with_landmarks)
    if not success:
        raise HTTPException(status_code=500, detail="❌ Encoding failed.")

    processed_image_b64 = base64.b64encode(buffer).decode('utf-8')

    return ProcessFrameResponse(
        rep_count=counter["count"],
        duration=duration,
        feedback=feedback,
        processed_image=processed_image_b64
    )

@app.post("/stop_session")
def stop_exercise_session(request: StopSessionRequest, background_tasks: BackgroundTasks, username: str = Depends(get_current_user)):
    if request.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found.")

    session_data = SESSIONS.pop(request.session_id)
    end_time = time.time()
    duration = end_time - session_data["start_time"]
    rep_count = session_data["counter"]["count"]

    session_record = {
        "session_id": request.session_id,
        "exercise": session_data["exercise"],
        "timestamp": datetime.datetime.now().isoformat(),
        "duration": duration,
        "rep_count": rep_count,
        "rep_history": session_data["rep_history"],
        "user": session_data["user"] # Include the username
    }

    background_tasks.add_task(save_session_data, session_record)
    return {"message": "Session ended and data saved.", "session_record": session_record}

@app.get("/exercise_data")  # New endpoint for data retrieval
def get_exercise_data(session_id: str, time_period: str, username: str = Depends(get_current_user)):
    print(f"Received session_id: {session_id}")
    if session_id not in SESSIONS:
        # Check if the user has access to the session data
        all_session_data = []
        with open(DATA_FILE, "r") as f:
            try:
                all_session_data = json.load(f)
            except json.JSONDecodeError:
                pass #Handle empty or corrupted JSON file
                
        user_has_access = False
        for session in all_session_data:
            if session.get("session_id") == session_id and session.get("user") == username:
                user_has_access = True
                break

        if not user_has_access:
            raise HTTPException(status_code=404, detail="Session not found or you don't have access.")
    else:
        if SESSIONS[session_id]["user"] != username:
            raise HTTPException(status_code=403, detail="You do not have access to this session.")


    rep_history = SESSIONS.get(session_id, {}).get("rep_history", []) if session_id in SESSIONS else []

    if time_period == "daily":
        data = aggregate_data(rep_history, "day")
    elif time_period == "weekly":
        data = aggregate_data(rep_history, "week")
    else:
        raise HTTPException(status_code=400, detail="Invalid time period.")

    return data

def aggregate_data(rep_history, time_unit):
    aggregated_data = {}
    for entry in rep_history:
        timestamp = datetime.datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00")) #Handle timezone
        if time_unit == "day":
            date_str = timestamp.strftime("%Y-%m-%d")
        elif time_unit == "week":
            date_str = timestamp.strftime("%Y-%W")  # Year and week number
        else:
            continue

        if date_str not in aggregated_data:
            aggregated_data[date_str] = {"rep_count": 0, "date": timestamp.strftime("%Y-%m-%d") if time_unit == "day" else get_week_start_date(timestamp).strftime("%Y-%m-%d")}
        aggregated_data[date_str]["rep_count"] += entry["rep_count"]

    return list(aggregated_data.values())

def get_week_start_date(date):
    return date - datetime.timedelta(days=date.weekday())


# ... (API endpoints remain the same)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)