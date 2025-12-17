from pybricks.parameters import Button
from pybricks.tools import wait

class Menu:

    def __init__(self, robot, parcour):
        self.course = parcour
        self.course.set_menu(self)  # Observer-Listener-Pattern to avoid cyclic dependency
        self.robot = robot
        # self.last_pressed = None
        self.SCREEN_WIDTH = self.robot.ev3.screen.width
        self.SCREEN_HEIGHT = self.robot.ev3.screen.height
        self.update()
        

    def update(self):
        self.robot.ev3.screen.clear()
        if not self.course.sections:
            return  # Avoid division by zero if no sections

        # Draw menu with all parcour sections
        for i, section in enumerate(self.course.sections):
            self.robot.ev3.screen.draw_text(
                x=3,
                y=int(i * (self.SCREEN_HEIGHT / len(self.course.sections))),
                text=section.get_name()
            )

        # Highlight selected section
        self.robot.ev3.screen.draw_box(
            x1=1,
            y1=int(self.course.current_section_index * (self.SCREEN_HEIGHT / len(self.course.sections))),
            x2=self.SCREEN_WIDTH - 1,
            y2=int((self.course.current_section_index + 1) * (self.SCREEN_HEIGHT / len(self.course.sections)) - 8)
        )

    def check_buttonpress(self):
        buttons_pressed = self.robot.ev3.buttons.pressed()

        if not buttons_pressed:  # Nothing pressed
            return

        if len(buttons_pressed) > 1:
            # Ignore multiple presses instead of raising an exception
            return

        if self.course.running and Button.LEFT not in buttons_pressed:
            # Abort parcour first
            return

        button = buttons_pressed[0]

        # Handle button presses
        if button == Button.UP:
            self.select_previous_section()
        elif button == Button.DOWN:
            self.select_next_section()
        elif button == Button.CENTER:
            self.confirm_selection()
        elif button == Button.LEFT:
            self.abort_parcour()
        else:
            # Unknown button, ignore
            return

        wait(300)  # Debounce delay
        print("Button  pressed")

from pybricks.parameters import Button
from pybricks.tools import wait

class Menu:

    def __init__(self, robot, parcour):
        self.course = parcour
        self.course.set_menu(self)  # Observer-Listener-Pattern to avoid cyclic dependency
        self.robot = robot
        # self.last_pressed = None
        self.SCREEN_WIDTH = self.robot.ev3.screen.width
        self.SCREEN_HEIGHT = self.robot.ev3.screen.height
        self.update()
        

    def update(self):
        self.robot.ev3.screen.clear()
        # draw menu with all parcour sections
        for i, section in enumerate(self.course.sections):
            self.robot.ev3.screen.draw_text(
                x = 3, 
                y = int(i * (self.SCREEN_HEIGHT / len(self.course.sections))), 
                text = section.get_name())

        # highlight selected section
        self.robot.ev3.screen.draw_box(
            x1 = 1, 
            y1 = int(self.course.current_section_index * (self.SCREEN_HEIGHT / len(self.course.sections))),
            x2 = self.SCREEN_WIDTH - 1,
            y2 = int((self.course.current_section_index + 1) * (self.SCREEN_HEIGHT / len(self.course.sections)) - 8)
        )

    def check_buttonpress(self):
        buttons_pressed = self.robot.ev3.buttons.pressed()

        if not buttons_pressed:  # Nothing pressed
            return

        if len(buttons_pressed) > 1:
            # Ignore multiple presses instead of raising an exception
            return

        if self.course.running and Button.LEFT not in buttons_pressed:
            # Abort parcour first
            return

        button = buttons_pressed[0]

        if button == Button.UP:                   # Falls match case nicht funktioniert
            self.select_previous_section()
        elif button == Button.DOWN:
            self.select_next_section()
        elif button == Button.CENTER:
            self.confirm_selection()
        elif button == Button.LEFT:
            self.abort_parcour()

        wait(250)  # die Tastendrücke werden sonst teilweise mehrfach erkannt

    def select_previous_section(self):
        self.course.current_section_index = (self.course.current_section_index - 1) % len(self.course.sections)
        self.update()
        
    def select_next_section(self):
        self.course.current_section_index = (self.course.current_section_index + 1) % len(self.course.sections)
        self.update()

    def confirm_selection(self):
        self.course.running = True
        current_section = self.course.sections[self.course.current_section_index]
        #current_section.update_section_screen(self.robot, current_section.status)

    def abort_parcour(self):
        self.course.running = False
        current_section = self.course.sections[self.course.current_section_index]
        current_section.reset(self.robot)
        self.update()
