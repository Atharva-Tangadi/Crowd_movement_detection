from app.config import settings

class CrowdAnalyzer:
    def __init__(self):
        self.peak_count = 0
        self.total_processed_frames = 0
        self.cumulative_count = 0
        
    def analyze(self, current_count: int) -> dict:
        """
        Analyzes crowd count and returns density classification.
        """
        self.total_processed_frames += 1
        self.cumulative_count += current_count
        
        if current_count > self.peak_count:
            self.peak_count = current_count
            
        avg_count = self.cumulative_count / self.total_processed_frames if self.total_processed_frames > 0 else 0
        
        # Density classification
        if current_count >= settings.density_high:
            density_status = "CRITICAL"
        elif current_count >= settings.density_medium:
            density_status = "HIGH"
        elif current_count >= settings.density_low:
            density_status = "MEDIUM"
        else:
            density_status = "LOW"
            
        return {
            'count': current_count,
            'peak': self.peak_count,
            'average': round(avg_count, 2),
            'status': density_status
        }
