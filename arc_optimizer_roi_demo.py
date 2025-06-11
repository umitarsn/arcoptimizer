
import streamlit as st
import numpy as np

st.set_page_config(page_title="Arc Optimizer – ROI Calculator", layout="wide")
st.title("📈 Arc Optimizer – ROI and Savings Simulation")

# Sidebar: Furnace configuration
st.sidebar.header("Furnace Configuration")
tap_weight = st.sidebar.number_input("Tap Weight per Heat (tons)", value=145)
heats_per_day = st.sidebar.slider("Heats per Day", 1, 20, 8)
working_days_per_month = st.sidebar.slider("Working Days per Month", 1, 31, 26)
energy_baseline = st.sidebar.number_input("Current Electricity Consumption (kWh/ton)", value=296)
expected_saving_rate = st.sidebar.slider("Expected Energy Saving (%)", 2.0, 10.0, 5.0)

# Editable price assumptions
st.sidebar.header("Price Inputs")
electricity_price = st.sidebar.number_input("Electricity Price (EUR/kWh)", value=0.10, step=0.01)
scrap_price = st.sidebar.number_input("Scrap Price (EUR/ton)", value=410)
software_cost = st.sidebar.number_input("Software Investment Cost (EUR)", value=200000)

# --- Calculations ---
total_tons_per_month = tap_weight * heats_per_day * working_days_per_month
baseline_energy = total_tons_per_month * energy_baseline
saved_energy_kwh = baseline_energy * (expected_saving_rate / 100)
monthly_energy_savings_eur = saved_energy_kwh * electricity_price

roi_months = software_cost / monthly_energy_savings_eur if monthly_energy_savings_eur > 0 else float("inf")

# --- Results Display ---
st.subheader("🔍 Monthly Impact Summary")
col1, col2 = st.columns(2)
with col1:
    st.metric("Monthly Production", f"{total_tons_per_month:,.0f} tons")
    st.metric("Baseline Energy Use", f"{baseline_energy:,.0f} kWh")
    st.metric("Energy Saved", f"{saved_energy_kwh:,.0f} kWh")
with col2:
    st.metric("Energy Savings (EUR)", f"{monthly_energy_savings_eur:,.0f} €")
    st.metric("Software Cost", f"{software_cost:,.0f} €")
    st.metric("ROI (months)", f"{roi_months:.1f}")

st.info("📌 ROI shows how long it will take for Arc Optimizer to pay for itself through energy savings alone.")
