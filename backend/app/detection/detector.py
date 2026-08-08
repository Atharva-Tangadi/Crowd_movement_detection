from ultralytics import YOLO
from app.config import settings

class PersonDetector:
    def __init__(self):
        try:
            # Load the YOLO model (will download if not found)
            # We use YOLO object directly as it supports built-in ByteTrack
            self.model = YOLO(settings.model_path)
            print(f"Loaded YOLO model: {settings.model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

    def track(self, frame):
        """
        Runs tracking on the frame using built-in ByteTrack.
        Returns results.
        """
        if self.model is None:
            return None
        
        # Classes=0 means person only
        # tracker="bytetrack.yaml" uses the built-in bytetrack config
        results = self.model.track(
            frame, 
            persist=True, 
            classes=0, 
            conf=settings.confidence_threshold,
            tracker="bytetrack.yaml",
            verbose=False
        )
        return results[0] if results else None
