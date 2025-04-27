'''
This script was created to find the points that make the circle (polygon) equidistant
from a given point on the grid. The points on the grid were hard-coded later, because
the grid size forms a dodecagon.
'''

def approx_points_on_circle(x0, y0, resolution=0.1, radius=0.5, tol=0):
    points = []
    steps = int((radius + tol) / resolution) + 1  # search radius in grid steps
    for i in range(-steps, steps + 1):
        for j in range(-steps, steps + 1):
            x = x0 + i * resolution
            y = y0 + j * resolution
            dist = ((x - x0)**2 + (y - y0)**2)**0.5
            if abs(dist - radius) <= tol:
                points.append([round(x, 10), round(y, 10)])
    return points

res = approx_points_on_circle(0, 0)
print(res)