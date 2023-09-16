import random
import time
import matplotlib.pyplot as plt


class PVAgent:
    def __init__(self, max_generation):
        self.max_generation = max_generation

    def generate_solar_energy(self):
        solar_energy = random.uniform(0, self.max_generation)
        return solar_energy


class WindAgent:
    def __init__(self, max_generation):
        self.max_generation = max_generation

    def generate_wind_energy(self):
        wind_energy = random.uniform(0, self.max_generation)
        return wind_energy


class ESSAgent:
    def __init__(self, max_capacity):
        self.max_capacity = max_capacity
        self.energy_stored = []
        self.cumulative_energy_consumed = 0  # Total energy consumed from ESS

    def store_energy(self, energy):
        if sum(self.energy_stored) + energy <= self.max_capacity:
            self.energy_stored.append(energy)
            return True
        else:
            return False

    def consume_energy(self, demand):
        available_energy = sum(self.energy_stored)
        if available_energy >= demand:
            consumed_energy = demand
            self.energy_stored.pop(0)
        else:
            consumed_energy = available_energy
            self.energy_stored.clear()

        self.cumulative_energy_consumed += consumed_energy
        return consumed_energy


class InverterAgent:
    def __init__(self, efficiency):
        self.efficiency = efficiency

    def convert_dc_to_ac(self, dc_power):
        ac_power = dc_power * self.efficiency
        return ac_power


class CriticalAgent:
    def __init__(self, demand):
        self.demand = demand
        self.energy_consumed = []

    def consume_energy(self, available_energy):
        consumed_energy = min(self.demand, available_energy)
        self.energy_consumed.append(consumed_energy)
        return consumed_energy


class NonCriticalAgent:
    def __init__(self, demand):
        self.demand = demand
        self.energy_consumed = []

    def consume_energy(self, available_energy):
        consumed_energy = min(self.demand, available_energy)
        self.energy_consumed.append(consumed_energy)
        return consumed_energy


# Constants
total_time_steps = 25
pv_capacity = 180.0
wind_capacity = 100.0
ess_capacity = 500.0
inverter_efficiency = 0.95
critical_demand = 180
non_critical_demand = 260

pv_panel = PVAgent(max_generation=pv_capacity)
wind_turbine = WindAgent(max_generation=wind_capacity)
ess = ESSAgent(max_capacity=ess_capacity)
inverter = InverterAgent(efficiency=inverter_efficiency)
critical_load = CriticalAgent(demand=critical_demand)
non_critical_load = NonCriticalAgent(demand=non_critical_demand)

solar_energy_data = []
wind_energy_data = []
ess_energy_consumed_each_step = []  # To record energy consumed from ESS at each time step
critical_energy_data = []
non_critical_energy_data = []

for time_step in range(total_time_steps):
    solar_energy = pv_panel.generate_solar_energy()
    wind_energy = wind_turbine.generate_wind_energy()

    total_generated_energy = solar_energy + wind_energy

    # Serve Critical Load first
    energy_for_critical = min(total_generated_energy, critical_load.demand)
    critical_consumed = critical_load.consume_energy(energy_for_critical)
    total_generated_energy -= critical_consumed

    # Then, serve Non-Critical Load
    energy_for_non_critical = min(total_generated_energy, non_critical_load.demand)
    non_critical_consumed = non_critical_load.consume_energy(energy_for_non_critical)
    total_generated_energy -= non_critical_consumed

    # Store excess generated energy if there's any
    if total_generated_energy > 0:
        ess.store_energy(total_generated_energy)

    # If there's still demand, consume from the ESS
    if critical_consumed < critical_load.demand:
        shortage_for_critical = critical_load.demand - critical_consumed
        available_energy_for_critical = ess.consume_energy(shortage_for_critical)
        converted_energy_for_critical = inverter.convert_dc_to_ac(available_energy_for_critical)
        critical_consumed += critical_load.consume_energy(converted_energy_for_critical)

    if non_critical_consumed < non_critical_load.demand:
        shortage_for_non_critical = non_critical_load.demand - non_critical_consumed
        available_energy_for_non_critical = ess.consume_energy(shortage_for_non_critical)
        converted_energy_for_non_critical = inverter.convert_dc_to_ac(available_energy_for_non_critical)
        non_critical_consumed += non_critical_load.consume_energy(converted_energy_for_non_critical)

    # Record energy consumed from the ESS at this time step
    current_ess_energy_consumed = ess.cumulative_energy_consumed - sum(ess_energy_consumed_each_step)
    ess_energy_consumed_each_step.append(current_ess_energy_consumed)

    solar_energy_data.append(solar_energy)
    wind_energy_data.append(wind_energy)
    critical_energy_data.append(critical_consumed)
    non_critical_energy_data.append(non_critical_consumed)

    time.sleep(1)

time_steps = range(total_time_steps)
plt.figure(figsize=(10, 6))
plt.plot(time_steps, solar_energy_data, label="PV Energy")
plt.plot(time_steps, wind_energy_data, label="Wind Energy")
plt.plot(time_steps, ess_energy_consumed_each_step, label="ESS Energy Consumed Each Step")
plt.plot(time_steps, critical_energy_data, label="Critical Load Consumption", linestyle='--')
plt.plot(time_steps, non_critical_energy_data, label="Non-Critical Load Consumption", linestyle='--')
plt.xlabel("Time Step")
plt.ylabel("Energy (kW)")
plt.title("Energy Management System")
plt.legend()
plt.grid(True)
plt.show()
