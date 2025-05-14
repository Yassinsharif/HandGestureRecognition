import cv2
import mediapipe as mp
import RPi.GPIO as GPIO
import time
import threading

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

delay = 0.001
pos1 = 0
pos2 = 0
motor_running = False
cooldown_until = 0  # cooldown timestamp

def move_motor_for_1_second(direction):
    global pos1, pos2, motor_running
    motor_running = True
    start_time = time.time()
    while time.time() - start_time < 1:
        if direction == "Left":
            pos1 = move_motor(motor1_pins, pos1, forward=True)   # swapped
        elif direction == "Right":
            pos1 = move_motor(motor1_pins, pos1, forward=False)  # swapped
        elif direction == "Up":
            pos2 = move_motor(motor2_pins, pos2, forward=False)  # swapped
        elif direction == "Down":
            pos2 = move_motor(motor2_pins, pos2, forward=True)   # swapped
    motor_running = False

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
    fingertips = [8, 12, 16, 20]
    pip_joints = [6, 10, 14, 18]
    for tip, pip in zip(fingertips, pip_joints):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            return False
    return True

# === Main Loop ===
cap = cv2.VideoCapture(0)
last_direction = None

try:
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

                tip_coords = (int(index_tip.x * w), int(index_tip.y * h))
                pip_coords = (int(index_pip.x * w), int(index_pip.y * h))

                if not is_fist(hand_landmarks):
                    direction = get_direction(tip_coords, pip_coords)
                    cv2.putText(image, f"Direction: {direction}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    # Cooldown logic: wait 3 seconds before accepting new input
                    if direction != last_direction and not motor_running and time.time() > cooldown_until:
                        print(f"Detected: {direction} – motor thread started")
                        last_direction = direction
                        cooldown_until = time.time() + 3  # 3 sec cooldown
                        t = threading.Thread(target=move_motor_for_1_second, args=(direction,))
                        t.start()
                else:
                    last_direction = None
                    cv2.putText(image, "Neutral (Fist)", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Gesture-Controlled Motors", image)
        if cv2.waitKey(5) & 0xFF == 27:  # ESC to exit
            break

finally:
    cap.release()
    GPIO.cleanup()
    cv2.destroyAllWindows()
