import serial
import time

try:
    # Replace 'COM4' with your Arduino's serial port
    arduino = serial.Serial('COM8', 9600, timeout=1)
    time.sleep(2) # Allow time for Arduino to reset and connect
    print("Arduino connected")

    while True:
        cmd = input("Manda")

        arduino.write(cmd.encode()) # Send 'l' as bytes
        print(arduino.readline().decode().strip()) # Read and print response


except serial.SerialException as e:
    print(f"Error: {e}")
finally:
    if 'arduino' in locals() and arduino.is_open:
        arduino.close()
        print("Serial port closed.")