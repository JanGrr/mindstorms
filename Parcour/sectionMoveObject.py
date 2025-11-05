from .section import Section
from pybricks.tools import wait

class SectionMoveObject(Section):

    class State(Enum):
        FIRST_FOLLOW_WALL = 1
        SECOND_FOLLOW_WALL = 2
        THIRD_DRIVE_BACK = 3
        FORTH_SPIN = 4
        FIFTH_DRIVE_FORWARD = 5
        SIXTH_GRAB_OBJECT = 6
        SEVENTH_DRIVE_BACK = 7
        EIGTH_RELEASE_OBJECT = 8

    def __init__(self):
        self.name = "Move Object"
        self.TARGET_WALL_DISTANCE_MM = 100
        self.PROPORTIONAL_GAIN = 1               # Je höher, desto "zitternder"
        self.DRIVE_SPEED = 100   # mm/s
        self.DRIVE_SPEED_SLOW = 30
        self.state = State.FIRST_FOLLOW_WALL

    def reset(self):
        self.state = State.FIRST_FOLLOW_WALL

    def run_one_step(self, robot):
        match self.state:
            case State.FIRST_FOLLOW_WALL:
                if robot.driven_distance() == 600:
                    robot.drive(self.DRIVE_SPEED, turn_rate=90)
                    wait(1000)
                    self.state = State.SECOND_FOLLOW_WALL
                else:
                    self.follow_wall(robot, 100)
            case SECOND_FOLLOW_WALL:
                if robot.ultrasonic_sensor.distance() < 50:         # Objekt erkannt
                    robot.drive(DRIVE_SPEED_SLOW, turn_rate=70)
                    wait(1000)
                    robot.move_gripper_and_ultrasonic()
                    robot.spin(angle=-45)                           # vlt lieber Gyro
                    wait(1000)
                    robot.straight(distance_mm=100)
                    robot.move_gripper_and_ultrasonic()
                    robot.straight(distance_mm=-500)
                    robot.move_gripper_and_ultrasonic()
                    robot.straight(distance_mm=-100)
                    robot.spin()
                    self.state = State.
                else:
                    self.follow_wall(robot, 100)
            case THIRD_DRIVE_BACK:
            case FORTH_SPIN:
            case FIFTH_DRIVE_FORWARD:
            case SIXTH_GRAB_OBJECT:
            case SEVENTH_DRIVE_BACK:
            case EIGTH_RELEASE_OBJECT:
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
        
    def follow_wall(self, robot, distanceToWall):
        deviation = robot.ultrasonic_sensor.distance() - distanceToWall
        correction = deviation * self.PROPORTIONAL_GAIN
        robot.drive(self.DRIVE_SPEED, turn_rate=correction)

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