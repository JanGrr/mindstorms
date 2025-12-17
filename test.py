import matplotlib.pyplot as plt
from math import cos, sin, sqrt, pi

def get_unit_vector(angle):
    return (cos(angle), sin(angle))

def get_distance_from_circle_to_square(angle):
    u = get_unit_vector(angle)
    distances = []

    if u[0] != 0:
        vector_to_x = ((1 / u[0]) * u[0], (1 / u[0]) * u[1])
        distance_to_x = sqrt(vector_to_x[0]**2 + vector_to_x[1]**2)
        distances.append(distance_to_x)
    
    if u[1] != 0:
        vector_to_y = ((1 / u[1]) * u[0], (1 / u[1]) * u[1])
        distance_to_y = sqrt(vector_to_y[0]**2 + vector_to_y[1]**2)
        distances.append(distance_to_y)
    
    return min(distances) - 1

# Angles from 0 to 360 degrees
angles = [i * (pi / 180) for i in range(0, 361)]
distances = [get_distance_from_circle_to_square(angle) for angle in angles]

plt.plot([angle * 180 / pi for angle in angles], distances)
plt.xlabel('Angle (degrees)')
plt.ylabel('Distance from circle to square')
plt.title('Distance from Unit Circle to 1x1 Square (Full Circle)')
plt.grid()
plt.show()
