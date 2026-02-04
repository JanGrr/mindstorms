#!/usr/bin/env pybricks-micropython

from robot import Robot
from Parcour.parcour import Parcour
from menu import Menu


robot = Robot()
course = Parcour()
menu = Menu(robot, course)

robot.calibrate_gripper_and_ultrasonic_angle()

iterantion = 0

while True:
    iterantion += 1
    if iterantion % 25 == 0:            # just check every 25th time, for more iterations per second 24 out of 25 times
        menu.check_buttonpress()
    if course.running:
        course.run_one_step(robot)
