#***Before using this example the motor/controller combination must be
#***tuned and the settings saved to the Roboclaw using IonMotion.
#***The Min and Max Positions must be at least 0 and 50000

import time
import socket
from roboclaw import Roboclaw, enableFailsafe, init_safety, check_watchdog, update_watchdog

# TCP server configuration
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 65432

#Windows comport name
#rc = Roboclaw("COM9",38400)
#Linux comport name
rc = Roboclaw("/dev/ttyACM0",115200)

client_conn = None  # Global socket connection reference

def print_and_send(message: str):
    """Console print always; send minimal protocol messages to client.
    Allowed outbound messages: 'C', '>', and any line starting with 'P:'.
    """
    print(message)
    if not (message in ('C', '>') or message.startswith('P:')):
        return
    if client_conn:
        try:
            client_conn.sendall((message + "\n").encode('utf-8'))
        except Exception:
            pass

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
enableFailsafe(5000)  # Set failsafe watchdog to 5000 ms (5 seconds)

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

print(f"\nTCP Server listening on {HOST}:{PORT}")
print("Waiting for client connection to start motor movements...")

try:
    # Wait for a client connection
    conn, addr = server_socket.accept()
    client_conn = conn  # Set global connection variable
    print(f"Connection established from {addr}")
    # Send only 'C' to client to signal connection established
    print_and_send('C')
    
    # Fixed motor parameters
    accel = 100
    speed = 300

    # Initial distance request prompt
    conn.settimeout(60.0)  # 60 second timeout for parameter input
    while True:
        print_and_send('>')
        data = conn.recv(1024).decode('utf-8').strip()
        # Handle position request
        if data.lower() == 'p':
            enc1 = rc.ReadEncM1(address)
            enc2 = rc.ReadEncM2(address)
            if enc1[0] and enc2[0]:
                print_and_send(f"P:{enc1[1]},{enc2[1]}")
            else:
                # If read failed, report zeros
                print_and_send("P:0,0")
            continue  # Re-prompt for distance
        # Parse distance parameter
        if data.startswith("DISTANCE:"):
            try:
                distance = int(data.split(":")[1])
                print(f"Received distance: {distance}")
                break
            except ValueError:
                print(f"Invalid distance value: {data.split(':')[1]}. Using default distance.")
                distance = 42000
                break
        else:
            print("Invalid format - using default distance")
            distance = 42000
            break
    
    conn.settimeout(None)  # Remove timeout for normal operation
    
    # Main loop - execute movements
    while(1):
        print("\nStarting movement")
        # Set speed sign opposite to distance sign
        if distance >= 0:
            speed_signed = -speed  # M1 uses negative speed for positive distance
            speed2_signed = speed  # M2 uses positive speed for positive distance
        else:
            speed_signed = speed   # M1 uses positive speed for negative distance
            speed2_signed = -speed # M2 uses negative speed for negative distance

        rc.SpeedAccelDistanceM1(address,accel,speed_signed,abs(distance),1)  # M1 speed inverted
        rc.SpeedAccelDistanceM2(address,accel,speed2_signed,abs(distance),1)
        rc.SpeedAccelDistanceM1(address,accel,0,0,0)  #distance travelled is v*v/2a = 12000*12000/2*48000 = 1500
        rc.SpeedAccelDistanceM2(address,accel,0,0,0)  #that makes the total move in one direction 48000
        update_watchdog()  # Update command time
        print("Watchdog timer reset")
        print("Monitoring movement...")
        buffers = (0,0,0)
        watchdog_triggered = False
        while (buffers[1] != 0x80 and buffers[2] != 0x80):  # Loop until distance command has completed
            displayspeed()
            
            # Send position to client every loop iteration
            enc1 = rc.ReadEncM1(address)
            enc2 = rc.ReadEncM2(address)
            if enc1[0] and enc2[0]:
                print_and_send(f"P:{enc1[1]},{enc2[1]}")
            else:
                print_and_send("P:0,0")
            
            time.sleep(0.2)  # 200ms loop for faster monitoring
            if check_watchdog():    # Check if watchdog timeout occurred
                print_and_send("Watchdog triggered - stopping motors")
                watchdog_triggered = True
                break  # Exit loop but don't raise exception
            buffers = rc.ReadBuffers(address)
        
        # Movement completed or watchdog triggered - wait for new distance
        # Prompt for next distance (watchdog or normal completion)
        conn.settimeout(60.0)  # 60 second timeout for parameter input
        while True:
            print_and_send('>')
            data = conn.recv(1024).decode('utf-8').strip()
            
            # Check if client disconnected
            if not data:
                print("Client disconnected")
                break  # Exit the inner prompt loop; outer will break below
            
            # Handle position request
            if data.lower() == 'p':
                enc1 = rc.ReadEncM1(address)
                enc2 = rc.ReadEncM2(address)
                if enc1[0] and enc2[0]:
                    print_and_send(f"P:{enc1[1]},{enc2[1]}")
                else:
                    print_and_send("P:0,0")
                continue  # Re-prompt without changing distance
            
            # Parse distance parameter
            if data.startswith("DISTANCE:"):
                try:
                    distance = int(data.split(":")[1])
                    print(f"Received distance: {distance}")
                except ValueError:
                    print(f"Invalid distance value: {data.split(':')[1]}. Using zero distance.")
                    distance = 0
                break  # Got a distance (valid or coerced) -> exit prompt loop
            else:
                print("Invalid format - using zero distance")
                distance = 0
                break
        if not data:
            break  # Exit the main loop on disconnect
        
        conn.settimeout(None)  # Remove timeout for normal operation
        continue  # Skip to next iteration with new distance

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

