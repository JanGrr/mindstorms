from .section import Section
from pybricks.tools import wait

class State:    # Enum
    START = 0
    FOLLOW_EAST_WALL = 1
    FOLLOW_WEST_WALL = 2

class SectionSearchColorFields(Section):
    
    def __init__(self):
        super().__init__()
        self.name = "Colorfields"
        self.state = State.START
        self.target_distance_to_wall = 770
        self.PROPORTIONAL_GAIN = 0.7
        self.DRIVE_SPEED = 30
        self.AREA_WIDTH = 954
        self.found_red = False
        self.found_white = False
        self.drive_distance = 810

    def reset(self, robot):
        robot.stop()
        self.state = State.START
        self.found_red = False
        self.found_white = False
        self.drive_distance = 800
        robot.reset_distance_and_angle()
        self.finished = False

    def run_one_step_a(self, robot):
        robot.calibrate_gripper_and_ultrasonic_angle()
        self.target_distance_to_wall = 185
        distance_to_wall = robot.ultrasonic_sensor.distance()
        print(distance_to_wall)
        deviation = distance_to_wall - self.target_distance_to_wall
        correction = deviation * self.PROPORTIONAL_GAIN
        speed = 200-(abs(deviation)*5)
        robot.drive(speed, turn_rate=-correction)

    def run_one_step(self, robot):

        if self.found_red and self.found_white:
            self.finished = True
            return

        if self.state == State.START:
            self.update_screen(robot)
            robot.calibrate_gripper_and_ultrasonic_angle()
            robot.straight(20)
            robot.reset_distance_and_angle()
            self.state = State.FOLLOW_WEST_WALL
            self.update_screen(robot)
            return

        r, g, b = robot.color_sensor.rgb()

        if self.target_distance_to_wall < 0 or self.target_distance_to_wall > self.AREA_WIDTH:
            Exception("didnt find color fields")

        if not self.found_red:
            self.check_for_red_colorfield(robot, r, g, b)

        if not self.found_white:
            self.check_for_white_colorfield(robot, r, g, b)

        self.p_regler(robot)

        if self.state == State.FOLLOW_WEST_WALL:#
            if robot.driven_distance() > self.drive_distance:   #robot.touch_sensor.pressed():
                robot.drive(45,-45)
                while robot.angle_turned() > -180:
                    pass
                self.target_distance_to_wall = self.AREA_WIDTH - self.target_distance_to_wall
                self.state = State.FOLLOW_EAST_WALL
                self.update_screen(robot)
                robot.reset_distance_and_angle()
                self.drive_distance = 550
           
        elif self.state == State.FOLLOW_EAST_WALL:
            if robot.driven_distance() > self.drive_distance:   #robot.touch_sensor.pressed():
                robot.drive(45,45)
                while robot.angle_turned() < 180:
                    pass
                self.target_distance_to_wall = self.AREA_WIDTH - self.target_distance_to_wall - 2*robot.AXLE_TRACK_MM
                self.state = State.FOLLOW_WEST_WALL
                self.update_screen(robot)
                robot.reset_distance_and_angle()

    def p_regler(self, robot):
        distance_to_wall = robot.ultrasonic_sensor.distance()
        #print(str(distance_to_wall) + "   " + str(self.target_distance_to_wall))
        deviation = distance_to_wall - self.target_distance_to_wall
        correction = deviation * self.PROPORTIONAL_GAIN
        speed = 150
        #print("correction: " + str(correction))
        correction = max(min(correction, 50), -50)
        #speed = 150-(abs(deviation)*5)
        robot.drive(speed, turn_rate=-correction)

    def check_for_red_colorfield(self, robot, r, g, b):
        is_red = r>30 # and g<20 and b<20
        if is_red:
            self.found_red = True
            self.update_screen(robot)
            robot.ev3.speaker.beep()
        return is_red

    def check_for_white_colorfield(self, robot, r, g, b):
        is_white = r>30 and g>40 and b>50
        if is_white:
            self.found_white = True
            self.update_screen(robot)
            robot.ev3.speaker.beep()
        return is_white

    def update_screen(self, robot):
        self.update_section_screen(robot, "State: " + str(self.state) + "  " + str(self.target_distance_to_wall), "Red: " + str(self.found_red), "White: " + str(self.found_white))
