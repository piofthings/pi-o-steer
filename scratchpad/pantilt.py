#!/usr/bin/env python3
# coding: latin-1

# Original Source: https://piborg.org

# Import the libraries we need
import UltraBorg3
import time

# Settings
panServoMin = -0.5                 # Smallest servo position to use
panServoMax = +0.5

tiltServoMin = -0.5
tiltServoMax = +0.5

startupDelay = 0.5              # Delay before making the initial move
pulseWidth = 0.01
titleServoMaxAngle = 1.4 / 135
tiltServoRate = 0.05               # Step distance for servo #4
panServoRate = 2.0 / 270
stepDelay = 0.1
# Start the UltraBorg
UB = UltraBorg3.UltraBorg()      # Create a new UltraBorg object
UB.Init()                       # Set the board up (checks the board is connected)

try:
    print('Move to central')
    # Initial settings
    tiltServoPosition = 0.4
    panServoPosition = 0.0
    # Set our initial servo positions
    UB.SetServoPosition1(tiltServoPosition)
    UB.SetServoPosition2(panServoPosition)
    # UB.SetServoPosition2(0.0015)
    # Wait a while to be sure the servos have caught up
    time.sleep(startupDelay)
    n = 0
    tiltDirection = 'straight'
    panDirection = 'left'
    UB.SetServoMaximum2(5000)
    UB.SetServoMinimum2(1000)

    print("Pan Servo Maximum " + repr(UB.GetServoMaximum2()))
    print("Pan Servo Minimum " + repr(UB.GetServoMinimum2()))
    while True:
        if panDirection == 'left':
            panServoPosition += panServoRate
            if panServoPosition > panServoMax:
                panDirection = 'right'
        elif panDirection == 'right':
            panServoPosition -= panServoRate
            if panServoPosition < panServoMin:
                panDirection = 'left'

        if tiltDirection == 'up':
            # Increase the servo positions at separate rates
            tiltServoPosition += tiltServoRate
            # Check if any of them are too large, if so wrap to the over end
            if tiltServoPosition > tiltServoMax:
                tiltDirection = 'down'
        elif tiltDirection == 'down':
            tiltServoPosition -= tiltServoRate
            if tiltServoPosition < tiltServoMin:
                tiltDirection = 'up'

        if (tiltServoPosition < tiltServoMax) and (tiltServoPosition > tiltServoMin):
            print('Tilt servo going ' + tiltDirection +
                  ' at' + repr(tiltServoPosition))
            UB.SetServoPosition1(tiltServoPosition)
        if (panServoPosition < panServoMax) and (panServoPosition > panServoMin):
            print('Pan  servo going ' + panDirection +
                  ' at' + repr(panServoPosition))
            UB.SetServoPosition2(panServoPosition)

        time.sleep(stepDelay)

    UB.SetServoPosition2(0)

except KeyboardInterrupt:
    # User has pressed CTRL+C
    UB.SetServoPosition2(0)

    print('Done')
