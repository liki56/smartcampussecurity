# scripts/gate_control.py
import os
import time

# Detect Raspberry Pi
ON_PI = os.name == "posix" and os.path.exists("/proc/device-tree/model")

# Try GPIO imports with fallbacks
try:
    if ON_PI:
        import RPi.GPIO as GPIO  # type: ignore
    else:
        # Use fake-rpi on Windows for simulation
        from fake_rpi.RPi import GPIO  # type: ignore
except (ModuleNotFoundError, ImportError):
    GPIO = None
    ON_PI = False

# GPIO pins
RELAY_PIN = 17
SERVO_PIN = 18
BUZZER_PIN = 27

# Global PWM variable
pwm = None


def init_hardware():
    """Initialize hardware (GPIO, servo, relay, buzzer)."""
    global pwm
    if not ON_PI or GPIO is None:
        print("[GATE] Running in simulation mode (not on Pi).")
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    GPIO.setup(SERVO_PIN, GPIO.OUT)

    pwm = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz PWM for servo
    pwm.start(7.5)  # Neutral position
    print("[GATE] Hardware initialized.")


def open_gate(duration: int = 2):
    """Open the gate for a given duration (seconds)."""
    if not ON_PI or GPIO is None:
        print("[GATE] OPEN (simulated)")
        time.sleep(duration)
        print("[GATE] CLOSE (simulated)")
        return

    GPIO.output(RELAY_PIN, GPIO.HIGH)
    pwm.ChangeDutyCycle(12.5)  # Open
    time.sleep(duration)
    pwm.ChangeDutyCycle(7.5)   # Neutral
    GPIO.output(RELAY_PIN, GPIO.LOW)
    print("[GATE] Gate opened and closed.")


def alert_buzzer(duration: int = 1):
    """Activate buzzer for a given duration (seconds)."""
    if not ON_PI or GPIO is None:
        print("[ALERT] Buzzer (simulated)")
        time.sleep(duration)
        return

    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    print("[ALERT] Buzzer activated.")


def cleanup():
    """Cleanup GPIO resources."""
    global pwm
    if not ON_PI or GPIO is None:
        print("[GATE] Cleanup (simulated)")
        return

    if pwm:
        pwm.stop()
    GPIO.cleanup()
    print("[GATE] GPIO cleaned up.")
