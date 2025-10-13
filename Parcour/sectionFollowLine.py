from .section import Section


class SectionFollowLine(Section):

    def __init__(self):
        super().__init__()
        self.name = "Follow Line"
        self.UNDERGROUND_REFLECTION = .13          # Average reflection of the ground
        self.UNDERGROUND_DELTA = .015          # Highest reflection we still consider as pure ground without a line
        self.LINE_REFLECTION = 0.8

        #P-Regulator Values
        self.PROPORTIONAL_GAIN = .5  # Proportional gain for the P-controller
        self.TARGET_VALUE = (self.UNDERGROUND_REFLECTION + self.LINE_REFLECTION) / 2  # Target reflection value between ground and line
        self.not_seen_line_for = 0
        self.SWITCH_TO_SEARCH_THRESHOLD = 15  # Number of consecutive readings below target to consider the line lost

        self.DRIVE_SPEED = 120                   
        self.SEARCH_DRIVE_SPEED = 20           # Higher value means a "shakier" adjustment
        self.SEARCH_WIDTH_ANGLE = 200            # Width of the search angle when the line is lost
        self.angle_turned_since_line_lost = 0    # Track how much the robot has turned since losing the line

        # State names as strings instead of Enum
        self.STATE_CALIBRATING = "CALIBRATING"
        self.STATE_SEEING_LINE = "SEEING_LINE"
        self.STATE_LOST_LINE = "LOST_LINE"
        self.STATE_GAP_RIGHT_TURN = "GAP_RIGHT_TURN"
        self.STATE_GAP_LEFT_TURN = "GAP_LEFT_TURN"

        #Info output
        self.draw_info_in = 0
        self.DRAW_INFO_EVERY_N_STEPS = 60

        self.state = self.STATE_CALIBRATING

    def reset(self, robot):
        self.angle_turned_since_line_lost = 0
        self.line_lost = False
        self.line_gap = False
        robot.stop()

    def run_one_step(self, robot):
        #if self.check_for_blue_line(robot):
        #    print("Blue line detected, finishing section.")
        #    self.finished = True
        #    robot.stop()
        #    robot.reset_distance_and_angle()
        #    return

        '''
        if self.STATE_CALIBRATING == self.state:
            self.calibrate(robot)
            self.state = self.STATE_SEEING_LINE
            return
        '''
        self.draw_info(robot)
        rgb = robot.color_sensor.rgb()
        reflection = (rgb[0] + rgb[1] + rgb[2]) / 300  
        print(reflection, self.UNDERGROUND_REFLECTION + self.UNDERGROUND_DELTA)
        seeing_line = reflection > (self.UNDERGROUND_REFLECTION + self.UNDERGROUND_DELTA)
        
        if seeing_line: 
            self.not_seen_line_for = 0
        else:
            self.not_seen_line_for += 1

        if self.not_seen_line_for < self.SWITCH_TO_SEARCH_THRESHOLD:  
            self.pControl(robot, reflection)
        else:  # NOT SEEING LINE
            self.searchMode(robot, reflection)
            

    def calibrate(self, robot):
        # Calibrate the color sensor for ground and line
        self.LINE_REFLECTION = robot.color_sensor.reflection()
        print("Line reflection:", self.LINE_REFLECTION)
        robot.spin(40)
        robot.ev3.speaker.beep()
        self.UNDERGROUND_REFLECTION = robot.color_sensor.reflection()
        print("Ground reflection:", self.UNDERGROUND_REFLECTION)
        robot.spin(-40)

    def pControl(self, robot, reflection):
            # Line-following using a P-controller
            deviation = reflection - self.TARGET_VALUE
            correction = deviation * self.PROPORTIONAL_GAIN
            straight_speed = self.DRIVE_SPEED * (.5-abs(correction))
            robot.drive(straight_speed, turn_rate=correction*self.DRIVE_SPEED*2)

    def searchMode(self, robot, reflection):
        robot.stop()
        pass

    def draw_info(self, robot):
        self.draw_info_in -= 1
        if self.draw_info_in > 0:
            return

        self.draw_info_in = self.DRAW_INFO_EVERY_N_STEPS


        robot.ev3.screen.clear()
        robot.ev3.screen.draw_text(0, 0, "Section: " + self.name)
        rgb = robot.color_sensor.rgb()
        reflection = (rgb[0] + rgb[1] + rgb[2]) / 300  
        robot.ev3.screen.draw_text(0, 40, "Reflection: {:.2f}".format(reflection))
        robot.ev3.screen.draw_text(0, 60, "line not seen:" + str(self.not_seen_line_for))