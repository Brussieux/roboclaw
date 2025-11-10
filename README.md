Roboclaw Python (ported to Python 3)
=================================

This folder contains a Python3-friendly port of the original Roboclaw Python scripts.

What I changed
- Converted bytes handling for serial I/O (chr/ord -> to_bytes / indexing).
- Replaced Python 2-only constructs like long() with int(), and updated prints to Python 3.
- Fixed minor bugs and normalized example output formatting.
- Added a simple smoke test that uses a FakeSerial to validate basic read/write logic without hardware.

How to run

1. Install requirements (if you use pyserial):

   ```bash
   python3 -m pip install pyserial
   ```

2. Run the smoke test (no hardware required):

   ```bash
   python3 tests/test_roboclaw_smoke.py
   ```

3. Run any example after editing the comport to match your system (e.g. `/dev/ttyACM0`):

   ```bash
   python3 roboclaw_read.py
   ```

Notes
- The library (`roboclaw.py`) no longer opens the serial port automatically in unit tests. Use `rc.Open()` when you want to connect to real hardware.
- If you want consistent styling or to run unit tests in CI, I can add a requirements file and a pytest-based test suite.
