import cv2
import mediapipe as mp
import RPi.GPIO as GPIO
import time

# === Motor Setup ===
motor1_pins = [16, 20, 21, 26]  # LEFT/RIGHT
motor2_pins = [17, 27, 18, 22]  # UP/DOWN

seq = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

GPIO.setmode(GPIO.BCM)
for pin in motor1_pins + motor2_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

delay = 0.001  # Step delay
pos1 = 0
pos2 = 0

def move_motor(pins, pos, forward=True):
    pos = (pos + 1) % 8 if forward else (pos - 1) % 8
    for i in range(4):
        GPIO.output(pins[i], seq[pos][i])
    time.sleep(delay)
    return pos

# === MediaPipe Setup ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def get_direction(index_tip, index_pip):
    dx = index_tip[0] - index_pip[0]
    dy = index_tip[1] - index_pip[1]
    if abs(dx) > abs(dy):
        return "Right" if dx > 0 else "Left"
    else:
        return "Down" if dy > 0 else "Up"

def is_fist(hand_landmarks):
    # Returns True if all fingers are curled (fist)
    fingertips = [8, 12, 16, 20]
    pip_joints = [6, 10, 14, 18]
    for tip, pip in zip(fingertips, pip_joints):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            return False  # Finger is extended
    return True  # All curled = fist

# === Main Loop ===
cap = cv2.VideoCapture(0)
last_direction = None
motor_active = False
motor_start_time = 0

try:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        image = cv2.flip(image, 1)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_image)
        current_time = time.time()

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                h, w, _ = image.shape
                index_tip = hand_landmarks.landmark[8]
                index_pip = hand_landmarks.landmark[6]

                tip_coords = (int(index_tip.x * w), int(index_tip.y * h))
                pip_coords = (int(index_pip.x * w), int(index_pip.y * h))

                if not is_fist(hand_landmarks):
                    direction = get_direction(tip_coords, pip_coords)
                    cv2.putText(image, f"Direction: {direction}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    if direction != last_direction and not motor_active:
                        print(f"Detected: {direction} – motor running 3s")
                        last_direction = direction
                        motor_active = True
                        motor_start_time = current_time
                else:
                    # Fist = neutral
                    last_direction = None
                    cv2.putText(image, "Neutral (Fist)", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # === Non-blocking motor run ===
        if motor_active and current_time - motor_start_time < 3:
            for _ in range(30):  # Adjust steps per frame for smoothness
                if last_direction == "Left":
                    pos1 = move_motor(motor1_pins, pos1, forward=False)
                elif last_direction == "Right":
                    pos1 = move_motor(motor1_pins, pos1, forward=True)
                elif last_direction == "Up":
                    pos2 = move_motor(motor2_pins, pos2, forward=True)
                elif last_direction == "Down":
                    pos2 = move_motor(motor2_pins, pos2, forward=False)
        elif motor_active:
            motor_active = False  # Stop after 3 seconds

        cv2.imshow("Gesture-Controlled Motors", image)
        if cv2.waitKey(5) & 0xFF == 27:  # ESC to exit
            break

finally:
    cap.release()
    GPIO.cleanup()
    cv2.destroyAllWindows()
