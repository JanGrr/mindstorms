from .section import Section
from .sectionTest import SectionTest
from .sectionFollowLine import SectionFollowLine
from .sectionMoveObject import SectionMoveObject
from .sectionCrossBridge import SectionCrossBridge
from .sectionSearchColorFields import SectionSearchColorFields

class Parcour:

    def __init__(self):
        self.sections = [
            SectionTest(),
            SectionFollowLine(),
            SectionMoveObject(),
            SectionCrossBridge(),
            SectionSearchColorFields()
        ]
        self.current_section_index = 0
        self.running = False
        self.menu = None

    def set_menu(self, observer):                       # Observer-Listerner-Pattern um zyklische Abhängigkeit zu umgehen
        self.menu = observer

    def get_section_name(self, section_index):
        return self.sections[section_index].get_name()
    
    def run_one_step(self, robot):
        if self.sections[self.current_section_index].finished:
            self.next_section(robot)
        else:
            self.sections[self.current_section_index].run_one_step(robot) 

    def next_section(self, robot):
        self.sections[self.current_section_index].reset(robot)
        if (self.current_section_index == len(self.sections) - 1):
            self.finished()
        else:
            self.current_section_index += 1
            #self.sections[self.current_section_index].update_section_screen(robot)

    def finished(self):
        self.running = False
        self.current_section_index = 0
        self.menu.update()

    def reset(self):
        self.current_section_index = 0
        self.running = False
        