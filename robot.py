from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction
from pybricks.robotics import DriveBase


class Robot:

    def __init__(self):
        self.ev3 = EV3Brick()
        self.motor_left = Motor(Port.A, Direction.COUNTERCLOCKWISE, gears=None)                                         # oder COUNTERCLOCKWISE, Gears z.B. [14, 20]
        self.motor_right = Motor(Port.B, Direction.COUNTERCLOCKWISE, gears=None)
        self.WHEEL_DIAMETER_MM = 80                                 # Raddurchmesser der Antriebsräder in mm
                                                                    # Wenn der Roboter bei straight(1000) nicht weit genug fährt, WHEEL_DIAMETER_MM leicht verringern
        self.AXLE_TRACK_MM = 120                                    # Abstand der beiden angetriebenen Räder voneinander in mm
                                                                    # Wenn der Roboter bei spin(360) weniger als 360° dreht, AXLE_TRACK_MM leicht erhöhen (aber immer erst WHEEL_DIAMETER_MM anpassen)
        self.drive_base = DriveBase(self.motor_left, self.motor_right, self.WHEEL_DIAMETER_MM, self.AXLE_TRACK_MM)      # Klasse die bereits Fahrfunktionen implementiert
        self.drive_base.settings(straight_speed=100, straight_acceleration=50, turn_rate=100, turn_acceleration=50)
        self.motor_small = Motor(Port.C, Direction.CLOCKWISE, gears=None)
        self.motor_small.reset_angle(0)
        self.GRIPPER_CLOSED_AND_ULTRASONIC_UP = True
        self.color_sensor = ColorSensor(Port.S1)
        #self.ultrasonic_sensor = UltrasonicSensor(Port.S2)
        self.gyro_sensor = GyroSensor(Port.S3)
        #self.touch_sensor = TouchSensor(Port.S4)
        self.run_motor_and_sensor_check()

    def run_motor_and_sensor_check(self):
        if (self.motor_left == None):        raise Exception('Left Motor not connected')
        if (self.motor_right == None):       raise Exception('Right Motor not connected')
        if (self.motor_small == None):       raise Exception('Small Motor not connected')
        if (self.color_sensor == None):      raise Exception('Colorsensor not connected')
        #if (self.ultrasonic_sensor == None): raise Exception('Ultrasonic sensor not connected')
        if (self.gyro_sensor == None):       raise Exception('Gyrosensor not connected')
        #if (self.touch_sensor == None):      raise Exception('Touchsensor not connected')

    def drive(self, drive_speed, turn_rate):                          # drive_speed in mm/s, turn_rate in deg/s
        self.drive_base.drive(drive_speed, turn_rate)                      # continoues drive untill stop() is called

    def stop(self): # einzelnen Motoren sofort anhalten, da drive_base.stop() die Motoren ausrollen lassen würde
        self.drive_base.stop() 
        self.motor_left.hold()
        self.motor_right.hold()

    def straight(self, distance_mm): # Programmcode läuft weiter oder?
        self.drive_base.straight(distance_mm)

    # Gyro-Idee zum geradeaus fahren
    # sinnvoll in z.B. 
    # drive_base.reset()
    # gyro_sensor.reset_angle(0)
    # while not touch_sensor.pressed(): 
    # oder while drive_base.distance() < distance_mm:
    # def straight_with_gyro():
    #     correction = 0 - gyro_sensor.angle() * constant         # target_angle = 0 sinnvoller Wert für Konstante so 1-3
    #     drive_base.drive(drive_speed= , turn_rate=correction)

    def spin(self, angle):
        self.drive_base.turn(angle)

    def driven_distance(self):
        return self.drive_base.distance()
    
    def angle_turned(self):
        return self.drive_base.angle()

    def reset_distance_and_angle(self):
        self.drive_base.reset()

    def move_gripper_and_ultrasonic(self):
        if(not self.GRIPPER_CLOSED_AND_ULTRASONIC_UP):
            self.motor_small.run_target(speed=30, target_angle=70, then=Stop.HOLD, wait=False)      # Gripper öffnen und Ultraschallsensor nach unten
            self.GRIPPER_CLOSED_AND_ULTRASONIC_UP = False
        else:
            self.motor_small.run_target(speed=30, target_angle=0, then=Stop.HOLD, wait=False)       # Gripper schließen und Ultraschallsensor zur Seite
            self.GRIPPER_CLOSED_AND_ULTRASONIC_UP = True
