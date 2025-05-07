#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import pygame

# Stepper motor pins
pins = [17, 18, 27, 22]

# Full step sequence (faster movement)
full_step_seq = [
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
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

# Setup Pygame
pygame.init()
pygame.display.set_mode((200, 100))
pygame.display.set_caption("Motor Control")

pos = 0
moving = False  # Variable to control movement
delay = 0.0002  # Small delay for faster movement

# Function to move motor one step
def move(forward=True):
    global pos
    pos = (pos + 1) % 8 if forward else (pos - 1) % 8
    for i in range(4):
        GPIO.output(pins[i], full_step_seq[pos][i])

try:
    print("Use LEFT and RIGHT arrows to rotate. SPACE to stop, ESC to quit.")
    running = True
    while running:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] and moving:
            move(forward=True)
        elif keys[pygame.K_LEFT] and moving:
            move(forward=False)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

            # Space key to toggle movement (stop/start)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                moving = not moving  # Toggle the movement state
                if moving:
                    print("Motor movement resumed.")
                else:
                    print("Motor movement stopped.")

        # Small wait to make the loop responsive
        pygame.time.wait(1)  # Minimal wait for responsiveness

finally:
    GPIO.cleanup()
    pygame.quit()
