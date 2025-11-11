#***Before using this example the motor/controller combination must be
#***tuned and the settings saved to the Roboclaw using IonMotion.
#***The Min and Max Positions must be at least 0 and 50000

import time
from roboclaw import Roboclaw
from roboclaw import init_safety, check_watchdog, update_watchdog

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

try:
    while(1):
        print("\nStarting first movement")
        rc.SpeedAccelM1M2(address,12000,12000,-12000)
        update_watchdog()  # Update command time
        print("Watchdog timer reset")
        
        print("Monitoring first movement...")
        for i in range(0,20):  # Reduced iterations but increased sleep time
            displayspeed()
            time.sleep(1)  # Sleep for 1 second to make watchdog testing easier
            if check_watchdog():    # Check if watchdog timeout occurred
                print("Watchdog triggered - stopping motors")
                raise Exception("Watchdog timeout")

        print("\nStarting second movement")
        rc.SpeedAccelM1M2(address,12000,-12000,12000)
        update_watchdog()  # Update command time
        print("Watchdog timer reset")
        
        print("Monitoring second movement...")
        for i in range(0,20):  # Reduced iterations but increased sleep time
            displayspeed()
            time.sleep(1)  # Sleep for 1 second to make watchdog testing easier
            if check_watchdog():    # Check if watchdog timeout occurred
                print("Watchdog triggered - stopping motors")
                raise Exception("Watchdog timeout")

except KeyboardInterrupt:
    # This will be handled by our signal handler
    pass
except Exception as e:
    print(f"An error occurred: {e}")
    raise  # Re-raise the exception after printing it
