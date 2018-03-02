#!/usr/bin/env python
# coding: latin-1

# Import the libraries we need
import UltraBorg
import time

# Settings
servoMin = -0.40                 # Smallest servo position to use
servoMax = +0.40                 # Largest servo position to use
startupDelay = 0.5              # Delay before making the initial move
stepDelay = 0.1                 # Delay between steps
rateStart = 0.05                # Step distance for all servos during initial move
rateServo4 = 0.01               # Step distance for servo #4

# Start the UltraBorg
UB = UltraBorg.UltraBorg()      # Create a new UltraBorg object
UB.Init()                       # Set the board up (checks the board is connected)

# Loop over the sequence until the user presses CTRL+C
print 'Press CTRL+C to finish'
try:
    print 'Move to central'
    # Initial settings
    servo4 = 0.0
    # Set our initial servo positions
    UB.SetServoPosition4(servo4)
    UB.SetServoPosition3(servo4)
except KeyboardInterrupt:
    # User has pressed CTRL+C
    print 'Done'
