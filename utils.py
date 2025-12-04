import cv2
import pygame
import time

# --- CONFIG ---
COLOR_BLUE = (255, 0, 0)   # Searching
COLOR_RED = (0, 0, 255)    # Locked
COLOR_GREEN = (0, 255, 0)  # Safe Zone

class TurretAudio:
    def __init__(self, filename="beep.mp3"):
        pygame.mixer.init()
        self.last_beep = 0
        self.cooldown = 0.108
        try:
            self.sound = pygame.mixer.Sound(filename)
        except:
            self.sound = None

    def play_lock(self):
        if self.sound and (time.time() - self.last_beep > self.cooldown):
            self.sound.play()
            self.last_beep = time.time()

def draw_hud(frame, center_x, threshold):
    """Draws the safe zone lines."""
    height = frame.shape[0]
    left = center_x - threshold
    right = center_x + threshold
    cv2.line(frame, (left, 0), (left, height), COLOR_GREEN, 2)
    cv2.line(frame, (right, 0), (right, height), COLOR_GREEN, 2)

def draw_target(frame, box, is_locked, motor_val):
    """Draws box and motor value."""
    x1, y1, x2, y2 = map(int, box)
    
    if is_locked:
        color = COLOR_RED
        text = "LOCKED [FIRE]"
    else:
        color = COLOR_BLUE
        # Show the motor value on screen e.g., "R: +45"
        direction = "R" if motor_val > 0 else "L"
        text = f"{direction}: {int(motor_val)}"

    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
    cv2.rectangle(frame, (x1, y1 - 30), (x1 + 200, y1), color, -1)
    cv2.putText(frame, text, (x1 + 5, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)