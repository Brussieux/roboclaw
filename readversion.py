import time
from roboclaw import Roboclaw

#Windows comport name
#rc = Roboclaw("COM11",115200)
#Linux comport name
rc = Roboclaw("/dev/ttyACM0",115200)

if rc.Open() == 0:
    print("Error: Could not open serial port")
    exit(1)

while 1:
    #Get version string
    version = rc.ReadVersion(0x80)
    if version[0] == False:
        print("GETVERSION Failed")
    else:
        # Remove newline characters and print the version string
        print(version[1].strip())
    time.sleep(1)
