from .section import Section
from pybricks.tools import wait
from pybricks.parameters import Stop, Color

import time

class SectionMoveObject(Section):
    
    def __init__(self):
        super().__init__()

        self.name = "Move Object" 
        #Drive Base Einstellungen
        self.speed = 280 # Vorwärtsgeschwindigkeit
        self.turn_acceleration = 300
        self.straight_acceleration = 300
        self.turn_rate = 100

        self.target_distance = 178 # mm, Abstand zur Wand links 
        self.kp = 0.9 # P-Gain
        self.kd = 0.20 # D-Gain
        self.started = False
        self.last_error = 0
        self.last_time = time.time()
        self.distance_travelled = 0
        self.max_distance = 1740
        self.turned = False

        self.state = 0  # Initialize state attribute
        
        #Konstanten
        self.SONICANGLE = -1
        self.STEERING = 70
        self.READYTOGRIP = 90
        self.HOLDPRINGELS = 38

    def reset(self, robot):
        self.started = False
        self.last_error = 0
        self.distance_travelled = 0
        self.last_time = time.time()
        self.turned = False
        self.finished = False
        robot.drive_base.stop()

    def goto_state(self, new_state):
        self.state = new_state
        print("nowInState:", new_state)   
    

    def run_one_step(self, robot):
        if self.state == 0: 
            robot.drive_base.stop()
            robot.drive_base.settings(self.speed, self.straight_acceleration, self.turn_rate, self.turn_acceleration)
            robot.set_gripper_and_ultrasonic_angle(self.SONICANGLE, turn_speed=250, wait=False)
            robot.calibrate_gripper_and_ultrasonic_angle()
            robot.reset_distance_and_angle()
            robot.drive_base.drive(self.speed, 0)
            self.goto_state(1)
            
        if self.state == 1:
            dist = robot.ultrasonic_sensor.distance()
            if dist is None:    #falls Sensor nichts erkennt
                dist = self.target_distance 
            
            error = dist - self.target_distance
            now = time.time()
            dt = now - self.last_time if now != self.last_time else 0.01
            dt = max(dt, 0.01)  # enforce minimum dt threshold
        
            d_error = (error - self.last_error) / dt
            steering = self.kp * error + self.kd * d_error
        
            steering = max(min(steering, self.STEERING), -self.STEERING)
            robot.drive_base.drive(self.speed, -steering)
        
        
            self.last_error = error
            self.last_time = now
            #self.distance_travelled += self.speed * dt
            self.distance_travelled = robot.driven_distance()
            if self.distance_travelled >= self.max_distance:
                robot.drive_base.stop()
                if self.turned:
                    self.goto_state(3)
                else:
                    self.goto_state(2)
                

        if self.state == 2:
            robot.drive(80, 120)
            robot.base_rgb = robot.color_sensor.rgb()
            print("Base RGB set to:", robot.base_rgb)
            while robot.angle_turned() < 77:
                pass
            robot.reset_distance_and_angle()
            self.distance_travelled = 0
            self.target_distance = 111
            self.max_distance = 280 # weniger als bis zum Objekt um dann farbsuche zu starten
            self.turned = True
            self.goto_state(1)
        
        if self.state == 3:
            #Farbe lesen
            detectedColor = robot.color_sensor.color()

            #Fahren bis Weiß erkannt wird
            robot.drive_base.drive(self.speed / 2, 0)
            if detectedColor == Color.WHITE:
                robot.drive_base.stop()
                robot.set_gripper_and_ultrasonic_angle(self.READYTOGRIP, turn_speed=250, wait=False)
                robot.drive_base.straight(-18)
                robot.drive_base.drive(self.speed, -25)               
                robot.spin(-25)
                robot.straight(103) #noch ein Stück vorfahren, damit Objekt sicher gegriffen wird
                robot.set_gripper_and_ultrasonic_angle(self.HOLDPRINGELS, turn_speed=250, wait=True)
                self.goto_state(4)

        if self.state == 4:
            #robot.drive_base.drive_time(-120, -40, 3000)
            robot.drive(-225, -40)
            while robot.angle_turned() > -90:
                pass
            robot.drive_base.stop()
            robot.straight(-140)
            robot.reset_distance_and_angle()
            robot.set_gripper_and_ultrasonic_angle(self.READYTOGRIP, turn_speed=250, wait=False)
            robot.straight(-100)
            robot.set_gripper_and_ultrasonic_angle(self.SONICANGLE, turn_speed=250, wait=False)
            self.goto_state(5)

        if self.state == 5:
            robot.spin(145)
            #robot.drive(30, 30)
            #while robot.angle_turned() < 145:
            #    pass
            robot.reset_distance_and_angle()
            self.distance_travelled = 0
            self.target_distance = 355
            self.max_distance = 20
            self.goto_state(6)


        if self.state == 6:
            dist = robot.ultrasonic_sensor.distance()
            print(dist)
            robot.spin(15)
            dist2 = robot.ultrasonic_sensor.distance()
            print("Zweite", dist2)
            while dist2 < dist:
                dist = dist2
                robot.spin(15)
                dist2 = robot.ultrasonic_sensor.distance()
                print("Zweite", dist2)

            robot.ev3.speaker.beep()
            self.goto_state(7)
            
        if self.state == 7:
            dist = robot.ultrasonic_sensor.distance()
            if dist is None:    #falls Sensor nichts erkennt
                dist = self.target_distance 
            
            self.distance_travelled = robot.driven_distance()

            error = dist - self.target_distance
            now = time.time()
            dt = now - self.last_time if now != self.last_time else 0.01
            dt = max(dt, 0.01)  # enforce minimum dt threshold
        
            d_error = (error - self.last_error) / dt
            steering = self.kp * error + self.kd * d_error
        
            steering = max(min(steering, self.STEERING), -self.STEERING)
            robot.drive_base.drive(self.speed / 4, -steering)
        
        
            self.last_error = error
            self.last_time = now

            if self.distance_travelled >= self.max_distance:
                robot.drive_base.stop()
                robot.drive(self.speed / 5, 0)
                self.goto_state(8)

        if self.state == 8:
            detectedColor = robot.color_sensor.rgb()
            print("Detected Color RGB:", detectedColor)
            print("Base Color RGB:", robot.base_rgb)
            base_r, base_g, base_b = robot.base_rgb
            relative_blue_change = (detectedColor[2] - base_b) / max(base_b, 1)
            if relative_blue_change > 3 and detectedColor[0] < 20:
                detectedColor = Color.BLUE
                robot.drive_base.stop()
                robot.ev3.speaker.beep()
                self.finished = True
