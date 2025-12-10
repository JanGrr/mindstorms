from .section import Section
from pybricks.tools import wait
from pybricks.parameters import Stop

class SectionTest(Section):

    def __init__(self):
        super().__init__()
        self.name = "Test Section"
        
        

    def reset(self, robot):
        robot.stop()

    def run_one_step(self, robot):
        robot.reset_distance_and_angle()
        print("Set 0 angle...")
        wait(5000)
        robot.set_gripper_and_ultrasonic_angle(90)
        print("Set 90 angle...")
        wait(1000)
        robot.set_gripper_and_ultrasonic_angle(0)
        print("Set 0 angle...")
        wait(1000)
        robot.set_gripper_and_ultrasonic_angle(30)
        print("Set 30 angle...")
        wait(1000)
        robot.set_gripper_and_ultrasonic_angle(-5)
        print("Set -5 angle...")
        wait(10000)

        
