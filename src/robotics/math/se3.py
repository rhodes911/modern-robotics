"""Minimal SE(3) utilities for rigid transforms."""
from __future__ import annotations

from typing import Tuple
import numpy as np

Array = np.ndarray


def from_RT(R: Array, p: Array) -> Array:
    """Build homogeneous transform from rotation R (3x3) and translation p (3,)."""
    T = np.eye(4)
    T[:3, :3] = np.asarray(R, dtype=float)
    T[:3, 3] = np.asarray(p, dtype=float).reshape(3)
    return T


def invert(T: Array) -> Array:
    """Invert homogeneous transform (R, p) -> (R^T, -R^T p)."""
    R = T[:3, :3]
    p = T[:3, 3]
    Tinv = np.eye(4)
    Tinv[:3, :3] = R.T
    Tinv[:3, 3] = -(R.T @ p)
    return Tinv


def adjoint(T: Array) -> Array:
    """Adjoint representation Ad_T (6x6) for SE(3)."""
    R = T[:3, :3]
    p = T[:3, 3]
    px = np.array([[0, -p[2], p[1]], [p[2], 0, -p[0]], [-p[1], p[0], 0]], dtype=float)
    Ad = np.zeros((6, 6))
    Ad[:3, :3] = R
    Ad[3:, 3:] = R
    Ad[3:, :3] = px @ R
    return Ad
