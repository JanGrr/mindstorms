from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction
from pybricks.robotics import DriveBase

class Robot:

    def __init__(self):
        self.ev3 = EV3Brick()
        self.motor_left = Motor(Port.A, Direction.COUNTERCLOCKWISE, gears=None)                                         # Gears e.g. [14, 20]
        self.motor_right = Motor(Port.B, Direction.COUNTERCLOCKWISE, gears=None)
        self.WHEEL_DIAMETER_MM = 55                                 # Wheel diameter of drive wheels in mm         
                                                                    # If the robot does not drive far enough with straight(1000), slightly decrease WHEEL_DIAMETER_MM
        self.AXLE_TRACK_MM = 105                                    # Distance between the two driven wheels in mm
                                                                    # If the robot turns less than 360° with spin(360), slightly increase AXLE_TRACK_MM (but always adjust WHEEL_DIAMETER_MM first)
        self.drive_base = DriveBase(self.motor_left, self.motor_right, self.WHEEL_DIAMETER_MM, self.AXLE_TRACK_MM)      # Class that already implements driving functions
        self.drive_base.settings(straight_speed=200, straight_acceleration=100, turn_rate=200, turn_acceleration=100)
        self.__motor_small = Motor(Port.C, Direction.CLOCKWISE, gears=None)
        self.color_sensor = ColorSensor(Port.S1)
        self.touch_sensor = TouchSensor(Port.S2)
        self.ultrasonic_sensor = UltrasonicSensor(Port.S3)
        self.gyro_sensor = GyroSensor(Port.S4)

    def drive(self, drive_speed, turn_rate):                          # drive_speed in mm/s, turn_rate in deg/s
        self.drive_base.drive(drive_speed, turn_rate)                      # continoues drive untill stop() is called

    def stop(self): # Stop individual motors immediately, because drive_base.stop() would let the motors coast
        self.drive_base.stop(Stop.HOLD)

    def straight(self, distance_mm):
        self.drive_base.straight(distance_mm)

    def reset_drive_base_settings(self):
        self.drive_base.stop()                  # NOT self.drive_base.stop(Stop.HOLD), bit confusing
        self.drive_base.settings(straight_speed=200, straight_acceleration=100, turn_rate=200, turn_acceleration=100)

    def spin(self, angle):
        self.drive_base.turn(angle)

    def driven_distance(self):
        return self.drive_base.distance()
    
    def angle_turned(self):
        return self.drive_base.angle()

    def reset_distance_and_angle(self):
        self.drive_base.reset()

    def calibrate_gripper_and_ultrasonic_angle(self):
        self.__motor_small.run_until_stalled(speed=-40, then=Stop.HOLD, duty_limit=80)  # Fully retract gripper and ultrasonic sensor
        self.__motor_small.reset_angle(0)

    # gets a target angle in degrees and moves the gripper and ultrasonic sensor to that angle
    def set_gripper_and_ultrasonic_angle(self, target_angle, turn_speed=20, wait=True):
        self.__motor_small.run_target(speed=turn_speed, target_angle=target_angle, then=Stop.HOLD, wait=wait)
