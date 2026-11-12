# Reverse-dial shaft alignment | Legacy deployment mirror

**Repository role:** This is the compatible standalone copy of the original `app.py` deployment. The [primary project repository](https://github.com/MehdiSoroush/reverse-pump-alignment) is the authoritative source for future development; this mirror uses the same calculation and test code as the primary project at the time of this engineering audit.

A reproducible, independently testable **reverse-dial indicator shaft-alignment calculator** for stationary-pump/movable-motor machine trains. It computes **vertical and horizontal coupling offsets, angularity, and theoretical front/rear foot adjustments** from two radial dial indicators.

> **Status:** Formula-based, analytically tested engineering calculation aid. **Not field validated** and not a substitute for measurement quality control, qualified alignment work, OEM alignment limits, or hot/cold target compensation.

## What it does

- Accepts signed 12/3/6/9-o'clock readings for both reverse-rim indicators.
- Corrects vertical differences using **separately measured signed bracket sag**.
- Converts full diametral readings into offset/angulation using the **half-TIR rule**.
- Calculates signed coupling-centre offset (`mm`) and angularity (`mm/100 mm`).
- Projects **both** parallel offset and angle to front and rear machine feet, for shim and lateral correction.
- Checks four-position dial closure, measurement geometry, and completion of measurement confirmations before showing foot moves.
- Displays a centreline graph and exports a results CSV.
- Includes a separate computation module and **17 unit tests** covering analytical and failure cases.

## Run locally

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

For an existing deployment that uses `app.py`, `streamlit run app.py` is also supported. Run the verification suite separately:

```bash
python -m pip install pytest
python -m pytest -q
```

The computation engine (`alignment.py`) itself depends only on the Python standard library. Streamlit and pandas are required for the interactive interface.

## Physical setup and sign convention — essential

The **pump is stationary at left** and **motor is movable at right**. In a conventional reverse-rim arrangement, **S** is the *left indicator measurement plane*, **M** is the *right indicator plane*; the gauges point toward opposite shafts. The observer looks **from the movable motor toward the stationary pump**. At 3 o'clock the probe is to the observer's right.

- `D`: distance between S and M measuring planes, positive, mm.
- `C`: distance from the S plane to coupling centre, with `0 <= C <= D`, mm.
- `sF`, `sR`: distances from coupling centre to the movable machine's front/rear feet, with `0 <= sF < sR`, mm.
- Dial readings: **signed millimetres**; conventional positive sign denotes gauge plunger compression. Enter all four clock positions for each dial, including nonzero reference readings.
- `sagS`, `sagM`: independently measured signed sag contributions to the bottom-minus-top reading (mm). These are *subtracted* from the observed vertical reading.

**Output directions:** positive **vertical** foot result means **add shims**, negative means **remove shims**. Positive **horizontal** result means move **toward 3 o'clock**, negative means move toward 9 o'clock. The physical probe installation and sign direction must correspond to this method; an inverted dial setup requires re-establishing the sign convention rather than blindly applying the numerical result.

## Formula overview

For either the vertical or horizontal plane, let the corrected diametral differences be `T_S` and `T_M`:

- Vertical: `T_S = (S6-S12)-sagS`, `T_M = (M6-M12)-sagM`.
- Horizontal: `T_S = S9-S3`, `T_M = M9-M3`.

Then:

```text
angularity A            = (T_S + T_M) / (2 D)            [mm/mm]
coupling offset O       = T_S / 2 - A C                 [mm]
front-foot correction   = A sF - O                     [mm]
rear-foot correction    = A sR - O                     [mm]
```

These equations follow PRÜFTECHNIK's reverse-indicator calculation method; see [**Methodology, geometric derivation, worked examples and limitations**](docs/METHODOLOGY.md). They are **not** the rim-and-face equations. In particular, a machine with **pure parallel offset** needs equal correction at both feet even when angularity is zero.

## Example (synthetic, not field data)

For `D = 100 mm`, `C = 40 mm`, `sF = 200 mm`, `sR = 600 mm`, vertical `S6-S12 = +0.40 mm` and `M6-M12 = -0.40 mm` (after sag correction), the slope is zero and coupling offset is `+0.20 mm`. **Both feet require −0.20 mm shim changes (remove shims).** The example assumes a consistent, physically verified measurement arrangement.

## Project layout

```text
alignment.py             Engineering equations, validation and result dataclasses
ui.py                    Streamlit interface with confirmations, plots and CSV
streamlit_app.py         Streamlit Community Cloud entry point
app.py                   Alternate/legacy deployment entry point
tests/test_alignment.py  Unit tests and independent interpolation check
docs/METHODOLOGY.md      Complete sign convention, equations, examples and sources
.github/workflows/       Windows/Linux Python test matrix
requirements.txt         UI dependencies
```

## Reliability and use restrictions

The unit tests cover pure offset, pure angularity, nonzero zeros, bracket-sag correction, horizontal sign convention, input checks, closure checking and independent line-interpolation equivalence. They do **not** constitute calibration or physical field verification. The user-selected 0.03 mm closure default is a **screening example**, not a published tolerance or equipment acceptance limit.

**Before moving any machine:** verify that indicator brackets, probe directions and mechanical assumptions match the convention; check soft foot, measured sag, machine constraints, piping strain, thermal-growth/cold targets, shaft runout, and manufacturer-specific tolerances; follow site procedures and confirm the result with a fresh measurement after adjustment.

### References

- [PRÜFTECHNIK *Engineer's Guide* (2017), reverse indicator method](https://0201.nccdn.net/1_2/000/000/190/be5/Pruftechnik-Engineers-Guide-2017.pdf) — reference geometry and equations.
- [PRÜFTECHNIK *A Practical Guide to Shaft Alignment* (2002)](https://backflowparts.com/wp-content/uploads/2021/06/Shaft_Alignment_Instructions.pdf) — measurement practices, dial closure and sag considerations.

This open-source project is independent and is **not affiliated with or endorsed by PRÜFTECHNIK**.

## License

Apache License 2.0; see [LICENSE](LICENSE).
