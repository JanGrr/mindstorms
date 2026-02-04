from pybricks.parameters import Color

class Section:

    def __init__(self):
        self.name = "Section"
        self.finished = False
    
    def get_name(self):
        return self.name
    
    def reset(self, robot):
        robot.stop()
        self.finished = False

    def run_one_step(self, robot):
        pass

    def check_for_blue_line(self, robot, r, g, b):
        is_blue = r<10 and b>30
        return is_blue

    def update_section_screen(self, robot, status1="", status2="", status3=""):
        robot.ev3.screen.clear()
        robot.ev3.screen.draw_text(x=3, y=3, text="[<-]  " + self.name)
        robot.ev3.screen.draw_text(x=3, y=33, text="" + status1)
        robot.ev3.screen.draw_text(x=3, y=63, text="" + status2)
        robot.ev3.screen.draw_text(x=3, y=93, text="" + status3)
