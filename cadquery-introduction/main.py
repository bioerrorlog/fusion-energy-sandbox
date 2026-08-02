import cadquery as cq
from cadquery.vis import show


def circle_solid():
    circle_solid = cq.Workplane("XY").circle(1.0).extrude(3.0)
    show(circle_solid)


def spine_solid():
    xyz_coordinates = [
        (-1.0, -2.0),
        (-0.5, 2.0),
        (1.0, 3.0),
        (2.0, 2.0),
    ]
    spine_solid = cq.Workplane("XY").spline(listOfXYTuple=xyz_coordinates, periodic=True).close().extrude(0.5)
    show(spine_solid)


if __name__ == "__main__":
    # circle_solid()
    spine_solid()
