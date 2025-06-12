import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import io
from PIL import Image

st.set_page_config(page_title="Arc Optimizer Dashboard", layout="wide")

# --- Layout with logo on the top-right ---
col_logo, col_title = st.columns([1, 8])
with col_logo:
    logo = Image.open("images.png")
    st.image(logo, width=120)
with col_title:
    company_name = st.sidebar.text_input("Company Name", value="Your Company")
    st.title(f"{company_name} ⚡ Arc Optimizer – EAF Optimization Dashboard")

# --- Editable Parameters ---
st.sidebar.header("Furnace & Cost Settings")
tap_weight = st.sidebar.number_input("Tap Weight per Heat (tons)", value=145)
heats_per_day = st.sidebar.slider("Heats per Day", 1, 20, 8)
days_per_month = st.sidebar.slider("Working Days per Month", 1, 31, 26)
energy_baseline = st.sidebar.number_input("Electricity Consumption (kWh/ton)", value=296)

electricity_price = st.sidebar.number_input("Electricity Price (€/kWh)", value=0.10, step=0.01)
scrap_price = st.sidebar.number_input("Scrap Price (€/ton)", value=410)
software_cost = st.sidebar.number_input("Software Cost (€)", value=200000)

prediction_minutes = st.sidebar.slider("Prediction Horizon (minutes)", 1, 10, 5)
duration = st.sidebar.slider("Simulation Duration (minutes)", 10, 60, 30)

# --- Simulated Data ---
time = np.linspace(0, duration + prediction_minutes, (duration + prediction_minutes) * 4)
np.random.seed(0)
mpc_power = 91 + 1.5 * np.sin(0.25 * time + 0.5)
base_power = mpc_power + 1.5 + 0.8 * np.sin(0.35 * time) + 0.8 * np.random.randn(len(time))

# Split time ranges
live_end_index = int(duration * 4)
time_live = time[:live_end_index]
time_pred = time[live_end_index:]
live_base = base_power[:live_end_index]
live_mpc = mpc_power[:live_end_index]
pred_base = base_power[live_end_index:]
pred_mpc = mpc_power[live_end_index:]

# Calculate savings
energy_savings = np.clip(base_power - mpc_power, 0, None)
total_saved_kwh = np.trapz(energy_savings, time)
expected_saving_pct = (np.mean(energy_savings) / np.mean(base_power)) * 100

# --- Graph Output ---
st.subheader("Power Input: Live vs. Predicted with Energy Savings")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(time, base_power, '--', label="Without MPC", color="red")
ax.plot(time, mpc_power, '-', label="With MPC", color="green")
ax.fill_between(time, mpc_power, base_power, where=(base_power > mpc_power),
                interpolate=True, color='lightgreen', alpha=0.4, label="Energy Savings")

ax.set_xlabel("Time (minutes)")
ax.set_ylabel("Power Input (MW)")
ax.set_title("Live and Future Power Input with Predicted Savings")
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

# --- Downloadable Report ---
st.markdown("### 📄 Download Report")
data = pd.DataFrame({
    "Time (min)": time,
    "Power Without MPC (MW)": base_power,
    "Power With MPC (MW)": mpc_power,
    "Savings (MW)": energy_savings
})

csv_buffer = io.StringIO()
data.to_csv(csv_buffer, index=False)
st.download_button("🔍 Download CSV Report", csv_buffer.getvalue(), file_name="apc_prediction_report.csv", mime="text/csv")
