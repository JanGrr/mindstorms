from pybricks.parameters import Button


class Menu:

    def __init__(self, ev3, parcour):
        self.course = parcour
        self.course.set_menu(self)  # Observer-Listerner-Pattern um zyklische Abhängigkeit zu umgehen
        self.ev3 = ev3
        # self.last_pressed = None
        self.SCREEN_WIDTH = self.ev3.screen.width
        self.SCREEN_HEIGHT = self.ev3.screen.height
        self.update()

    def update(self):
        self.ev3.screen.clear()
        # draw menu with all parcour sections
        for i in range(len(self.course.sections)):
            self.ev3.screen.draw_text(
                x = 3, 
                y = int(i * (self.SCREEN_HEIGHT / len(self.course.sections))), 
                text = self.course.sections[i].get_name())

        # highlight selected section
        self.ev3.screen.draw_box(
            x1 = 1, 
            y1 = int(self.course.current_section_index * (self.SCREEN_HEIGHT / len(self.course.sections))),
            x2 = self.SCREEN_WIDTH - 1,
            y2 = int((self.course.current_section_index + 1) * (self.SCREEN_HEIGHT / len(self.course.sections)) - 8)
        )

    def check_buttonpress(self):
        buttons_pressed = self.ev3.buttons.pressed()

        if not buttons_pressed:     # oder if buttons_pressed.size() == 0: 
            return  # nichts gedrückt

        if len(buttons_pressed) > 1:
            raise Exception("Multiple buttons pressed")

        if self.course.running and Button.BACK not in buttons_pressed:
            raise Exception("Abort parcour first")

        button = buttons_pressed[0]

        match button:
            case Button.UP:
                self.select_previous_section()
                # self.last_pressed = Button.UP
            case Button.DOWN:
                self.select_next_section()
                # self.last_pressed = Button.DOWN
            case Button.CENTER:
                self.confirm_selection()
                # self.last_pressed = Button.CENTER
            case Button.BACK:
                self.abort_parcour()
                # self.last_pressed = Button.BACK
            case _:
                raise Exception("This button does nothing")
        
        # if button == Button.UP:                   # Falls match case nicht funktioniert
        #     self.select_previous_section()
              # self.last_pressed = Button.UP
        # elif button == Button.DOWN:
        #     self.select_next_section()
              # self.last_pressed = Button.DOWN
        # elif button == Button.CENTER:
        #     self.confirm_selection()
              # self.last_pressed = Button.CENTER
        # elif button == Button.BACK:
        #     self.abort_parcour()
              # self.last_pressed = Button.BACK
        # else:
        #     raise Exception("This button does nothing")

    def select_previous_section(self):
        self.course.current_section_index = (self.course.current_section_index - 1) % len(self.course.sections)
        self.update()
        
    def select_next_section(self):
        self.course.current_section_index = (self.course.current_section_index + 1) % len(self.course.sections)
        self.update()

    def confirm_selection(self):
        self.course.running = True
    
    def abort_parcour(self):
        self.course.running = False
        self.course.sections[self.course.current_section_index].reset()
 