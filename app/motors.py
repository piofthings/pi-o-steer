#!/usr/bin/env python
# Original Source: https://github.com/piborg/MoveMyServo

# Import the libraries we need
from references import ThunderBorg
import time

class Motors():
    tickSpeed = 0.1 #seconds
    forwardSpeed = 0.0
    leftSpeed = 0.0
    rightSpeed = 0.0
    reverseSpeed = 0.0

    frontPrev = 0

    def __init__(self, thunderBorgInstance, tickSpeed):
        self.tb = thunderBorgInstance
        self.tickSpeed = tickSpeed
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
            self.maxPower = 0.5
        else:
            self.maxPower = self.voltageOut / float(self.voltageIn)

        self.speed = self.maxPower;

        self.tb.MotorsOff()

    def move(self, right, front, left, back):

        distanceMoved = -1

        if (front != 'No reading'):
            if (self.frontPrev != 0):
                distanceMoved = (self.frontPrev - front)
                print 'Distance moved %d' % distanceMoved

                if (distanceMoved > 0 and self.speed > 0):
                    self.forwardSpeed = (self.frontPrev - front)/self.tickSpeed #mm/seconds
                    #print 'Speed (mm/s) %d' % self.forwardSpeed
                    if (self.forwardSpeed > front):
                        self.speed = 0
            self.frontPrev = front
        else:
            print 'Distance moved was not read'


        self.tb.SetMotor1(self.driveRight * self.speed)
        self.tb.SetMotor2(self.driveLeft * self.speed)

        print 'Left  % 4d mm' % (left)
        print 'Front %(front) 4d mm and speed %(forwardSpeed) 4d' % { "front": front, "forwardSpeed": self.forwardSpeed }
        print 'Right % 4d mm' % (right)
#        print 'Back  % 4d mm' % (back)
        #self.lef

    def shutdown(self):
        self.tb.MotorsOff()
        self.tb.SetCommsFailsafe(False)
        self.tb.SetLedShowBattery(False)
        self.tb.SetLeds(0,0,0)
