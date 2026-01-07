#!/usr/bin/env pybricks-micropython

from robot import Robot
from Parcour.parcour import Parcour
from menu import Menu


robot = Robot()
course = Parcour()
menu = Menu(robot, course)

robot.calibrate_gripper_and_ultrasonic_angle()

while True:
    menu.check_buttonpress()
    if course.running:
        course.run_one_step(robot)
