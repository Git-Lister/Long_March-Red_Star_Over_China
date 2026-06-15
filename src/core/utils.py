"""Utility functions: clamp, weighted choice, JSON I/O."""

import json
import random
from typing import Any, List


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Return value constrained between min_val and max_val."""
    if min_val > max_val:
        raise ValueError(
            f"min_val ({min_val}) cannot be greater than max_val ({max_val})"
        )
    return max(min_val, min(value, max_val))


def weighted_choice(choices: List[Any], weights: List[float]) -> Any:
    """
    Return a single element from choices, weighted by the corresponding
    probability weights. Weights are normalised internally, so they need
    not sum to 1.
    """
    if not choices:
        raise ValueError("choices list cannot be empty")
    if len(choices) != len(weights):
        raise ValueError(
            f"choices length ({len(choices)}) must match weights length ({len(weights)})"
        )
    if all(w == 0 for w in weights):
        raise ValueError("at least one weight must be > 0")
    return random.choices(choices, weights=weights, k=1)[0]


def load_json(filepath: str) -> dict:
    """Load and return a JSON file as a dict."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filepath: str, data: dict) -> None:
    """Save a dict to a JSON file, creating directories if needed."""
    import os

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
