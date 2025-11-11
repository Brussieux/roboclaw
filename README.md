RoboClaw Python (Python 3)
==========================

This project provides a Python 3 interface (`roboclaw.py`) and a set of concise example scripts for common RoboClaw operations (speed, distance, position, PWM, EEPROM, version reading, mixed drive, TCP control, etc.). Safety features (watchdog + Ctrl+C handling) are now integrated directly into `roboclaw.py`.

Key Changes vs Original
-----------------------
* Python 3 migration (print functions, byte handling, removal of long())
* Unified safety system: `init_safety`, `check_watchdog`, `update_watchdog`, `enableFailsafe(ms)` built into the core module
* Minimal TCP protocol implementation (`speedacceldistance.py` + `RCIHM.py`) with position streaming every 200 ms
* Simplified examples; only essential output is printed
* Added a smoke test using a fake serial backend (see `tests/`)

Safety / Failsafe
-----------------
Call these before issuing motor commands:

```python
from roboclaw import Roboclaw, init_safety, enableFailsafe, update_watchdog, check_watchdog

rc = Roboclaw('/dev/ttyACM0', 115200)
rc.Open()
address = 0x80
init_safety(rc, address)        # sets up signal handler and starts watchdog timer
enableFailsafe(5000)            # optional: set watchdog timeout to 5000 ms

# every time you send movement commands:
update_watchdog()
if check_watchdog():
    print('Timed out')
```

If the watchdog interval passes without `update_watchdog()` the motors are stopped automatically. Ctrl+C (SIGINT) also stops motors cleanly.

TCP Control Protocol (Optional)
-------------------------------
Server: `speedacceldistance.py` exposes a TCP port (65432) and streams encoder positions:
* Outgoing messages: `C` (connect), `>` (prompt), `P:<m1>,<m2>` (positions)
* Incoming messages: `DISTANCE:<counts>` or `p` (position query at prompt)
Client: `RCIHM.py` prints only protocol tokens (`C`, `>`, `P:` lines) for a minimal HMI.

Running Examples
----------------
1. Install pyserial (if not already):
```bash
python3 -m pip install pyserial
```
2. Standard encoder read:
```bash
python3 read.py
```
3. Distance with TCP streaming:
```bash
python3 speedacceldistance.py
python3 RCIHM.py   # in another terminal / host
```

Example Scripts Overview
------------------------
* `read.py` – continuous encoder & speed display
* `readversion.py` – prints firmware version each second
* `readeeprom.py` / `writeeeprom.py` – EEPROM access
* `speed.py`, `speedaccel.py`, `speeddistance.py`, `speedacceldistance.py` – movement variants
* `position.py` – position move with accel/decel profile
* `mixedpwm.py`, `mixedspeedaccel.py` – mixed channel control
* `bareminimum.py` – minimal open/loop example
* `RCIHM.py` – minimal TCP HMI client

Testing
-------
Run the smoke test (no hardware needed):
```bash
python3 tests/test_roboclaw_smoke.py
```

Contributing / Next Steps
-------------------------
Potential improvements:
* Add pytest + real hardware integration tests
* Abstract TCP protocol into a class
* Optional async I/O for client/server

License
-------
This code is adapted for internal use. Ensure compliance with RoboClaw vendor licensing for distribution.

Troubleshooting
---------------
* If serial port fails: verify user is in the `dialout` group on Linux.
* Watchdog firing early: confirm you call `update_watchdog()` after every movement command.
* No TCP position updates: ensure movement started and client didn't send malformed input.

Let me know if you’d like a requirements file or a more detailed protocol spec (a shorter extract of `PROTOCOL.txt`).
