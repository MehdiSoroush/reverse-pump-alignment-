import streamlit as st
import pandas as pd

st.title("Reverse Dial Alignment Calculator")

# Input fields
A12 = st.number_input("Dial A at 12 o'clock (Top) [mm]", value=0.0)
A6 = st.number_input("Dial A at 6 o'clock (Bottom) [mm]", value=0.0)
B12 = st.number_input("Dial B at 12 o'clock (Top) [mm]", value=0.0)
B6 = st.number_input("Dial B at 6 o'clock (Bottom) [mm]", value=0.0)
A9 = st.number_input("Dial A at 9 o'clock (Left) [mm]", value=0.0)
A3 = st.number_input("Dial A at 3 o'clock (Right) [mm]", value=0.0)
B9 = st.number_input("Dial B at 9 o'clock (Left) [mm]", value=0.0)
B3 = st.number_input("Dial B at 3 o'clock (Right) [mm]", value=0.0)
D1 = st.number_input("Distance between A and B [mm]", value=100.0)
D2 = st.number_input("Distance near dial to coupling center [mm]", value=50.0)
D3 = st.number_input("Distance coupling center to front feet [mm]", value=200.0)
D4 = st.number_input("Distance front to rear feet [mm]", value=400.0)

# Calculations
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

# Show results
st.subheader("Results")
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
st.dataframe(pd.DataFrame(results.items(), columns=["Parameter", "Value"]))

# Optional: Download as Excel
df = pd.DataFrame(results.items(), columns=["Parameter", "Value"])
st.download_button("Download Excel", df.to_csv(index=False), "alignment_results.csv")
