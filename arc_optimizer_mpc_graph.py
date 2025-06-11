
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Arc Optimizer: MPC vs Non-MPC", layout="wide")

st.title("📊 Arc Optimizer – MPC vs Non-MPC Power Profile Demo")

st.markdown("""
This interactive demo allows you to visualize the effect of using Model Predictive Control (MPC) over time.
You can adjust the simulation time window to see how the control profiles differ.
""")

# Simulation parameters
duration = st.slider("Simulation Time (minutes)", min_value=10, max_value=60, value=30, step=5)

time = np.linspace(0, duration, duration * 4)  # 4 points per minute
base_power = 90 + 5 * np.sin(0.3 * time)      # Non-MPC: sinusoidal fluctuations
mpc_power = 90 + 2 * np.sin(0.3 * time + 0.5)  # MPC: smoother response

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(time, base_power, label="MPC OFF", linestyle='--', color="red")
ax.plot(time, mpc_power, label="MPC ON", linestyle='-', color="green")

ax.set_title("Electrode Power vs Time")
ax.set_xlabel("Time (minutes)")
ax.set_ylabel("Power Input (MW)")
ax.legend()
ax.grid(True)

st.pyplot(fig)
