# lidar_client.py
import socket
import time
from rplidar import RPLidar

PORT_NAME = '/dev/ttyUSB0'
MAIN_HOST = '127.0.0.1'
MAIN_PORT = 6000
MAX_BUF = 300

lidar = RPLidar(PORT_NAME)
lidar._set_pwm(500)
time.sleep(1)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((MAIN_HOST, MAIN_PORT))
print("[LIDAR] Connected to main_controller")

try:
    for scan in lidar.iter_scans(max_buf_meas=MAX_BUF):
        for (_, angle, distance) in scan:
            msg = f"{angle},{distance}\n"
            try:
                sock.sendall(msg.encode())
            except BrokenPipeError:
                print("[LIDAR] Connection closed")
                break
        time.sleep(0.05)  # prevent buffer overflow

except KeyboardInterrupt:
    print("[LIDAR] Stopped by user")
finally:
    try:
        lidar.stop()
        lidar.stop_motor()
        lidar.disconnect()
    except:
        pass
    sock.close()
    print("[LIDAR] Shutdown complete")
