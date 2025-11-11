import time
from roboclaw import Roboclaw
from roboclaw import init_safety, check_watchdog, update_watchdog

#Windows comport name
#rc = Roboclaw("COM11",115200)
#Linux comport name
rc = Roboclaw("/dev/ttyACM0",115200)

rc.Open()
address = 0x80

# Initialize safety features
init_safety(rc, address)

try:
    while(1):
        print("\nForward M1, Backward M2")
        rc.ForwardM1(address,32)    #1/4 power forward
        rc.BackwardM2(address,32)   #1/4 power backward
        update_watchdog()
        print("Watchdog timer reset")
        
        for _ in range(2):  # 2 seconds total
            time.sleep(1)
            if check_watchdog():
                print("Watchdog triggered - stopping motors")
                raise Exception("Watchdog timeout")
        
        print("\nBackward M1, Forward M2")
        rc.BackwardM1(address,32)   #1/4 power backward
        rc.ForwardM2(address,32)    #1/4 power forward
        update_watchdog()
        print("Watchdog timer reset")
        
        for _ in range(2):
            time.sleep(1)
            if check_watchdog():
                print("Watchdog triggered - stopping motors")
                raise Exception("Watchdog timeout")

        print("\nStopped")
        rc.BackwardM1(address,0)    #Stopped
        rc.ForwardM2(address,0)     #Stopped
        update_watchdog()
        print("Watchdog timer reset")
        
        for _ in range(2):
            time.sleep(1)
            if check_watchdog():
                print("Watchdog triggered - stopping motors")
                raise Exception("Watchdog timeout")

        m1duty = 16
        m2duty = -16
        print("\nForwardBackward M1/M2 - Forward")
        rc.ForwardBackwardM1(address,64+m1duty) #1/4 power forward
        rc.ForwardBackwardM2(address,64+m2duty) #1/4 power backward
        update_watchdog()
        print("Watchdog timer reset")
        
        for _ in range(2):
            time.sleep(1)
            if check_watchdog():
                print("Watchdog triggered - stopping motors")
                raise Exception("Watchdog timeout")
        
        m1duty = -16
        m2duty = 16
        print("\nForwardBackward M1/M2 - Reverse")
        rc.ForwardBackwardM1(address,64+m1duty) #1/4 power backward
        rc.ForwardBackwardM2(address,64+m2duty) #1/4 power forward
        update_watchdog()
        print("Watchdog timer reset")
        
        for _ in range(2):
            time.sleep(1)
            if check_watchdog():
                print("Watchdog triggered - stopping motors")
                raise Exception("Watchdog timeout")

        print("\nForwardBackward M1/M2 - Stopped")
        rc.ForwardBackwardM1(address,64)    #Stopped
        rc.ForwardBackwardM2(address,64)    #Stopped
        update_watchdog()
        print("Watchdog timer reset")
        
        for _ in range(2):
            time.sleep(1)
            if check_watchdog():
                print("Watchdog triggered - stopping motors")
                raise Exception("Watchdog timeout")

except KeyboardInterrupt:
    # This will be handled by our signal handler
    pass
except Exception as e:
    print(f"An error occurred: {e}")
    raise  # Re-raise the exception after printing it