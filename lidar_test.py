#!/usr/bin/env python3
from rplidar import RPLidar
import matplotlib.pyplot as plt
import numpy as np
import signal
import sys
import time

# ==== CONFIG ====
PORT_NAME = '/dev/ttyUSB0'
MAX_BUF = 2000     # Larger buffer to avoid overflow
PWM_SPEED = 500    # Optional: reduce spin speed (300–600 recommended)
SHOW_PLOT = True   # Set False if you only want text output
# =================

running = True

def signal_handler(sig, frame):
    global running
    running = False
    print("\nStopping...")

signal.signal(signal.SIGINT, signal_handler)

print("Starting LiDAR... Press Ctrl+C to stop")

# Initialize LiDAR
lidar = RPLidar(PORT_NAME)
lidar._set_pwm(PWM_SPEED)
time.sleep(1)  # give time to spin up

# Optional live plot
if SHOW_PLOT:
    plt.ion()
    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(111, projection='polar')
    scan_plot, = ax.plot([], [], 'g.', markersize=2)
    ax.set_rmax(4000)
    ax.grid(True)
    ax.set_title("RPLidar A1 - Live Scan", va='bottom')

try:
    for i, scan in enumerate(lidar.iter_scans(max_buf_meas=MAX_BUF)):
        distances = [d for (_, _, d) in scan]
        angles = [np.deg2rad(a) for (_, a, _) in scan]
        print(f"Scan {i}: {len(scan)} points")

        if SHOW_PLOT:
            scan_plot.set_data(angles, distances)
            plt.pause(0.001)

        if not running:
            break

except Exception as e:
    print("Error:", e)

finally:
    print("Stopping motor and disconnecting LiDAR...")
    try:
        lidar.stop()
        lidar.stop_motor()
        lidar.disconnect()
    except:
        pass
    print("LiDAR stopped cleanly.")
