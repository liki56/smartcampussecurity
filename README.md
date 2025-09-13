SmartCampusSecurity — Quick start
1. Setup env: sudo apt install … ; python3 -m venv venv ; source venv/bin/activate
2. pip install -r requirements.txt
3. Capture faces: python scripts/capture_faces.py
4. Add id_cards/<USN>.jpg
5. Train: python scripts/face_train.py
6. Run system: python main.py
