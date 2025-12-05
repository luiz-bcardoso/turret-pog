from ultralytics import YOLO
import cv2
import utils  # Import your utils.py
import serial
import time

#  Setup
model = YOLO('yolov8n.pt') 
audio = utils.TurretAudio("beep.mp3") 
cap = cv2.VideoCapture(1)

# Settings
THRESHOLD = 50 

print("> Turret System Online...")


try:
    # Replace 'COM4' with your Arduino's serial port
    arduino = serial.Serial('COM8', 9600, timeout=1)
    time.sleep(2) # Allow time for Arduino to reset and connect
    print("Arduino connected")


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
                    arduino.write("3".encode())
                    print(f"ATIRAR")
                else:
                    # Outside Safe Zone -> Calculate correction
                    # If to the right (positive), subtract threshold to smooth start
                    if distance > 0:
                        motor_speed = distance - THRESHOLD
                        arduino.write("1".encode())
                        print(f"TA NA DIREITA")
                    # If to the left (negative), add threshold
                    else:
                        arduino.write("2".encode())
                        motor_speed = distance + THRESHOLD
                        print(f"TA NA ESQUERDA")

                    # Print command
                    # TODO: Send motor command here
                     # Send 'l' as bytes
                    #print(arduino.readline().decode().strip()) # Read and print response
                # Visuals
                # Pass the Calculated motor_speed to be drawn

                utils.draw_target(frame, box.xyxy[0], is_locked, motor_speed)

        cv2.imshow("Turret HUD", frame)
        if cv2.waitKey(1) == ord('q'):
            break

except serial.SerialException as e:
    print(f"Error: {e}")
finally:
    if 'arduino' in locals() and arduino.is_open:
        arduino.close()
        print("Serial port closed.")

    cap.release()
    cv2.destroyAllWindows()

