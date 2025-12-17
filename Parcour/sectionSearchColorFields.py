from .section import Section
from pybricks.tools import wait, StopWatch
from math import pi

class SectionSearchColorFields(Section):
    
    def __init__(self):
        super().__init__()
        self.name = "Search Colorfields"
        # Geometry
        self.CIRCLE_DIAMETER = 1300  # mm
        self.SPACING = 80  # mm
        self.r_max = self.CIRCLE_DIAMETER / 2 - 20    # safety margin (mm)
        self.r_min = 80            # stop radius (mm)
        self.b = self.SPACING / (2 * pi)

        # Motion
        self.V_MAX = 800  # mm/s
        self.v = self.V_MAX              # mm/s
        self.theta = 0.0
        self.r = self.r_max

        # Timing
        self.watch = StopWatch()
        self.watch.reset()

        #Color
        self.base_rgb = None

    def reset(self, robot):
        self.theta = 0.0
        self.r = self.r_max
        self.watch.reset()
        self.base_rgb = None
        self.v = self.V_MAX

    def run_one_step(self, robot):
        
        if self.base_rgb is None:
            self.base_rgb = robot.color_sensor.rgb()

        dt = self.watch.time() / 1000  # ms → s
        self.watch.reset()

        if self.r <= self.r_min:
            robot.stop()
            return False   # finished

        # Angular velocity
        omega_rad = self.v / self.r
        omega_deg = omega_rad * 180 / pi

        # Optional safety cap
        if omega_deg > 120:
            omega_deg = 120

        # Adjust speed based on radius
        self.v = self.V_MAX * (0.6*(self.r - self.r_min) / (self.r_max - self.r_min) + 0.4)

        # Drive
        robot.drive(self.v, omega_deg)

        # Integrate motion
        self.theta += omega_rad * dt
        self.r = self.r_max - self.b * self.theta

        self.check_for_color(robot)

    def check_for_color(self, robot):
        r, g, b = robot.color_sensor.rgb()
        base_r, base_g, base_b = self.base_rgb

        relative_red_change = r / max(base_r, 1)
        relative_green_change = g / max(base_g, 1)
        relative_blue_change = b / max(base_b, 1)

        threshold = 2  # 200% change

        if relative_red_change > threshold:
            if relative_green_change > threshold and relative_blue_change > threshold:
                print("White detected")
                robot.ev3.speaker.beep(frequency=1000, duration=200)
            else:
                print("Red detected")
                robot.ev3.speaker.beep(frequency=600, duration=200)

