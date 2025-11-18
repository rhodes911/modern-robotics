"""Minimal SO(3) utilities with type hints.

These helpers are intentionally lightweight. For full-featured implementations,
use the Modern Robotics (MR) library placed under `mr/`.
"""
from __future__ import annotations

from typing import Tuple
import numpy as np

Array = np.ndarray


def hat(omega: Array) -> Array:
    """Map a 3-vector to a 3x3 skew-symmetric matrix (so(3) hat).

    Args:
        omega: shape (3,) angular velocity vector.
    Returns:
        3x3 skew-symmetric matrix.
    """
    wx, wy, wz = omega
    return np.array([[0.0, -wz, wy], [wz, 0.0, -wx], [-wy, wx, 0.0]])


def vee(omega_hat: Array) -> Array:
    """Map a 3x3 skew-symmetric matrix to a 3-vector (so(3) vee)."""
    return np.array([omega_hat[2, 1], omega_hat[0, 2], omega_hat[1, 0]])


def exp(omega: Array, theta: float) -> Array:
    """Exponential map on SO(3) using Rodrigues' formula.

    Args:
        omega: unit axis (3,), not necessarily normalized (will normalize internally).
        theta: rotation angle in radians.
    Returns:
        3x3 rotation matrix.
    """
    omega = np.asarray(omega, dtype=float).reshape(3)
    norm = np.linalg.norm(omega)
    if norm == 0:
        return np.eye(3)
    k = omega / norm
    K = hat(k)
    ct, st = np.cos(theta), np.sin(theta)
    return np.eye(3) + st * K + (1 - ct) * (K @ K)


def is_rotation(R: Array, atol: float = 1e-6) -> bool:
    """Check if R is a proper rotation (orthonormal, det≈+1)."""
    R = np.asarray(R, dtype=float)
    return np.allclose(R.T @ R, np.eye(3), atol=atol) and np.allclose(np.linalg.det(R), 1.0, atol=1e-6)
