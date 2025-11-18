"""Feedback control stubs (trajectory tracking, operational space).

Implement PID/jacobian-based control as introduced in Course 4 and 5.
"""
from __future__ import annotations

import numpy as np

Array = np.ndarray


def pid(q: Array, qd: Array, e_int: Array, Kp: Array, Ki: Array, Kd: Array, dt: float) -> Array:
    """Basic joint-space PID step (fill in details later)."""
    raise NotImplementedError("Implement PID control step")
