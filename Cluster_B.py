# Full code for the energy management simulation

import random
import time
import matplotlib.pyplot as plt


# Class definitions

class PVAgent:
    def __init__(self, max_generation):
        self.max_generation = max_generation

    def generate_solar_energy(self):
        return random.uniform(0, self.max_generation)


class DieselGeneratorAgent:
    def __init__(self, max_generation):
        self.max_generation = max_generation

    def generate_diesel_energy(self):
        return random.uniform(0, self.max_generation)


class ESSAgent:
    def __init__(self, max_capacity):
        self.max_capacity = max_capacity
        self.energy_stored = 0

    def store_energy(self, energy):
        self.energy_stored += energy
        if self.energy_stored > self.max_capacity:
            self.energy_stored = self.max_capacity

    def consume_energy(self, demand):
        energy_taken = min(self.energy_stored, demand)
        self.energy_stored -= energy_taken
        return energy_taken


class LoadAgent:
    def __init__(self, demand):
        self.demand = demand

    def consume_energy(self, available_energy):
        energy_consumed = min(self.demand, available_energy)
        self.demand -= energy_consumed
        return energy_consumed


# Simulation setup and loop

total_time_steps = 15
pv_capacity = 100.0
generator_capacity = 250.0
ess_capacity = 300.0
critical_demand_val = 160
non_critical_demand_val = 290

pv_panel = PVAgent(pv_capacity)
diesel_generator = DieselGeneratorAgent(generator_capacity)
ess = ESSAgent(ess_capacity)
critical_load = LoadAgent(critical_demand_val)
non_critical_load = LoadAgent(non_critical_demand_val)

solar_energy_data = []
diesel_energy_data = []
ess_energy_data = []
critical_energy_data = []
non_critical_energy_data = []

for time_step in range(total_time_steps):
    solar_energy = pv_panel.generate_solar_energy()
    total_available_energy = solar_energy

    # Consume critical load with solar energy
    critical_consumed = critical_load.consume_energy(min(critical_load.demand, total_available_energy))
    total_available_energy -= critical_consumed

    # Consume non-critical load with solar energy if any energy is left after serving critical load
    non_critical_consumed = non_critical_load.consume_energy(min(non_critical_load.demand, total_available_energy))
    total_available_energy -= non_critical_consumed

    # Use diesel generator if there's still a demand after using solar energy
    from_diesel = 0
    if critical_load.demand + non_critical_load.demand > critical_consumed + non_critical_consumed:
        from_diesel = diesel_generator.generate_diesel_energy()
        total_available_energy += from_diesel

        # Consume critical load with diesel energy if there's still a demand after using solar energy
        critical_consumed_diesel = critical_load.consume_energy(min(critical_load.demand, total_available_energy))
        total_available_energy -= critical_consumed_diesel
        critical_consumed += critical_consumed_diesel

        # Consume non-critical load with diesel energy if any energy is left after serving critical load
        non_critical_consumed_diesel = non_critical_load.consume_energy(
            min(non_critical_load.demand, total_available_energy))
        total_available_energy -= non_critical_consumed_diesel
        non_critical_consumed += non_critical_consumed_diesel

    # Use energy from ESS if there's still a demand after solar and diesel
    if critical_load.demand + non_critical_load.demand > critical_consumed + non_critical_consumed:
        from_ess = ess.consume_energy(
            critical_load.demand + non_critical_load.demand - critical_consumed - non_critical_consumed)
        total_available_energy += from_ess

        # Consume critical load with ESS energy
        critical_consumed_ess = critical_load.consume_energy(min(critical_load.demand, total_available_energy))
        total_available_energy -= critical_consumed_ess
        critical_consumed += critical_consumed_ess

        # Consume non-critical load with ESS energy if any energy is left after serving critical load
        non_critical_consumed_ess = non_critical_load.consume_energy(
            min(non_critical_load.demand, total_available_energy))
        total_available_energy -= non_critical_consumed_ess
        non_critical_consumed += non_critical_consumed_ess

    # Check for excess energy and store in ESS
    excess_energy = total_available_energy
    if excess_energy > 0:
        ess.store_energy(excess_energy)

    ess_energy_data.append(ess.energy_stored)
    solar_energy_data.append(solar_energy)
    diesel_energy_data.append(from_diesel)
    critical_energy_data.append(critical_consumed)
    non_critical_energy_data.append(non_critical_consumed)

    time.sleep(1)

plt.figure(figsize=(10, 6))
plt.plot(range(total_time_steps), solar_energy_data, label="PV Energy")
plt.plot(range(total_time_steps), diesel_energy_data, label="Diesel Generator Energy")
plt.plot(range(total_time_steps), ess_energy_data, label="ESS Stored Energy")
plt.plot(range(total_time_steps), critical_energy_data, label="Critical Load Consumption", linestyle='--')
plt.plot(range(total_time_steps), non_critical_energy_data, label="Non-Critical Load Consumption", linestyle='--')
plt.xlabel("Time Step")
plt.ylabel("Energy (kW)")
plt.title("Energy Management System")
plt.legend()
plt.grid(True)
plt.show()
