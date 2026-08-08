import time
from app.config import settings
from datetime import datetime

class AnomalyDetector:
    def __init__(self):
        self.last_alert_time = 0
        self.active_alerts = []

    def check_anomalies(self, crowd_data, movement_data):
        """
        Check for anomalous conditions and generate alerts with cooldown.
        """
        current_time = time.time()
        new_alerts = []
        
        # 1. Overcrowding / High Density
        if crowd_data['status'] in ["HIGH", "CRITICAL"]:
            new_alerts.append({
                "type": "OVERCROWDING",
                "severity": crowd_data['status'],
                "description": f"Crowd density exceeded safe threshold. Current count: {crowd_data['count']}",
                "timestamp": datetime.now().isoformat()
            })
            
        # 2. Wrong-way movement
        direction_counts = movement_data['counts']
        dominant = movement_data['dominant']
        moving_people = sum([v for k, v in direction_counts.items() if k not in ["Stationary", "Unknown"]])
        
        if dominant != "Mixed/None" and moving_people > 0:
            opposites = {
                "NORTH": "SOUTH",
                "SOUTH": "NORTH",
                "EAST": "WEST",
                "WEST": "EAST"
            }
            if dominant in opposites:
                opposite_dir = opposites[dominant]
                wrong_way_count = direction_counts.get(opposite_dir, 0)
                if wrong_way_count / moving_people >= settings.wrong_way_threshold and wrong_way_count >= 3:
                    new_alerts.append({
                        "type": "WRONG_WAY_MOVEMENT",
                        "severity": "MEDIUM",
                        "description": f"Significant wrong-way movement detected opposite to {dominant}.",
                        "timestamp": datetime.now().isoformat()
                    })

        # Apply Cooldown
        if new_alerts and (current_time - self.last_alert_time) > settings.alert_cooldown_seconds:
            # We just take the highest severity if there are multiple, or keep all.
            # Keeping all is fine, but let's just return the top priority one to avoid spam
            # Sort by severity: CRITICAL > HIGH > MEDIUM > LOW
            severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
            new_alerts.sort(key=lambda x: severity_order.get(x['severity'], 4))
            
            # Emit the top alert
            top_alert = new_alerts[0]
            self.active_alerts.append(top_alert)
            self.last_alert_time = current_time
            
        # Keep only recent alerts in history (e.g., last 10)
        self.active_alerts = self.active_alerts[-10:]
            
        return self.active_alerts[-1] if self.active_alerts and (current_time - self.last_alert_time) <= 1.0 else None
