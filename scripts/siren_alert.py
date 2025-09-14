# scripts/siren_alert.py
"""
Siren Alert Module
------------------
This module provides a function to play a siren sound whenever access is denied.

📂 Project Structure Example:
    project_root/
    ├── assets/
    │   └── siren.mp3   (or siren.wav)
    ├── scripts/
    │   └── siren_alert.py
    └── main.py

Usage:
    from scripts.siren_alert import play_siren
    play_siren()
"""

import os
import playsound

def play_siren():
    """
    Plays the siren alert sound.
    Looks for 'siren.mp3' or 'siren.wav' inside the 'assets' folder at project root.
    """
    # Assets folder path (relative to project root)
    assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")

    # Supported siren file names
    possible_files = ["siren.mp3", "siren.wav"]

    # Find the first available file
    sound_file = None
    for fname in possible_files:
        fpath = os.path.join(assets_dir, fname)
        if os.path.exists(fpath):
            sound_file = fpath
            break

    if sound_file:
        try:
            print(f"[INFO] Playing siren sound: {os.path.basename(sound_file)}")
            playsound.playsound(sound_file)
        except Exception as e:
            print(f"[ERROR] Unable to play siren sound: {e}")
    else:
        print("[WARNING] No siren sound file found! Place 'siren.mp3' or 'siren.wav' inside the assets folder.")
