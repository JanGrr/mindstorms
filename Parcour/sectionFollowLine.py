from .section import Section


class SectionFollowLine(Section):

    def __init__(self):
        super().__init__()
        self.name = "Follow Line"
        self.UNDERGROUND_REFLECTION = 0          # Average reflection of the ground
        self.UNDERGROUND_DELTA = 10          # Highest reflection we still consider as pure ground without a line
        self.LINE_REFLECTION = 100
        self.PROPORTIONAL_GAIN = .6  # Proportional gain for the P-controller
        self.TARGET_VALUE = (self.UNDERGROUND_REFLECTION + self.LINE_REFLECTION) / 200  # Target reflection value between ground and line
        self.REFLECTION_RANGE = None
        self.DRIVE_SPEED = 120                   
        self.SEARCH_DRIVE_SPEED = 20           # Higher value means a "shakier" adjustment
        self.SEARCH_WIDTH_ANGLE = 200            # Width of the search angle when the line is lost
        self.angle_turned_since_line_lost = 0    # Track how much the robot has turned since losing the line
        self.line_lost = False
        self.line_gap = False

        # State names as strings instead of Enum
        self.STATE_CALIBRATING = "CALIBRATING"
        self.STATE_SEEING_LINE = "SEEING_LINE"
        self.STATE_LOST_LINE = "LOST_LINE"
        self.STATE_GAP_RIGHT_TURN = "GAP_RIGHT_TURN"
        self.STATE_GAP_LEFT_TURN = "GAP_LEFT_TURN"

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

        rgb = robot.color_sensor.rgb()
        reflection = (rgb[0] + rgb[1] + rgb[2]) / 300  
        print(reflection)

        
        
        if True:
            self.state = self.STATE_SEEING_LINE
            self.angle_turned_since_line_lost = 0

            # Line-following using a P-controller
            deviation = reflection - self.TARGET_VALUE
            correction = deviation * self.PROPORTIONAL_GAIN
            straight_speed = self.DRIVE_SPEED * (.5-abs(correction))
            robot.drive(straight_speed, turn_rate=correction*self.DRIVE_SPEED*2)
        '''
        else:  # NOT SEEING LINE
            robot.stop()
            robot.ev3.speaker.beep()
            return
            
        
            
            self.angle_turned_since_line_lost = robot.angle_turned()

            if self.state == self.STATE_SEEING_LINE:
                self.state = self.STATE_LOST_LINE
                robot.drive(0, 90)  # Turn left at 90°/s
                robot.reset_distance_and_angle()
                # TODO: Display or sound indication

            elif self.state == self.STATE_LOST_LINE:
                if self.angle_turned_since_line_lost > 100:  # Has turned more than 100° since losing the line?
                    self.state = self.STATE_GAP_RIGHT_TURN
                    robot.drive(0, -90)  # Turn right
                    # TODO: Display or sound indication

            elif self.state == self.STATE_GAP_RIGHT_TURN:
                if self.angle_turned_since_line_lost < -45:  # Check for left turn indication
                    self.state = self.STATE_GAP_LEFT_TURN
                    robot.drive(20, 90)  # Drive forward and turn left

            elif self.state == self.STATE_GAP_LEFT_TURN:
                if self.angle_turned_since_line_lost > 45:  # Check for right turn indication
                    self.state = self.STATE_GAP_RIGHT_TURN
                    robot.drive(20, -90)  # Drive forward and turn right

            else:
                raise Exception('Calling a non-existing State')
        '''            

    def calibrate(self, robot):
        # Calibrate the color sensor for ground and line
        self.LINE_REFLECTION = robot.color_sensor.reflection()
        print("Line reflection:", self.LINE_REFLECTION)
        robot.spin(40)
        robot.ev3.speaker.beep()
        self.UNDERGROUND_REFLECTION = robot.color_sensor.reflection()
        print("Ground reflection:", self.UNDERGROUND_REFLECTION)
        robot.spin(-40)