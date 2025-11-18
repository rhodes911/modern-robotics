"""Inverse dynamics stubs (Recursive Newton-Euler)."""
from __future__ import annotations

import numpy as np

Array = np.ndarray


def inverse_dynamics(thetalist: Array, dthetalist: Array, ddthetalist: Array,
                      g: Array, Ftip: Array, Mlist: Array, Glist: Array, Slist: Array) -> Array:
    """Compute joint torques required for desired motion."""
    raise NotImplementedError("Implement inverse dynamics")
