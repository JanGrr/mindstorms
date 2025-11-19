from .section import Section

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
        self.DRIVE_SPEED = 30                   # mm/s
        self.DRIVE_SPEED_OBSTACLE = 50          # mm/s
        self.SEARCH_DRIVE_SPEED = 20
        self.PROPORTIONAL_GAIN = 0.75               # Je höher, desto "zitternder"
        self.SEARCH_WIDTH_ANGLE = 30            # Wie breit der Suchwinkel nach links und rechts ist, wenn die Linie verloren wurde
        self.SEARCH_TURN_SPEED = 30                # deg/s
        self.angle_turned_since_line_lost = 0    # könnte man evtl weglassen & stattdessen delta berechnen!
        self.line_lost = False
        self.line_gap = False
        self.state = State.SEEING_LINE

    def reset(self, robot):
        robot.stop()
        self.angle_turned_since_line_lost = 0
        self.line_lost = False
        self.line_gap = False
        self.state = State.SEEING_LINE

    def update_section_screen(self, robot, status=""):
        robot.ev3.screen.clear()
        robot.ev3.screen.draw_text(x=3, y=3, text="[<-]" + self.name)
        robot.ev3.screen.draw_text(x=3, y=33, text="Status: " + status)

        r, g, b = robot.color_sensor.rgb()                             # Alternative
        print("Blue: " + str(r) + " " + str(g) + " " + str(b))

    # P-Regler, also berechnet die zu korrigierende Drehung proportional zur Abweichung von dem Sollwert (der rechten Linienkante)
    def run_one_step(self, robot):
        if self.check_for_blue_line(robot):
            #robot.ev3.say("Blaue Linie gefunden")
            self.finished = True
            robot.stop()
            robot.reset_distance_and_angle()
            # TODO Celebration?
            return

        # if self.state == State.CALIBRATING:
        #     self.calibrate(robot)
        #     self.state = State.SEEING_LINE
        #     return

        if robot.touch_sensor.pressed():
            self.state = State.OBSTACLE
            self.update_section_screen(robot, status="Obstacle")
            # robot.ev3.speaker.say("Hindernis erkannt")
            self.drive_around_obstacle(robot)
            return

        r, g, b = robot.color_sensor.rgb()      # statt reflection = robot.color_sensor.reflection(), da er sonst die ganze Zeit zwischen den Modis springt um die blaue Linie zu erkennen
        reflection = (r + g + b) / 3
        seeing_line = reflection > self.UNDERGROUND_REFLECTION + self.UNDERGROUND_DELTA    # boolean

        if seeing_line:
            if self.state != State.SEEING_LINE:
                self.update_section_screen(robot, status ="on line")

            self.state = State.SEEING_LINE
            self.angle_turned_since_line_lost = 0

            # Linie entlang fahren mithilfe eines P-Reglers
            deviation = reflection - self.TARGET_VALUE
            correction = deviation * self.PROPORTIONAL_GAIN
            if deviation < 25:                                       #TODO vlt proportional speed
                robot.drive(self.DRIVE_SPEED, turn_rate=correction)     #TODO DRIVE_SPEED auch P-regler?
            else:
                robot.drive(drive_speed=0, turn_rate=correction)     #TODO DRIVE_SPEED auch P-regler?

            
        else: # NOT SEEING LINE
            self.angle_turned_since_line_lost = robot.angle_turned()
            if self.state == State.SEEING_LINE: # Linie sollte nur verloren gehen, wenn starker Knick der Linie nach links (max. 90°) oder Lücke
                self.update_section_screen(robot, status="lost line")
                self.state = State.LOST_LINE
                robot.drive(0, -30)   # nach Links drehen mit 90°/s  # TODO vlt statt 0, doch bisschen Geschwindigkeit?
                robot.reset_distance_and_angle()
                # TODO Display oder Ton?

            elif self.state == State.LOST_LINE:
                # Wenn Linie verloren, dann maximal 100° nach Links drehen um zwischen starker Linkskurve und Lücke zu unterscheiden
                # Linie nicht wiedergefunden -> Lücke, also wieder gerade drehen und suchen
                print(str(self.angle_turned_since_line_lost))
                if self.angle_turned_since_line_lost < -60:  # Schon 100° gedreht seit Linienverlust? -> Ja = Lücke
                    self.update_section_screen(robot, status="gap right")
                    self.state = State.GAP_RIGHT_TURN
                    robot.drive(self.SEARCH_DRIVE_SPEED, self.SEARCH_TURN_SPEED)
                    # TODO Display oder Ton?

            elif self.state == State.GAP_RIGHT_TURN:
                print(str(self.angle_turned_since_line_lost))
                if self.angle_turned_since_line_lost > self.SEARCH_WIDTH_ANGLE:  # Schon 100° gedreht seit Linienverlust? -> Ja = Lücke
                    self.update_section_screen(robot, status="gap left")
                    self.state = State.GAP_LEFT_TURN
                    robot.drive(self.SEARCH_DRIVE_SPEED, -self.SEARCH_TURN_SPEED)

            elif self.state == State.GAP_LEFT_TURN:
                if self.angle_turned_since_line_lost < -self.SEARCH_WIDTH_ANGLE:  # Schon 100° gedreht seit Linienverlust? -> Ja = Lücke
                    self.update_section_screen(robot, status="gap right")
                    self.state = State.GAP_RIGHT_TURN
                    robot.drive(self.SEARCH_DRIVE_SPEED, self.SEARCH_TURN_SPEED)

            else:
                return  # do nothing, just search for line when in state.OBSTACLE

    def calibrate(self, robot):     # TODO lieber min und max Werte speicher und LINE_REFLECTION = max und UNDERGROUND_REFLECTION = min
        self.LINE_REFLECTION = robot.color_sensor.reflection()
        robot.ev3.speaker.say("Linie " + str(self.LINE_REFLECTION))
        robot.spin(40)
        self.UNDERGROUND_REFLECTION = robot.color_sensor.reflection()
        robot.ev3.speaker.say("Untergrund " + str(self.UNDERGROUND_REFLECTION))
        robot.spin(-40)

    def drive_around_obstacle(self, robot):
        robot.stop()
        robot.straight(-50)
        robot.spin(60)
        robot.drive(self.DRIVE_SPEED_OBSTACLE, turn_rate=-12)