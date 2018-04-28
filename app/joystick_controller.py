#!/usr/bin/env python3
# coding: Latin-1

# Original Source: https://piborg.org

# Load library functions we want
import time
import os
import sys
import pygame
from references import UltraBorg3
from references import ThunderBorg3


class JoystickController():

    # Settings for the joystick
    axisUpDown = 1                          # Joystick axis to read for up / down position
    # Set this to True if up and down appear to be swapped
    axisUpDownInverted = False
    # Joystick axis to read for left / right position
    axisLeftRight = 2
    # Set this to True if left and right appear to be swapped
    axisLeftRightInverted = False
    # Joystick button number for driving slowly whilst held (L2)
    buttonSlow = 6
    # Speed to slow to when the drive slowly button is held, e.g. 0.5 would be half speed
    slowFactor = 0.5
    # Joystick button number for turning fast (R2)
    buttonFastTurn = 7

    leftTrigger = 0
    kickButton = 1
    # Time between updates in seconds, smaller responds faster but uses more processor time
    interval = 0.00

    # Power settings
    voltageIn = 1.2 * 10                    # Total battery voltage to the ThunderBorg
    # Maximum motor voltage, we limit it to 95% to allow the RPi to get uninterrupted power
    voltageOut = 12.0 * 0.95

    def __init__(self, thunder_borg_instance, ultraborg_instance):
        # Re-direct our output to standard error, we need to ignore standard out to hide some nasty print statements from pygame
        sys.stdout = sys.stderr

        # Setup the ThunderBorg
        self.__tb = thunder_borg_instance
        self.__ub = ultraborg_instance
        # TB.i2cAddress = 0x15                  # Uncomment and change the value if you have changed the board address

        self.__ub.SetServoPosition3(0)
        if not self.__tb.foundChip:
            boards = ThunderBorg3.ScanForThunderBorg()
            if len(boards) == 0:
                print('No ThunderBorg found, check you are attached :)')
            else:
                print('No ThunderBorg at address %02X, but we did find boards:' %
                      (self.__tb.i2cAddress))
                for board in boards:
                    print('    %02X (%d)' % (board, board))
                print(
                    'If you need to change the I�C address change the setup line so it is correct, e.g.')
                print('TB.i2cAddress = 0x%02X' % (boards[0]))
            sys.exit()
        # Ensure the communications failsafe has been enabled!
        failsafe = False
        for i in range(5):
            self.__tb.SetCommsFailsafe(True)
            failsafe = self.__tb.GetCommsFailsafe()
            if failsafe:
                break
        if not failsafe:
            print('Board %02X failed to report in failsafe mode!' %
                  (self.__tb.i2cAddress))
            sys.exit()

        # Setup the power limits
        if self.voltageOut > self.voltageIn:
            self.maxPower = 1.0
        else:
            self.maxPower = self.voltageOut / float(self.voltageIn)

        # Show battery monitoring settings
        battMin, battMax = self.__tb.GetBatteryMonitoringLimits()
        battCurrent = self.__tb.GetBatteryReading()
        print('Battery monitoring settings:')
        print('    Minimum  (red)     %02.2f V' % (battMin))
        print('    Half-way (yellow)  %02.2f V' % ((battMin + battMax) / 2))
        print('    Maximum  (green)   %02.2f V' % (battMax))
        print('')
        print('    Current voltage    %02.2f V' % (battCurrent))
        print()

    def run(self):
        # Setup pygame and wait for the joystick to become available
        self.__tb.MotorsOff()
        self.__tb.SetLedShowBattery(False)
        self.__tb.SetLeds(0, 0, 1)
        # Removes the need to have a GUI window
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        # pygame.display.set_mode((1,1))
        print('Waiting for joystick... (press CTRL+C to abort)')
        self.__tb.SetLeds(0, 0, 0)
        while True:
            try:
                try:
                    pygame.joystick.init()
                    # Attempt to setup the joystick
                    if pygame.joystick.get_count() < 1:
                        # No joystick attached, set LEDs blue
                        self.__tb.SetLeds(0, 0, 1)
                        pygame.joystick.quit()
                        time.sleep(0.1)
                    else:
                        # We have a joystick, attempt to initialise it!
                        joystick = pygame.joystick.Joystick(0)
                        break
                except pygame.error:
                    # Failed to connect to the joystick, set LEDs blue
                    self.__tb.SetLeds(0, 0, 1)
                    pygame.joystick.quit()
                    time.sleep(0.1)
            except KeyboardInterrupt:
                # CTRL+C exit, give up
                print('\nUser aborted')
                self.__tb.SetCommsFailsafe(False)
                self.__tb.SetLeds(0, 0, 0)
                sys.exit()
        print('Joystick found')
        joystick.init()
        self.__tb.SetLedShowBattery(True)
        ledBatteryMode = True
        try:
            print('Press CTRL+C to quit')
            driveLeft = 0.0
            driveRight = 0.0
            running = True
            hadEvent = False
            upDown = 0.0
            leftRight = 0.0
            # Loop indefinitely
            while running:
                # Get the latest events from the system
                hadEvent = False
                events = pygame.event.get()
                # Handle each event individually
                for event in events:
                    if event.type == pygame.QUIT:
                        # User exit
                        running = False
                    elif event.type == pygame.JOYBUTTONDOWN:
                        # A button on the joystick just got pushed down
                        hadEvent = True
                    elif event.type == pygame.JOYBUTTONUP:
                        # A button on the joystick just got pushed down
                        releaseEvent = True
                    elif event.type == pygame.JOYAXISMOTION:
                        # A joystick has been moved
                        hadEvent = True
                    if hadEvent:
                        if(joystick.get_button(self.leftTrigger)):
                            print(joystick.get_button(self.leftTrigger))
                            self.__ub.SetServoPosition3(-0.6)
                        if(joystick.get_button(self.kickButton)):
                            self.__ub.SetServoPosition3(0.7)
                        # Read axis positions (-1 to +1)
                        if self.axisUpDownInverted:
                            upDown = -joystick.get_axis(self.axisUpDown)
                        else:
                            upDown = joystick.get_axis(self.axisUpDown)
                        if self.axisLeftRightInverted:
                            leftRight = -joystick.get_axis(self.axisLeftRight)
                        else:
                            leftRight = joystick.get_axis(self.axisLeftRight)
                        # Apply steering speeds
                        if not joystick.get_button(self.buttonFastTurn):
                            leftRight *= 0.5

                        # Determine the drive power levels
                        driveLeft = -upDown
                        driveRight = -upDown
                        if leftRight < -0.05:
                            # Turning left
                            driveLeft *= 1.0 + (2.0 * leftRight)
                        elif leftRight > 0.05:
                            # Turning right
                            driveRight *= 1.0 - (2.0 * leftRight)
                        # Check for button presses
                        if joystick.get_button(self.buttonSlow):
                            driveLeft *= self.slowFactor
                            driveRight *= self.slowFactor
                        # Set the motors to the new speeds
                        self.__tb.SetMotor1(driveRight * self.maxPower)
                        self.__tb.SetMotor2(driveLeft * self.maxPower)
                # Change LEDs to purple to show motor faults
                if self.__tb.GetDriveFault1() or self.__tb.GetDriveFault2():
                    if ledBatteryMode:
                        self.__tb.SetLedShowBattery(False)
                        self.__tb.SetLeds(1, 0, 1)
                        ledBatteryMode = False
                else:
                    if not ledBatteryMode:
                        self.__tb.SetLedShowBattery(True)
                        ledBatteryMode = True
                # Wait for the interval period
                time.sleep(self.interval)
            # Disable all drives
            self.__tb.MotorsOff()
        except KeyboardInterrupt:
            # CTRL+C exit, disable all drives
            self.__tb.MotorsOff()
            self.__tb.SetCommsFailsafe(False)
            self.__tb.SetLedShowBattery(False)
            self.__tb.SetLeds(0, 0, 0)
        print

    def init_main():
        self.__tb.Init()
        self.__ub.Init()


def main():
    tb = ThunderBorg3.ThunderBorg()
    ub = UltraBorg3.UltraBorg()
    controller = GolfJoystickController(tb, ub)
    controller.init_main()
    controller.run()


if __name__ == '__main__':
    main()
