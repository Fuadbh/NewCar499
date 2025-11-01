# main_controller.py
import socket

MOTOR_HOST = '127.0.0.1'
MOTOR_PORT = 5000
LIDAR_HOST = '0.0.0.0'
LIDAR_PORT = 6000

OBSTACLE_THRESHOLD = 400  # mm

# Connect to motor server
motor_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
motor_sock.connect((MOTOR_HOST, MOTOR_PORT))
print("[MAIN] Connected to motor server")

# Listen for LiDAR
lidar_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lidar_sock.bind((LIDAR_HOST, LIDAR_PORT))
lidar_sock.listen(1)
print(f"[MAIN] Listening for LiDAR data on port {LIDAR_PORT}")

conn, addr = lidar_sock.accept()
print(f"[MAIN] LiDAR connected from {addr}")

def decide_action(angle, distance):
    if distance > OBSTACLE_THRESHOLD:
        return "forward"
    # Front sector
    if (angle >= 330 or angle <= 30):
        return "stop"
    # Left sector
    elif 30 < angle <= 90:
        return "right"
    # Right sector
    elif 270 <= angle < 330:
        return "left"
    # Rear/other
    else:
        return "forward"

try:
    while True:
        data = conn.recv(1024).decode().strip()
        if not data:
            continue
        for line in data.splitlines():
            try:
                angle_str, dist_str = line.split(",")
                angle = float(angle_str)
                distance = float(dist_str)
            except ValueError:
                continue

            action = decide_action(angle, distance)
            motor_sock.sendall(f"{action}\n".encode())
            print(f"[MAIN] Angle: {angle:.1f}, Distance: {distance:.1f} -> Action: {action}")

except KeyboardInterrupt:
    print("[MAIN] Stopped by user")
finally:
    motor_sock.sendall(b"stop\n")
    motor_sock.sendall(b"exit\n")
    motor_sock.close()
    conn.close()
    lidar_sock.close()
    print("[MAIN] Shutdown complete")
