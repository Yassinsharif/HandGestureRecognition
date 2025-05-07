#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import pygame

# Stepper motor pins
pins = [17, 18, 27, 22]

# Step sequence (fast full-step mode)
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
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

# Setup Pygame
pygame.init()
pygame.display.set_mode((200, 100))
pygame.display.set_caption("Motor Control")

pos = 0
delay = 0.002  # Control speed

# Function to move one step
def move(forward=True):
    global pos
    pos = (pos + 1) % 8 if forward else (pos - 1) % 8
    for i in range(4):
        GPIO.output(pins[i], seq[pos][i])

try:
    print("Hold LEFT or RIGHT arrows to rotate. Hold SPACE to pause. ESC to quit.")
    running = True
    while running:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            running = False
            break

        if not keys[pygame.K_SPACE]:  # Only move if Space is NOT held
            if keys[pygame.K_RIGHT]:
                move(forward=True)
            elif keys[pygame.K_LEFT]:
                move(forward=False)

        pygame.event.pump()  # Process internal Pygame events
        time.sleep(delay)

finally:
    GPIO.cleanup()
    pygame.quit()
