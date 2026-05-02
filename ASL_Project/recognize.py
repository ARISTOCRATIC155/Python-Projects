import cv2
import mediapipe as mp
import numpy as np
import pickle
from mediapipe.tasks import python
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode

# Load model
with open("asl_model.pkl", "rb") as f:
    model = pickle.load(f)

# Load hand landmarker
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    running_mode=RunningMode.VIDEO
)
detector = HandLandmarker.create_from_options(options)

CONFIDENCE_THRESHOLD = 0.7
current_word = []
cap = cv2.VideoCapture(0)
frame_count = 0

print("Camera opened. Show your hand.")
print("Press 'n' to add current predicted letter to word.")
print("Press 'c' to clear current word.")
print("Press 'w' to write current word to notes.txt and clear.")
print("Press 'q' to quit.")

def predict_letter(landmarks):
    proba = model.predict_proba([landmarks])[0]
    max_idx = np.argmax(proba)
    confidence = proba[max_idx]
    if confidence >= CONFIDENCE_THRESHOLD:
        return model.classes_[max_idx], confidence
    return "?", confidence

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    detection_result = detector.detect_for_video(mp_image, frame_count)
    frame_count += 1

    predicted_letter = "?"
    confidence = 0.0
    landmarks = []

    if detection_result.hand_landmarks:
        hand = detection_result.hand_landmarks[0]
        for lm in hand:
            landmarks.append(lm.x)
            landmarks.append(lm.y)
            x = int(lm.x * frame.shape[1])
            y = int(lm.y * frame.shape[0])
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
        predicted_letter, confidence = predict_letter(landmarks)

    cv2.putText(frame, f"Predicted: {predicted_letter} ({confidence*100:.1f}%)", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Current word: {''.join(current_word)}", (10, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(frame, "n:add  c:clear  w:write  q:quit", (10, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    cv2.imshow("ASL Recognition", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('n') and predicted_letter != "?":
        current_word.append(predicted_letter)
        print(f"Added '{predicted_letter}'. Word: {''.join(current_word)}")
    elif key == ord('c'):
        current_word.clear()
        print("Word cleared.")
    elif key == ord('w'):
        if current_word:
            with open("notes.txt", "a") as f:
                f.write("".join(current_word) + "\n")
            print(f"Written '{''.join(current_word)}' to notes.txt")
            current_word.clear()
        else:
            print("No word to write.")

cap.release()
cv2.destroyAllWindows()