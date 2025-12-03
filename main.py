from ultralytics import YOLO
import cv2

# Load model (v11 or v8)
model = YOLO('yolov8n.pt') 

cap = cv2.VideoCapture(0)
threshold = 50

# Define colors (OpenCV uses BGR format, not RGB)
COLOR_BLUE = (255, 0, 0)  # Searching
COLOR_RED = (0, 0, 255)   # Locked

while True:
    ret, frame = cap.read()
    if not ret: break

    # 1. High Confidence Only: Changed conf to 0.8 (80%)
    results = model(frame, stream=True, classes=[0], conf=0.8, verbose=False)

    # Get screen dimensions for center math
    height, width, _ = frame.shape
    screen_center_x = width // 2
    
    left_limit = screen_center_x - threshold
    right_limit = screen_center_x + threshold

    cv2.line(frame, (left_limit, 0), (left_limit, height), (0, 255, 0), 2)
    cv2.line(frame, (right_limit, 0), (right_limit, height), (0, 255, 0), 2)

    for r in results:
        boxes = r.boxes
        
        for box in boxes:
            # Get box coordinates (x1, y1, x2, y2)
            # We need these to draw the rectangle manually
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # Calculate the center of the PERSON
            person_center_x = int((x1 + x2) / 2)
            distance_from_center = person_center_x - screen_center_x
            motor_speed = 0
            
            # --- COLOR LOGIC ---
            # Check if person is inside the threshold area
            if abs(distance_from_center) <= threshold:
                # Inside the Safe Zone (Green Lines)
                motor_speed = 0
                text = "LOCKED [FIRE]"
                current_color = COLOR_RED
            else:
                # Outside the zone - Calculate how far out we are
                # We subtract the threshold so the motor starts slow right at the line
                if distance_from_center > 0:
                    # Target is to the RIGHT
                    motor_speed = distance_from_center - threshold
                    text = f"RIGHT (+{motor_speed})"
                else:
                    # Target is to the LEFT
                    motor_speed = distance_from_center + threshold
                    text = f"LEFT ({motor_speed})"
                
                current_color = COLOR_BLUE
                
                # Print direction (optional)
                if motor_speed != 0:
                    print(f"MOVE MOTOR: {motor_speed}")

            # --- DRAWING ---
            # Draw the box
            cv2.rectangle(frame, (x1, y1), (x2, y2), current_color, 3)
            
            # Draw the text above the box
            cv2.putText(frame, text, (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, current_color, 2)

    # Show the video
    cv2.imshow("Turret Sight", frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()