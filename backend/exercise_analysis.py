import numpy as np
import mediapipe as mp
import time
import logging
import pickle
from ultralytics import YOLO

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
print("Pose model loaded successfully:", pose)

#Loading Models
# Load model
with open("D://MediaTrix//AI based Fitness WebApp//mark_1//backend//Models//bicep//KNN_model.pkl", "rb") as f:
    bicep_model = pickle.load(f)
with open("D://MediaTrix//AI based Fitness WebApp//mark_1//backend//Models//plank//LR_model.pkl", "rb") as f:
    plank_model = pickle.load(f)
with open("D://MediaTrix//AI based Fitness WebApp//mark_1//backend//Models//pushup//RF_model.pkl", "rb") as f:
    pushup_model = pickle.load(f)
with open("D://MediaTrix//AI based Fitness WebApp//mark_1//backend//Models//squat//LR_model.pkl", "rb") as f:
    count_model = pickle.load(f)
pose_model = YOLO("D://MediaTrix//AI based Fitness WebApp//mark_1//backend//Models//Excercise_Model.pt")

def calculate_angle(p1, p2, p3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    
    angle = np.degrees(np.arctan2(y3 - y2, x3 - x2) - np.arctan2(y1 - y2, x1 - x2))
    return abs(angle) if abs(angle) < 180 else 360 - abs(angle)

def feedback_and_count(exercise, landmarks, counter, start_time):
    errors, duration = [], time.time() - start_time if exercise in ["Plank", "Wall Sit", "Side Bridges"] else 0
    if "stage" not in counter:
        counter["stage"] = "down"
    if "state" not in counter:
        counter["state"] = False
    
    if exercise == "Situps":
        hip_angle = calculate_angle(
            [landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y],
            [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y],
            [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y]
        )
        if hip_angle > 160 and not counter["state"]:
            counter["state"] = True
        if hip_angle < 100 and counter["state"]:
            counter["count"] += 1
            counter["state"] = False
        if hip_angle < 60:
            errors.append("Straighten your back.")

    if exercise == "Wall Sit":
        knee_angle = calculate_angle(
            [landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y],
            [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y],
            [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y]
        )
        if not (80 <= knee_angle <= 100):
            errors.append("Keep your knees at 90 degrees.")
    
    if exercise == "Crunches": 
        shoulder_angle = calculate_angle(
        [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y],
        [landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y],
        [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y]
        )
        if shoulder_angle > 160 and not counter["state"]:
            counter["state"] = True
        if shoulder_angle < 110 and counter["state"]:
            counter["count"] += 1
            counter["state"] = False
        if landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y > landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y:
            errors.append("Engage your core; do not rely on momentum.")

    if exercise == "Plank":
        # Extract relevant landmarks
        left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
        right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y]
        left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
        right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y]
        left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]
        right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y]

        shoulder_hip_angle_left = calculate_angle(left_shoulder, left_hip, left_ankle)
        shoulder_hip_angle_right = calculate_angle(right_shoulder, right_hip, right_ankle)
        hip_ankle_angle_left = calculate_angle(left_hip, left_ankle, right_ankle)
        hip_ankle_angle_right = calculate_angle(right_hip, right_ankle, left_ankle)

        if shoulder_hip_angle_left < 160 or shoulder_hip_angle_left > 180 or shoulder_hip_angle_right < 160 or shoulder_hip_angle_right > 180:
            errors.append("Keep your back straight; avoid sagging or arching.")
        elif hip_ankle_angle_left < 160 or hip_ankle_angle_left > 180 or hip_ankle_angle_right < 160 or hip_ankle_angle_right > 180:
            errors.append("Align your hips and ankles; avoid raising or lowering your hips.")
        else:
            errors.append("Good posture! Keep holding the plank.")
        
    if exercise == "Mountain Climber":
        knee_angle = calculate_angle(
        [landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y],
        [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y],
        [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y]
        )
        if knee_angle < 90 and not counter["state"]:
            counter["state"] = True
        if knee_angle > 150 and counter["state"]:
            counter["count"] += 1
            counter["state"] = False
        if landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y > landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y:
            errors.append("Keep your hips aligned; avoid letting them sag or rise too high.")

    elif exercise in ["Curls", "Shoulder Press", "Bench Press", "Skull Crushers", "Overhead Extensions", "Inclined Dumbell Press"]:
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y]
        angle = calculate_angle(shoulder, elbow, wrist)

        if exercise == "Curls":
            if angle < 90 and counter["stage"] == "down":
                counter["stage"] = "up"
                counter["count"] += 1
            elif angle > 160:
                counter["stage"] = "down"
            elif angle < 160 and angle > 90:
                errors.append("Maintain 90 degree elbow bend.")
        elif exercise == "Shoulder Press":
            if angle > 160:
                counter["stage"] = "down"
            if angle < 90 and counter["stage"] == "down":
                counter["stage"] = "up"
                counter["count"] += 1
            if counter["stage"] == "up" and (angle < 70 or angle > 110):
                errors.append("Keep your elbows in line with your shoulders.")
        elif exercise in ["Bench Press", "Skull Crushers", "Overhead Extensions", "Inclined Dumbell Press"]:
            if angle > 160:
                counter["stage"] = "down"
            if angle < 90 and counter["stage"] == "down":
                counter["stage"] = "up"
                counter["count"] += 1
            if exercise == "Bench Press" and angle > 160:
                errors.append("Control the movement, avoid locking elbows.")
            elif exercise == "Skull Crushers" and angle > 150:
                errors.append("Control the movement, avoid locking elbows.")
            elif exercise == "Overhead Extensions" and angle > 170:
                errors.append("Avoid overextending the arms.")
            elif exercise == "Inclined Dumbell Press" and angle > 160:
                errors.append("Keep your arms aligned, avoid locking elbows.")

    elif exercise == "Dips":
        elbow_angle = calculate_angle(
            [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y],
            [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y],
            [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y])
        if elbow_angle > 160 and not counter["state"]:
            counter["state"] = True
        if elbow_angle < 90 and counter["state"]:
            counter["count"] += 1
            counter["state"] = False
        if elbow_angle > 160:
            errors.append("Lower until elbows reach at least 90 degrees.")

    elif exercise == "Pushups":
        left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
        left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y]
        left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y]
        elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)

        if elbow_angle > 160 and not counter["state"]:
            counter["state"] = True
        if elbow_angle < 90 and counter["state"]:
            counter["count"] += 1
            counter["state"] = False
        if elbow_angle > 160:
            errors.append("Lower until elbows reach at least 90 degrees.")

    elif exercise == "Squats":
        left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
        left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y]
        left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]
        knee_angle = calculate_angle(left_hip, left_knee, left_ankle)

        if knee_angle < 90 and not counter["state"]:
            counter["state"] = True
        if knee_angle > 170 and counter["state"]:
            counter["count"] += 1
            counter["state"] = False
        if knee_angle < 90:
            errors.append("Go deeper, thighs parallel to the ground.")

    elif exercise == "Side Bridges":
        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
        knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y]
        ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]

        angle = calculate_angle(hip, knee, ankle)

        if angle < 150:
            errors.append("Raise your hips higher for proper alignment.")
        elif angle > 170:
            errors.append("Avoid hyperextending your back. Keep your body in a straight line.")

    return errors, counter["count"], duration