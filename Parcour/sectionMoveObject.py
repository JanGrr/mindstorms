from .section import Section
from pybricks.tools import wait
from pybricks.parameters import Stop

import time

class SectionMoveObject(Section):
    
    def __init__(self):
        super().__init__()

        self.name = "Move Object"
        self.target_distance = 250 # mm Abstand zur Wand links 
        #TODO Distanz vllt näher ran, damit Sensor genauer wird????
        self.speed = 120 # Vorwärtsgeschwindigkeit
        self.kp = 1.2 # P-Gain
        self.kd = 4.0 # D-Gain
        self.correctSensorPosition = False 

        self.last_error = 0
        self.last_time = time.time()
        self.distance_travelled = 0
        self.max_distance = 19500
        self.firstPartDone = False
        self.turned = False
        
        #Konstanten
        self.SONICANGLE = 39
        self.STEERING = 80
        self.GRIPPINGANGLE = 3

    def reset(self, robot):
        # TODO: Implement reset logic if needed
        self.last_error = 0
        self.distance_travelled = 0
        self.last_time = time.time()
        self.firstPartDone = False
        self.turned = False

    # Fahren, entlang der linken Wand
    def run_one_step(self, robot):
        #Sensor über Motor in die richtige Position bewegen
        #1
        if not self.correctSensorPosition:
            robot.set_gripper_and_ultrasonic_angle(self.SONICANGLE)
            self.correctSensorPosition = True
        dist = robot.ultrasonic_sensor.distance()
        #robot.ev3.speaker.beep()
        print("Abstand: " + str(dist) + " mm") # <-- zeigt jeden Schritt

        if dist is None:    #falls Sensor nichts erkennt
            dist = self.target_distance 
            
        error = dist - self.target_distance
        #now = time.time()
        #dt = now - self.last_time if now != self.last_time else 0.01
        
        #d_error = (error - self.last_error) / dt
        steering = self.kp * error
        #steering = self.kp * error + self.kd * d_error
        
        steering = max(min(steering, self.STEERING), -self.STEERING)

        self.update_section_screen(robot, status= str(dist) + " mm", status2="Error:" + str(error), status3="Steering" + str(steering))
        #2
        robot.drive_base.drive(self.speed, steering)
        
        
        self.last_error = error
        #self.last_time = now
        #self.distance_travelled += self.speed * dt
        self.distance_travelled += self.speed * 0.01
            
        #3
        if self.distance_travelled >= self.max_distance:
            robot.drive_base.stop() 
            print("firstPartDone")
            self.update_section_screen(robot, status="firstPartDOne",status2="", status3="")
            self.firstPartDone = True
            wait(1000)

        #4&5
        if self.firstPartDone == True and self.turned == False:
            robot.spin(90)
            self.target_distance = 110
            self.max_distance = 600
            print("turned")
            self.turned = True
        
        #6a
        robot.set_gripper_and_ultrasonic_angle(self.GRIPPINGANGLE)
        #7
        color = robot.color_sensor.color()
        self.update_section_screen(robot, status=color)
        robot.drive_base.drive_time(-120, 30, 4000)
        """
        while color != color.WHITE
            robot.drive_base.drive(-120, 30)
         """
        
        #8 
        robot.set_gripper_and_ultrasonic_angle(self.SONICANGLE)
        #TODO driveLeftWall() Funktion coden
        
         
        #9
        
