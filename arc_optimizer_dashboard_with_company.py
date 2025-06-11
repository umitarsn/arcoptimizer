
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from itertools import groupby
from operator import itemgetter

st.set_page_config(page_title="Arc Optimizer Dashboard", layout="wide")

# --- Editable Company Name ---
company_name = st.sidebar.text_input("Company Name", value="Your Company")

st.title(f"{company_name} ⚡ Arc Optimizer – EAF Optimization Dashboard")

# --- Editable Parameters ---
st.sidebar.header("Furnace & Cost Settings")
tap_weight = st.sidebar.number_input("Tap Weight per Heat (tons)", value=145)
heats_per_day = st.sidebar.slider("Heats per Day", 1, 20, 8)
days_per_month = st.sidebar.slider("Working Days per Month", 1, 31, 26)
energy_baseline = st.sidebar.number_input("Electricity Consumption (kWh/ton)", value=296)
expected_saving_pct = st.sidebar.slider("Energy Saving (%)", 2.0, 10.0, 5.0)

electricity_price = st.sidebar.number_input("Electricity Price (€/kWh)", value=0.10, step=0.01)
scrap_price = st.sidebar.number_input("Scrap Price (€/ton)", value=410)
software_cost = st.sidebar.number_input("Software Cost (€)", value=200000)

duration = st.sidebar.slider("Simulation Duration (minutes)", 10, 60, 30)

# --- Simulated MPC Curve ---
time = np.linspace(0, duration, duration * 4)
np.random.seed(0)
mpc_power = 91 + 1.5 * np.sin(0.25 * time + 0.5)
base_power = mpc_power + 1.5 + 0.8 * np.sin(0.35 * time) + 0.8 * np.random.randn(len(time))

energy_savings = np.clip(base_power - mpc_power, 0, None)
total_saved_kwh = np.trapz(energy_savings, time)

# --- Graph Output ---
st.subheader("Electrode Power Profile with MPC")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(time, base_power, '--', label="MPC OFF", color="red")
ax.plot(time, mpc_power, '-', label="MPC ON", color="green")
ax.fill_between(time, mpc_power, base_power, where=(base_power > mpc_power),
                interpolate=True, color='lightgreen', alpha=0.4, label="Energy Savings")

mask = (base_power > mpc_power)
change_points = [i for i, x in enumerate(mask) if x]
for k, g in groupby(enumerate(change_points), lambda i: i[0] - i[1]):
    group = list(map(itemgetter(1), g))
    if len(group) > 5:
        mid = time[group[len(group)//2]]
        ax.annotate("Savings", xy=(mid, mpc_power[group[len(group)//2]] + 0.5),
                    xytext=(mid, mpc_power[group[len(group)//2]] + 2),
                    arrowprops=dict(arrowstyle="->", color='green'), fontsize=9, color='green')

ax.set_xlabel("Time (minutes)")
ax.set_ylabel("Power Input (MW)")
ax.set_title("Electrode Power Input Over Time")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# --- KPI Table ---
st.markdown("### 🔍 Optimization Gains Summary")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("⚡ Energy Savings", f"{expected_saving_pct:.1f} %")
with col2:
    st.metric("⏱️ Power-On Time Reduction", "6.2 %")
with col3:
    st.metric("🧱 Refractory Life Extension", "4.0 %")

# --- ROI Table ---
st.markdown("### 💰 Investment Return Summary")

monthly_tons = tap_weight * heats_per_day * days_per_month
monthly_energy_baseline = monthly_tons * energy_baseline
monthly_kwh_saved = monthly_energy_baseline * (expected_saving_pct / 100)
monthly_eur_saved = monthly_kwh_saved * electricity_price
roi_months = software_cost / monthly_eur_saved if monthly_eur_saved else float("inf")

col4, col5, col6 = st.columns(3)
with col4:
    st.metric("Monthly Savings", f"{monthly_eur_saved:,.0f} €")
with col5:
    st.metric("Production", f"{monthly_tons:,.0f} tons/month")
with col6:
    st.metric("ROI", f"{roi_months:.1f} months")
