import cv2
import mediapipe as mp
import csv
import os
from mediapipe.tasks import python
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode

# Load hand landmarker
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    running_mode=RunningMode.VIDEO
)
detector = HandLandmarker.create_from_options(options)

# CSV file
csv_file = "hand_landmarks.csv"
if not os.path.isfile(csv_file):
    with open(csv_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([f'x{i}' for i in range(21)] + [f'y{i}' for i in range(21)] + ['label'])

cap = cv2.VideoCapture(0)
print("Press 's' to save the current hand landmarks.")
print("Press 'q' to quit.")
label = input("Enter the letter you are showing (e.g., A, B, C): ").upper()

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    detection_result = detector.detect_for_video(mp_image, frame_count)
    frame_count += 1

    landmarks = []
    if detection_result.hand_landmarks:
        hand = detection_result.hand_landmarks[0]
        for lm in hand:
            landmarks.append(lm.x)
            landmarks.append(lm.y)
            # Draw landmarks
            x = int(lm.x * frame.shape[1])
            y = int(lm.y * frame.shape[0])
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        cv2.putText(frame, f"Label: {label}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Press 's' to save", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    cv2.imshow("Data Collection", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        if detection_result.hand_landmarks:
            with open(csv_file, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(landmarks + [label])
            print(f"Saved sample for letter {label}")
        else:
            print("No hand detected. Cannot save.")

cap.release()
cv2.destroyAllWindows()