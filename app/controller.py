#!/usr/bin/env python
# Original Source: https://github.com/piborg/MoveMyServo

import time

from references import UltraBorg
from references import ThunderBorg

from ultrasonics import Ultrasonics
from motors import Motors

class Controller():
    ub = UltraBorg.UltraBorg()
    tb = ThunderBorg.ThunderBorg()


    def __init__(self):
        self.ub.Init()
        self.tb.Init()
        self.us = Ultrasonics(self.ub);
        self.motors = Motors(self.tb);

    def run(self):
        try:
            while True:
                self.us.read()
                self.motors.move(self.us.right, self.us.front, self.us.left, self.us.back)
                time.sleep(.08)
        except KeyboardInterrupt:
            # User has pressed CTRL+C
            print 'Done'
            if(self.motors):
                self.motors.shutdown()

        except:
            if(self.motors):
                self.motors.shutdown()
def main():
    controller = Controller()
    controller.run()

if __name__ == '__main__':
    main()