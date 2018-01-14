#!/usr/bin/env python
# Original Source: https://github.com/piborg/MoveMyServo

# Import the libraries we need
from references import ThunderBorg
import time

class Motors():
    def __init__(self, thunderBorgInstance):
        self.tb = thunderBorgInstance
        self.safeDistance = 500 #mm
        if not self.tb.foundChip:
            boards = ThunderBorg.ScanForThunderBorg()
            if len(boards) == 0:
                print 'No ThunderBorg found, check you are attached :)'
            else:
                print 'No ThunderBorg at address %02X, but we did find boards:' % (self.tb.i2cAddress)
                for board in boards:
                    print ' %02X (%d)' % (board, board)
                print 'If you need to change the I2C address change the setup line so it is correct, e.g.'
                print 'self.tb.i2cAddress = 0x%02X' % (boards[0])
            sys.exit()
        # Ensure the communications failsafe has been enabled!
        failsafe = False
        for i in range(5):
            self.tb.SetCommsFailsafe(True)
            failsafe = self.tb.GetCommsFailsafe()
            if failsafe:
                break
        if not failsafe:
            print 'Board %02X failed to report in failsafe mode!' % (self.tb.i2cAddress)
            sys.exit()

        self.driveRight = 1.0
        self.driveLeft = 1.0
        # Power settings
        self.voltageIn = 1.2 * 10                    # Total battery voltage to the ThunderBorg
        self.voltageOut = 12.0 * 0.95                # Maximum motor voltage, we limit it to 95% to allow the RPi to get uninterrupted power

        # Setup the power limits
        if self.voltageOut > self.voltageIn:
            self.maxPower = 1.0
        else:
            self.maxPower = self.voltageOut / float(self.voltageIn)

        self.tb.MotorsOff()

    def move(self, right, front, left, back):
        self.speed = self.maxPower;
        if(front < self.safeDistance + self.safeDistance/2):
            distanceLeft = front - self.safeDistance
            self.speed = (distanceLeft/self.safeDistance) * self.maxPower

        self.tb.SetMotor1(self.driveRight * self.speed)
        self.tb.SetMotor2(self.driveLeft * self.speed)

    def shutdown(self):
        self.tb.MotorsOff()
        self.tb.SetCommsFailsafe(False)
        self.tb.SetLedShowBattery(False)
        self.tb.SetLeds(0,0,0)
