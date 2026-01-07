from .section import Section
from pybricks.parameters import Port, Stop, Direction
from pybricks.tools import wait

class SectionCrossBridge(Section):

    def __init__(self):
        super().__init__()
        self.name = "Cross Bridge"

        self.states = ["CALIBRATE", "DRIVE_SECURITY", "EXTEND_ULTRASONIC", "SPIN_LEFT", "DRIVE_TO_LEFT_EDGE", "TURN_IN_ON_LEFT_EDGE", "UP_SECTION", "TURN_1", "MIDDLE_SECTION", "TURN_2", "DOWN_SECTION", "END_SECTION", "RUN_TILL_BLUE", "FINISHED"]
        self.state_index = 0
        self.state = self.states[self.state_index]

        self.sectionStarted = False

        self.robot = None

        self.errors = []
        


    def reset(self, robot):
        robot.set_gripper_and_ultrasonic_angle(0)
        robot.stop()
        self.finished = False




    def run_one_step(self, robot):
        self.robot = robot
        if not self.check_ultrasonic_value_reasonable(robot):
            robot.stop()
            print("Ultrasonic Sensor Value not reasonable, waiting...")
            return

        if len(self.errors) > 40:
            self.errors = self.errors[-10:]


        if self.state == "CALIBRATE":
            self.calibrate(robot)
        elif self.state == "DRIVE_SECURITY":
            self.drive_security(robot)
        elif self.state == "EXTEND_ULTRASONIC":
            self.extend_ultrasonic(robot)
        elif self.state == "SPIN_LEFT":
            self.spin_left(robot)
        elif self.state == "DRIVE_TO_LEFT_EDGE":
            self.drive_to_left_edge(robot)
        elif self.state == "TURN_IN_ON_LEFT_EDGE":
            self.turn_in_on_left_edge(robot)
        elif self.state == "UP_SECTION":
            self.up_section(robot)
        elif self.state == "TURN_1":
            self.turn_1(robot)
        elif self.state == "MIDDLE_SECTION":
            self.middle_section(robot)
        elif self.state == "TURN_2":
            self.turn_2(robot)
        elif self.state == "DOWN_SECTION":
            self.down_section(robot)
        elif self.state == "END_SECTION":
            self.end_section(robot)
        elif self.state == "RUN_TILL_BLUE":
            self.run_till_blue(robot)
        elif self.state == "FINISHED":
            self.finished_state(robot)

    def check_ultrasonic_value_reasonable(self, robot):
        if robot.ultrasonic_sensor.distance() == 2550:
            return False
        return True

    def next_state(self):
        self.state_index += 1
        self.state = self.states[self.state_index]
        self.sectionStarted = False
        print("Next State: " + self.state)
        self.robot.ev3.speaker.beep()

    def p_controll(self, robot, target_value=80, prop_gain=1, speed=50):
        ultrasonic_distance = robot.ultrasonic_sensor.distance()
        ultrasonic_distance = min(ultrasonic_distance, 160)  
        error = ultrasonic_distance - target_value
        self.errors.append(error)
        steering = (prop_gain * error)
        robot.drive(speed, steering)

    def calibrate(self, robot):
        robot.reset_distance_and_angle()
        robot.calibrate_gripper_and_ultrasonic_angle()
        self.next_state()

    def drive_security(self, robot):
        robot.drive_base.settings(straight_speed=400, straight_acceleration=150, turn_rate=400, turn_acceleration=150)
        robot.straight(200)  # Kleines stück vorfahren
        self.next_state()

    def extend_ultrasonic(self, robot):
        robot.set_gripper_and_ultrasonic_angle(90, turn_speed=130, wait=False)  # Ultrasonic Sensor ausfahren
        self.next_state()

    def spin_left(self, robot):
        robot.spin(-30)
        self.next_state()
    
    def drive_to_left_edge(self, robot):
        ultrasonic_distance = robot.ultrasonic_sensor.distance()
        if ultrasonic_distance > 80:
            self.next_state()
            return
        robot.drive(40, 0)

    def turn_in_on_left_edge(self, robot):
        if len(self.errors) >= 10:
            if sum(self.errors[-10:]) / 10 < 5:
                self.next_state()
                return
        self.p_controll(robot, target_value=80, prop_gain=1.5, speed=100)

    def up_section(self, robot):
        if robot.driven_distance() > 700:
            self.next_state()
            return
        self.p_controll(robot, target_value=80, prop_gain=.7, speed=400)

    def turn_1(self, robot):
        if robot.driven_distance() > 1100:
            self.next_state()
            return
        self.p_controll(robot, target_value=80, prop_gain=1.2, speed=80)


    def middle_section(self, robot):
        driven_distance = robot.driven_distance()
        if driven_distance > 1800:
            self.next_state()
            return
        
        if driven_distance > 1600:
            self.p_controll(robot, target_value=80, prop_gain=.7, speed=150+(750*(driven_distance-1600)/200))
            return

        self.p_controll(robot, target_value=80, prop_gain=.65, speed=900)

    def turn_2(self, robot):
        if robot.driven_distance() > 2200:
            self.next_state()
            return
        self.p_controll(robot, target_value=80, prop_gain=1.2, speed=80)

    def down_section(self, robot):
        if robot.driven_distance() > 2350:
            self.next_state()
            return
        self.p_controll(robot, target_value=80, prop_gain=1, speed=150)

    def end_section(self, robot):
        robot.base_rgb = robot.color_sensor.rgb()
        robot.set_gripper_and_ultrasonic_angle(0, turn_speed=130, wait=False)
        angle = robot.angle_turned()
        while robot.angle_turned() < angle + 30:
            robot.drive(100, 100)
        distance = robot.driven_distance()
        while robot.driven_distance() < distance + 100:
            robot.drive(150, 0)
        angle = robot.angle_turned()
        while robot.angle_turned() > angle - 30:
            robot.drive(100, -100)
        self.next_state()

    def run_till_blue(self, robot):
        if self.sees_blue(robot):
            self.next_state()
            return
        robot.drive(60, 0)

    def finished_state(self, robot):
        self.reset(robot)
        

    def sees_blue(self, robot):
        r,g,b = robot.color_sensor.rgb()
        base_r, base_g, base_b = robot.base_rgb
        relative_blue_change = (b - base_b) / max(base_b, 1)
        return relative_blue_change > 2
        
        
        