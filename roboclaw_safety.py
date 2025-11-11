import time
import signal
import sys

# Global variables for watchdog
last_command_time = 0
WATCHDOG_TIMEOUT = 10  # 10 seconds timeout (default)

def enableFailsafe(failsafeTime: int):
    """Enable/adjust the failsafe watchdog timeout.

    Parameters:
        failsafeTime (int): Timeout in milliseconds. When the time since the
            last command exceeds this value, the watchdog triggers and motors
            are stopped.

    Notes:
        - Internally, the watchdog operates in seconds; the provided
          millisecond value is converted to seconds.
        - Values <= 0 will set a very small timeout (1 ms) to avoid disabling
          the failsafe by mistake.
    """
    global WATCHDOG_TIMEOUT
    try:
        ms = int(failsafeTime)
    except (TypeError, ValueError):
        # Keep current timeout if invalid input is provided
        return
    if ms <= 0:
        ms = 1  # Clamp to 1ms minimum to keep failsafe enabled
    WATCHDOG_TIMEOUT = ms / 1000.0

def init_safety(roboclaw, address):
    """Initialize safety features with the given roboclaw instance"""
    global rc, dev_address
    rc = roboclaw
    dev_address = address
    
    # Setup signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize last command time
    global last_command_time
    last_command_time = time.time()

def stop_motors():
    """Stop all motors safely"""
    # Stop motor 1 by setting speed to 0
    rc.ForwardM1(dev_address, 0)
    rc.BackwardM1(dev_address, 0)
    # Stop motor 2 by setting speed to 0
    rc.ForwardM2(dev_address, 0)
    rc.BackwardM2(dev_address, 0)
    # Short delay to ensure commands are processed
    time.sleep(0.1)
    print("Motors stopped")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('You pressed Ctrl+C!')
    stop_motors()
    sys.exit(0)

def check_watchdog():
    """Check if watchdog timeout has occurred"""
    global last_command_time
    if time.time() - last_command_time > WATCHDOG_TIMEOUT:
        print("Watchdog timeout - stopping motors")
        stop_motors()
        return True
    return False

def update_watchdog():
    """Update the watchdog timer"""
    global last_command_time
    last_command_time = time.time()

def safety_wrapper(func):
    """Decorator to add safety features to motor control functions"""
    def wrapper(*args, **kwargs):
        update_watchdog()  # Update watchdog before command
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            print(f"Error in motor command: {e}")
            stop_motors()
            raise
    return wrapper