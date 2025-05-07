import cv2
import mediapipe as mp
import math

# Initialize MediaPipe Hand Landmarker
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def get_direction(index_tip, index_pip):
    dx = index_tip[0] - index_pip[0]
    dy = index_tip[1] - index_pip[1]

    # Determine direction
    if abs(dx) > abs(dy):
        return "Right" if dx > 0 else "Left"
    else:
        return "Down" if dy > 0 else "Up"

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    image = cv2.flip(image, 1)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_image)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            h, w, _ = image.shape
            index_tip = hand_landmarks.landmark[8]
            index_pip = hand_landmarks.landmark[6]

            # Convert to pixel coordinates
            index_tip_coords = (int(index_tip.x * w), int(index_tip.y * h))
            index_pip_coords = (int(index_pip.x * w), int(index_pip.y * h))

            direction = get_direction(index_tip_coords, index_pip_coords)
            cv2.putText(image, f"Direction: {direction}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Finger Direction Detection", image)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
