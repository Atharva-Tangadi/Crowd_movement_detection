import numpy as np
from app.detection.detector import PersonDetector

detector = PersonDetector()
dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
results = detector.track(dummy_frame)
print("Tracking completed successfully:", results)
