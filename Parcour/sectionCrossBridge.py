from .section import Section
from pybricks.parameters import Port, Stop, Direction

class SectionCrossBridge(Section):

    def __init__(self):
        super().__init__()
        self.name = "Cross Bridge"

        self.states = ["CALIBRATE", "DRIVE_SECURITY", "SPIN_LEFT", "EXTEND_ULTRASONIC_LOW", "DRIVE_TO_LEFT_EDGE", "UP_SECTION", "TURN_1", "EXTEND_ULTRASONIC_HIGH", "MIDDLE_SECTION", "EXTEND_ULTRASONIC_LOW", "TURN_2", "END_SECTION", "FINISHED"]
        self.state_index = 0
        self.state = self.states[self.state_index]

        self.sectionStarted = False

        self.robot = None
        

    def reset(self, robot):
        robot.set_gripper_and_ultrasonic_angle(0)
        robot.stop()

    def run_one_step(self, robot):
        self.robot = robot
        if self.state == "CALIBRATE":
            self.calibrate(robot)
        elif self.state == "DRIVE_SECURITY":
            self.drive_security(robot)
        elif self.state == "EXTEND_ULTRASONIC_LOW":
            self.extend_ultrasonic_low(robot)
        elif self.state == "EXTEND_ULTRASONIC_HIGH":
            self.extend_ultrasonic_high(robot)
        elif self.state == "SPIN_LEFT":
            self.spin_left(robot)
        elif self.state == "DRIVE_TO_LEFT_EDGE":
            self.drive_to_left_edge(robot)
        elif self.state == "UP_SECTION":
            self.up_section(robot)
        elif self.state == "TURN_1":
            self.turn_1(robot)
        elif self.state == "MIDDLE_SECTION":
            self.middle_section(robot)
        elif self.state == "TURN_2":
            self.turn_2(robot)
        elif self.state == "END_SECTION":
            self.end_section(robot)
        elif self.state == "FINISHED":
            self.finished_state(robot)

    def next_state(self):
        self.state_index += 1
        self.state = self.states[self.state_index]
        self.sectionStarted = False
        print("Next State: " + self.state)
        self.robot.ev3.speaker.beep()

    def p_controll(self, robot, target_value=80, prop_gain=1, speed=50):
        ultrasonic_distance = robot.ultrasonic_sensor.distance()
        error = ultrasonic_distance - target_value
        steering = (prop_gain * error)
        robot.drive(speed, steering)

    def calibrate(self, robot):
        robot.reset_distance_and_angle()
        self.next_state()

    def drive_security(self, robot):
        robot.straight(400)  # Kleines stück vorfahren
        self.next_state()

    def extend_ultrasonic_low(self, robot):
        robot.set_gripper_and_ultrasonic_angle(90)  # Ultrasonic Sensor ausfahren
        self.next_state()

    def extend_ultrasonic_high(self, robot):
        robot.set_gripper_and_ultrasonic_angle(60)  # Ultrasonic Sensor ausfahren
        self.next_state()

    def spin_left(self, robot):
        robot.spin(-20)
        self.next_state()
    
    def drive_to_left_edge(self, robot):
        if robot.ultrasonic_sensor.distance() > 80:
            self.next_state()
            return
        robot.drive(20, 0)

    def up_section(self, robot):
        if robot.driven_distance() > 700:
            self.next_state()
            return
        self.p_controll(robot, target_value=80, prop_gain=1, speed=60)

    def turn_1(self, robot):
        if robot.driven_distance() > 1100:
            self.next_state()
            return
        self.p_controll(robot, target_value=80, prop_gain=1, speed=20)


    def middle_section(self, robot):
        if robot.driven_distance() > 1900:
            self.next_state()
            return
        self.p_controll(robot, target_value=100, prop_gain=1.3, speed=80)

    def turn_2(self, robot):
        if robot.driven_distance() > 2300:
            self.next_state()
            return
        self.p_controll(robot, target_value=80, prop_gain=3, speed=20)

    def end_section(self, robot):
        if robot.driven_distance() > 2700: #Später blaue linie erkennen
            self.next_state()
            return
        self.p_controll(robot, target_value=80, prop_gain=3, speed=60)


    def finished_state(self, robot):
        robot.stop()
        print("Finnished")
        
        