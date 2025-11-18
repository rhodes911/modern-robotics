"""Forward dynamics stubs (Euler-Lagrange / Newton-Euler)."""
from __future__ import annotations

import numpy as np

Array = np.ndarray


def forward_dynamics(thetalist: Array, dthetalist: Array, taulist: Array,
                     g: Array, Ftip: Array, Mlist: Array, Glist: Array, Slist: Array) -> Array:
    """Compute joint accelerations given state and inputs.

    Follow MR formulation (use MR as reference while coding your own).
    """
    raise NotImplementedError("Implement forward dynamics")
