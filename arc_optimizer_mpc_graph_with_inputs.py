
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from itertools import groupby
from operator import itemgetter

st.set_page_config(page_title="Arc Optimizer: MPC Energy Profile", layout="wide")
st.title("⚡ Arc Optimizer – EAF MPC Simulation with Editable Furnace Info")

# Sidebar: Editable Furnace Inputs
st.sidebar.header("Furnace Configuration")
tap_weight = st.sidebar.number_input("Tap Weight (tons)", value=145)
hot_heel = st.sidebar.number_input("Hot Heel (tons)", value=15)
elec_consumption = st.sidebar.number_input("Baseline Energy (kWh/ton)", value=296)
burners = st.sidebar.slider("Number of Burners", 0, 10, 7)
nat_gas = st.sidebar.number_input("Natural Gas (m³/ton)", value=8)
carbon = st.sidebar.number_input("Injected Carbon (kg/ton)", value=13)

st.sidebar.markdown("---")
duration = st.sidebar.slider("Simulation Time (minutes)", min_value=10, max_value=60, value=30, step=5)

# Generate curves
time = np.linspace(0, duration, duration * 4)
base_power = 91 + 2.5 * np.sin(0.25 * time) + 0.5 * np.random.randn(len(time))  # MPC OFF
mpc_power = 91 + 1.5 * np.sin(0.25 * time + 0.5)  # MPC ON

# Energy savings calculation
energy_savings = base_power - mpc_power
total_savings_kwh = np.trapz(energy_savings[energy_savings > 0], time[energy_savings > 0])

# Plotting
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(time, base_power, '--', label="MPC OFF", color="red")
ax.plot(time, mpc_power, '-', label="MPC ON", color="green")
ax.fill_between(time, mpc_power, base_power, where=(base_power > mpc_power), interpolate=True,
                color='lightgreen', alpha=0.4, label="Energy Savings")

# Annotate significant savings blocks
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

ax.set_xlabel("Time (minutes)")
ax.set_ylabel("Power Input (MW)")
ax.set_title("Electrode Power vs Time")
ax.legend()
ax.grid(True)

st.pyplot(fig)

st.success(f"Estimated Energy Saved with MPC: {total_savings_kwh:.2f} MWh over {duration} minutes")

# Show furnace config summary
st.markdown("### 🔧 Current Furnace Configuration")
st.write({
    "Tap Weight (tons)": tap_weight,
    "Hot Heel (tons)": hot_heel,
    "Energy (kWh/ton)": elec_consumption,
    "Burners": burners,
    "Natural Gas (m³/ton)": nat_gas,
    "Carbon Injected (kg/ton)": carbon
})
