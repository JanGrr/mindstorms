from .section import Section
from pybricks.tools import wait
from pybricks.parameters import Stop

import time

class SectionMoveObject(Section):
    
    def __init__(self):
        super().__init__()

        self.name = "Move Object"
        self.target_distance = 350 # mm Abstand zur Wand links 
        #TODO Distanz vllt näher ran, damit Sensor genauer wird????
        self.speed = 120 # Vorwärtsgeschwindigkeit
        self.kp = 1.2 # P-Gain
        self.kd = 4.0 # D-Gain
        self.sensorPosition = False

        self.last_error = 0
        self.last_time = time.time()
        self.distance_travelled = 0
        self.max_distance = 1950
        self.done = False
        self.turned = False

    def reset(self, robot):
        # TODO: Implement reset logic if needed
        self.last_error = 0
        self.distance_travelled = 0
        self.last_time = time.time()
        self.done = False

        # Fahren, entlang der linken Wand
    def run_one_step(self, robot):
        #Sensor über Motor in die richtige Position bewegen
        if not self.sensorPosition:
            robot.motor_small.run_target(speed=10, target_angle=40, then=Stop.HOLD, wait=False)
            self.sensorPosition = True
        dist = robot.ultrasonic.distance()
        robot.ev3.speaker.beep()
        print(f"Abstand: {dist} mm")  # <-- zeigt jeden Schritt

        if dist is None:    #falls Sensor nichts erkennt
            dist = self.target_distance 
            
        error = dist - self.target_distance
        now = time.time()
        dt = now - self.last_time if now != self.last_time else 0.01
        
        d_error = (error - self.last_error) / dt
        steering = self.kp * error + self.kd * d_error
        
        steering = max(min(steering, 80), -80)
        
        robot.drive_base.drive(self.speed, steering)
        
        self.last_error = error
        self.last_time = now
        self.distance_travelled += self.speed * dt
        
        #Angekommen?
        if self.distance_travelled >= self.max_distance:
            robot.drive_base.stop()
            self.done = True

        #nächste Wand
        if self.done == True and self.turned == False:
            robot.spin(90)
            self.target_distance = 110
            self.max_distance = 600
            self.turned = True
        

        wait(10)