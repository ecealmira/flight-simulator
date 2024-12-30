import socket
import json
import numpy as np
import time
import math

HEADER = 64
PORT = 5050
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg: str) -> None:
    """
    Sends a message to the server.

    Parameters
    ----------
    msg : str
        The message to send, encoded in UTF-8 format.
    """
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def calculate_coordinates(drone_number: int, current_time: int) -> str:
    """
    Calculates coordinates for multiple drones and formats them as a JSON string.

    Parameters
    ----------
    drone_number : int
        The number of drones to calculate coordinates for.
    current_time : int
        The current time step for the simulation.

    Returns
    -------
    str
        JSON-formatted string containing coordinates for all drones.
    """
    coordinate_list = []

    for i in range(1, drone_number + 1):
        coor = {
            "x": (current_time**1.1) - (8 * current_time) + (3 * (current_time**0.2) * i) + calculate_error(1.5),
            "y": (current_time**0.9) + (3 * current_time) + (10 * i) + calculate_error(1.5),
            "z": 10 * i + calculate_error(1.5)
        }
        coordinate_list.append(coor)

    coordinate_msg = {"msg_type": "coords", "coords": coordinate_list}
    return json.dumps(coordinate_msg)

def calculate_error(limit_point: float) -> float:
    """
    Adds a random error value within a given limit.

    Parameters
    ----------
    limit_point : float
        The upper limit for the error value.

    Returns
    -------
    float
        Random error value sampled from a normal distribution.
    """
    mean = 0
    std_dev = limit_point / 3
    return np.random.normal(mean, std_dev)


def send_messages():
    # Send number of wanted points to be plotted
    last_k_elements = 20
    last_point_num_dict = {"msg_type": "last_points_number", "last_points_number": last_k_elements}
    send(json.dumps(last_point_num_dict))

    # Send numbers for the wanted time
    time_interval = 0.01  
    run_time = 1  # Run for 1 second
    total_point_number = math.ceil(run_time / time_interval)
    print(f"{total_point_number} points have been send")
    for i in range(total_point_number):
        send(calculate_coordinates(3, i + 1))
        time.sleep(time_interval)

    # End message for the ending of new points
    end_msg_dict = {"msg_type": "END"}
    send(json.dumps(end_msg_dict))

    # Message from disconnect from the servers
    dis_msg_dict = {"msg_type": DISCONNECT_MESSAGE}
    send(json.dumps(dis_msg_dict))

send_messages()
