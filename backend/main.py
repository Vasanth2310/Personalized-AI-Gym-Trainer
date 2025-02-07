import cv2
import numpy as np
import base64
import json
import os
import time
import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from uuid import uuid4
from exercise_analysis import feedback_and_count, process_image 

# IMPORTANT: Replace with a strong, randomly generated secret key in production!
SECRET_KEY = os.environ.get("SECRET_KEY") or "YOUR_VERY_STRONG_SECRET_KEY_HERE"  # Use env variable or replace
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

# Configure CORS (Adjust allow_origins for production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS = {}
# Use a database for users in a real application!  This is for demonstration only.
USERS = {}  # In-memory user storage (for demonstration ONLY - use a database in production)

DATA_FILE = "session_data.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)


def save_session_data(session_record):
    with open(DATA_FILE, "r+") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
        data.append(session_record)
        f.seek(0)
        json.dump(data, f, indent=2)


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
        if username is None or username not in USERS:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


class UserCreate(BaseModel):
    username: str
    password: str
    name: str  # Added name field


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


@app.post("/register")
def register(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        if USERS.get(form_data.username):
            raise HTTPException(status_code=400, detail="Username already exists")
        hashed_password = hash_password(form_data.password)
        USERS[form_data.username] = hashed_password
        print(f"User {form_data.username} registered.")
        return {"message": "User registered successfully"}
    except Exception as e:
        print(f"Error during registration: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = USERS.get(form_data.username)
    if not user or not verify_password(form_data.password, user):
        raise HTTPException(status_code=400, detail="Incorrect username or password")  # More specific message
    token = create_access_token({"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/start_session", response_model=StartSessionResponse)
def start_session(request: StartSessionRequest, username: str = Depends(get_current_user)):
    session_id = str(uuid4())
    counter = {"count": 0, "state": False, "stage": "down"}
    SESSIONS[session_id] = {
        "exercise": request.exercise,
        "start_time": time.time(),
        "counter": counter,
        "rep_history": []
    }
    return StartSessionResponse(session_id=session_id)

@app.post("/process_frame", response_model=ProcessFrameResponse)
async def process_frame(session_id: str, file: UploadFile = File(...), username: str = Depends(get_current_user)):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found.")
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image file.")
    frame, results = process_image(frame)
    counter = SESSIONS[session_id]["counter"]
    start_time = SESSIONS[session_id]["start_time"]
    exercise = SESSIONS[session_id]["exercise"]
    if results.pose_landmarks:
        landmarks = {i: lm for i, lm in enumerate(results.pose_landmarks.landmark)}
        feedback, rep_count, duration = feedback_and_count(exercise, landmarks, counter, start_time)
    else:
        feedback, rep_count, duration = (["No person detected."], counter["count"], time.time() - start_time)
    _, buffer = cv2.imencode('.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    processed_image_b64 = base64.b64encode(buffer).decode('utf-8')
    return ProcessFrameResponse(
        rep_count=counter["count"],
        duration=duration,
        feedback=feedback,
        processed_image=processed_image_b64
    )

@app.post("/stop_session")
def stop_session(request: StopSessionRequest, background_tasks: BackgroundTasks, username: str = Depends(get_current_user)):
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
        "rep_count": rep_count
    }
    background_tasks.add_task(save_session_data, session_record)
    return {"message": "Session ended and data saved.", "session_record": session_record}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)