#***Before using this example the motor/controller combination must be
#***tuned and the settings saved to the Roboclaw using IonMotion.
#***The Min and Max Positions must be at least 0 and 50000

import time
from roboclaw import Roboclaw
from roboclaw_safety import init_safety, check_watchdog, update_watchdog

#Windows comport name
#rc = Roboclaw("COM3",115200)
#Linux comport name
rc = Roboclaw("/dev/ttyACM0",115200)

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

# Read PID values
pid = rc.ReadM1VelocityPID(address)
if pid[0]:
    print(f"M1 PID: P={pid[1]}, I={pid[2]}, D={pid[3]}, QPPS={pid[4]}")
else:
    print("Failed to read PID values")

try:
    while(1):
        print("Forward 1/4 speed")
        rc.ForwardM1(address,32)    # 1/4 power forward (0-127)
        rc.ForwardM2(address,0)
        update_watchdog()  # Update command time
        
        for i in range(0,5):        # 5 iterations
            if check_watchdog():    # Check if watchdog timeout occurred
                break
            displayspeed()
            time.sleep(2)

        # Only continue if watchdog hasn't triggered
        if check_watchdog():
            break

        print("Reverse 1/4 speed")
        rc.BackwardM1(address,32)   # 1/4 power backward (0-127)
        rc.ForwardM2(address,0)
        update_watchdog()  # Update command time
        for i in range(0,200):
            if check_watchdog():    # Check if watchdog timeout occurred
                break
            displayspeed()
            time.sleep(2)
            
        # Check watchdog again after loop
        if check_watchdog():
            break

except KeyboardInterrupt:
    # This will be handled by our signal handler
    pass
except Exception as e:
    print(f"An error occurred: {e}")
    raise  # Re-raise the exception after printing it