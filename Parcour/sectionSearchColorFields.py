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
        self.target_distance_to_wall = 740
        self.PROPORTIONAL_GAIN = 2
        self.DERIVATIVE_GAIN = 0
        self.DRIVE_SPEED = 150
        self.AREA_WIDTH = 954
        self.found_red = False
        self.found_white = False
        self.drive_distance = 700
        self.last_error = 0

    def reset(self, robot):
        robot.stop()
        self.state = State.START
        self.found_red = False
        self.found_white = False
        self.drive_distance = 710
        self.last_error = 0
        robot.reset_distance_and_angle()
        self.finished = False

    def run_one_step(self, robot):

        if self.found_red and self.found_white:
            self.finished = True
            robot.drive(0, 800)
            for _ in range(6):
                wait(500)
                robot.set_gripper_and_ultrasonic_angle(90, turn_speed=250, wait=False)
                wait(500)
                robot.set_gripper_and_ultrasonic_angle(0, turn_speed=250, wait=False)
            return

        if self.state == State.START:
            self.update_screen(robot)
            robot.set_gripper_and_ultrasonic_angle(0)
            robot.straight(100)
            robot.gyro_sensor.reset_angle(0)
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

        if self.state == State.FOLLOW_WEST_WALL:
            if ((robot.driven_distance() > self.drive_distance) or robot.touch_sensor.pressed()):
                robot.drive(45,-45*2.2)
                while robot.gyro_sensor.angle() > -165:
                    pass
                print(" = " + str(self.AREA_WIDTH) + " - " + str(self.target_distance_to_wall) + " - 90")
                self.target_distance_to_wall = self.AREA_WIDTH - self.target_distance_to_wall - 70                  # - 90
                self.state = State.FOLLOW_EAST_WALL
                self.update_screen(robot)
                self.drive_distance = 590
                robot.reset_distance_and_angle()
                print(str(self.target_distance_to_wall))
                print(str(robot.ultrasonic_sensor.distance()))
           
        elif self.state == State.FOLLOW_EAST_WALL:
            if ((robot.driven_distance() > self.drive_distance) or robot.touch_sensor.pressed()):
                robot.drive(45,45*2)
                while robot.gyro_sensor.angle() < -15:
                    pass
                self.target_distance_to_wall = self.AREA_WIDTH - self.target_distance_to_wall - 180                  # - 190
                self.state = State.FOLLOW_WEST_WALL
                self.update_screen(robot)
                robot.reset_distance_and_angle()
                print(str(self.target_distance_to_wall))
                print(str(robot.ultrasonic_sensor.distance()))

    def pd_regler(self, robot):
        distance_to_wall = robot.ultrasonic_sensor.distance()
        error = distance_to_wall - self.target_distance_to_wall
        derivative = error - self.last_error
        self.last_error = error
        correction = (error * self.PROPORTIONAL_GAIN) + (derivative * self.DERIVATIVE_GAIN)

        # if (distance_to_wall < self.target_distance_to_wall - 30 or distance_to_wall > self.target_distance_to_wall + 30):
        #     if (robot.angle_turned() > 0):
        #         print("1")
        #         correction = -3
        #     else:
        #         print("2")
        #         correction = 3
        # else:
        #     if (robot.angle_turned() > 10 and correction > 0):
        #         print("3")
        #         correction = 0
        #     elif (robot.angle_turned() < -10 and correction < 0):
        #         print("4")
        #         correction = 0

        robot.drive(drive_speed=self.DRIVE_SPEED, turn_rate=-correction)
        print("dist: " + str(distance_to_wall) + "  target: " + str(self.target_distance_to_wall) + "  error: " + str(error) + "  correction: " + str(-correction))

    def check_for_red_colorfield(self, robot, r, g, b):             #TODO
        is_red = r>15 and g<12 and b<8
        if is_red:
            self.found_red = True
            self.update_screen(robot)
            robot.ev3.speaker.beep()
        return is_red

    def check_for_white_colorfield(self, robot, r, g, b):           #TODO
        reflection = (r + g + b) / 3
        is_white = reflection > 76
        if is_white:
            self.found_white = True
            self.update_screen(robot)
            robot.ev3.speaker.beep()
        return is_white

    def update_screen(self, robot):
        self.update_section_screen(robot, "State: " + str(self.state) + "  " + str(self.target_distance_to_wall), "Red: " + str(self.found_red), "White: " + str(self.found_white))
