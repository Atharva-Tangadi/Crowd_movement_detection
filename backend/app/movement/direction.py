import math
from typing import Dict, Tuple, List, Optional
from app.config import settings

class MovementAnalyzer:
    def __init__(self):
        # Store previous positions: track_id -> (x, y)
        self.previous_positions: Dict[int, Tuple[float, float]] = {}
        # Store directions for counting dominant direction
        self.current_directions: Dict[int, str] = {}
        
    def _get_center(self, bbox) -> Tuple[float, float]:
        """Calculates center of a bounding box [x1, y1, x2, y2]"""
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    def _calculate_direction(self, dx: float, dy: float) -> Optional[str]:
        """Determine direction based on movement vectors."""
        # If movement is too small, person is stationary
        if abs(dx) < settings.movement_threshold and abs(dy) < settings.movement_threshold:
            return "Stationary"

        # Determine primary direction
        if abs(dx) > abs(dy):
            if dx > 0:
                return "EAST"
            else:
                return "WEST"
        else:
            if dy > 0:
                return "SOUTH" # y increases downwards in image coords
            else:
                return "NORTH"

    def analyze_frame(self, track_boxes, track_ids) -> Dict:
        """
        Analyzes movement for the current frame.
        track_boxes: list of [x1, y1, x2, y2]
        track_ids: list of integer IDs
        """
        frame_directions = {}
        active_ids = set()

        for bbox, track_id in zip(track_boxes, track_ids):
            t_id = int(track_id)
            active_ids.add(t_id)
            center = self._get_center(bbox)
            
            if t_id in self.previous_positions:
                prev_center = self.previous_positions[t_id]
                dx = float(center[0] - prev_center[0])
                dy = float(center[1] - prev_center[1])
                
                direction = self._calculate_direction(dx, dy)
                frame_directions[str(t_id)] = {
                    'direction': direction,
                    'dx': dx,
                    'dy': dy,
                    'speed': float(math.sqrt(dx**2 + dy**2))
                }
                self.current_directions[t_id] = direction
            else:
                # First time seeing this ID
                frame_directions[str(t_id)] = {
                    'direction': "Unknown",
                    'dx': 0.0,
                    'dy': 0.0,
                    'speed': 0.0
                }
                
            # Update previous position
            self.previous_positions[t_id] = center
            
        # Clean up stale IDs
        stale_ids = set(self.previous_positions.keys()) - active_ids
        for stale_id in stale_ids:
            del self.previous_positions[stale_id]
            if stale_id in self.current_directions:
                del self.current_directions[stale_id]
                
        # Calculate dominant direction
        direction_counts = {"NORTH": 0, "SOUTH": 0, "EAST": 0, "WEST": 0, "Stationary": 0, "Unknown": 0}
        for d in self.current_directions.values():
            if d in direction_counts:
                direction_counts[d] += 1
                
        moving_people = sum([v for k, v in direction_counts.items() if k not in ["Stationary", "Unknown"]])
        dominant_direction = "Mixed/None"
        dominant_percentage = 0.0
        
        if moving_people > 0:
            for k in ["NORTH", "SOUTH", "EAST", "WEST"]:
                if direction_counts[k] > 0:
                    pct = direction_counts[k] / moving_people
                    if pct > dominant_percentage:
                        dominant_percentage = pct
                        dominant_direction = k
        
        # Require > 40% for a dominant direction
        if dominant_percentage < 0.4:
            dominant_direction = "Mixed/None"
            
        return {
            'individual': frame_directions,
            'counts': direction_counts,
            'dominant': dominant_direction,
            'dominant_pct': dominant_percentage
        }
