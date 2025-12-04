from ultralytics import YOLO
import cv2
import utils  # Import your utils.py

#  Setup
model = YOLO('yolov8n.pt') 
audio = utils.TurretAudio("beep.mp3") 
cap = cv2.VideoCapture(1)

# Settings
THRESHOLD = 50 

print("> Turret System Online...")

while True:
    ret, frame = cap.read()
    if not ret: break

    # 1. AI Detection
    # stream=True makes it faster. classes=[0] detects ONLY humans. conf=0.x% confidence
    results = model(frame, stream=True, classes=[0], conf=0.8, verbose=False)

    # 2. Geometry
    height, width, _ = frame.shape
    screen_center_x = width // 2

    # 3. Draw HUD
    utils.draw_hud(frame, screen_center_x, THRESHOLD)

    # 4. Process Logic
    for r in results:
        for box in r.boxes:
            # Get person center
            x1, y1, x2, y2 = box.xyxy[0]
            person_center_x = int((x1 + x2) / 2)
            
            # Calculate distance from center
            distance = person_center_x - screen_center_x
            motor_speed = 0
            is_locked = False

            # Check if inside Deadzone/Threshold
            if abs(distance) <= THRESHOLD:
                # Inside Safe Zone -> Do not move
                is_locked = True
                motor_speed = 0
                audio.play_lock()
            else:
                # Outside Safe Zone -> Calculate correction
                # If to the right (positive), subtract threshold to smooth start
                if distance > 0:
                    motor_speed = distance - THRESHOLD
                # If to the left (negative), add threshold
                else:
                    motor_speed = distance + THRESHOLD
                
                # Print command
                print(f" > Move Motor (x): {int(motor_speed)}")
                # TODO: Send motor command here

            # Visuals
            # Pass the Calculated motor_speed to be drawn
            utils.draw_target(frame, box.xyxy[0], is_locked, motor_speed)

    cv2.imshow("Turret HUD", frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()