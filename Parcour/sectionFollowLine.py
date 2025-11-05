from .section import Section
from enum import Enum

class SectionFollowLine(Section):

    class State(Enum):
        SEEING_LINE = 1
        LOST_LINE = 2
        GAP_RIGHT_TURN = 3
        GAP_LEFT_TURN = 4

    def __init__(self):
        self.name = "Follow Line"
        self.UNDERGROUND_REFLECTION = 9          # Durchschnittliche Reflection des Untergrunds
        self.UNDERGROUND_THRESHOLD = 15         # höchste Reflection des Untergrunds, dass wir trotzdem noch denken es ist der reine Untergrund ohne Linie
        self.LINE_REFLECTION = 85
        self.TARGET_VALUE = (self.UNDERGROUND_REFLECTION + self.LINE_REFLECTION) / 2
        self.DRIVE_SPEED = 100                   # mm/s
        self.SEARCH_DRIVE_SPEED = 20
        self.PROPORTIONAL_GAIN = 1               # Je höher, desto "zitternder"
        self.SEARCH_WIDTH_ANGLE = 200            # Wie breit der Suchwinkel nach links und rechts ist, wenn die Linie verloren wurde
        self.angle_turned_since_line_lost = 0    # könnte man evtl weglassen & stattdessen delta berechnen!
        self.line_lost = False
        self.line_gap = False
        self.state = State.SEEING_LINE

    def reset(self):
        self.angle_turned_since_line_lost = 0
        self.line_lost = False
        self.line_gap = False

    # P-Regler, also berechnet die zu korrigierende Drehung proportional zur Abweichung von dem Sollwert (der rechten Linienkante)
    def run_one_step(self, robot):
        if self.check_for_blue_line(robot):
            self.finished = True
            robot.stop()
            robot.reset_distance_and_angle()
            # TODO Celebration?
            return

        reflection = robot.color_sensor.reflection()
        seeing_line = reflection > self.UNDERGROUND_THRESHOLD    # boolean

        if seeing_line:
            self.state = State.SEEING_LINE
            self.angle_turned_since_line_lost = 0

            # Linie entlang fahren mithilfe eines P-Reglers
            deviation = reflection - self.TARGET_VALUE
            correction = deviation * self.PROPORTIONAL_GAIN
            robot.drive(self.DRIVE_SPEED, turn_rate=correction)
        else: # NOT SEEING LINE
            self.angle_turned_since_line_lost = robot.angle_turned()
            match self.state:
                case State.SEEING_LINE: # Linie sollte nur verloren gehen, wenn starker Knick der Linie nach links (max. 90°) oder Lücke
                    self.state = State.LOST_LINE
                    robot.drive(0, 90)   # nach Links drehen mit 90°/s  # TODO vlt statt 0, doch bisschen Geschwindigkeit?
                    robot.reset_distance_and_angle()
                    # TODO Display oder Ton?
                case State.LOST_LINE:
                    # Wenn Linie verloren, dann maximal 100° nach Links drehen um zwischen starker Linkskurve und Lücke zu unterscheiden
                    # Linie nicht wiedergefunden -> Lücke, also wieder gerade drehen und suchen
                    if self.angle_turned_since_line_lost > 100:  # Schon 100° gedreht seit Linienverlust? -> Ja = Lücke
                        self.state = State.GAP_RIGHT_TURN
                        robot.drive(self.SEARCH_DRIVE_SPEED, -90)
                        # TODO Display oder Ton?
                case State.GAP_RIGHT_TURN:                       # vlt muss statt < -45 eher < 315 genutzt werden? 
                    if self.angle_turned_since_line_lost < -45:  # Schon 100° gedreht seit Linienverlust? -> Ja = Lücke
                        self.state = State.GAP_LEFT_TURN
                        robot.drive(self.SEARCH_DRIVE_SPEED, 90)
                case State.GAP_LEFT_TURN: 
                    if self.angle_turned_since_line_lost > 45:  # Schon 100° gedreht seit Linienverlust? -> Ja = Lücke
                        self.state = State.GAP_RIGHT_TURN
                        robot.drive(self.SEARCH_DRIVE_SPEED, -90)
                case _:
                    raise Exception('calling a non existing State')
            
            # falls match case nicht funktioniert
            
            # if self.state == State.SEEING_LINE:
            #     self.state = State.LOST_LINE
            #     robot.drive(0, 90)   # nach Links drehen mit 90°/s  # TODO vlt statt 0, doch bisschen Geschwindigkeit?
            #     robot.reset_distance_and_angle()
            #     # TODO Display oder Ton?
            # elif self.state == State.LOST_LINE:
            #     # Wenn Linie verloren, dann maximal 100° nach Links drehen um zwischen starker Linkskurve und Lücke zu unterscheiden
            #     # Linie nicht wiedergefunden -> Lücke, also wieder gerade drehen und suchen
            #     if self.angle_turned_since_line_lost > 100:  # Schon 100° gedreht seit Linienverlust? -> Ja = Lücke
            #         self.state = State.GAP_RIGHT_TURN
            #         robot.drive(0, -90)
            #         # TODO Display oder Ton?
            # elif self.state == GAP_Right_TURN:
            #     if self.angle_turned_since_line_lost > -45:  # Schon 100° gedreht seit Linienverlust? -> Ja = Lücke
            #         self.state = State.GAP_LEFT_TURN
            #         robot.drive(20, 90)
            # elif self.state == GAP_LEFT_TURN:
            #     if self.angle_turned_since_line_lost > 45:  # Schon 100° gedreht seit Linienverlust? -> Ja = Lücke
            #         self.state = State.GAP_RIGHT_TURN
            #         robot.drive(20, -90)
            # else:
            #     raise Exception('calling a non existing State')
