import time
import random
import matplotlib.pyplot as plt

class PIDController:
    def __init__(self, Kp, Ki, Kd, setpoint):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint

        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = time.time()

    def update(self, current_value):
        current_time = time.time()
        dt = current_time - self.last_time
        if dt <= 0:
            dt = 1e-3  # Prevent division by zero

        # 1. Calculate Error
        error = self.setpoint - current_value

        # 2. Calculate Integral
        self.integral += error * dt

        # 3. Calculate Derivative
        derivative = (error - self.last_error) / dt

        # Compute total control output
        output = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)

        # Save state for next iteration
        self.last_error = error
        self.last_time = current_time

        return output

def simulate_system():
    # 1. Initialize PID
    # We increased Kd slightly here to help fight the unpredictable Brown noise
    Kp = 0.0
    Ki = 10
    Kd = 0.0
    target_temp = 70.0

    pid = PIDController(Kp, Ki, Kd, setpoint=target_temp)

    # Simulation and physics variables
    current_temp = 20.0
    outside_temp = 10.0
    insulation_factor = 0.05

    # Tracking data for plotting
    time_history = []
    temp_history = []
    target_history = []

    print("Simulating PID loop with noise and drift for 200 steps...")

    # Run simulation loop for 200 iterations to see the drift take effect
    for step in range(200):
        time.sleep(0.01)

        # Get the controller's decision
        heater_power = pid.update(current_temp)
        heater_power = max(0.0, min(100.0, heater_power))

        # Standard physics: heat gain and loss
        heat_gain = heater_power * 0.1
        heat_loss = (current_temp - outside_temp) * insulation_factor

        # --- NEW: ENVIRONMENTAL DISTURBANCES ---
        # 1. Constant Drift: A persistent drop of 0.1 degrees per step
        drift = -0.1

        # 2. Brown Noise: Adding a random Gaussian step to the rate of change
        # creates a random walk (Brown noise) in the absolute temperature.
        brown_noise_step = random.gauss(mu=0.0, sigma=0.5)

        # Update current temperature with all factors
        current_temp += heat_gain - heat_loss + drift + brown_noise_step

        # Record history
        time_history.append(step)
        temp_history.append(current_temp)
        target_history.append(target_temp)

    # --- PLOT THE RESULTS ---
    plt.figure(figsize=(10, 5))
    plt.plot(time_history, temp_history, label='Actual Temp (with Noise & Drift)', color='red', linewidth=2)
    plt.axhline(y=target_temp, color='blue', linestyle='--', label='Target (Setpoint)')

    plt.title(f'PID Control vs. Disturbances (Kp={Kp}, Ki={Ki}, Kd={Kd})')
    plt.xlabel('Time Steps')
    plt.ylabel('Temperature (°C)')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    simulate_system()