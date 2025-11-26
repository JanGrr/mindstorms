from .section import Section
from pybricks.parameters import Port, Stop, Direction

class SectionCrossBridge(Section):

    def __init__(self):
        super().__init__()
        self.name = "Cross Bridge"

        self.states = ["DRIVE_SECURITY", "EXTENT_ULTRASONIC", "EXTEND_ULTRASONIC", "FINISHED"]
        self.state_index = 0
        self.state = self.states[self.state_index]
        

    def reset(self, robot):
        pass

    def run_one_step(self, robot):
        if self.state == "DRIVE_SECURITY":
            self.drive_security(robot)
        elif self.state == "EXTENT_ULTRASONIC":
            self.extend_ultrasonic(robot)
        if self.state == "FINISHED":
            self.finished()

    def next_state(self):
        self.state_index += 1
        self.state = self.states[self.state_index]
        print("Next State: " + self.state)

    def drive_security(self, robot):
        robot.straight(50)  # Kleines stück vorfahren
        self.next_state()

    def extend_ultrasonic(self, robot):
        robot.set_gripper_and_ultrasonic_angle(100)  # Ultraschallsensor nach unten
        self.next_state()

    def finished(self):
        print("Finnished")
        
        