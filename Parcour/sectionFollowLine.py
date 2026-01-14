from .section import Section

class State:    # Enum
    SEEING_LINE = 1
    LOST_LINE = 2

class SectionFollowLine(Section):

    def __init__(self):
        super().__init__()
        self.name = "Follow Line"
        self.UNDERGROUND_REFLECTION = 7          # average reflection of the underground
        self.UNDERGROUND_DELTA = 10              # UNDERGROUND_REFLECTION + UNDERGROUND_DELTA = highest reflection of the underground that we still consider as pure underground without line
        self.LINE_REFLECTION = 77
        self.TARGET_VALUE = (self.UNDERGROUND_REFLECTION + self.LINE_REFLECTION) / 2
        self.DRIVE_SPEED = 100                   # mm/s
        self.DRIVE_SPEED_OBSTACLE = 200          # mm/s
        self.TURN_SPEED = 40                     # deg/s
        self.PROPORTIONAL_GAIN = 1.5             # the higher, the "shakier"
        self.DERIVATIVE_GAIN = 1.5
        self.last_error = 0
        self.state = State.SEEING_LINE

    def reset(self, robot):
        robot.stop()
        self.finished = False
        self.last_error = 0
        self.state = State.SEEING_LINE

    def run_one_step(self, robot):
        r, g, b = robot.color_sensor.rgb()

        if self.check_for_blue_line(robot, r, g, b):
            robot.ev3.speaker.beep()
            self.finished = True
            return

        if robot.touch_sensor.pressed():
            self.drive_around_obstacle(robot)
            return

        r, g, b = robot.color_sensor.rgb()              # instead of reflection = robot.color_sensor.reflection(), because otherwise it keeps switching modes to detect the blue line
        reflection = (r + g + b) / 3                    # reflection should be a value between 0 and 100
        seeing_line = reflection > self.UNDERGROUND_REFLECTION + self.UNDERGROUND_DELTA    # boolean

        if seeing_line:
            self.pd_regler(robot, reflection)           # drive along the right edge of the line using a PD-controller
            
            if self.state != State.SEEING_LINE:
                self.update_section_screen(robot, "on line")
                self.state = State.SEEING_LINE
            
        else: # NOT SEEING LINE

            if self.state == State.SEEING_LINE:         # line should only be lost if there is a sharp bend in the line to the left (max. 90°) or a gap
                robot.drive(0, -self.TURN_SPEED)        # turn left
                robot.reset_distance_and_angle()
                self.update_section_screen(robot, "lost line")
                self.state = State.LOST_LINE

            elif self.state == State.LOST_LINE:
                angle_turned_since_line_lost = robot.angle_turned()
                if angle_turned_since_line_lost < -60:   # check for gap
                    self.drive_around_gap(robot)

    def pd_regler(self, robot, reflection):
        error = reflection - self.TARGET_VALUE
        derivative = error - self.last_error
        self.last_error = error
        correction = (error * self.PROPORTIONAL_GAIN) + (derivative * self.DERIVATIVE_GAIN)

        speed = self.DRIVE_SPEED - (self.DRIVE_SPEED / 25) * abs(error)
        speed = max(speed, 0)
        robot.drive(drive_speed=speed, turn_rate=correction)

    def drive_around_gap(self, robot):
        robot.drive(drive_speed=(self.TURN_SPEED / 3), turn_rate=self.TURN_SPEED)
        self.update_section_screen(robot, "gap")
        while robot.angle_turned() < 20:            # Turn back a bit more then just straight to find the right side of the line again
            continue
        robot.drive(self.DRIVE_SPEED, turn_rate=-(self.DRIVE_SPEED / 3))  # drive in a slight arc towards the right edge of the line

    def drive_around_obstacle(self, robot):
        robot.stop()
        self.state = State.LOST_LINE
        self.update_section_screen(robot, "Obstacle")
        robot.straight(-30)
        robot.spin(72)
        robot.drive(self.DRIVE_SPEED_OBSTACLE, turn_rate=-(self.DRIVE_SPEED_OBSTACLE / 4))  # Bogen fahren
        
        # Quickly around the obstacle, but slowly approach the line
        already_distance_driven = robot.driven_distance()
        while robot.driven_distance() < already_distance_driven + 450:
            pass
        robot.reset_distance_and_angle()
        robot.drive(self.DRIVE_SPEED, turn_rate=-(self.DRIVE_SPEED / 4))