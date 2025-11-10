#***Before using this example the motor/controller combination must be
#***tuned and the settings saved to the Roboclaw using IonMotion.
#***The Min and Max Positions must be at least 0 and 50000

import time
import socket
from roboclaw import Roboclaw
from roboclaw_safety import init_safety, check_watchdog, update_watchdog

# TCP server configuration
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 65432

#Windows comport name
#rc = Roboclaw("COM9",38400)
#Linux comport name
rc = Roboclaw("/dev/ttyACM1",115200)

# Global variable for socket connection
client_conn = None

def print_and_send(message):
    """Print to console and send to connected client"""
    print(message)
    if client_conn:
        try:
            client_conn.sendall((message + "\n").encode())
        except:
            pass  # Ignore send errors

def displayspeed():
    enc1 = rc.ReadEncM1(address)
    enc2 = rc.ReadEncM2(address)
    speed1 = rc.ReadSpeedM1(address)
    speed2 = rc.ReadSpeedM2(address)

    print("Encoder1:", end=' ')
    if enc1[0] == 1:
        print(enc1[1], format(enc1[2], '02x'), end=' ')
    else:
        print("failed", end=' ')
    print("Encoder2:", end=' ')
    if enc2[0] == 1:
        print(enc2[1], format(enc2[2], '02x'), end=' ')
    else:
        print("failed", end=' ')
    print("Speed1:", end=' ')
    if speed1[0]:
        print(speed1[1], end=' ')
    else:
        print("failed", end=' ')
    print("Speed2:", end=' ')
    if speed2[0]:
        print(speed2[1])
    else:
        print("failed")

rc.Open()
address = 0x80

# Initialize safety features
init_safety(rc, address)

version = rc.ReadVersion(address)
if version[0] == False:
    print("GETVERSION Failed")
else:
    print(repr(version[1]))

# Create TCP socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print_and_send(f"\nTCP Server listening on {HOST}:{PORT}")
print_and_send("Waiting for client connection to start motor movements...")

try:
    # Wait for a client connection
    conn, addr = server_socket.accept()
    client_conn = conn  # Set global connection variable
    print_and_send(f"Connection established from {addr}")
    conn.sendall(b"Connected to RoboClaw controller\n")
    
    while(1):
        print_and_send("\nStarting first movement")
        rc.SpeedAccelDistanceM1(address,12000,12000,42000,1)
        rc.SpeedAccelDistanceM2(address,12000,-12000,42000,1)
        rc.SpeedAccelDistanceM1(address,12000,0,0,0)  #distance travelled is v*v/2a = 12000*12000/2*48000 = 1500
        rc.SpeedAccelDistanceM2(address,12000,0,0,0)  #that makes the total move in one direction 48000
        update_watchdog()  # Update command time
        print_and_send("Watchdog timer reset")
        
        print_and_send("Monitoring first movement...")
        buffers = (0,0,0)
        while (buffers[1] != 0x80 and buffers[2] != 0x80):  # Loop until distance command has completed
            print_and_send(f"Buffers: {buffers[1]} {buffers[2]}")
            displayspeed()
            time.sleep(1)  # Longer sleep to make watchdog testing easier
            if check_watchdog():    # Check if watchdog timeout occurred
                print_and_send("Watchdog triggered - stopping motors")
                raise Exception("Watchdog timeout")
            buffers = rc.ReadBuffers(address)

        print_and_send("\nStarting second movement")
        rc.SpeedAccelDistanceM1(address,48000,-12000,46500,1)
        rc.SpeedAccelDistanceM2(address,48000,12000,46500,1)
        rc.SpeedAccelDistanceM1(address,48000,0,0,0)  #distance travelled is v*v/2a = 12000*12000/2*48000 = 1500
        rc.SpeedAccelDistanceM2(address,48000,0,0,0)  #that makes the total move in one direction 48000
        update_watchdog()  # Update command time
        print_and_send("Watchdog timer reset")
        
        print_and_send("Monitoring second movement...")
        buffers = (0,0,0)
        while (buffers[1] != 0x80 and buffers[2] != 0x80):  # Loop until distance command has completed
            print_and_send(f"Buffers: {buffers[1]} {buffers[2]}")
            displayspeed()
            time.sleep(1)  # Longer sleep to make watchdog testing easier
            if check_watchdog():    # Check if watchdog timeout occurred
                print_and_send("Watchdog triggered - stopping motors")
                raise Exception("Watchdog timeout")
            buffers = rc.ReadBuffers(address)

except KeyboardInterrupt:
    # This will be handled by our signal handler
    pass
except Exception as e:
    print_and_send(f"An error occurred: {e}")
    raise  # Re-raise the exception after printing it
finally:
    # Close the connection and server socket
    try:
        conn.close()
    except:
        pass
    server_socket.close()
    print_and_send("Server socket closed")

