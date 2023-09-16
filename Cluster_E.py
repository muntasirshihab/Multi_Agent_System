import random
import time
import matplotlib.pyplot as plt

class PvAgent:
    def __init__(self, max_generation):
        self.max_generation = max_generation

    def generate_solar_energy(self):
        solar_energy = random.uniform(0, self.max_generation)
        return solar_energy

class BiogasAgent:
    def __init__(self, max_generation):
        self.max_generation = max_generation

    def generate_biogas_energy(self):
        biogas_energy = random.uniform(0, self.max_generation)
        return biogas_energy

class ESSAgent:
    def __init__(self, max_capacity):
        self.max_capacity = max_capacity
        self.energy_stored = 0

    def store_energy(self, energy):
        self.energy_stored += energy
        if self.energy_stored > self.max_capacity:
            # Any energy that exceeds the ESS capacity is considered wasted/curtailed
            curtailed_energy = self.energy_stored - self.max_capacity
            self.energy_stored = self.max_capacity
            return curtailed_energy
        return 0

class CriticalAgent:
    def __init__(self, demand):
        self.demand = demand

    def consume_energy(self, available_energy):
        consumed_energy = min(self.demand, available_energy)
        self.demand -= consumed_energy
        return consumed_energy

class NonCriticalAgent:
    def __init__(self, demand):
        self.demand = demand

    def consume_energy(self, available_energy):
        consumed_energy = min(self.demand, available_energy)
        self.demand -= consumed_energy
        return consumed_energy

# Constants
total_time_steps = 10
pv_capacity = 100.0
biogas_capacity = 100.0
ess_capacity = 300.0
critical_demand = 160
non_critical_demand = 280

pv_panel = PvAgent(max_generation=pv_capacity)
biogas_generator = BiogasAgent(max_generation=biogas_capacity)
ess = ESSAgent(max_capacity=ess_capacity)
critical_load = CriticalAgent(demand=critical_demand)
non_critical_load = NonCriticalAgent(demand=non_critical_demand)

solar_energy_data = []
biogas_energy_data = []
ess_storage_data = []
critical_consumption_data = []
non_critical_consumption_data = []

for time_step in range(total_time_steps):
    solar_energy = pv_panel.generate_solar_energy()
    biogas_energy = biogas_generator.generate_biogas_energy()

    total_generated_energy = solar_energy + biogas_energy

    # Serve Critical Load first
    critical_consumed = critical_load.consume_energy(total_generated_energy)
    total_generated_energy -= critical_consumed

    # Serve Non-Critical Load next
    non_critical_consumed = non_critical_load.consume_energy(total_generated_energy)
    total_generated_energy -= non_critical_consumed

    # Store any excess energy in the ESS
    curtailed_energy = ess.store_energy(total_generated_energy)

    # Record data for visualization
    solar_energy_data.append(solar_energy)
    biogas_energy_data.append(biogas_energy)
    ess_storage_data.append(ess.energy_stored)
    critical_consumption_data.append(critical_consumed)
    non_critical_consumption_data.append(non_critical_consumed)

    time.sleep(1)

# Visualization
time_steps = range(total_time_steps)
plt.figure(figsize=(10, 6))
plt.plot(time_steps, solar_energy_data, label="PV Energy")
plt.plot(time_steps, biogas_energy_data, label="Biogas Energy")
plt.plot(time_steps, ess_storage_data, label="ESS Stored Energy")
plt.plot(time_steps, critical_consumption_data, label="Critical Load Consumption", linestyle='--')
plt.plot(time_steps, non_critical_consumption_data, label="Non-Critical Load Consumption", linestyle='--')
plt.xlabel("Time Step")
plt.ylabel("Energy (kW)")
plt.title("Energy Management System")
plt.legend()
plt.grid(True)
plt.show()