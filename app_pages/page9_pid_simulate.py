import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.title("PID Temperature Simulation")
st.write(
    "Simulate a PID controller maintaining a target temperature "
    "against environmental disturbances (constant drift + Brown noise)."
)

with st.sidebar:
    st.header("PID Gains")
    Kp = st.number_input("Kp (proportional)", value=0.0, step=0.1, format="%.2f")
    Ki = st.number_input("Ki (integral)", value=10.0, step=0.5, format="%.2f")
    Kd = st.number_input("Kd (derivative)", value=0.0, step=0.1, format="%.2f")

    st.header("Temperature")
    target_temp = st.number_input("Target temperature (°C)", value=70.0, step=1.0)
    initial_temp = st.number_input("Initial temperature (°C)", value=20.0, step=1.0)
    outside_temp = st.number_input("Outside temperature (°C)", value=10.0, step=1.0)

    st.header("Physics")
    insulation_factor = st.slider("Insulation factor", 0.001, 0.2, 0.05, 0.001, format="%.3f")
    heater_efficiency = st.slider("Heater efficiency", 0.01, 0.5, 0.1, 0.01)
    heater_max = st.number_input("Max heater power", value=100.0, step=10.0)

    st.header("Disturbances")
    drift_rate = st.number_input("Drift (°C/step)", value=-0.1, step=0.01, format="%.3f")
    noise_sigma = st.slider("Brown noise σ", 0.0, 2.0, 0.5, 0.01)

    st.header("Simulation")
    num_steps = st.number_input("Number of steps", value=200, min_value=10, max_value=5000, step=10)
    dt = st.number_input("Time step dt (s)", value=0.01, min_value=0.001, step=0.001, format="%.3f")
    seed = st.number_input("Random seed", value=42, min_value=0, step=1)


def run_simulation(Kp, Ki, Kd, target_temp, initial_temp, outside_temp,
                   insulation_factor, heater_efficiency, heater_max,
                   drift_rate, noise_sigma, num_steps, dt, seed):
    rng = np.random.default_rng(int(seed))

    time_history = np.zeros(num_steps)
    temp_history = np.zeros(num_steps)
    heater_history = np.zeros(num_steps)
    error_history = np.zeros(num_steps)

    current_temp = initial_temp
    integral = 0.0
    last_error = 0.0

    for step in range(num_steps):
        error = target_temp - current_temp
        integral += error * dt
        derivative = (error - last_error) / dt if step > 0 else 0.0

        output = Kp * error + Ki * integral + Kd * derivative
        heater_power = np.clip(output, 0.0, heater_max)

        heat_gain = heater_power * heater_efficiency
        heat_loss = (current_temp - outside_temp) * insulation_factor
        brown_noise = rng.normal(0.0, noise_sigma)

        current_temp += heat_gain - heat_loss + drift_rate + brown_noise

        time_history[step] = step * dt
        temp_history[step] = current_temp
        heater_history[step] = heater_power
        error_history[step] = error
        last_error = error

    return time_history, temp_history, heater_history, error_history


time_hist, temp_hist, heater_hist, error_hist = run_simulation(
    Kp, Ki, Kd, target_temp, initial_temp, outside_temp,
    insulation_factor, heater_efficiency, heater_max,
    drift_rate, noise_sigma, num_steps, dt, seed
)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=time_hist, y=temp_hist,
    mode='lines', line=dict(color='red', width=2),
    name='Actual Temperature'
))
fig.add_hline(
    y=target_temp, line_dash="dash", line_color="blue",
    annotation_text="Setpoint", annotation_position="top left"
)
fig.update_layout(
    title=f"PID Control vs. Disturbances (Kp={Kp}, Ki={Ki}, Kd={Kd})",
    xaxis_title="Time (s)",
    yaxis_title="Temperature (°C)",
    template="plotly_white",
    height=450,
    xaxis=dict(showgrid=True, gridwidth=1, gridcolor="lightgray", griddash="dash"),
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor="lightgray", griddash="dash"),
)
st.plotly_chart(fig, width='stretch')

# col1, col2 = st.columns(2)

# with col1:
fig_heater = go.Figure()
fig_heater.add_trace(go.Scatter(
    x=time_hist, y=heater_hist,
    mode='lines', line=dict(color='orange', width=2),
    name='Heater Power'
))
fig_heater.update_layout(
    title="Heater Output",
    xaxis_title="Time (s)",
    yaxis_title="Heater Power",
    template="plotly_white",
    height=450,
    xaxis=dict(showgrid=True, gridwidth=1, gridcolor="lightgray", griddash="dash"),
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor="lightgray", griddash="dash"),
)
st.plotly_chart(fig_heater, width='stretch')

# with col2:
fig_error = go.Figure()
fig_error.add_trace(go.Scatter(
    x=time_hist, y=error_hist,
    mode='lines', line=dict(color='purple', width=2),
    name='Error'
))
fig_error.add_hline(y=0, line_dash="dash", line_color="gray")
fig_error.update_layout(
    title="Error Signal (Setpoint - Actual)",
    xaxis_title="Time (s)",
    yaxis_title="Error (°C)",
    template="plotly_white",
    height=450,
    xaxis=dict(showgrid=True, gridwidth=1, gridcolor="lightgray", griddash="dash"),
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor="lightgray", griddash="dash"),
)
st.plotly_chart(fig_error, width='stretch')

with st.expander("Simulation Metrics"):
    steady_state = temp_hist[-num_steps // 4:]
    st.write(f"**Final temperature:** {temp_hist[-1]:.2f} °C")
    st.write(f"**Mean (last 25%):** {steady_state.mean():.2f} °C")
    st.write(f"**Std dev (last 25%):** {steady_state.std():.2f} °C")
    st.write(f"**Steady-state error:** {target_temp - steady_state.mean():.2f} °C")

with st.expander("PID Theory", expanded=False):
    st.markdown(r"""
### 1. $K_p$ : Proportional Gain

- **Also known as:** Proportional Band (sometimes inverted/expressed as a percentage in industrial systems).
- **What it does:** It multiplies the current error. A high $K_p$ makes the system respond aggressively to any deviation from the target, while a low $K_p$ makes the system sluggish.

### 2. $K_i$ : Integral Gain

- **Also known as:** Reset Gain.
- **Alternative form** ($T_i$): **Integral Time** or **Reset Time**. In many industrial controllers (like PLCs), instead of $K_i$, engineers use $T_i$, which represents how many minutes or seconds it takes for the integral action to match the proportional action.
- **What it does:** It multiplies the accumulated historical error to eliminate the final offset.

### 3. $K_d$ : Derivative Gain

- **Also known as:** Rate Gain.
- **Alternative form** ($T_d$): **Derivative Time** or **Rate Time**. Similar to the integral term, industrial systems often use $T_d$, which represents the time interval over which the controller predicts the error's trajectory.
- **What it does:** It multiplies the current rate of change of the error to act as a brake and prevent overshoot.

### The Standard PID Formula

When you look at the actual mathematical equation for a PID controller, you can see exactly how these gains scale each behavior:

$$u(t) = K_p e(t) + K_i \int_0^t e(\tau) d\tau + K_d \frac{de(t)}{dt}$$

Where:

- $u(t)$ is the control output (e.g., how much voltage to send to a motor).
- $e(t)$ is the current error ($Target - Actual$).
""")
