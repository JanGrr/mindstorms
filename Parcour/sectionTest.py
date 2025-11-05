from .section import Section

class SectionTest(Section):

    def __init__(self):
        super().__init__()
        self.name = "Test Section"
        

    def reset(self, robot):
        robot.stop()

    def run_one_step(self, robot):
        #Run both motors
        robot.drive(0, 90)
        
