import socket
import threading
import json
import queue
import pandas as pd
from datetime import datetime

# Constants
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

# Server Initialization
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# Queue to pass data between threads
plot_queue = queue.Queue()

# CSV File Initialization
header_list = ['time_ms', 'drone_index', 'x', 'y', 'z']
with open('drone_coordinates.csv', 'w', newline='') as csvfile:
    csvfile.write(";".join(header_list) + "\n")

def main_plot_loop() -> None:
    """
    Continuously fetches new data from the queue and updates the plot.
    It terminates when an "END" message is received in the queue.
    """
    collecting = True

    while collecting:
        try:
            new_points = plot_queue.get(timeout=1)
            if new_points == "END":
                collecting = False
                break
            # Update all points and log them to the CSV
            update_all_points(new_points)
        except queue.Empty: # If the queue is empty, continue
            continue
    

def handle_client(conn: socket.socket, addr: tuple) -> None:
    """
    Handles incoming client connections and processes messages.
    It closes the connection upon receiving a disconnect message.

    Parameters
    ----------
    conn : socket.socket
        The socket connection object for the client.
    addr : tuple
        The address of the connected client.
    """
    print(f"{addr[0]} connected.")
    connected = True

    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            received_msg = conn.recv(msg_length).decode(FORMAT)
            loaded_msg = json.loads(received_msg)

            print(f"[{addr[0]}] {received_msg}")

            if loaded_msg["msg_type"] == "last_points_number": # How many points will be plotted
                last_points_number = loaded_msg["last_points_number"]
                print(f"Set to keep last {last_points_number} elements per drone.")
            elif loaded_msg["msg_type"] == "coords": # Get coordinates
                points_list = loaded_msg["coords"]
                plot_queue.put(points_list)
            elif loaded_msg["msg_type"] == "END": # Ending for the coming points
                plot_queue.put("END")
            elif loaded_msg["msg_type"] == DISCONNECT_MESSAGE: # Disconnect the connection
                print("Disconnected.")
                connected = False

    conn.close()

def start() -> None:
    """
    Starts the server to listen for incoming connections.
    """
    server.listen()
    print("Server is listening")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"Active Connections: {threading.active_count() - 1}")

def update_all_points(new_points: list[dict[str, float]]) -> None:
    """
    Updates the DataFrame with new points and logs them to a CSV file.

    Parameters
    ----------
    new_points : List[Dict[str, float]]
        A list of dictionaries containing the coordinates and other relevant 
        data for each drone point.    
    """

    # Add timestamp and create a DataFrame from the new points
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    new_points_df = pd.DataFrame(new_points)
    new_points_df["time_ms"] = current_time
    new_points_df["drone_index"] = new_points_df.index + 1
    
    # Change the order of the columns
    new_points_df = new_points_df[["time_ms", "drone_index", "x", "y", "z"]]

    # Load new points to the CSV file
    with open('drone_coordinates.csv', 'a', newline='') as csvfile:
        new_points_df.to_csv(
            csvfile, 
            sep=';', 
            header=False, 
            index=False, 
            float_format='%.6f', 
            decimal=","
        )


# Start the thread
print("Server is starting")
server_thread = threading.Thread(target=start)
server_thread.start()

# Start plotting
main_plot_loop()
