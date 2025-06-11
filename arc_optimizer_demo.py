
import streamlit as st

st.set_page_config(page_title="Arc Optimizer Demo", layout="centered")

st.title("⚡ Arc Optimizer – EAF Efficiency Demo")
st.markdown("This demo estimates potential energy savings and power-on time improvements in Electric Arc Furnaces (EAFs) using the Arc Optimizer control model.")

st.header("Input Parameters")

tap_weight = st.number_input("Tap Weight (tons)", value=145)
hot_heel = st.number_input("Hot Heel (tons)", value=15)
elec_consumption = st.number_input("Current Electrical Consumption (kWh/ton)", value=296)
burners = st.number_input("Number of Burners", value=7)
nat_gas = st.number_input("Natural Gas Usage (m³/ton)", value=8)
carbon_injected = st.number_input("Carbon Injected (kg/ton)", value=13)
charged_lime = st.number_input("Charged Lime (kg/ton)", value=52.5)
charged_dolomite = st.number_input("Charged Dolomite (kg/ton)", value=7)
power_on_time = st.number_input("Current Power-On Time (min)", value=32)

st.header("Predicted Optimized Results")

base_energy = tap_weight * elec_consumption
hotheel_energy = hot_heel * elec_consumption
slag_energy = tap_weight * ((charged_lime * 0.4 + charged_dolomite * 0.3) / 1000)
chem_energy = tap_weight * (nat_gas * 9 + carbon_injected * 2)
burner_factor = 0.9 if burners >= 5 else 1.0

net_energy = (base_energy - hotheel_energy + slag_energy - chem_energy) * burner_factor
optimized_elec_per_ton = net_energy / tap_weight
optimized_pot = max(power_on_time - 2, 28)

st.success(f"🔋 Optimized Electrical Energy per ton: {optimized_elec_per_ton:.2f} kWh/ton")
st.success(f"⏱️ Optimized Power-On Time: {optimized_pot:.1f} minutes")
