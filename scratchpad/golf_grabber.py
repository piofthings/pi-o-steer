#!/usr/bin/env python3
# coding: latin-1

# Original Source: https://piborg.org

# Import the libraries we need
import UltraBorg3
import time

# Settings
panServoMin = -0.70                # Smallest servo position to use
panServoMax = +0.7

tiltServoMin = -0.5
tiltServoMax = +0.5

startupDelay = 0.5              # Delay before making the initial move
pulseWidth = 0.01

panServoRate = 2.0 / 135
stepDelay = 0.1
# Start the UltraBorg
UB = UltraBorg3.UltraBorg()      # Create a new UltraBorg object
UB.Init()                       # Set the board up (checks the board is connected)

try:
    print('Move to central')
    # Initial settings
    grabberInitialPosition = 0.0
    # Set our initial servo positions
    UB.SetServoPosition3(grabberInitialPosition)
    # Wait a while to be sure the servos have caught up
    time.sleep(startupDelay)
    n = 0
    tiltDirection = 'straight'
    panDirection = 'left'

    while True:
        if panDirection == 'left':
            grabberInitialPosition += panServoRate
            if grabberInitialPosition > panServoMax:
                panDirection = 'right'
        elif panDirection == 'right':
            grabberInitialPosition -= panServoRate
            if grabberInitialPosition < panServoMin:
                panDirection = 'left'

        if (grabberInitialPosition < panServoMax) and (grabberInitialPosition > panServoMin):
            print('Pan  servo going ' + panDirection +
                  ' at' + repr(grabberInitialPosition))
            UB.SetServoPosition3(grabberInitialPosition)

        time.sleep(stepDelay)

    UB.SetServoPosition3(0)

except KeyboardInterrupt:
    # User has pressed CTRL+C
    UB.SetServoPosition3(0)

    print('Done')
