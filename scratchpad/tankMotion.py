#!/usr/bin/env python
# coding: Latin-1

# Simple example of a motor sequence script

# Import library functions we need

import ThunderBorg
import time
import sys

# Setup the ThunderBorg
global TB
TB = ThunderBorg.ThunderBorg()     # Create a new ThunderBorg object
# TB.i2cAddress = 0x15              # Uncomment and change the value if you have changed the board address
TB.Init()                          # Set the board up (checks the board is connected)
if not TB.foundChip:
    boards = ThunderBorg.ScanForThunderBorg()
    if len(boards) == 0:
        print 'No ThunderBorg found, check you are attached :)'
    else:
        print 'No ThunderBorg at address %02X, but we did find boards:' % (TB.i2cAddress)
        for board in boards:
            print '    %02X (%d)' % (board, board)
        print 'If you need to change the I�C address change the setup line so it is correct, e.g.'
        print 'TB.i2cAddress = 0x%02X' % (boards[0])
    sys.exit()

stepDelay = 0.21
# Number of seconds between each sequence step

# Loop over the sequence until the user presses CTRL+C
print 'Press CTRL+C to finish'
try:
    t = True
    last_time = time.time()

    while t:
        # Go through each entry in the sequence in order
        # for step in sequence:
        # Set the first motor to the first value in the pair
        TB.SetMotor1(1)
        # Set the second motor to the second value in the pair
        TB.SetMotor2(-1)
        # print '%+.1f %+.1f' % (step[0], step[1])
        now = time.time()
        if (now - last_time) > stepDelay:
            t = False

    TB.SetMotor1(0)
    TB.SetMotor2(0)

    TB.MotorsOff()                 # Turn both motors off

except KeyboardInterrupt:
    # User has pressed CTRL+C
    TB.SetMotor1(0)
    TB.SetMotor2(0)

    TB.MotorsOff()                 # Turn both motors off
    print 'Done'
