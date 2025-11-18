"""Inverse kinematics stubs (Newton-Raphson with body or space Jacobians)."""
from __future__ import annotations

from typing import Tuple
import numpy as np

Array = np.ndarray


def ik_body(M: Array, Blist: Array, T_sd: Array, thetalist0: Array, 
            eomg: float = 1e-3, ev: float = 1e-3, max_iter: int = 100) -> Tuple[Array, bool]:
    """Body-frame IK via iterative Newton method.

    Returns:
        thetalist, success
    """
    raise NotImplementedError("Implement body-frame inverse kinematics")
