def safe_float(value: any, default: float = 0.0) -> float:
    """Safely extracts a float from potentially drifting schema values."""
    try:
        if isinstance(value, dict):
            value = (
                value.get("final")
                or value.get("value")
                or value.get("fusion")
                or value.get("score")
                or 0
            )
        return float(value)
    except Exception:
        return default

def map_raw_score_to_percentage(raw_score: any) -> int:
    """
    Maps an RRF score (typically low floats like 0.01-0.03) to a 0-100 percentage.
    This is heuristic-based to ensure the recruiter sees intuitive numbers.
    Assume RRF max around 0.033 (1/30). We will scale such that 0.033 is ~99%.
    """
    val = safe_float(raw_score)
    
    # Heuristic scaling for RRF
    # If the score is an adversarial penalty it will be very low
    percent = val * 3000  # 0.033 * 3000 = 99
    
    if percent > 99:
        percent = 99
    elif percent < 1:
        percent = 1
        
    return int(percent)

def get_match_tier(percent: int) -> str:
    if percent >= 80:
        return "Highly Recommended"
    elif percent >= 50:
        return "Strong Match"
    elif percent >= 25:
        return "Needs Review"
    else:
        return "Poor Match"
