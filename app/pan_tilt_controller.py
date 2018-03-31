#!/usr/bin/env python3

from references import UltraBorg3


# max_pan_degrees : 270 degrees or 135 degrees depending on servo
# pan(...): -(max_pan_degrees/2) to +(max_pan_degrees/2) e.g. for 270 degrees motor it is 270
# Tilt Motor = UltraBorg motor 1
# Pan Motor = UltraBorg motor 2

class PanTiltController():

    def __init__(self, ultraborg_instance, max_pan_degrees, max_tilt_degrees):
        self.__ultraborg = ultraborg_instance
        self.__max_pan_degrees = max_pan_degrees
        self.__max_tilt_degrees = max_tilt_degrees
        self.__abs_pan_per_degree = 1 / self.__max_pan_degrees
        self.__abs_tilt_per_degree = 1 / self.__max_tilt_degrees

    def pan(self, degrees):
        if(abs(degrees) < self.__max_pan_degrees / 2) and abs(degrees) > self.__min_pan_degrees / 2):
            turn_absolute=self.__abs_pan_per_degree * degrees
            self.__ultraborg.SetServoPosition2(turn_absolute)
            return True
        else:
            return False

    def pan_absolute(self, value):
        if(abs(value) * self.__abs_pan_per_degree > self.__min_pan_degrees / 2) and
            (abs(value) * self.__abs_pan_per_degree < self.__abs_pan_per_degree):
            self.__ultraborg.SetServoPosition2(value)
            return True
        else:
            return False

    def tilt(self, degrees):
        if(abs(degrees) < self.__max_tilt_degrees / 2) and abs(degrees) > self.__min_tilt_degrees / 2):
            turn_absolute=self.__abs_tilt_per_degree * degrees
            self.__ultraborg.SetServoPosition1(turn_absolute)

    def tilt_absolute(self, value):
        if(abs(value) * self.__abs_tilt_per_degree > self.__min_tilt_degrees / 2) and
            (abs(value) * self.__abs_tilt_per_degree < self.__abs_tilt_per_degree):
            self.__ultraborg.SetServoPosition1(value)
            return True
        else:
            return False
