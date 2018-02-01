#!/usr/bin/env python
# coding: latin-1

# Original Source: https://piborg.org

# Import the libraries we need
import UltraBorg
import time

# Settings
servoMin = -0.90                 # Smallest servo position to use
servoMax = +0.90                 # Largest servo position to use
startupDelay = 0.5              # Delay before making the initial move
stepDelay = 0.4                 # Delay between steps
rateStart = 0.05                # Step distance for all servos during initial move
rateServo4 = 0.1               # Step distance for servo #4

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
    # Wait a while to be sure the servos have caught up
    time.sleep(startupDelay)
#    print 'Sweep to start position'
#    while servo4 > servoMin:
        # Reduce the servo positions
#        servo4 -= rateStart
        # Check if they are too small
#        if servo4 < servoMin:
#            servo4 = servoMin
        # Set our new servo positions
#        UB.SetServoPosition4(servo4)
        # Wait until the next step
#        time.sleep(stepDelay)
    print 'Sweep all servos through the range'
    direction = 'left'
    while True:
	if direction == 'left':
        	# Increase the servo positions at separate rates
	        servo4 += rateServo4
        	# Check if any of them are too large, if so wrap to the over end
	        if servo4 > servoMax:
        	    #servo4 -= (servoMax - servoMin)
		    direction = 'right'
	else:
		servo4 -= rateServo4
		if servo4 < servoMin:
		    direction = 'left'

	if (servo4 < servoMax) & (servo4 > servoMin):
		print 'Servo going ' + direction + ' at' + repr(servo4)
        	# Set our new servo positions
	        UB.SetServoPosition4(servo4)
            UB.SetServoPosition3(servo4*-1)
	        # Wait until the next step
	        time.sleep(stepDelay)
except KeyboardInterrupt:
    # User has pressed CTRL+C
    print 'Done'
