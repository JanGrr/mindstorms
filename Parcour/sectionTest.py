from .section import Section
from pybricks.tools import wait
from pybricks.parameters import Stop

class SectionTest(Section):

    def __init__(self):
        super().__init__()
        self.name = "Test Section"
        self.calibrated = False
        
        

    def reset(self, robot):
        robot.stop()

    def run_one_step(self, robot):
        robot.drive(10, 0)
        print(robot.color_sensor.rgb())
        wait(1000)

        
