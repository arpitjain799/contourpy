from contourpy import contour_generator, Interp, LineType
import numpy as np
from numpy.testing import assert_allclose
import pytest


@pytest.fixture
def xyz_log():
    n = 4
    angle = 0.4
    x, y = np.meshgrid(np.linspace(0.0, 1.0, n), np.linspace(0.0, 1.0, n))

    # Rotate grid
    rot = [[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]]
    x, y = np.einsum("ji,mni->jmn", rot, np.dstack([x, y]))

    z = 10.0**(2.5*y)
    return x, y, z


@pytest.mark.parametrize("name", ["serial", "threaded"])
def test_interp_log(xyz_log, name):
    x, y, z = xyz_log
    cont_gen = contour_generator(x, y, z, name, interp=Interp.Log, line_type=LineType.Separate)
    for level in [0.3, 1, 3, 10, 30, 100]:
        expected_y = np.log10(level) / 2.5
        lines = cont_gen.lines(level)
        assert len(lines) == 1
        line_y = lines[0][:, 1]
        assert_allclose(line_y, expected_y, atol=1e-15)


@pytest.mark.parametrize("name", ["serial", "threaded"])
def test_interp_log_saddle(name):
    x = y = np.asarray([-1.0, 1.0])
    z = np.asarray([[1.0, 100.0], [100.0, 1.0]])
    # z at middle of saddle quad is 10.0 for log interpolation.  Contour lines above z=10 should
    # rotate clockwise around the middle, contour lines below z=10 rotate anticlockwise.
    cont_gen = contour_generator(x, y, z, name, interp=Interp.Log, line_type=LineType.Separate)
    for level in [1.1, 9.9, 10.1, 99.9]:
        lines = cont_gen.lines(level)
        assert len(lines) == 2
        for line in lines:
            assert line.shape == (2, 2)
            cross_product = np.cross(line[0], line[1])
            if level > 10.0:
                assert cross_product < 0.0
            else:
                assert cross_product > 0.0
