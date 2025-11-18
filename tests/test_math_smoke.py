import numpy as np
from src.robotics.math.so3 import hat, exp, is_rotation
from src.robotics.math.se3 import from_RT, invert, adjoint


def test_so3_hat_exp_identity():
    R = exp([0, 0, 1], 0.0)
    assert np.allclose(R, np.eye(3))
    assert is_rotation(R)


def test_se3_invert_identity():
    R = np.eye(3)
    p = np.array([1.0, 2.0, 3.0])
    T = from_RT(R, p)
    Tinv = invert(T)
    I = T @ Tinv
    assert np.allclose(I, np.eye(4))


def test_adjoint_shape():
    T = np.eye(4)
    Ad = adjoint(T)
    assert Ad.shape == (6, 6)
