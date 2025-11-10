import time
from roboclaw import Roboclaw
from roboclaw_safety import init_safety, check_watchdog, update_watchdog

#Windows comport name
#rc = Roboclaw("COM9",115200)
#Linux comport name
rc = Roboclaw("/dev/ttyACM0",115200)

rc.Open()
address = 0x80

# Initialize safety features
init_safety(rc, address)

# Initial stop
rc.ForwardMixed(address, 0)
rc.TurnRightMixed(address, 0)
update_watchdog()

try:
    while(1):
        print("\nForward mixed")
        rc.ForwardMixed(address, 32)
        update_watchdog()
        print("Watchdog timer reset")
        for _ in range(2):
            time.sleep(1)
            if check_watchdog():
                print("Watchdog triggered - stopping motors")
                raise Exception("Watchdog timeout")

        print("\nBackward mixed")
        rc.BackwardMixed(address, 32)
        update_watchdog()
        print("Watchdog timer reset")
        for _ in range(2):
            time.sleep(1)
            if check_watchdog():
                print("Watchdog triggered - stopping motors")
                raise Exception("Watchdog timeout")

        print("\nTurn right mixed")
        rc.TurnRightMixed(address, 32)
        update_watchdog()
        print("Watchdog timer reset")
        for _ in range(2):
            time.sleep(1)
            if check_watchdog():
                print("Watchdog triggered - stopping motors")
                raise Exception("Watchdog timeout")

        print("\nTurn left mixed")
        rc.TurnLeftMixed(address, 32)
        update_watchdog()
        print("Watchdog timer reset")
        for _ in range(2):
            time.sleep(1)
            if check_watchdog():
                print("Watchdog triggered - stopping motors")
                raise Exception("Watchdog timeout")

        print("\nForward + Turn right mixed")
        rc.ForwardMixed(address, 0)
        rc.TurnRightMixed(address, 32)
        update_watchdog()
        print("Watchdog timer reset")
        for _ in range(2):
            time.sleep(1)
            if check_watchdog():
                print("Watchdog triggered - stopping motors")
                raise Exception("Watchdog timeout")

        print("\nTurn left mixed")
        rc.TurnLeftMixed(address, 32)
        update_watchdog()
        print("Watchdog timer reset")
        for _ in range(2):
            time.sleep(1)
            if check_watchdog():
                print("Watchdog triggered - stopping motors")
                raise Exception("Watchdog timeout")

        print("\nStop turn")
        rc.TurnRightMixed(address, 0)
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
