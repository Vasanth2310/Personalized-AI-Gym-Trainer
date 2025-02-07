import cv2
import numpy as np
import mediapipe as mp
import time

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

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

    if exercise == "Plank":
        shoulder_hip_angle = calculate_angle(
            [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y],
            [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y],
            [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]
        )
        if not (160 <= shoulder_hip_angle <= 180):
                errors.append("Keep your back straight; avoid sagging or arching.")

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

    if exercise == "Plank":
        # Extract relevant landmarks
        left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
        right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y]
        left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
        right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y]
        left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]
        right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y]

        # Calculate angles
        shoulder_hip_angle = calculate_angle(left_shoulder, left_hip, left_ankle)
        hip_ankle_angle = calculate_angle(left_hip, left_ankle, right_ankle)

        # Provide feedback
        if shoulder_hip_angle < 160 or shoulder_hip_angle > 180:
            errors.append("Keep your back straight; avoid sagging or arching.")
        elif hip_ankle_angle < 160 or hip_ankle_angle > 180:
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


    if exercise == "Curls":
        # Get coordinates
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

        # Calculate angle
        angle = calculate_angle(shoulder, elbow, wrist)

        # Check posture
        if angle < 90:
            if counter["stage"] == "down":
               counter["stage"] = "up"
               counter["count"] += 1
        elif angle > 160:
            counter["stage"] = "down"
        else:
            errors.append("Keep your elbows at 90 degrees.")

    if exercise == "Shoulder Press":
        # Get coordinates
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

        # Calculate angle
        angle = calculate_angle(shoulder, elbow, wrist)

        # Check posture
        if angle > 160:
            counter["stage"] = "down"
        if angle < 90 and counter["stage"] == "down":
            counter["stage"] = "up"
            counter["count"] += 1
        if counter["stage"] == "up" and (angle < 70 or angle > 110):
            errors.append("Keep your elbows in line with your shoulders.")

    if exercise == "Dips":
        elbow_angle = calculate_angle(
        [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y],
        [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y],
        [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y])
        if elbow_angle > 160 and not counter["state"]:
            counter["state"] = True
        if elbow_angle < 90 and counter["state"]:
            counter["count"] += 1
            counter["state"] = False
    
    if exercise == "Pushups":
        left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
        left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y]
        left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y]

        # Calculate angle
        elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)

        # Provide feedback
        if elbow_angle > 160:
            errors.append("Keep your elbows at 90 degrees.")
        else:
            errors.append("Good push-up posture!")

    if exercise == "Squats":
        # Extract relevant landmarks
        left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
        left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y]
        left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]

        # Calculate angle
        knee_angle = calculate_angle(left_hip, left_knee, left_ankle)

        # Provide feedback
        if knee_angle < 90:
            errors.append("Keep your back straight and knees aligned.")
        elif 90 <= knee_angle <= 180:
            errors.append("Good squat posture!")
        else:
            errors.append("Adjust your posture for a proper squat.")

    if exercise == "Bench Press":
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

        angle = calculate_angle(shoulder, elbow, wrist)

        if angle > 160:
            stage = "down"
        if angle < 90 and stage == "down":
            stage = "up"
            counter["count"] += 1
        if angle > 160:
            errors.append("Keep your arms controlled, avoid locking elbows.")

    if exercise == "Skull Crushers":
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

        angle = calculate_angle(shoulder, elbow, wrist)

        if angle > 150:
            stage = "down"
        if angle < 60 and stage == "down":
            stage = "up"
            counter["count"] += 1
        if angle > 150:
            errors.append("Control the movement, avoid locking elbows.")

    if exercise == "Overhead Extensions":
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

        angle = calculate_angle(shoulder, elbow, wrist)

        if angle > 170:
            stage = "down"
        if angle < 60 and stage == "down":
            stage = "up"
            counter["count"] += 1
        if angle > 170:
            errors.append("Avoid overextending the arms.")

    if exercise == "Inclined Dumbell Press":
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

        # Calculate angle
        angle = calculate_angle(shoulder, elbow, wrist)

        # Rep counting logic
        if angle > 160:
            stage = "down"
        if angle < 90 and stage == "down":
            stage = "up"
            counter["count"] += 1
        if angle > 160:
            errors.append("Keep your arms aligned, avoid locking elbows.")

    if exercise == "Side Bridges":
        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

        angle = calculate_angle(hip, knee, ankle)

        if angle < 150:
            errors.append("Raise your hips higher for proper alignment.")
    
    return errors, counter["count"], duration

def process_image(image):
    frame = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    results = pose.process(frame)
    return frame, results
