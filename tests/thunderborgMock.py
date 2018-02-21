
class ThunderBorg():

    def MotorsOff(self):
        print("Motors Off")

    def SetCommsFailsafe(self, failsafe):
        print("Comms Failsafe: " + failsafe)

    def SetLedShowBattery(self, showLedBattery):
        print("showLedBattery" + showLedBattery)

    def SetLeds(self, red, green, blue):
        print("Set LEDs")

    def SetMotor1(self, speed):
        print("Set Motor 1:" + speed)

    def SetMotor2(self, speed):
        print("Set Motor 2:" + speed)
