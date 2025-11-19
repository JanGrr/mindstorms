from Parcour.section import Section
from Parcour.sectionFollowLine import SectionFollowLine
from Parcour.sectionMoveObject import SectionMoveObject
from Parcour.sectionCrossBridge import SectionCrossBridge
from Parcour.sectionSearchColorFields import SectionSearchColorFields

class Parcour:

    def __init__(self):
        self.sections = [
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
            self.sections[self.current_section_index].update_section_screen(robot)
        else:
            self.sections[self.current_section_index].run_one_step(robot) 

    def next_section(self, robot):
        self.sections[self.current_section_index].reset(robot)
        if (self.current_section_index == len(self.sections) - 1):
            self.finished()
        else:
            self.current_section_index += 1

    def finished(self):
        self.running = False
        # self.current_section_index = 0

    def reset(self):
        self.current_section_index = 0
        self.running = False
        