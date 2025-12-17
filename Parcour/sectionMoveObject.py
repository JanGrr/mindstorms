from .section import Section
from pybricks.tools import wait
from pybricks.parameters import Stop, Color

import time

class SectionMoveObject(Section):
    
    def __init__(self):
        super().__init__()

        self.name = "Move Object"
        self.target_distance = 180 # mm Abstand zur Wand links 
        #TODO Distanz vllt näher ran, damit Sensor genauer wird????
        self.speed = 280 # Vorwärtsgeschwindigkeit
        self.kp = 0.9 # P-Gain
        self.kd = 0.20 # D-Gain
        self.started = False

        self.last_error = 0
        self.last_time = time.time()
        self.distance_travelled = 0
        self.max_distance = 1800
        self.turned = False
        self.findBlue = False

        self.state = 0  # Initialize state attribute
        
        #Konstanten
        self.SONICANGLE = -5
        self.STEERING = 70
        self.GRIPPINGANGLE = 90
        self.HOLDPRINGELS = 43

    def reset(self, robot):
        # TODO: Implement reset logic if needed
        self.started = False
        self.last_error = 0
        self.distance_travelled = 0
        self.last_time = time.time()
        self.turned = False
        self.findBlue = False
        self.finished = False

    def goto_state(self, new_state):
        self.state = new_state
        print("nowInState:", new_state)   
    

    # Fahren, entlang der linken Wand
    def run_one_step(self, robot):
        #Sensor über Motor in die richtige Position bewegen
        #1
        if self.state == 0:
            robot.set_gripper_and_ultrasonic_angle(self.SONICANGLE)
            robot.calibrate_gripper_and_ultrasonic_angle()
            robot.reset_distance_and_angle()
            robot.drive_base.drive_time(120, 0, 1000)
            robot.base_rgb = robot.color_sensor.rgb()
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
            #steering = self.kp * error
            steering = self.kp * error + self.kd * d_error
        
            steering = max(min(steering, self.STEERING), -self.STEERING)
            self.update_section_screen(robot, status1="pd-Regler", status2="", status3="")
        #2
            robot.drive_base.drive(self.speed, -steering)
        
        
            self.last_error = error
            self.last_time = now
            #self.distance_travelled += self.speed * dt
            self.distance_travelled = robot.driven_distance()
            if self.distance_travelled >= self.max_distance:
                robot.drive_base.stop()
                self.update_section_screen(robot, status1="firstPartDone", status2="", status3="")
                if self.findBlue:

                    self.goto_state(7)  # Move to find blue
                elif self.turned:
                    self.goto_state(4)
                else:
                    self.goto_state(3)
                

        #4&5
        if self.state == 3:
            robot.drive(30, 30)
            while robot.angle_turned() < 90:
                pass
            robot.reset_distance_and_angle()
            self.distance_travelled = 0
            self.target_distance = 110
            self.max_distance = 260 # weniger als bis zum Objekt um dann farbsuche zu starten
            self.turned = True
            self.goto_state(1)
        
        #6a
        if self.state == 4:

            #Farbe lesen
            detectedColor = robot.color_sensor.color()
            self.update_section_screen(robot, status1=str(detectedColor), status2="WIR SIND NICHT IM QUADRAT", status3="")

            #Fahren bis Weiß erkannt wird
            robot.drive_base.drive(self.speed / 2, 0)
            if detectedColor == Color.WHITE:
                robot.stop()
                #robot.drive_base.straight(-4) #etwas zurückfahren, damit Objekt sicher gegriffen wird
                robot.set_gripper_and_ultrasonic_angle(self.GRIPPINGANGLE, turn_speed=100)
                robot.spin(-25)
                robot.straight(95) #noch ein Stück vorfahren, damit Objekt sicher gegriffen wird
                robot.set_gripper_and_ultrasonic_angle(self.HOLDPRINGELS, turn_speed=100)
                self.goto_state(5)

        if self.state == 5:
            #robot.drive_base.drive_time(-120, -40, 3000)
            robot.drive(-285, -40)
            while robot.angle_turned() > -90:
                pass
            robot.stop()
            robot.straight(-180)
            robot.reset_distance_and_angle()
            robot.set_gripper_and_ultrasonic_angle(self.GRIPPINGANGLE, turn_speed=100)
            robot.straight(-100)
            robot.set_gripper_and_ultrasonic_angle(self.SONICANGLE, turn_speed=100)
            self.goto_state(6)

        if self.state == 6:
            #robot.spin(100)
            robot.drive(30, 30)
            while robot.angle_turned() < 145:
                pass
            robot.reset_distance_and_angle()
            self.distance_travelled = 0
            self.target_distance = 345
            self.max_distance = 400
            self.findBlue = True
            self.goto_state(7)


        if self.state == 7:
            dist = robot.ultrasonic_sensor.distance()
            print(dist)
            robot.spin(15)
            dist2 = robot.ultrasonic_sensor.distance()
            print("Zweite", dist2)
            self.update_section_screen(robot, status1=str(dist), status2=str(dist2) , status3="")
            while dist2 < dist:
                dist = dist2
                robot.spin(15)
                dist2 = robot.ultrasonic_sensor.distance()
                print("Zweite", dist2)

            robot.ev3.speaker.beep()
            self.goto_state(8)
            
        if self.state == 8:
            dist = robot.ultrasonic_sensor.distance()
            detectedColor = robot.color_sensor.rgb()
            if dist is None:    #falls Sensor nichts erkennt
                dist = self.target_distance 
            
            error = dist - self.target_distance
            now = time.time()
            dt = now - self.last_time if now != self.last_time else 0.01
            dt = max(dt, 0.01)  # enforce minimum dt threshold
        
            d_error = (error - self.last_error) / dt
            #steering = self.kp * error
            steering = self.kp * error + self.kd * d_error
        
            steering = max(min(steering, self.STEERING), -self.STEERING)
            self.update_section_screen(robot, status1= str(dist) + " mm", status2="Error:" + str(error), status3="Steering: " + str(steering))
        #2
            robot.drive_base.drive(self.speed / 4, -steering)
        
        
            self.last_error = error
            self.last_time = now
            #self.distance_travelled += self.speed * dt
         
            self.update_section_screen(robot, status1=str(detectedColor), status2="Auf Blau warten", status3="")
            base_r, base_g, base_b = robot.base_rgb
            relative_blue_change = (detectedColor[2] - base_b) / max(base_b, 1)
            if relative_blue_change > 3:
                detectedColor = Color.BLUE
                robot.drive_base.stop()
                self.goto_state(9)

        if self.state == 9:
            # beep
            robot.ev3.speaker.beep()
            robot.stop()
            self.update_section_screen(robot, status1="Section Finished", status2="", status3="")
            self.finished = True
            self.goto_state(10)



        
