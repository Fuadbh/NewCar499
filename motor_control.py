# motor_control.py
from time import sleep
import sys

# Try to import gpiozero, fall back to mock mode if unavailable
GPIO_AVAILABLE = False
Motor = None
BadPinFactory = None

try:
    from gpiozero import Motor
    try:
        from gpiozero.exc import BadPinFactory
    except ImportError:
        BadPinFactory = Exception
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError) as e:
    GPIO_AVAILABLE = False
    print(f"Warning: GPIO not available ({e}). Running in mock mode (motors will not actually move).")

class MockMotor:
    """Mock motor for testing without GPIO hardware"""
    def __init__(self, *args, **kwargs):
        self.speed = 0.0
        self.direction = None
    
    def forward(self, speed=1.0):
        self.speed = speed
        self.direction = 'forward'
        print(f"  [MOCK] Motor forward at speed {speed:.2f}")
    
    def backward(self, speed=1.0):
        self.speed = speed
        self.direction = 'backward'
        print(f"  [MOCK] Motor backward at speed {speed:.2f}")
    
    def stop(self):
        self.speed = 0.0
        self.direction = None
        print(f"  [MOCK] Motor stopped")
    
    def close(self):
        self.stop()

class MotorDriver:
    def __init__(self, left_pins, right_pins, mock_mode=None):
        """
        Initialize motor driver
        
        Args:
            left_pins: Tuple of (forward, backward, enable) pins for left motor
            right_pins: Tuple of (forward, backward, enable) pins for right motor
            mock_mode: If True, use mock motors. If None, auto-detect based on GPIO availability
        """
        # Auto-detect mock mode if not explicitly set
        if mock_mode is None:
            mock_mode = not GPIO_AVAILABLE
        
        self.mock_mode = mock_mode
        
        if mock_mode:
            print("  Using mock motors (no GPIO hardware)")
            self.left_motor = MockMotor()
            self.right_motor = MockMotor()
        else:
            if Motor is None:
                print("  Warning: Motor class not available. Falling back to mock mode.")
                self.mock_mode = True
                self.left_motor = MockMotor()
                self.right_motor = MockMotor()
            else:
                try:
                    self.left_motor = Motor(forward=left_pins[0], backward=left_pins[1],
                                            enable=left_pins[2], pwm=True)
                    self.right_motor = Motor(forward=right_pins[0], backward=right_pins[1],
                                             enable=right_pins[2], pwm=True)
                except Exception as e:
                    print(f"  Warning: Failed to initialize GPIO motors ({type(e).__name__}: {e}). Falling back to mock mode.")
                    self.mock_mode = True
                    self.left_motor = MockMotor()
                    self.right_motor = MockMotor()
        
        self.current_speed = 0.5
        self.is_forward = True
        self.stop_all()

    def move_forward(self, speed=None):
        speed = speed or self.current_speed
        self.left_motor.forward(speed)
        self.right_motor.forward(speed)
        self.is_forward = True

    def move_backward(self, speed=None):
        speed = speed or self.current_speed
        self.left_motor.backward(speed)
        self.right_motor.backward(speed)
        self.is_forward = False

    def stop_all(self):
        self.left_motor.stop()
        self.right_motor.stop()

    def turn_left(self, speed=None):
        speed = speed or self.current_speed
        self.left_motor.backward(speed * 0.6)
        self.right_motor.forward(speed)

    def turn_right(self, speed=None):
        speed = speed or self.current_speed
        self.left_motor.forward(speed)
        self.right_motor.backward(speed * 0.6)

    def set_speed(self, level):
        """Set speed between 0.0–1.0"""
        self.current_speed = max(0.0, min(1.0, level))
        if self.is_forward:
            self.move_forward(self.current_speed)
        else:
            self.move_backward(self.current_speed)

    def close(self):
        self.stop_all()
        self.left_motor.close()
        self.right_motor.close()
