import random
import time
import pandas as pd
from IPython.display import display, clear_output

# ----------------------
# Classes
# ----------------------
class BaseStation:
    def __init__(self, bs_id, location, capacity=5):
        self.bs_id = bs_id
        self.location = location
        self.capacity = capacity
        self.connected_devices = []
        self.allocation_speed = None

class SmartPhone:
    def __init__(self, device_id):
        self.device_id = device_id
        self.location = None
    def connect(self, bs):
        bs.connected_devices.append(self)

class Passenger:
    def __init__(self, passenger_id, device, destination):
        self.passenger_id = passenger_id
        self.device = device
        self.destination = destination
        self.allocated_driver = None

class Driver:
    def __init__(self, driver_id, name, location):
        self.driver_id = driver_id
        self.name = name
        self.location = location
        self.available = True
        self.current_passenger = None

# ----------------------
# Utility
# ----------------------
LOCATIONS = ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Shakahola"]
LOCATION_INDEX = {loc: i for i, loc in enumerate(LOCATIONS)}

def compute_distance(loc1, loc2):
    return abs(LOCATION_INDEX[loc1] - LOCATION_INDEX[loc2])

def compute_allocation_speed(base_station, passengers):
    base_speed = 100
    speeds = []
    for p in passengers:
        if p.device.location == base_station.location:
            distance = compute_distance(p.device.location, base_station.location)
            distance_factor = 1 + distance
            load_factor = 1 + len(base_station.connected_devices) / base_station.capacity
            speed = base_speed / (distance_factor * load_factor)
            speeds.append(speed)
    return round(sum(speeds)/len(speeds), 2) if speeds else None

class NetworkSimulator:
    def __init__(self):
        self.base_stations = []
        self.devices = []
        self.passengers = []
        self.drivers = []

    def add_base_station(self, bs): self.base_stations.append(bs)
    def add_device(self, device): self.devices.append(device)
    def add_passenger(self, passenger): self.passengers.append(passenger)
    def add_driver(self, driver): self.drivers.append(driver)

    def assign_drivers(self):
        # reset allocations each step
        for d in self.drivers:
            d.available = True
            d.current_passenger = None
        for p in self.passengers:
            p.allocated_driver = None

        # randomly allocate drivers to passengers
        available_drivers = self.drivers[:]
        random.shuffle(available_drivers)
        for passenger in self.passengers:
            if available_drivers:
                driver = available_drivers.pop()
                driver.available = False
                driver.current_passenger = passenger.passenger_id
                passenger.allocated_driver = driver.name

    def update_allocation_speeds(self):
        for bs in self.base_stations:
            bs.allocation_speed = compute_allocation_speed(bs, self.passengers)

# ----------------------
# Setup
# ----------------------
NETWORK = NetworkSimulator()
BASE_STATIONS = [BaseStation(f"BS-{i+1:03}", loc) for i, loc in enumerate(LOCATIONS)]
for bs in BASE_STATIONS: NETWORK.add_base_station(bs)

for i in range(10):
    device = SmartPhone(f"D-{1000+i}")
    NETWORK.add_device(device)
    passenger = Passenger(f"P-{300+i}", device, random.choice(LOCATIONS))
    NETWORK.add_passenger(passenger)

driver_names = ["Alice","Bob","Charlie","David","Eva","Frank","Grace","Hannah","Ian","Jane",
                "Kevin","Laura","Mike","Nina","Oscar"]
for i in range(15):
    driver = Driver(f"DR-{200+i}", driver_names[i], random.choice(LOCATIONS))
    NETWORK.add_driver(driver)

# ----------------------
# Infinite Simulation Loop
# ----------------------
try:
    step = 0
    while True:  # run until interrupted
        clear_output(wait=True)

        # Randomize passenger locations/destinations
        for passenger in NETWORK.passengers:
            passenger.device.location = random.choice(LOCATIONS)
            passenger.destination = random.choice([loc for loc in LOCATIONS if loc != passenger.device.location])

        # Randomize driver locations
        for driver in NETWORK.drivers:
            driver.location = random.choice(LOCATIONS)

        # Reset base station connections and reconnect devices
        for bs in NETWORK.base_stations:
            bs.connected_devices.clear()
        for device in NETWORK.devices:
            candidates = [bs for bs in NETWORK.base_stations if bs.location == device.location]
            if candidates:
                bs = random.choice(candidates)
                device.connect(bs)

        # Assign drivers fresh each step
        NETWORK.assign_drivers()

        # Update allocation speeds
        NETWORK.update_allocation_speeds()

        # Build DataFrames
        driver_data = [{"Driver": d.name,
                        "Location": d.location,
                        "Status": "Busy" if d.current_passenger else "Available"}
                       for d in NETWORK.drivers]

        bs_data = [{"BaseStation": bs.bs_id,
                    "Location": bs.location,
                    "Connected Devices": len(bs.connected_devices),
                    "Allocation Speed": bs.allocation_speed}
                   for bs in NETWORK.base_stations]

        rides_data = [{"Passenger": p.passenger_id,
                       "Location": p.device.location,
                       "Destination": p.destination,
                       "Allocated Driver": p.allocated_driver}
                      for p in NETWORK.passengers]

        print(f"--- Step {step} ---")
        display(pd.DataFrame(driver_data))
        display(pd.DataFrame(bs_data))
        display(pd.DataFrame(rides_data))

        step += 1
        time.sleep(1)  # pacing

except KeyboardInterrupt:
    print("\nSimulation stopped manually.")
