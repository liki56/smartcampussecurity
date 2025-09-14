# scripts/gate_control.py
"""
Gate Control Module
-------------------
Handles hardware interactions for:
 - Gate relay
 - Servo motor
 - Buzzer

Runs in two modes:
 1. Raspberry Pi with real GPIO (production)
 2. Simulation mode on non-Pi systems (development/testing)
"""

import os
import time

# Detect Raspberry Pi (Linux + device tree model)
ON_PI = os.name == "posix" and os.path.exists("/proc/device-tree/model")

# Try GPIO imports with fallbacks
try:
    if ON_PI:
        import RPi.GPIO as GPIO  # type: ignore
    else:
        # Use fake-rpi for simulation on Windows/Linux dev
        from fake_rpi.RPi import GPIO  # type: ignore
except (ModuleNotFoundError, ImportError):
    GPIO = None
    ON_PI = False

# GPIO pins
RELAY_PIN = 17   # Relay for gate
SERVO_PIN = 18   # Servo for gate arm
BUZZER_PIN = 27  # Buzzer

# Global PWM variable (for servo control)
pwm = None


def init_hardware():
    """Initialize hardware (GPIO, servo, relay, buzzer)."""
    global pwm
    if not ON_PI or GPIO is None:
        print("[GATE] Running in SIMULATION mode (not on Pi).")
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    GPIO.setup(SERVO_PIN, GPIO.OUT)

    pwm = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz PWM for servo
    pwm.start(7.5)  # Neutral position
    print("[GATE] Hardware initialized (real GPIO).")


def open_gate(duration: int = 2):
    """
    Open the gate for a given duration (seconds),
    then close it automatically.
    """
    if not ON_PI or GPIO is None:
        print("[GATE] OPEN (simulated)")
        time.sleep(duration)
        print("[GATE] CLOSE (simulated)")
        return

    GPIO.output(RELAY_PIN, GPIO.HIGH)
    pwm.ChangeDutyCycle(12.5)  # Open
    print("[GATE] Gate opened.")
    time.sleep(duration)

    pwm.ChangeDutyCycle(7.5)   # Neutral
    GPIO.output(RELAY_PIN, GPIO.LOW)
    print("[GATE] Gate closed.")


def alert_buzzer(duration: int = 1):
    """
    Activate buzzer for a given duration (seconds).
    """
    if not ON_PI or GPIO is None:
        print("[ALERT] Buzzer (simulated)")
        time.sleep(duration)
        return

    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    print("[ALERT] Buzzer ON")
    time.sleep(duration)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    print("[ALERT] Buzzer OFF")


def cleanup():
    """
    Cleanup GPIO resources. Call this before program exit.
    """
    global pwm
    if not ON_PI or GPIO is None:
        print("[GATE] Cleanup (simulated)")
        return

    if pwm:
        pwm.stop()
        pwm = None
    GPIO.cleanup()
    print("[GATE] GPIO cleaned up.")
