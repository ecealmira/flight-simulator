# Flight Simulator
A Python-based simulation for real-time drone coordinate generation, data reception, and visualization. This project models drone movements, communicates over a network, and visualizes results in a dynamic, real-time environment.

It includes:

- A generator that calculates and sends drone coordinates.
- A listener that receives and logs the data.
- A visualizer to plot drone trajectories dynamically.

# System Components

## Generator
Simulates drone movement using mathematical models and random noise for realism.
Sending the drone coordinates to the server (listener) over a socket connection.

### Key Features:
Calculates drone positions (x, y, z) at each time step and introduces random error to simulate real-world inaccuracies.
Sends periodic updates and control messages, including:
- Drone coordinates.
- Start and end notifications.
- Disconnect messages.

## Listener
Accepts and decodes data from the generator.

Stores data in a CSV file and adds it to a queue for visualization.

Handles client disconnection and end-of-transmission messages.

### Key Features:
- Multi-threaded to support concurrent client connections.
- Logs received data with timestamps and drone indices.

## Visualization
The visualization component (flight_simulator.py) reads drone coordinate from the CSV file and dynamically plots the drones' trajectories in real-time, with continuous updates.

### Key Features:
- Displays the last N points for each drone.
- Dynamically adjusts plot limits for better visualization.
- Provides a continuous and interactive plotting experience.

# How It Works
Clone this repository:
```
git clone https://github.com/yourusername/flight-simulator.git
cd flight-simulator
```

Start the listener (server):
```
python listener.py
```

Run the generator (client):
```
python generator.py
```

Launch the visualizer:
```
python flight_simulator.py
```
