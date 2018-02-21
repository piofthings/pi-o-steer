#!/usr/bin/env python
# coding: latin-1

# Original Source: http://piborg.org

# Import the libraries we need
import UltraBorg
import time

# Start the UltraBorg
UB = UltraBorg.UltraBorg()      # Create a new UltraBorg object
UB.Init()                       # Set the board up (checks the board is connected)

# Loop over the sequence until the user presses CTRL+C
print 'Press CTRL+C to finish'
try:
    while True:
        # Read all four ultrasonic values
        usm1 = UB.GetDistance1()
        time.sleep(0.08)
        usm3 = UB.GetDistance3()
        time.sleep(0.08)
        usm2 = UB.GetDistance2()
        time.sleep(0.08)

        usm4 = UB.GetDistance4()
        time.sleep(0.08)
        # Convert to the nearest millimeter
        usm1 = int(usm1)
        usm2 = int(usm2)
        usm3 = int(usm3)
        usm4 = int(usm4)
        # Display the readings
        if usm1 == 0:
            print 'Right No reading'
        else:
            print 'Right % 4d mm' % (usm1)
        if usm2 == 0:
            print 'Front No reading'
        else:
            print 'Front % 4d mm' % (usm2)
        if usm3 == 0:
            print 'Left No reading'
        else:
            print 'Left % 4d mm' % (usm3)
        if usm4 == 0:
            print 'Back No reading'
        else:
            print 'Back % 4d mm' % (usm4)
        print
        # Wait between readings
        time.sleep(.1)
except KeyboardInterrupt:
    # User has pressed CTRL+C
    print 'Done'
