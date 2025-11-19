from pybricks.parameters import Color

class Section:

    def __init__(self):
        self.name = "Section"
        self.finished = False
    
    def get_name(self):
        return self.name
    
    def reset(self, robot):
        pass

    # macht es sinn true zurück zu geben, wenn Sektion beendet?
    def run_one_step(self, robot):
        pass

    def check_for_blue_line(self, robot):
        #return robot.color_sensor.color() == Color.BLUE
        r, g, b = robot.color_sensor.rgb()                             # Alternative
        is_blue = b >= 29 and g < 30 and r < 10 
        return is_blue

    def update_section_screen(self, robot):
        robot.ev3.screen.clear()
        robot.ev3.screen.draw_text("[<-]   " + self.name)
        robot.ev3.screen.draw_text("Status:")
        