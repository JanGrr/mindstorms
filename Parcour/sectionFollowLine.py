from .section import Section
from pybricks.tools import wait

class State:    # Enum
    CALIBRATING = 0
    SEEING_LINE = 1
    LOST_LINE = 2
    GAP_RIGHT_TURN = 3
    GAP_LEFT_TURN = 4
    OBSTACLE = 5

class SectionFollowLine(Section):

    def __init__(self):
        super().__init__()
        self.name = "Follow Line"
        self.UNDERGROUND_REFLECTION = 9          # Durchschnittliche Reflection des Untergrunds
        self.UNDERGROUND_DELTA = 10              # UNDERGROUND_REFLECTION + UNDERGROUND_DELTA = höchste Reflection des Untergrunds, dass wir trotzdem noch denken es ist der reine Untergrund ohne Linie
        self.LINE_REFLECTION = 85
        self.TARGET_VALUE = (self.UNDERGROUND_REFLECTION + self.LINE_REFLECTION) / 2
        self.DRIVE_SPEED = 100                   # mm/s
        self.DRIVE_SPEED_OBSTACLE = 200          # mm/s
        self.SEARCH_DRIVE_SPEED = 20
        self.PROPORTIONAL_GAIN = 1.5               # Je höher, desto "zitternder"
        self.INTEGRAL_GAIN = 0
        self.integral = 0
        self.DERIVATIVE_GAIN = 1.5
        self.last_error = 0
        self.SEARCH_WIDTH_ANGLE = 30            # Wie breit der Suchwinkel nach links und rechts ist, wenn die Linie verloren wurde
        self.SEARCH_TURN_SPEED = 30                # deg/s
        self.angle_turned_since_line_lost = 0    # könnte man evtl weglassen & stattdessen delta berechnen!
        self.line_lost = False
        self.line_gap = False
        self.state = State.SEEING_LINE
        self.status = "on line"

    def reset(self, robot):
        robot.stop()
        self.status = "on line"
        self.angle_turned_since_line_lost = 0
        self.line_lost = False
        self.line_gap = False
        self.state = State.SEEING_LINE
        self.integral = 0
        self.last_error = 0

    def run_one_step(self, robot):

        r, g, b = robot.color_sensor.rgb()                             #TODO Um Blau Werte zu finden

        if self.check_for_blue_line(robot, r, g, b):
            #robot.ev3.say("Blaue Linie gefunden")
            self.finished = True
            # TODO Celebration?
            return

        if robot.touch_sensor.pressed():
            robot.stop()
            self.state = State.OBSTACLE
            self.status="Obstacle"
            self.update_section_screen(robot, self.status)
            # robot.ev3.speaker.say("Hindernis erkannt")
            self.drive_around_obstacle(robot)
            return

        r, g, b = robot.color_sensor.rgb()      # statt reflection = robot.color_sensor.reflection(), da er sonst die ganze Zeit zwischen den Modis springt um die blaue Linie zu erkennen
        reflection = (r + g + b) / 3            # Wert zwischen 0 und 100
        seeing_line = reflection > self.UNDERGROUND_REFLECTION + self.UNDERGROUND_DELTA    # boolean

        if seeing_line:
            if self.state != State.SEEING_LINE:
                self.status ="on line"
                self.update_section_screen(robot, self.status)

            self.state = State.SEEING_LINE
            self.angle_turned_since_line_lost = 0

            self.pid_regler(robot, reflection)    # Linie entlang fahren mithilfe eines P-Reglers
            
        else: # NOT SEEING LINE
            self.angle_turned_since_line_lost = robot.angle_turned()
            if self.state == State.SEEING_LINE: # Linie sollte nur verloren gehen, wenn starker Knick der Linie nach links (max. 90°) oder Lücke
                self.status="lost line"
                self.update_section_screen(robot, self.status)
                self.state = State.LOST_LINE
                robot.drive(0, -30)   # nach Links drehen mit 90°/s  # TODO vlt statt 0, doch bisschen Geschwindigkeit?
                robot.reset_distance_and_angle()
                # TODO Display oder Ton?

            elif self.state == State.LOST_LINE:
                # check for gap
                if self.angle_turned_since_line_lost < -60:
                    self.status="gap"
                    self.update_section_screen(robot, self.status)
                    robot.drive(10, self.SEARCH_TURN_SPEED)
                    while robot.angle_turned() < 20:
                        continue
                    robot.drive(self.DRIVE_SPEED, turn_rate=-(self.DRIVE_SPEED / 3))  # Bogen fahren um Lücke zu überqueren
                    # TODO Display oder Ton?

            else:
                return  # do nothing, just search for line when in state.OBSTACLE

    def p_regler(self, robot, reflection):
        error = reflection - self.TARGET_VALUE
        correction = error * self.PROPORTIONAL_GAIN
        if error < 25:                                       #TODO vlt proportional speed (DRIVE_SPEED auch P-regler?)
            robot.drive(self.DRIVE_SPEED, turn_rate=correction)
        else:
            robot.drive(drive_speed=0, turn_rate=correction)

    def pid_regler(self, robot, reflection):
        error = reflection - self.TARGET_VALUE
        self.integral = self.integral + error
        derivative = error - self.last_error
        self.last_error = error
        correction = (error * self.PROPORTIONAL_GAIN) + (self.integral * self.INTEGRAL_GAIN) + (derivative * self.DERIVATIVE_GAIN)
        if error < 30:
            robot.drive(self.DRIVE_SPEED, turn_rate=correction)
        else:
            robot.drive(drive_speed=0, turn_rate=correction)


    def calibrate(self, robot):     # TODO lieber min und max Werte speicher und LINE_REFLECTION = max und UNDERGROUND_REFLECTION = min
        self.LINE_REFLECTION = robot.color_sensor.reflection()
        robot.ev3.speaker.say("Linie " + str(self.LINE_REFLECTION))
        robot.spin(40)
        self.UNDERGROUND_REFLECTION = robot.color_sensor.reflection()
        robot.ev3.speaker.say("Untergrund " + str(self.UNDERGROUND_REFLECTION))
        robot.spin(-40)

    def drive_around_obstacle(self, robot):
        robot.straight(-10)
        robot.spin(75)
        robot.drive(self.DRIVE_SPEED_OBSTACLE, turn_rate=-(self.DRIVE_SPEED_OBSTACLE / 4))  # Bogen fahren
        
        already_distance_driven = robot.driven_distance()
        while robot.driven_distance() < already_distance_driven + 450:
            pass
        robot.drive(self.DRIVE_SPEED, turn_rate=-(self.DRIVE_SPEED / 4))
