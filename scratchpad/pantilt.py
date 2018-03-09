#!/usr/bin/env python3
# coding: latin-1

# Original Source: https://piborg.org

# Import the libraries we need
import UltraBorg3
import time

# Settings
startupDelay = 0.5              # Delay before making the initial move
pulseWidth = 0.01
rateServo4 = 0.20               # Step distance for servo #4

# Start the UltraBorg
UB = UltraBorg3.UltraBorg()      # Create a new UltraBorg object
UB.Init()                       # Set the board up (checks the board is connected)

try:
    print('Move to central')
    # Initial settings
    servo1 = 0.0
    # Set our initial servo positions
    position = UB.GetServoStartup2()
    print(position)
    UB.SetServoPosition1(servo1)
    # UB.SetServoPosition2(0.0015)
    # Wait a while to be sure the servos have caught up
    time.sleep(startupDelay)
    n = 0
    while n < 20:
        n = n + 1
        UB.SetServoPosition2(rateServo4)
        # Wait until the next step
        time.sleep(pulseWidth)

    UB.SetServoPosition2(0)

except KeyboardInterrupt:
    # User has pressed CTRL+C
    UB.SetServoPosition2(0)

    print('Done')
