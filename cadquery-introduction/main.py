import cadquery as cq
from cadquery.vis import show


def main():
    circle_solid = cq.Workplane("XY").circle(1.0).extrude(3.0)
    show(circle_solid)


if __name__ == "__main__":
    main()
