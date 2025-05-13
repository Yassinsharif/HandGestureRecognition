import RPi.GPIO as GPIO
import time
import pygame

# Motor 1 (LEFT/RIGHT) - Physical pins 36, 37, 38, 40 => GPIO 16, 26, 20, 21
motor1_pins = [16, 20, 21, 26]

# Motor 2 (UP/DOWN) - Physical pins 11, 12, 13, 15 => GPIO 17, 18, 27, 22
motor2_pins = [17, 27, 18, 22]

# Step sequence (half-step for smooth movement)
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

# Setup GPIO
GPIO.setmode(GPIO.BCM)
for pin in motor1_pins + motor2_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

# Setup Pygame
pygame.init()
pygame.display.set_mode((200, 100))
pygame.display.set_caption("Motor Control")

pos1 = 0  # Step position for motor 1
pos2 = 0  # Step position for motor 2
delay = 0.001  # Speed control

# Move one step in specified direction
def move_motor(pins, pos, forward=True):
    pos = (pos + 1) % 8 if forward else (pos - 1) % 8
    for i in range(4):
        GPIO.output(pins[i], seq[pos][i])
    return pos

try:
    print("← → control Motor 1 | ↑ ↓ control Motor 2 | Hold SPACE to pause | ESC to exit")
    running = True
    while running:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            running = False
            break

        if not keys[pygame.K_SPACE]:  # Only move if not paused
            if keys[pygame.K_RIGHT]:
                pos1 = move_motor(motor1_pins, pos1, forward=True)
            elif keys[pygame.K_LEFT]:
                pos1 = move_motor(motor1_pins, pos1, forward=False)

            if keys[pygame.K_UP]:
                pos2 = move_motor(motor2_pins, pos2, forward=True)
            elif keys[pygame.K_DOWN]:
                pos2 = move_motor(motor2_pins, pos2, forward=False)

        pygame.event.pump()
        time.sleep(delay)

finally:
    GPIO.cleanup()
    pygame.quit()
