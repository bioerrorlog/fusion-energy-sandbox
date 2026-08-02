import numpy as np
import cadquery as cq
from cadquery.vis import show


# Parameters (cm)
R0 = 300        # major radius
A = 100         # plasma minor radius
KAPPA = 1.8     # elongation
DELTA = 0.55    # triangularity (negative values give a negative-triangularity shape)
ANGLE = 270     # revolve angle; 360 for a full torus

# Inner to outer: (name, thickness, color)
RADIAL_BUILD = [
    ("sol",         20, "lightgray"),   # scrape-off layer
    ("first_wall",   5, "gray"),
    ("blanket",     60, "orange"),      # tritium breeding blanket
    ("shield",      30, "darkgreen"),
    ("vessel",      20, "steelblue"),   # vacuum vessel
]


def profile(offset):
    """(R, Z) points of a Miller plasma cross-section expanded outward by offset."""
    t = np.linspace(0, 2 * np.pi, 120, endpoint=False)
    r = R0 + (A + offset) * np.cos(t + DELTA * np.sin(t))
    z = (KAPPA * A + offset) * np.sin(t)
    return list(zip(r.tolist(), z.tolist()))


def revolve(points):
    """Revolve a closed profile on the XZ plane about the global Z axis.

    In Workplane("XZ") the local y axis is the global Z, so the rotation axis
    is (0,1,0). Shifting the local origin with .center() shifts that axis too,
    so always pass absolute coordinates to polyline.
    """
    return (cq.Workplane("XZ")
            .polyline(points).close()
            .revolve(ANGLE, (0, 0, 0), (0, 1, 0)))


def rect(r_min, r_max, z_min, z_max):
    """Helper that builds a rectangular cross-section in absolute coordinates."""
    return [(r_min, z_min), (r_min, z_max), (r_max, z_max), (r_max, z_min)]


def build_layers():
    """Stack up radial_build and carve each layer as outer minus inner."""
    plasma = revolve(profile(0))
    layers, prev, offset = {}, plasma, 0
    for name, thickness, _ in RADIAL_BUILD:
        offset += thickness
        outer = revolve(profile(offset))
        layers[name] = outer.cut(prev)
        prev = outer
    return plasma, layers, offset


def tf_coil(r_in, r_out, z_half, leg, width):
    """A single rectangular TF coil: cut the inner frame out of the outer one."""
    def slab(pts):
        return (cq.Workplane("XZ", origin=(0, width / 2, 0))
                .polyline(pts).close().extrude(width))

    outer = slab(rect(r_in, r_out, -z_half, z_half))
    inner = slab(rect(r_in + leg, r_out - leg, -z_half + leg, z_half - leg))
    return outer.cut(inner)


def pf_coil(r, z, w, h):
    """PF coil: just a rectangular cross-section revolved about the Z axis."""
    return revolve(rect(r - w / 2, r + w / 2, z - h / 2, z + h / 2))


def main():
    plasma, layers, offset = build_layers()
    z_max = KAPPA * A + offset

    # Divertor: carve the lower region out of first_wall + blanket, then
    # remove that region from the donor layers so nothing overlaps.
    block = revolve(rect(R0 - 40, R0 + 90, -z_max - 50, -KAPPA * A * 0.55))
    divertor = layers["first_wall"].union(layers["blanket"]).intersect(block)
    for name in ("first_wall", "blanket"):
        layers[name] = layers[name].cut(block)

    asm = cq.Assembly(plasma, name="plasma", color=cq.Color("magenta"))
    for name, _, color in RADIAL_BUILD:
        asm.add(layers[name], name=name, color=cq.Color(color))

    asm.add(divertor, name="divertor", color=cq.Color("red"))

    # Place 7 TF coils in the toroidal direction
    coil = tf_coil(R0 - offset - A - 60, R0 + offset + A + 60,
                   z_max + 60, leg=45, width=40)
    for i, deg in enumerate(np.linspace(0, ANGLE, 7)):
        asm.add(coil.rotate((0, 0, 0), (0, 0, 1), float(deg)),
                name=f"tf_{i}", color=cq.Color("gold"))

    # PF coils: (R, Z, width, height)
    for i, (r, z, w, h) in enumerate([
        (R0 + offset + A + 140, 380, 40, 40),
        (R0 + offset + A + 190, 210, 60, 60),
        (R0 + offset + A + 190, -210, 60, 60),
        (R0 + offset + A + 140, -380, 40, 40),
    ]):
        asm.add(pf_coil(r, z, w, h), name=f"pf_{i}", color=cq.Color("blue"))

    asm.export("tokamak.step")
    print("wrote tokamak.step")

    show(asm)


if __name__ == "__main__":
    main()
