from .section import Section

class SectionCrossBridge(Section):

    def __init__(self):
        super().__init__()
        self.name = "Cross Bridge"

    def reset(self, robot):
        pass

    def run_one_step(self, robot):
        pass