from dataclasses import dataclass


@dataclass(frozen=True)
class PollinationFeatures:
    temperature_c: float
    humidity_percent: float
    ndvi: float
    bee_count: int
    pollen_level: int


def baseline_psi(features: PollinationFeatures) -> int:
    """Return a transparent baseline score until trained artifacts are validated."""
    score = 0
    score += 25 if 20 <= features.temperature_c <= 32 else 12
    score += 20 if 50 <= features.humidity_percent <= 80 else 10
    score += 20 if features.ndvi >= 0.6 else 8
    score += 20 if features.bee_count >= 3 else 8
    score += 15 if features.pollen_level >= 3 else 6
    return max(0, min(100, score))
