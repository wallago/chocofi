"""
Chocofi Case - Geometry helpers (FreeCAD native API only).
"""

import math
import FreeCAD
import Part
from pcb_data import SEGMENTS


def build_pcb_wire():
    """Build a closed wire from KiCad Edge.Cuts. Flips Y for FreeCAD."""
    edges = []
    for seg in SEGMENTS:
        if seg[0] == "line":
            p1 = FreeCAD.Vector(seg[1][0], -seg[1][1], 0)
            p2 = FreeCAD.Vector(seg[2][0], -seg[2][1], 0)
            if p1.distanceToPoint(p2) > 0.001:
                edges.append(Part.makeLine(p1, p2))
        elif seg[0] == "arc":
            p1 = FreeCAD.Vector(seg[1][0], -seg[1][1], 0)
            p2 = FreeCAD.Vector(seg[2][0], -seg[2][1], 0)
            pm = FreeCAD.Vector(seg[3][0], -seg[3][1], 0)
            try:
                edges.append(Part.Arc(p1, pm, p2).toShape())
            except Exception:
                if p1.distanceToPoint(p2) > 0.001:
                    edges.append(Part.makeLine(p1, p2))
    return Part.Wire(edges)


def make_hole(x, y, z_base, height, diameter):
    """Cylindrical through-hole at KiCad coords (x, y)."""
    return Part.makeCylinder(
        diameter / 2.0, height + 2, FreeCAD.Vector(x, -y, z_base - 1)
    )


def make_plate_cutout(x, y, rot, z_base, height, size):
    """Square cutout (for switch plate) at KiCad coords with rotation."""
    half = size / 2.0
    box = Part.makeBox(size, size, height + 2, FreeCAD.Vector(-half, -half, z_base - 1))
    if rot != 0:
        box.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), -rot)
    box.translate(FreeCAD.Vector(x, -y, 0))
    return box


def transform_local_to_global(lx, ly, fp_x, fp_y, fp_rot_deg):
    """Transform footprint-local coords to global KiCad coords."""
    rad = math.radians(fp_rot_deg)
    gx = fp_x + lx * math.cos(rad) - ly * math.sin(rad)
    gy = fp_y + lx * math.sin(rad) + ly * math.cos(rad)
    return gx, gy
