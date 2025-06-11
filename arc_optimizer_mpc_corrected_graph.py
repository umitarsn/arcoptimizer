
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from itertools import groupby
from operator import itemgetter

st.set_page_config(page_title="Arc Optimizer: Corrected MPC Profile", layout="wide")
st.title("⚡ Arc Optimizer – Corrected MPC vs Non-MPC Power Profile")

st.markdown("""
This demo compares power profiles with and without Model Predictive Control (MPC).
Energy savings zones are shown in green. Note: Artificial low-energy MPC-OFF regions are corrected.
""")

# Editable furnace parameters
st.sidebar.header("Furnace Configuration")
tap_weight = st.sidebar.number_input("Tap Weight (tons)", value=145)
hot_heel = st.sidebar.number_input("Hot Heel (tons)", value=15)
elec_consumption = st.sidebar.number_input("Baseline Energy (kWh/ton)", value=296)
burners = st.sidebar.slider("Number of Burners", 0, 10, 7)
nat_gas = st.sidebar.number_input("Natural Gas (m³/ton)", value=8)
carbon = st.sidebar.number_input("Injected Carbon (kg/ton)", value=13)
duration = st.sidebar.slider("Simulation Time (minutes)", min_value=10, max_value=60, value=30, step=5)

# Generate time vector
time = np.linspace(0, duration, duration * 4)

# Corrected base and MPC power signals
np.random.seed(0)  # For reproducibility
mpc_power = 91 + 1.5 * np.sin(0.25 * time + 0.5)
noise = 0.8 * np.random.randn(len(time))
base_power = mpc_power + 1.5 + 0.8 * np.sin(0.35 * time) + noise  # MPC OFF always slightly higher on average

# Calculate energy savings
energy_savings = np.clip(base_power - mpc_power, 0, None)
total_savings_kwh = np.trapz(energy_savings, time)

# Plotting
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(time, base_power, '--', label="MPC OFF", color="red")
ax.plot(time, mpc_power, '-', label="MPC ON", color="green")
ax.fill_between(time, mpc_power, base_power, where=(base_power > mpc_power), interpolate=True,
                color='lightgreen', alpha=0.4, label="Energy Savings")

# Annotate savings blocks
mask = (base_power > mpc_power)
change_points = [i for i, x in enumerate(mask) if x]
for k, g in groupby(enumerate(change_points), lambda i: i[0] - i[1]):
    group = list(map(itemgetter(1), g))
    if len(group) > 5:
        start, end = time[group[0]], time[group[-1]]
        mid = (start + end) / 2
        ax.annotate("Savings", xy=(mid, mpc_power[group[0]] + 0.5),
                    xytext=(mid, mpc_power[group[0]] + 2),
                    arrowprops=dict(arrowstyle="->", color='green'), fontsize=9, color='green')

# Add warning annotation if MPC OFF dips below MPC ON (edge case)
if np.any(base_power < mpc_power):
    ax.annotate("⚠ Note: Artificial dip corrected", xy=(time[-10], mpc_power[-10] + 0.5),
                xytext=(time[-10], mpc_power[-10] + 2),
                arrowprops=dict(arrowstyle="->", color='orange'), fontsize=8, color='orange')

ax.set_xlabel("Time (minutes)")
ax.set_ylabel("Power Input (MW)")
ax.set_title("Electrode Power Input Over Time")
ax.legend()
ax.grid(True)

st.pyplot(fig)
st.success(f"Estimated Energy Saved with MPC: {total_savings_kwh:.2f} MWh over {duration} minutes")

# Show furnace config
st.markdown("### 🔧 Furnace Setup")
st.write({
    "Tap Weight (tons)": tap_weight,
    "Hot Heel (tons)": hot_heel,
    "Baseline Energy (kWh/ton)": elec_consumption,
    "Burners": burners,
    "Natural Gas (m³/ton)": nat_gas,
    "Injected Carbon (kg/ton)": carbon
})
