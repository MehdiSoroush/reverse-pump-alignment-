import streamlit as st
import pandas as pd

st.title("🔧 Reverse Dial Alignment Calculator")

st.markdown("Enter your dial indicator readings and machine distances below:")

# Input fields
A12 = st.number_input("Dial A at 12 o'clock (Top) [mm]", value=0.0)
A6 = st.number_input("Dial A at 6 o'clock (Bottom) [mm]", value=0.0)
B12 = st.number_input("Dial B at 12 o'clock (Top) [mm]", value=0.0)
B6 = st.number_input("Dial B at 6 o'clock (Bottom) [mm]", value=0.0)
A9 = st.number_input("Dial A at 9 o'clock (Left) [mm]", value=0.0)
A3 = st.number_input("Dial A at 3 o'clock (Right) [mm]", value=0.0)
B9 = st.number_input("Dial B at 9 o'clock (Left) [mm]", value=0.0)
B3 = st.number_input("Dial B at 3 o'clock (Right) [mm]", value=0.0)
D1 = st.number_input("Distance between indicators A and B [mm]", value=100.0)
D2 = st.number_input("Distance from near dial to coupling center [mm]", value=50.0)
D3 = st.number_input("Distance from coupling center to front feet [mm]", value=200.0)
D4 = st.number_input("Distance from front feet to rear feet [mm]", value=400.0)

# --- Calculations ---
ΔA_vertical = A12 - A6
ΔB_vertical = B12 - B6
Angular_Vertical = (ΔA_vertical - ΔB_vertical) / D1 if D1 != 0 else 0
Offset_Vertical = ΔB_vertical - (Angular_Vertical * D2)
Correction_Front_Vertical = Angular_Vertical * D3
Correction_Rear_Vertical = Angular_Vertical * (D3 + D4)

ΔA_horizontal = A9 - A3
ΔB_horizontal = B9 - B3
Angular_Horizontal = (ΔA_horizontal - ΔB_horizontal) / D1 if D1 != 0 else 0
Offset_Horizontal = ΔB_horizontal - (Angular_Horizontal * D2)
Correction_Front_Horizontal = Angular_Horizontal * D3
Correction_Rear_Horizontal = Angular_Horizontal * (D3 + D4)

# --- Results table ---
results = {
    "ΔA_vertical": ΔA_vertical,
    "ΔB_vertical": ΔB_vertical,
    "Angular_Vertical": Angular_Vertical,
    "Offset_Vertical": Offset_Vertical,
    "Correction_Front_Vertical": Correction_Front_Vertical,
    "Correction_Rear_Vertical": Correction_Rear_Vertical,
    "ΔA_horizontal": ΔA_horizontal,
    "ΔB_horizontal": ΔB_horizontal,
    "Angular_Horizontal": Angular_Horizontal,
    "Offset_Horizontal": Offset_Horizontal,
    "Correction_Front_Horizontal": Correction_Front_Horizontal,
    "Correction_Rear_Horizontal": Correction_Rear_Horizontal
}

df = pd.DataFrame(results.items(), columns=["Parameter", "Value"])
st.subheader("📊 Results")
st.dataframe(df)

# Download option
st.download_button(
    "Download results as CSV",
    df.to_csv(index=False),
    "alignment_results.csv",
    "text/csv"
)

# --- Legend / Explanations ---
st.subheader("📖 Legend: What Each Parameter Means")

legend = {
    "A12": "Dial A at 12 o’clock (top) position",
    "A6": "Dial A at 6 o’clock (bottom) position",
    "B12": "Dial B at 12 o’clock (top) position",
    "B6": "Dial B at 6 o’clock (bottom) position",
    "A9": "Dial A at 9 o’clock (left side)",
    "A3": "Dial A at 3 o’clock (right side)",
    "B9": "Dial B at 9 o’clock (left side)",
    "B3": "Dial B at 3 o’clock (right side)",
    "D1": "Span between the two indicators (A to B)",
    "D2": "Distance from near dial to coupling center",
    "D3": "Distance from coupling center to front feet",
    "D4": "Distance from front feet to rear feet",
    "ΔA_vertical": "Difference in A readings top vs bottom",
    "ΔB_vertical": "Difference in B readings top vs bottom",
    "Angular_Vertical": "Slope of vertical misalignment (mm/mm)",
    "Offset_Vertical": "Vertical offset at coupling center",
    "Correction_Front_Vertical": "Shim/slide needed at front feet (vertical)",
    "Correction_Rear_Vertical": "Shim/slide needed at rear feet (vertical)",
    "ΔA_horizontal": "Difference in A readings left vs right",
    "ΔB_horizontal": "Difference in B readings left vs right",
    "Angular_Horizontal": "Slope of horizontal misalignment (mm/mm)",
    "Offset_Horizontal": "Horizontal offset at coupling center",
    "Correction_Front_Horizontal": "Shim/slide needed at front feet (horizontal)",
    "Correction_Rear_Horizontal": "Shim/slide needed at rear feet (horizontal)"
}

for key, desc in legend.items():
    st.markdown(f"**{key}** → {desc}")