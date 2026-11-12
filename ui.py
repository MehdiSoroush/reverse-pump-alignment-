"""Streamlit front end for the independently testable alignment engine."""

import pandas as pd
import streamlit as st

from alignment import Dial, Geometry, calculate


REFERENCE = (
    "https://0201.nccdn.net/1_2/000/000/190/be5/"
    "Pruftechnik-Engineers-Guide-2017.pdf"
)


def _dial_inputs(label: str) -> Dial:
    st.markdown(f"**{label}: signed indicator readings (mm)**")
    upper = st.columns(2)
    top = upper[0].number_input(f"{label} · 12 o'clock (top)", value=0.0,
                                step=0.01, format="%.3f")
    right = upper[1].number_input(f"{label} · 3 o'clock (right)", value=0.0,
                                  step=0.01, format="%.3f")
    lower = st.columns(2)
    bottom = lower[0].number_input(f"{label} · 6 o'clock (bottom)", value=0.0,
                                   step=0.01, format="%.3f")
    left = lower[1].number_input(f"{label} · 9 o'clock (left)", value=0.0,
                                 step=0.01, format="%.3f")
    return Dial(top=top, right=right, bottom=bottom, left=left)


def _direction(value: float, positive: str, negative: str) -> str:
    if abs(value) < 1e-9:
        return "No theoretical move"
    return f"{abs(value):.3f} mm — {positive if value > 0 else negative}"


def render() -> None:
    st.set_page_config(page_title="Reverse Dial Shaft Alignment | Engineering Calculator",
                       page_icon="🔧", layout="wide")
    st.title("Reverse-dial shaft alignment calculator")
    st.caption("Stationary pump (left) · movable motor (right) · all dimensions and dial readings in mm")
    st.warning(
        "Engineering calculation aid — not a substitute for trained field judgement, "
        "manufacturer tolerances, a soft-foot check, thermal-growth targets, "
        "pipe-strain checks, or a verified dial-indicator setup. "
        "Do not move equipment based on unverified measurements."
    )

    with st.expander("**Measurement arrangement and sign convention — read before entering data**", expanded=True):
        st.markdown(
            "1. Viewed along the shaft **from the movable motor toward the stationary pump**, "
            "3 o'clock is to your right and 9 o'clock to your left. "
            "The **S** indicator is the **left** measurement plane and the "
            "**M** indicator is the **right** measurement plane. Each radial indicator "
            "measures the opposing shaft, in the standard reverse-dial setup.\n"
            "2. Rotate **both shafts together** and enter signed readings at 12, 3, 6, "
            "and 9 o'clock. Do not switch dial mounting, zero/sign orientation, or viewing direction mid-test.\n"
            "3. Positive readings indicate **plunger compression** (the conventional "
            "dial convention used by the cited guide). Specify **signed** 6-minus-12 "
            "bracket-sag contributions, measured separately, below.\n"
            "4. Positive vertical corrections mean **add shims**; negative means "
            "**remove shims**. Positive horizontal corrections mean **move toward "
            "3 o'clock**; negative means **toward 9 o'clock**."
        )
        st.markdown(f"Reference: [PRÜFTECHNIK Engineer's Guide (2017), reverse indicator method]({REFERENCE}).")

    left, right = st.columns(2)
    with left:
        s = _dial_inputs("S — left indicator plane")
    with right:
        m = _dial_inputs("M — right indicator plane")

    st.subheader("Geometry and measurement quality")
    st.caption("Example values are placeholders only. Measure all distances before enabling calculations.")
    g1, g2 = st.columns(2)
    with g1:
        span = st.number_input("D · axial distance S → M (mm)", value=100.0, min_value=0.0,
                               step=10.0)
        coupling = st.number_input("C · axial distance S → coupling centre (mm)",
                                   value=50.0, min_value=0.0, step=10.0)
        sag_s = st.number_input("S · bracket sag contribution to (6 − 12), mm",
                                value=0.0, step=0.01, format="%.3f")
    with g2:
        front = st.number_input("sF · coupling → movable front feet (mm)",
                                value=200.0, min_value=0.0, step=10.0)
        rear = st.number_input("sR · coupling → movable rear feet (mm)",
                               value=600.0, min_value=0.0, step=10.0)
        sag_m = st.number_input("M · bracket sag contribution to (6 − 12), mm",
                                value=0.0, step=0.01, format="%.3f")
    closure_limit = st.number_input(
        "Maximum acceptable absolute four-position closure error per indicator (mm)",
        value=0.03, min_value=0.0, step=0.01, format="%.3f",
        help="Illustrative operator-selected data-quality threshold, not an OEM/API acceptance tolerance."
    )
    st.caption("Brackets should be checked for sag using the actual installed span. "
               "Do not assume zero sag without measurement or a justified negligible-sag assessment.")
    confirmed_readings = st.checkbox("I have completed and verified all eight dial readings, indicator mounting, and viewing direction.")
    confirmed_geometry = st.checkbox("I have measured the geometry and corrected or checked bracket sag; the values above are not unverified defaults.")

    geometry = Geometry(span, coupling, front, rear)
    try:
        result = calculate(s, m, geometry, sag_s_mm=sag_s,
                           sag_m_mm=sag_m, closure_limit_mm=closure_limit)
    except ValueError as exc:
        st.error(f"Invalid input: {exc}")
        return

    q1, q2 = st.columns(2)
    q1.metric("S four-position closure", f"{result.s_closure_mm:+.3f} mm")
    q2.metric("M four-position closure", f"{result.m_closure_mm:+.3f} mm")
    if not result.closure_ok:
        st.error("Dial-reading closure exceeds the selected limit. Recheck the readings "
                 "and measurement setup; foot corrections are withheld.")
        return
    if not (confirmed_readings and confirmed_geometry):
        st.info("Confirm both measurement-quality statements to display calculated foot moves.")
        return

    st.success("Input closure check passed. Results still require independent field verification.")
    summary = pd.DataFrame([
        {"Plane": "Vertical", "Offset at coupling (mm)": result.vertical.offset_mm,
         "Angularity (mm/100 mm)": result.vertical.slope_mm_per_mm * 100,
         "Front feet correction (mm)": result.vertical.front_move_mm,
         "Rear feet correction (mm)": result.vertical.rear_move_mm},
        {"Plane": "Horizontal", "Offset at coupling (mm)": result.horizontal.offset_mm,
         "Angularity (mm/100 mm)": result.horizontal.slope_mm_per_mm * 100,
         "Front feet correction (mm)": result.horizontal.front_move_mm,
         "Rear feet correction (mm)": result.horizontal.rear_move_mm},
    ])
    st.subheader("Calculated coupling alignment and foot moves")
    st.dataframe(summary, hide_index=True, use_container_width=True)
    cv, ch = st.columns(2)
    with cv:
        st.markdown("**Vertical — front/rear feet**")
        st.write(_direction(result.vertical.front_move_mm, "ADD SHIMS", "REMOVE SHIMS"))
        st.write(_direction(result.vertical.rear_move_mm, "ADD SHIMS", "REMOVE SHIMS"))
    with ch:
        st.markdown("**Horizontal — front/rear feet**")
        st.write(_direction(result.horizontal.front_move_mm, "MOVE TOWARD 3 O'CLOCK",
                            "MOVE TOWARD 9 O'CLOCK"))
        st.write(_direction(result.horizontal.rear_move_mm, "MOVE TOWARD 3 O'CLOCK",
                            "MOVE TOWARD 9 O'CLOCK"))

    st.subheader("Uncorrected relative centreline offsets (linear extrapolation)")
    stations = [("S indicator", -coupling), ("Coupling", 0.0),
                ("M indicator", span - coupling),
                ("Front feet", front), ("Rear feet", rear)]
    plotted = pd.DataFrame([
        {"Axial location (mm from coupling)": x,
         "Vertical (mm)": result.vertical.relative_offset_at(x),
         "Horizontal (mm)": result.horizontal.relative_offset_at(x)}
        for _, x in sorted(stations, key=lambda t: t[1])
    ]).set_index("Axial location (mm from coupling)")
    st.line_chart(plotted)
    st.caption("Curve is a rigid-line mathematical construction, not a shaft deflection or "
               "structural analysis. At each foot, the proposed move is the negative "
               "of the plotted relative offset.")

    # A measurement record must include the inputs and screening results, not
    # only the calculated foot moves; retain provenance for repeat checks.
    fields = [
        ("S 12", s.top, "mm"), ("S 3", s.right, "mm"),
        ("S 6", s.bottom, "mm"), ("S 9", s.left, "mm"),
        ("M 12", m.top, "mm"), ("M 3", m.right, "mm"),
        ("M 6", m.bottom, "mm"), ("M 9", m.left, "mm"),
        ("Indicator span D", span, "mm"),
        ("S to coupling C", coupling, "mm"),
        ("Coupling to front feet", front, "mm"),
        ("Coupling to rear feet", rear, "mm"),
        ("S sag contribution", sag_s, "mm"),
        ("M sag contribution", sag_m, "mm"),
        ("Dial closure screening limit", closure_limit, "mm"),
        ("S closure error", result.s_closure_mm, "mm"),
        ("M closure error", result.m_closure_mm, "mm"),
        ("Vertical coupling offset", result.vertical.offset_mm, "mm"),
        ("Vertical angularity", result.vertical.slope_mm_per_mm * 100, "mm/100 mm"),
        ("Vertical front correction", result.vertical.front_move_mm, "mm"),
        ("Vertical rear correction", result.vertical.rear_move_mm, "mm"),
        ("Horizontal coupling offset", result.horizontal.offset_mm, "mm"),
        ("Horizontal angularity", result.horizontal.slope_mm_per_mm * 100, "mm/100 mm"),
        ("Horizontal front correction", result.horizontal.front_move_mm, "mm"),
        ("Horizontal rear correction", result.horizontal.rear_move_mm, "mm"),
    ]
    record = pd.DataFrame(fields, columns=["Quantity", "Value", "Unit"])
    st.download_button("Download complete measurement and result record (CSV)",
                       data=record.to_csv(index=False),
                       file_name="reverse_dial_alignment_measurement_record.csv",
                       mime="text/csv")
    st.caption("CSV includes the entered readings, geometry, sag, closure errors "
               "and calculated moves. Record the equipment ID, date, method "
               "and technician identity separately in the maintenance record.")
    st.markdown("**Before any field correction:** check soft foot, machine constraints, "
                "shaft runout, bracket sag, pipe strain and applicable running/cold targets; "
                "make a controlled move, torque bolts, then remeasure. "
                "See `docs/METHODOLOGY.md` for derivation, limitations, and test cases.")


if __name__ == "__main__":
    render()
