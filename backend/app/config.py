from pydantic import BaseModel

class Config(BaseModel):
    # Model
    model_path: str = "yolo11n.pt"  # Will be downloaded automatically by ultralytics if not found
    confidence_threshold: float = 0.5
    img_size: int = 640
    
    # Movement and Direction
    movement_threshold: float = 2.0  # minimum pixel movement to consider
    
    # Crowd Density
    density_low: int = 10
    density_medium: int = 30
    density_high: int = 50
    
    # Anomaly Detection
    alert_cooldown_seconds: int = 5
    wrong_way_threshold: float = 0.3  # 30% of people moving opposite to dominant
    
    # Processing
    target_fps: int = 15  # Process 15 frames per second max
    camera_index: int = 0

settings = Config()
