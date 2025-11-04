from .section import Section

class SectionMoveObject(Section):

    def __init__(self):
        self.name = "Move Object"
        self.TARGET_WALL_DISTANCE_MM = 100
        self.PROPORTIONAL_GAIN = 1               # Je höher, desto "zitternder"
        self.DRIVE_SPEED = 100   # mm/s

    def reset(self):
        pass

    def run_one_step(self, robot):
        self.follow_wall(robot, 100, 'touch sensor')
        robot.spin(90)
        self.follow_wall(robot, 100, 'touch sensor')
        # robot.straight(50)  -> vlt zum ausrichten gegen Wand fahren
        # Greifen der Dose hardcoden
        robot.straight(-300)
        robot.spin(-45)
        robot.straight(100)
        robot.move_gripper_and_ultrasonic()
        # Dose in Zielbereich ziehen
        robot.straight(-500)
        # ausrichten zur Brücke
        robot.move_gripper_and_ultrasonic()
        robot.straight(-100)
        robot.spin(135)
        self.follow_wall(robot, 400, 'blue line')
        

    def follow_wall(self, robot, distanceToWall, untill = 'blue line'):
        if untill == 'blue line':
            condition = lambda : self.check_for_blue_line(robot)
        elif untill == 'touch sensor':
            condition = lambda : robot.touch_sensor.pressed() == False
        else:
            raise Exception("Invalid condition for follow_wall")

        while condition():             
            deviation = robot.ultrasonic_sensor.distance() - distanceToWall
            correction = deviation * self.PROPORTIONAL_GAIN
            robot.drive(self.DRIVE_SPEED, turn_rate=correction)
        robot.stop()