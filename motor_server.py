# motor_server.py
import socket
from motor_control2 import MotorDriver

HOST = '0.0.0.0'
PORT = 5000

# Define motor pins: (forward, backward, enable)
LEFT_PINS = (17, 22, 25)
RIGHT_PINS = (23, 24, 5)

motors = MotorDriver(left_pins=LEFT_PINS, right_pins=RIGHT_PINS)
print("[MOTOR SERVER] Motors initialized")

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind((HOST, PORT))
server_sock.listen(1)
print(f"[MOTOR SERVER] Listening on {HOST}:{PORT}...")

conn, addr = server_sock.accept()
print(f"[MOTOR SERVER] Connection from {addr}")

try:
    while True:
        data = conn.recv(1024).decode().strip()
        if not data:
            continue
        for cmd in data.splitlines():
            cmd = cmd.lower()
            print(f"[MOTOR SERVER] Command received: {cmd}")

            if cmd == 'forward':
                motors.move_forward()
            elif cmd == 'backward':
                motors.move_backward()
            elif cmd == 'stop':
                motors.stop_all()
            elif cmd == 'left':
                motors.turn_left()
            elif cmd == 'right':
                motors.turn_right()
            elif cmd == 'exit':
                motors.stop_all()
                motors.close()
                conn.close()
                server_sock.close()
                print("[MOTOR SERVER] Shutdown complete")
                exit(0)
            else:
                print("[MOTOR SERVER] Unknown command")

except KeyboardInterrupt:
    motors.stop_all()
    motors.close()
    conn.close()
    server_sock.close()
    print("[MOTOR SERVER] Stopped by user")
