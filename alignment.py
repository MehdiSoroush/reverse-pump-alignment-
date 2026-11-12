"""Reverse-dial shaft-alignment calculations (SI millimetres).

Convention follows PRUFTECHNIK, Engineer's Guide (2017), pp. 45–47:
S is the LEFT rim indicator, M is the RIGHT rim indicator, and the movable
machine is to the right of the stationary machine. Both shafts turn together.
The clock face is viewed FROM the movable machine TOWARD the stationary machine.
"""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Dial:
    """Signed readings at four clock positions in mm; zeroing is optional."""

    top: float
    right: float
    bottom: float
    left: float

    @property
    def closure(self) -> float:
        """Closure error (T+B)-(R+L) in mm; ideally zero."""
        return self.top + self.bottom - self.right - self.left


@dataclass(frozen=True)
class Geometry:
    """Distances in mm, increasing left-to-right along the machine train."""

    indicator_span: float  # S to M
    coupling_from_s: float  # S plane to coupling centre
    front_from_coupling: float  # coupling centre to movable front feet
    rear_from_coupling: float  # coupling centre to movable rear feet

    def validate(self) -> None:
        vals = (self.indicator_span, self.coupling_from_s,
                self.front_from_coupling, self.rear_from_coupling)
        if not all(isfinite(float(x)) for x in vals):
            raise ValueError("All distances must be finite.")
        if self.indicator_span <= 0:
            raise ValueError("Indicator span must be greater than zero.")
        if not (0 <= self.coupling_from_s <= self.indicator_span):
            raise ValueError("Coupling centre must lie between S and M indicator planes.")
        if self.front_from_coupling < 0:
            raise ValueError("Front-feet distance must be nonnegative.")
        if self.rear_from_coupling <= self.front_from_coupling:
            raise ValueError("Rear feet must be farther from the coupling than front feet.")


@dataclass(frozen=True)
class Plane:
    """Measured alignment state and corrective machine-foot moves.

    offset_mm = value of the plotted relative-centreline curve at coupling.
    slope_mm_per_mm = negative derivative of that curve versus distance.
    front/rear moves are NEGATIVE of the measured curve at each foot.
    Vertical: positive move means add shims.
    Horizontal: positive move means toward 3 o'clock.
    """

    s_corrected_tir_mm: float
    m_corrected_tir_mm: float
    offset_mm: float
    slope_mm_per_mm: float
    front_move_mm: float
    rear_move_mm: float

    def relative_offset_at(self, x_from_coupling_mm: float) -> float:
        """Uncorrected machine offset at any axial station (mm)."""
        return self.offset_mm - self.slope_mm_per_mm * x_from_coupling_mm


@dataclass(frozen=True)
class Alignment:
    vertical: Plane
    horizontal: Plane
    s_closure_mm: float
    m_closure_mm: float
    closure_limit_mm: float

    @property
    def closure_ok(self) -> bool:
        return (abs(self.s_closure_mm) <= self.closure_limit_mm
                and abs(self.m_closure_mm) <= self.closure_limit_mm)


def _plane(s_tir: float, m_tir: float, geom: Geometry) -> Plane:
    """2017 PRUFTECHNIK reverse-rim equations expressed in linear form.

    O = S_TIR/2 - ((S_TIR+M_TIR)/(2D))*C
    A = (S_TIR+M_TIR)/(2D)
    foot_move = A*distance_from_coupling - O
    """
    slope = (s_tir + m_tir) / (2 * geom.indicator_span)
    offset = s_tir / 2 - slope * geom.coupling_from_s
    return Plane(s_tir, m_tir, offset, slope,
                 slope * geom.front_from_coupling - offset,
                 slope * geom.rear_from_coupling - offset)


def calculate(s: Dial, m: Dial, geometry: Geometry, *, sag_s_mm: float = 0.0,
              sag_m_mm: float = 0.0, closure_limit_mm: float = 0.03) -> Alignment:
    """Compute shaft offset, angularity, and vertical/horizontal foot moves.

    Sag values are SIGNED vertical bottom-minus-top contributions measured
    from the bracket setup alone. They are SUBTRACTED from observed vertical
    TIRs. Horizontal TIR is left-minus-right per the stated clock convention.
    Zero sag is valid only if negligible or already corrected in the readings.

    A closure failure does not raise: the caller must inspect ``closure_ok``
    and NOT present the foot moves as reliable until readings are rechecked.
    """
    geometry.validate()
    measurements = (s.top, s.right, s.bottom, s.left,
                    m.top, m.right, m.bottom, m.left,
                    sag_s_mm, sag_m_mm, closure_limit_mm)
    if not all(isfinite(float(v)) for v in measurements):
        raise ValueError("Dial readings, sag and closure tolerance must be finite.")
    if closure_limit_mm < 0:
        raise ValueError("Closure tolerance cannot be negative.")
    s_v = (s.bottom - s.top) - sag_s_mm
    m_v = (m.bottom - m.top) - sag_m_mm
    s_h = s.left - s.right
    m_h = m.left - m.right
    return Alignment(vertical=_plane(s_v, m_v, geometry),
                     horizontal=_plane(s_h, m_h, geometry),
                     s_closure_mm=s.closure, m_closure_mm=m.closure,
                     closure_limit_mm=closure_limit_mm)
