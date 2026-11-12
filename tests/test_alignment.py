"""Algebraic and geometry tests for the manufacturer-based equations."""

import math
import pytest
from alignment import Alignment, Dial, Geometry, calculate

G = Geometry(indicator_span=100, coupling_from_s=40,
             front_from_coupling=200, rear_from_coupling=600)
ZERO = Dial(0, 0, 0, 0)


def d(bottom=0, left=0, top=0, right=0):
    # Enforce the ideal four-point closure T+B = R+L by default.
    if right == 0 and (top == 0 and (bottom or left)):
        right = bottom - left
    return Dial(top, right, bottom, left)


def test_zero_readings_yield_zero_corrections():
    a = calculate(ZERO, ZERO, G)
    assert a.closure_ok
    assert a.vertical.front_move_mm == a.vertical.rear_move_mm == 0
    assert a.horizontal.front_move_mm == a.horizontal.rear_move_mm == 0


def test_pure_vertical_offset_requires_equal_feet_moves():
    # S_TIR=+0.4; M_TIR=-0.4 => 0.2 mm parallel offset, zero angle.
    s, m = d(bottom=.4), d(bottom=-.4)
    a = calculate(s, m, G)
    assert a.closure_ok
    assert a.vertical.slope_mm_per_mm == pytest.approx(0)
    assert a.vertical.offset_mm == pytest.approx(.2)
    assert a.vertical.front_move_mm == pytest.approx(-.2)
    assert a.vertical.rear_move_mm == pytest.approx(-.2)


def test_pure_vertical_angle_through_coupling():
    # Choose values for VO=0, VA=0.001. S_TIR=2*VA*C;
    # M_TIR=2*VA*(D-C). This yields different foot movements.
    a = calculate(d(bottom=.08), d(bottom=.12), G)
    assert a.vertical.offset_mm == pytest.approx(0)
    assert a.vertical.slope_mm_per_mm == pytest.approx(.001)
    assert a.vertical.front_move_mm == pytest.approx(.2)
    assert a.vertical.rear_move_mm == pytest.approx(.6)


def test_pure_horizontal_offset_requires_equal_lateral_moves():
    # S (9-3) = +0.4, M (9-3) = -0.4.
    # Build internally consistent four-point dial values.
    s = Dial(top=0, right=-.4, bottom=-.4, left=0)
    m = Dial(top=0, right=.4, bottom=.4, left=0)
    a = calculate(s, m, G)
    assert a.closure_ok
    assert a.horizontal.offset_mm == pytest.approx(.2)
    assert a.horizontal.slope_mm_per_mm == pytest.approx(0)
    assert a.horizontal.front_move_mm == pytest.approx(-.2)
    assert a.horizontal.rear_move_mm == pytest.approx(-.2)


def test_corrects_sag_without_affecting_horizontal():
    a = calculate(d(bottom=.5), d(bottom=-.4), G, sag_s_mm=.1)
    assert a.vertical.offset_mm == pytest.approx(.2)
    assert a.vertical.slope_mm_per_mm == pytest.approx(0)


def test_uses_nonzero_top_readings_and_keeps_closure():
    s = Dial(top=.3, right=.5, bottom=.7, left=.5)
    m = Dial(top=.4, right=.2, bottom=0, left=.2)
    a = calculate(s, m, G)
    assert a.closure_ok
    assert a.vertical.offset_mm == pytest.approx(.2)
    assert a.vertical.slope_mm_per_mm == pytest.approx(0)


def test_closure_flags_bad_readings():
    s = Dial(top=0, right=0, bottom=.2, left=0)
    a = calculate(s, ZERO, G)
    assert a.closure_ok is False
    assert a.s_closure_mm == pytest.approx(.2)


def test_independent_line_interpolation_equals_foot_corrections():
    # Independent geometric construction: offsets at S and M are
    # +S_TIR/2 and -M_TIR/2, respectively.
    s, m = d(bottom=.3), d(bottom=.1)
    a = calculate(s, m, G).vertical
    y_s, y_m = .3 / 2, -.1 / 2
    for x, output in ((G.coupling_from_s + G.front_from_coupling, a.front_move_mm),
                      (G.coupling_from_s + G.rear_from_coupling, a.rear_move_mm)):
        independent_line = y_s + (y_m - y_s) * (x / G.indicator_span)
        assert output == pytest.approx(-independent_line)


@pytest.mark.parametrize("geometry", [
    Geometry(0, 0, 10, 20), Geometry(-10, 0, 10, 20),
    Geometry(100, -1, 10, 20), Geometry(100, 110, 10, 20),
    Geometry(100, 50, -1, 20), Geometry(100, 50, 30, 20),
    Geometry(100, 50, 20, 20),
])
def test_rejects_bad_geometry(geometry):
    with pytest.raises(ValueError):
        calculate(ZERO, ZERO, geometry)


def test_rejects_nan_inf_and_negative_closure_limit():
    with pytest.raises(ValueError):
        calculate(Dial(math.nan, 0, 0, 0), ZERO, G)
    with pytest.raises(ValueError):
        calculate(ZERO, ZERO, G, sag_s_mm=math.inf)
    with pytest.raises(ValueError):
        calculate(ZERO, ZERO, G, closure_limit_mm=-.01)


def test_default_geometry_is_not_forced():
    g = Geometry(200, 50, 300, 800)
    a = calculate(d(bottom=.6), d(bottom=-.2), g)
    slope = (.6 - .2) / (2 * 200)
    offset = .6 / 2 - slope * 50
    assert a.vertical.front_move_mm == pytest.approx(slope * 300 - offset)


def test_pure_horizontal_angularity_through_coupling():
    # Four-position inputs have S9-S3=.08 and M9-M3=.12.
    s = Dial(top=0, right=-.08, bottom=-.08, left=0)
    m = Dial(top=0, right=-.12, bottom=-.12, left=0)
    a = calculate(s, m, G)
    assert a.closure_ok
    assert a.horizontal.offset_mm == pytest.approx(0)
    assert a.horizontal.slope_mm_per_mm == pytest.approx(.001)
    assert a.horizontal.front_move_mm == pytest.approx(.2)
    assert a.horizontal.rear_move_mm == pytest.approx(.6)


def test_parallel_and_angular_components_both_reach_feet():
    a = calculate(d(bottom=.3), d(bottom=.1), G).vertical
    assert a.slope_mm_per_mm == pytest.approx(.002)
    assert a.offset_mm == pytest.approx(.07)
    assert a.front_move_mm == pytest.approx(.33)
    assert a.rear_move_mm == pytest.approx(1.13)


def test_reversing_all_dial_signs_reverses_all_moves():
    s, m = d(bottom=.3), d(bottom=.1)
    plus = calculate(s, m, G).vertical
    negative = calculate(Dial(-s.top, -s.right, -s.bottom, -s.left),
                         Dial(-m.top, -m.right, -m.bottom, -m.left), G).vertical
    assert negative.front_move_mm == pytest.approx(-plus.front_move_mm)
    assert negative.rear_move_mm == pytest.approx(-plus.rear_move_mm)
