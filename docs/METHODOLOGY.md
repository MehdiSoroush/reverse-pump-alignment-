# Reverse-dial indicator method: formulation, assumptions, and verification

## Scope

This calculator determines cold, relative shaft alignment at the coupling and the *theoretical rigid-body adjustment* at the feet of the movable machine. It implements the **reverse-rim (two radial indicator)** configuration described in PRÜFTECHNIK's *Engineer's Guide* (2017), section "Reverse indicator method – by calculation". It does **not** implement a rim-and-face method, estimate thermal growth, certify machine acceptance, or predict loaded shaft bending.

## Measurement and geometry convention

```
stationary machine (pump)                  movable machine (motor)
       S indicator     coupling    M indicator     FRONT feet      REAR feet
       |---------------|-----------|---------------|----------------|
       x=0             x=C         x=D        x=C+sF          x=C+sR
```

The drawing is schematic, **not to scale**. S and M label *measurement planes*, not bracket anchor locations. Each indicator contacts the opposing shaft; the mounting and polarity must conform to the reference method. The viewpoint is from the **movable machine toward the stationary machine**. At 3 o'clock the probe is on the observer's right, at 9 o'clock on the left. Positive dial readings represent probe compression. Both shafts rotate together through all four positions. All inputs and outputs are millimetres unless explicitly noted.

- `D`: distance between the S and M indicator measurement planes, `D > 0`.
- `C`: distance from S to the coupling centre, `0 <= C <= D`.
- `sF`, `sR`: positive axial distances from coupling centre to the front and rear feet of the movable machine, `0 <= sF < sR`.
- `S12`, `S3`, `S6`, `S9`: signed S dial readings at 12, 3, 6 and 9 o'clock; similarly M.
- `sagS`, `sagM`: signed **6-minus-12** apparent readings due to bracket sag alone, measured separately in the same gauge configuration; not absolute deflection magnitudes.

## Equations

Correct the vertical total indicated readings (TIR) for bracket sag:

\[
T_S^V = S_6 - S_{12} - sag_S,\quad T_M^V = M_6 - M_{12} - sag_M.
\]

The horizontal quantities follow the manufacturer convention:

\[
T_S^H = S_9-S_3,\quad T_M^H = M_9-M_3.
\]

For either plane, substituting the appropriate `T_S` and `T_M`:

\[
A = \frac{T_S+T_M}{2D}, \qquad O = \frac{T_S}{2}-A C.
\]

`O` is the signed offset at the **coupling centre** in mm; `A` is the signed angularity as a small-angle slope in mm/mm (multiply by 100 to show mm/100 mm). Full total-indicator readings are **not** shaft-centre offsets: divide diametral TIR by two.

The signed *relative centreline offset curve* at axial station `x` measured from the coupling is

\[
y(x) = O - A x.
\]

The requested rigid-body correction of the movable machine at each foot is therefore

\[
\boxed{move_F=A s_F-O,\qquad move_R=A s_R-O.}
\]

Positive vertical result = **add shims**; negative = remove shims. Positive horizontal result = move **toward 3 o'clock** as viewed from the motor toward the pump; negative = toward 9 o'clock. Signs require the physical probe orientation to match this convention. If the actual mounting reverses a reading's sign, **do not use the results** without re-establishing the proper mapping.

An independent way to check the algebra is to interpolate the relative offsets at the two indicator planes:

\[
y_S=T_S/2,\qquad y_M=-T_M/2,\qquad
 y(x_{\rm from\,S})=y_S+\frac{y_M-y_S}{D}\,x_{\rm from\,S}.
\]

The foot correction is the **negative** of `y(C + sF)` or `y(C + sR)`. This is equivalent to the equations above and is covered by an automated regression test.

## Worked synthetic examples (NOT field measurements)

Geometry: `D=100 mm`, `C=40 mm`, `sF=200 mm`, `sR=600 mm`. Sag is assumed already zero/corrected **for these synthetic cases only**.

1. **Pure parallel vertical offset:** `S6-S12=+0.40 mm`, `M6-M12=-0.40 mm`. Then `A=0`, `O=+0.20 mm`, and both feet require `-0.20 mm` (**remove shims**). This case reveals the serious fault in the old code: its angularity-only corrections gave zero.
2. **Pure vertical angle at coupling:** `S6-S12=+0.08 mm`, `M6-M12=+0.12 mm`. Then `A=+0.001 mm/mm` (0.10 mm/100 mm), `O=0`, and movements at the front and rear feet are respectively `+0.20 mm` and `+0.60 mm` (add shims).
3. **Bracket sag:** if an observed `S6-S12=+0.50 mm` includes `+0.10 mm` of sag contribution, use `sagS=+0.10 mm`. The corrected reading is `+0.40 mm`, *not* `+0.60 mm`.

## Four-position closure and input checks

For an ideal radial reading sequence with a consistent zero and instrument orientation,

\[
S_{12}+S_6 \approx S_3+S_9
\]

(and likewise for M). The app reports `(top+bottom)-(right+left)` for each indicator. A user-selected **illustrative** threshold of 0.03 mm is the default; this is a measurement screening threshold, **not an OEM or API acceptance criterion**. If exceeded, the app withholds corrections pending remeasurement. Actual uncertainty must consider resolution, dial sensitivity, bracket sag, mounting play, runout and repeatability; a passing closure check alone proves none of these conditions.

Any invalid geometry, non-finite input, or negative closure limit is rejected. Both completion/geometry confirmation boxes must be checked before corrections are shown. The program cannot confirm the physical bracket mounting or whether a technician recorded readings correctly.

## Verification evidence and limitations

The unit test suite (`python -m pytest -q`) checks zero readings, nonzero top reference, pure parallel offset in both planes, pure angularity, sag subtraction, failure of dial closure, independent interpolation and invalid-geometry handling. These are **analytical/synthetic checks**, not comparisons with recorded machinery or calibrated instruments. No machine was measured or moved to validate the implementation.

Further limitations: rigid-straight shaft centreline approximation; assumes a stationary left machine and a right machine that can be moved; ignores soft foot, coupling backlash, thermal growth, pipe strain, mechanical looseness, dial calibration, bearing clearance, shaft runout, casing deflection, and shaft bending. Cold offsets may be deliberate targets and not a failure. **Do not declare an alignment acceptable based solely on these computed movements.** OEM/project criteria and qualified personnel govern on-site procedures.

## Sources

1. PRÜFTECHNIK, *An Engineer's Guide to Shaft Alignment, Vibration Analysis, Dynamic Balancing and Wear Debris Analysis*, document ALI 9.600.G, Edition 12, September 2017, "Reverse indicator method – by calculation", pp. 45–47. [PDF](https://0201.nccdn.net/1_2/000/000/190/be5/Pruftechnik-Engineers-Guide-2017.pdf).
2. PRÜFTECHNIK LTD, *A Practical Guide to Shaft Alignment*, Edition 4 (2002), pp. 41–43, reverse-indicator calculation and sag checks. [PDF](https://backflowparts.com/wp-content/uploads/2021/06/Shaft_Alignment_Instructions.pdf).

The implementation uses the published method with the explicitly stated conventions above; it is **not** affiliated with or endorsed by PRÜFTECHNIK. Manufacturer documents are linked rather than reproduced.
