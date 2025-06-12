import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import io
from PIL import Image

st.set_page_config(page_title="Arc Optimizer Dashboard", layout="wide")

# --- Layout with logo aligned top-right over full app ---
logo = Image.open("images.png")
st.markdown("""
    <div style='display: flex; justify-content: flex-end;'>
        <img src='data:image/png;base64,""" + st.image(logo, output_format="PNG", use_column_width=False).image_data.tobytes().hex() + """' width='120'/>
    </div>
    """, unsafe_allow_html=True)

# --- Fixed Company Name ---
company_name = "HABAS"
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

# Recalculate only future segment for prediction horizon
time_pred = time[-prediction_minutes * 4:]
pred_base = base_power[-prediction_minutes * 4:]
pred_mpc = mpc_power[-prediction_minutes * 4:]

# Calculate savings on predicted data
energy_savings = np.clip(pred_base - pred_mpc, 0, None)
total_saved_kwh = np.trapz(energy_savings, time_pred)
expected_saving_pct = (np.mean(energy_savings) / np.mean(pred_base)) * 100 if np.mean(pred_base) != 0 else 0

# --- Graph Output ---
st.subheader("Predicted Power Input with Energy Savings")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(time_pred, pred_base, '--', label="Without MPC", color="red")
ax.plot(time_pred, pred_mpc, '-', label="With MPC", color="green")
ax.fill_between(time_pred, pred_mpc, pred_base, where=(pred_base > pred_mpc),
                interpolate=True, color='lightgreen', alpha=0.4, label="Predicted Energy Savings")

ax.set_xlabel("Time (minutes)")
ax.set_ylabel("Power Input (MW)")
ax.set_title("Future Power Prediction Only (Based on Selected Horizon)")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# --- KPI Table ---
st.markdown("### 🔍 Optimization Gains Summary")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("⚡ Predicted Energy Savings", f"{expected_saving_pct:.1f} %")
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
    "Time (min)": time_pred,
    "Power Without MPC (MW)": pred_base,
    "Power With MPC (MW)": pred_mpc,
    "Savings (MW)": energy_savings
})

csv_buffer = io.StringIO()
data.to_csv(csv_buffer, index=False)
st.download_button("🔍 Download CSV Report", csv_buffer.getvalue(), file_name="apc_prediction_report.csv", mime="text/csv")
