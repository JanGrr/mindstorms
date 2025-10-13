from .section import Section
from pybricks.tools import wait

class SectionTest(Section):

    def __init__(self):
        super().__init__()
        self.name = "Test Section"
        

    def reset(self, robot):
        robot.stop()

    def run_one_step(self, robot):
        #Run both motors
        
        robot.drive_base.turn(90)
        wait(1000)
        robot.drive_base.turn(-90)
        wait(1000)
        
