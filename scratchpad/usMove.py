#!/usr/bin/env python
# Original Source: https://github.com/piborg/MoveMyServo

# Import the libraries we need
import UltraBorg
import time

# Settings
distanceMin = 50.0             # Minimum distance in mm, corresponds to servo at -100%
distanceMax = 100.0             # Maximum distance in mm, corresponds to servo at +100%
fastMode = True                 # True moves faster, False gives a more stable position
updateInterval = 0.1            # Time between updates, smaller is faster

# Start the UltraBorg
UB = UltraBorg.UltraBorg()      # Create a new UltraBorg object
UB.Init()                       # Set the board up (checks the board is connected)

# Calculate our divisor
distanceDiv = (distanceMax - distanceMin) / 2.0

# Loop over the sequence until the user presses CTRL+C
print 'Press CTRL+C to finish'
try:
    # Set our initial position
    lastServoPosition = 0.0
    newServoPosition = 0.0
    UB.SetServoPosition1(lastServoPosition)
    # This is the loop which reads the sensor and sets the servo
    while True:
        # Read the ultrasonic values
        if fastMode:
            # We use the raw values so we respond quickly
            distanceMeasured = UB.GetRawDistance1()
        else:
            # We use the filtered values so we get nice stable readings
            distanceMeasured = UB.GetDistance1()
        # Convert to the nearest millimeter
        distanceMeasured = int(distanceMeasured)
        # Generate the servo positions based on the distance readings
        if distanceMeasured != 0:
            newServoPosition = ((distanceMeasured - distanceMin) / distanceDiv) - 1.0
            if newServoPosition > 0.9:
                newServoPosition = 0.9
            elif newServoPosition < -0.9:
                newServoPosition = -0.9
        # Display our readings
        print '%4d mm -> %.1f %%' % (distanceMeasured, newServoPosition * 100.0)
        # Set our new servo position if it has changed
        if newServoPosition != lastServoPosition:
            UB.SetServoPosition4(newServoPosition)
	    UB.SetServoPosition3(newServoPosition * -1)
            lastServoPosition = newServoPosition
        # Wait between readings
        time.sleep(updateInterval)

except KeyboardInterrupt:
    # User has pressed CTRL+C
    print 'Done'
