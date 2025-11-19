from .section import Section

class SectionCrossBridge(Section):

    def __init__(self):
        super().__init__()
        self.name = "Cross Bridge"

    def reset(self, robot):
        pass

    def update_section_screen(self, robot):
        robot.ev3.screen.clear()
        robot.ev3.screen.draw_text("[<-]   " + self.name)
        robot.ev3.screen.draw_text("Status:")

    def run_one_step(self, robot):
        pass