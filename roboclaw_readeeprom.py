import time
from roboclaw import Roboclaw

#Windows comport name
#rc = Roboclaw("COM7",115200)
#Linux comport name
rc = Roboclaw("/dev/ttyACM0",115200)

rc.Open()

#Get version string
for x in range(0,255):
    value = rc.ReadEeprom(0x80,x)
    value = rc.ReadEeprom(0x80, x)
    if value[0] == False:
        print(f"EEPROM: {x} Failed")
    else:
        print(f"EEPROM: {x} {value[1]}")
