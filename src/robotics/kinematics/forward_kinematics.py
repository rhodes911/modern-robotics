"""Forward kinematics stubs.

Implement product of exponentials (PoE) and body/frame FK per Modern Robotics.
Use MR library for reference but write your own here for learning.
"""
from __future__ import annotations

from typing import Iterable
import numpy as np

Array = np.ndarray


def poe_fk_space(M: Array, Slist: Array, thetalist: Array) -> Array:
    """Space-frame PoE: T(θ) = e^[S1 θ1] ... e^[Sn θn] M.

    Args:
        M: Home configuration (4x4).
        Slist: Screw axes in space frame (6xn).
        thetalist: Joint angles (n,).
    Returns:
        4x4 transform.
    """
    raise NotImplementedError("Implement PoE forward kinematics (space frame)")


def poe_fk_body(M: Array, Blist: Array, thetalist: Array) -> Array:
    """Body-frame PoE: T(θ) = M e^[B1 θ1] ... e^[Bn θn]."""
    raise NotImplementedError("Implement PoE forward kinematics (body frame)")
