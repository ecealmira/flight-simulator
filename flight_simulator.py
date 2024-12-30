import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
from queue import Queue

# Load the CSV with the correct separator and decimal configuration
drone_coordinates_df = pd.read_csv("../Cezeri_programs/drone_coordinates.csv", sep=";", decimal=",")
print(drone_coordinates_df.head())

def update_queue(data_queues, drone_id, x, y, last_n_point_number):
    """
    Update the queue for the given drone with new coordinates.

    Parameters
    ----------
    data_queues : dict
        Dictionary of queues storing the last N points for each drone.
    drone_id : int
        The ID of the drone to update.
    x : float
        The x-coordinate of the new point.
    y : float
        The y-coordinate of the new point.
    buffer_size : int
        The maximum size of the queue.
    """
    if data_queues[drone_id].qsize() >= last_n_point_number:
        data_queues[drone_id].get()  # Remove the oldest point

    # Add the new point as a tuple (x, y)
    data_queues[drone_id].put((x, y))

def show_points(last_n_point_number: int, update_interval: float, plot_limit: int) -> None:
    """
    Plots and updates the last N points for each drone in real-time.

    Parameters
    ----------
    last_n_point_number : int
        The number of points to keep per drone.
    update_interval : float
        Time in seconds between updates.
    plot_limit : int
        Margin added to the plot limits.
    """
    # Prepare figure and axis
    fig, ax = plt.subplots()
    drone_plots = {}  # Store plot lines for each drone
    data_queues = {drone_id: Queue() for drone_id in drone_coordinates_df["drone_index"].unique()}

    # Initialize plot lines for each drone
    for drone_id in drone_coordinates_df["drone_index"].unique():
        drone_plots[drone_id], = ax.plot([], [], marker='o', label=f"Drone {drone_id}")

    ax.legend(loc='upper right')
    # Iterate over the data in real-time
    for _, row in drone_coordinates_df.iterrows():
        drone_id = row["drone_index"]
        x, y = row["x"], row["y"]

        # Update the data queue for the current drone
        update_queue(data_queues, drone_id, x, y, last_n_point_number)

        # Update the plots with the latest queued data
        x_min, x_max = float('inf'), float('-inf')
        y_min, y_max = float('inf'), float('-inf')

        for drone_id, queue in data_queues.items():
            # Extract x and y values from the queue
            points = list(queue.queue)  # Get the list of points in the queue
            x_values = [p[0] for p in points]
            y_values = [p[1] for p in points]

            drone_plots[drone_id].set_data(x_values, y_values)

            # Track min and max values for dynamic plot limits
            x_min, x_max = min(x_min, min(x_values, default=x_min)), max(x_max, max(x_values, default=x_max))
            y_min, y_max = min(y_min, min(y_values, default=y_min)), max(y_max, max(y_values, default=y_max))

        # Set plot limits with added buffer for better visualization
        ax.set_xlim(x_min - plot_limit, x_max + plot_limit)
        ax.set_ylim(y_min - plot_limit, y_max + plot_limit)

        # Redraw the plot with updated data
        plt.draw()
        plt.pause(update_interval)  # Pause to simulate real-time updates


def main():
    """Main function to run the real-time plotting."""
    last_n_point_number = 20  # Number of points to keep in the plot for each drone
    update_interval = 0.1  # Time (seconds) between updates
    plot_limit = 50  # Set the margin for the plot limits

    show_points(last_n_point_number, update_interval, plot_limit)

if __name__ == "__main__":
    main()
