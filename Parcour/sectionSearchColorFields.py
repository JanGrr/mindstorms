from .section import Section
from pybricks.tools import wait

class State:    # Enum
    START = 0
    FOLLOW_EAST_WALL = 1
    FOLLOW_WEST_WALL = 2

class SectionSearchColorFields(Section):        # done by Jan
    
    def __init__(self):
        super().__init__()
        self.name = "Colorfields"
        self.state = State.START
        self.target_distance_to_wall = 740
        self.PROPORTIONAL_GAIN = 2
        self.DERIVATIVE_GAIN = 0
        self.DRIVE_SPEED = 250
        self.AREA_WIDTH = 954
        self.found_red = False
        self.found_white = False
        self.drive_distance = 700
        self.last_error = 0
        self.last_distance = None
        self.wrong_distance_count = 0
        

    def reset(self, robot):
        robot.stop()
        self.state = State.START
        self.target_distance_to_wall = 740
        self.found_red = False
        self.found_white = False
        self.drive_distance = 700
        self.last_error = 0
        robot.reset_distance_and_angle()
        self.finished = False
        self.last_distance = None
        self.wrong_distance_count = 0

    def run_one_step(self, robot):

        if self.found_red and self.found_white:
            self.finished = True
            return

        if self.state == State.START:
            self.update_screen(robot)
            robot.set_gripper_and_ultrasonic_angle(0)
            robot.straight(100)                             # move an inch forward to avoid reading the wrong wall with the ultrasonic sensor
            robot.gyro_sensor.reset_angle(0)                # using gyro to turn accurately (not as accurate as hoped)
            robot.reset_distance_and_angle()
            self.state = State.FOLLOW_WEST_WALL
            self.update_screen(robot)
            return

        r, g, b = robot.color_sensor.rgb()

        if self.target_distance_to_wall < 0 or self.target_distance_to_wall > self.AREA_WIDTH:
            Exception("Invalid distance to wall: " + str(self.target_distance_to_wall))

        if not self.found_red:
            self.check_for_red_colorfield(robot, r, g, b)

        if not self.found_white:
            self.check_for_white_colorfield(robot, r, g, b)

        self.pd_regler(robot)

        # robot.stop()              # Alternative for turning?
        # robot.spin(45)
        # robot.straight(50)
        # robot.spin(45)

        if self.state == State.FOLLOW_WEST_WALL:
            if ((robot.driven_distance() > self.drive_distance) or robot.touch_sensor.pressed()):
                robot.drive(30,-30*2.2)                        # first part of turn fast
                while robot.gyro_sensor.angle() > -165:
                    pass
                robot.drive(10,-10*2.2)                        # last degrees slow for accuracy
                while robot.gyro_sensor.angle() > -178:
                    pass
                self.last_distance = None
                self.target_distance_to_wall = self.AREA_WIDTH - self.target_distance_to_wall - 70                  # - 90
                self.state = State.FOLLOW_EAST_WALL
                self.update_screen(robot)
                self.drive_distance = 570
                robot.reset_distance_and_angle()
           
        elif self.state == State.FOLLOW_EAST_WALL:
            if ((robot.driven_distance() > self.drive_distance) or robot.touch_sensor.pressed()):
                robot.drive(30,30*2)
                while robot.gyro_sensor.angle() < -15:
                    pass
                robot.drive(10,10*2.2)
                while robot.gyro_sensor.angle() < -2:
                    pass
                self.last_distance = None
                self.target_distance_to_wall = self.AREA_WIDTH - self.target_distance_to_wall - 180                  # - 190
                self.state = State.FOLLOW_WEST_WALL
                self.update_screen(robot)
                robot.reset_distance_and_angle()

    def pd_regler(self, robot):
        distance_to_wall = robot.ultrasonic_sensor.distance()
        self.stupid_wrong_distance_value_avoider(distance_to_wall)      #  would love to delete this part, but ultrasonic sensor values are super random sometimes
        
        error = distance_to_wall - self.target_distance_to_wall
        derivative = error - self.last_error
        self.last_error = error
        correction = (error * self.PROPORTIONAL_GAIN) + (derivative * self.DERIVATIVE_GAIN)
        robot.drive(drive_speed=self.DRIVE_SPEED, turn_rate=-correction)

    def stupid_wrong_distance_value_avoider(self, distance_to_wall):    # shouldn't be necessary, but ultrasonic sensor sometimes gives totally wrong values
        if not self.last_distance:
            self.last_distance = distance_to_wall
        if abs(distance_to_wall - self.last_distance) > 100:
            robot.drive(0,0)
            if self.wrong_distance_count > 100:
                self.wrong_distance_count = 0
                self.last_distance = distance_to_wall
            self.wrong_distance_count += 1
            return    
        self.last_distance = distance_to_wall

    def check_for_red_colorfield(self, robot, r, g, b):
        is_red = r>15 and g<12 and b<8
        if is_red:
            self.found_red = True
            self.update_screen(robot)
            robot.ev3.speaker.beep()
        return is_red

    def check_for_white_colorfield(self, robot, r, g, b):
        reflection = (r + g + b) / 3
        is_white = reflection > 76
        if is_white:
            self.found_white = True
            self.update_screen(robot)
            robot.ev3.speaker.beep()
        return is_white

    def update_screen(self, robot):
        self.update_section_screen(robot, "State: " + str(self.state) + "  " + str(self.target_distance_to_wall), "Red: " + str(self.found_red), "White: " + str(self.found_white))
