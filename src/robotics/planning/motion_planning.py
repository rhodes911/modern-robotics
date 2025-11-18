"""Motion planning stubs (e.g., grid-based, sampling-based planners).

Implement RRT/RRT-Connect or simple PRM as you progress through Course 4.
"""
from __future__ import annotations

from typing import List, Tuple, Optional
import numpy as np

Array = np.ndarray


def rrt(start: Array, goal: Array, is_free_fn, sample_fn, steer_fn, 
        max_iters: int = 10_000, goal_sample_rate: float = 0.05):
    """Skeleton for RRT planner (fill in per course guidance)."""
    raise NotImplementedError("Implement RRT planner")
