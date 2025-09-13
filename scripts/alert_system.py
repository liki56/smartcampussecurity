# scripts/alert_system.py
import os
import platform
import time

def play_alert_sound():
    """Play a beep or alert sound depending on OS."""
    try:
        if platform.system() == "Windows":
            import winsound
            winsound.Beep(1000, 500)   # frequency=1000Hz, duration=500ms
        elif platform.system() == "Darwin":  # macOS
            os.system("say 'Alert detected!'")
        else:  # Linux / Raspberry Pi
            os.system("play -nq -t alsa synth 0.3 sine 880")
    except Exception as e:
        print(f"[!] Could not play sound: {e}")

def log_alert(message, logfile="alerts.log"):
    """Save alert message with timestamp into alerts.log"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(logfile, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[ALERT] {message}")

def send_alert(message):
    """
    Main function to trigger alerts:
    - Play sound
    - Log message
    - (Optional) send notification in future
    """
    play_alert_sound()
    log_alert(message)

if __name__ == "__main__":
    # Test the alert system
    send_alert("Unauthorized entry detected: Face and ID mismatch!")
