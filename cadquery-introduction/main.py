import cadquery as cq
from cadquery.vis import show


def circle_solid() -> cq.Workplane:
    circle_solid = cq.Workplane("XY").circle(1.0).extrude(3.0)
    return circle_solid


def spine_solid() -> cq.Workplane:
    xyz_coordinates = [
        (-1.0, -2.0),
        (-0.5, 2.0),
        (1.0, 3.0),
        (2.0, 2.0),
    ]
    spine_solid = cq.Workplane("XY").spline(listOfXYTuple=xyz_coordinates, periodic=True).close().extrude(0.5)
    return spine_solid


def cut_spline() -> cq.Workplane:
    cut_spline = spine_solid().cut(circle_solid())
    return cut_spline


def assembly() -> cq.Assembly:
    assembly = cq.Assembly()
    assembly.add(circle_solid(), color=cq.Color("red"))
    assembly.add(cut_spline(), color=cq.Color("blue"))
    return assembly


if __name__ == "__main__":
    # show(circle_solid())
    # show(spine_solid())
    # show(cut_spline())
    # show(assembly())
    assembly().export('my-cad-geometry.step')
