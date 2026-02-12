"""
Chocofi Bottom Case - Floor
=================================================
"""

import FreeCAD
import Part
import os

# ══════════════════════════════════════════
# PARAMETERS
# ══════════════════════════════════════════
WALL_THICKNESS = 2.2  # mm border wall thickness
FLOOR_THICKNESS = 1.2  # mm
WALL_HEIGHT = 5.0  # mm height of border walls above the floor
TOLERANCE = 0.5  # mm gap between PCB edge and inner wall

# ══════════════════════════════════════════
# PCB OUTLINE from KiCad Edge.Cuts
# ══════════════════════════════════════════
SEGMENTS = [
    ("line", (112.910, 44.495), (112.927, 49.452)),
    ("arc", (112.927, 49.452), (112.427, 49.952), (112.781, 49.805)),
    ("line", (112.427, 49.952), (95.397, 49.952)),
    ("arc", (95.397, 49.952), (94.897, 50.452), (95.044, 50.098)),
    ("line", (94.897, 50.452), (94.895, 61.466)),
    ("arc", (94.895, 61.466), (94.395, 61.966), (94.749, 61.819)),
    ("line", (94.395, 61.966), (77.299, 61.921)),
    ("arc", (77.299, 61.921), (76.842, 62.378), (76.976, 62.055)),
    ("line", (76.842, 62.378), (76.893, 76.653)),
    ("line", (76.893, 76.653), (76.893, 93.722)),
    ("line", (76.893, 93.722), (76.893, 110.689)),
    ("line", (76.893, 110.689), (76.893, 112.061)),
    ("arc", (76.893, 112.061), (77.553, 112.721), (77.086, 112.528)),
    ("line", (77.553, 112.721), (94.012, 112.721)),
    ("arc", (94.012, 112.721), (94.673, 112.061), (94.479, 112.528)),
    ("line", (94.673, 112.061), (94.673, 110.689)),
    ("line", (94.673, 110.689), (94.724, 101.417)),
    ("arc", (94.724, 101.417), (95.333, 100.808), (94.902, 100.986)),
    ("line", (95.333, 100.808), (112.504, 100.808)),
    ("arc", (112.504, 100.808), (113.175, 101.240), (112.903, 100.925)),
    ("line", (113.175, 101.240), (124.899, 121.052)),
    ("arc", (124.899, 121.052), (125.254, 121.186), (125.064, 121.151)),
    ("line", (125.254, 121.186), (143.034, 121.205)),
    ("line", (143.034, 121.205), (160.357, 125.929)),
    ("line", (160.357, 125.929), (174.169, 133.905)),
    ("arc", (174.169, 133.905), (175.648, 133.600), (174.945, 133.929)),
    ("line", (175.648, 133.600), (188.094, 111.959)),
    ("line", (188.094, 111.959), (188.000, 54.250)),
    ("arc", (188.000, 54.250), (187.500, 53.750), (187.854, 53.896)),
    ("line", (187.500, 53.750), (167.210, 53.760)),
    ("arc", (167.210, 53.760), (166.730, 53.400), (166.910, 53.660)),
    ("arc", (166.730, 53.400), (166.240, 53.000), (166.557, 53.113)),
    ("line", (166.240, 53.000), (149.173, 53.014)),
    ("arc", (149.173, 53.014), (148.673, 52.514), (148.820, 52.868)),
    ("line", (148.673, 52.514), (148.673, 51.014)),
    ("arc", (148.673, 51.014), (148.173, 50.514), (148.527, 50.660)),
    ("line", (148.173, 50.514), (131.190, 50.498)),
    ("arc", (131.190, 50.498), (130.690, 49.998), (130.836, 50.352)),
    ("line", (130.690, 49.998), (130.690, 44.481)),
    ("arc", (130.690, 44.481), (130.190, 43.981), (130.544, 44.128)),
    ("line", (130.190, 43.981), (113.410, 43.995)),
    ("arc", (113.410, 43.995), (112.910, 44.495), (113.056, 44.141)),
]

# ══════════════════════════════════════════
# BUILD WIRE
# ══════════════════════════════════════════
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

pcb_wire = Part.Wire(edges)

# ══════════════════════════════════════════
# BUILD THE CASE
# ══════════════════════════════════════════

TOTAL_HEIGHT = FLOOR_THICKNESS + WALL_HEIGHT

inner_wire = pcb_wire.makeOffset2D(TOLERANCE)
outer_wire = pcb_wire.makeOffset2D(TOLERANCE + WALL_THICKNESS)

inner_face = Part.Face(inner_wire)
outer_face = Part.Face(outer_wire)

floor_solid = outer_face.extrude(FreeCAD.Vector(0, 0, FLOOR_THICKNESS))

wall_face = outer_face.cut(inner_face)
wall_solid = wall_face.extrude(FreeCAD.Vector(0, 0, WALL_HEIGHT))
wall_solid.translate(FreeCAD.Vector(0, 0, FLOOR_THICKNESS))

case = floor_solid.fuse(wall_solid)

# ── OUTER RIDGE for top plate snap-fit ──
RIDGE_WIDTH = 1.2
RIDGE_HEIGHT = 2.0

ridge_z = FLOOR_THICKNESS + WALL_HEIGHT

ridge_inner_wire = pcb_wire.makeOffset2D(TOLERANCE + WALL_THICKNESS - RIDGE_WIDTH)
ridge_inner_face = Part.Face(ridge_inner_wire)

ridge_face = outer_face.cut(ridge_inner_face)
ridge_solid = ridge_face.extrude(FreeCAD.Vector(0, 0, RIDGE_HEIGHT))
ridge_solid.translate(FreeCAD.Vector(0, 0, ridge_z))

case = case.fuse(ridge_solid)

# ── STANDOFFS with M2 heat-set insert holes ──
# M2 heat-set inserts: 3mm long, 3.5mm OD
# Screws come from the top plate down into the inserts
STANDOFF_HEIGHT = 3.5  # mm above floor (battery space)
STANDOFF_OUTER_R = 3.5  # mm (5mm diameter post)
INSERT_HOLE_D = 3.2  # mm - slightly under 3.5mm OD for press-fit
INSERT_HOLE_DEPTH = 3.0  # mm - insert length

MOUNTING_HOLES = [
    (148.971, 69.85),
    (185.42, 106.426),
    (123.952, 104.14),
    (167.005, 110.363),
    (171.323, 96.901),
    (95.0, 83.82),
    (95.0, 66.802),
]

for mx, my in MOUNTING_HOLES:
    pos = FreeCAD.Vector(mx, -my, FLOOR_THICKNESS)
    # Solid standoff post (no through hole)
    post = Part.makeCylinder(STANDOFF_OUTER_R, STANDOFF_HEIGHT, pos)
    case = case.fuse(post)
    # Blind hole from top for heat-set insert
    insert_z = FLOOR_THICKNESS + STANDOFF_HEIGHT - INSERT_HOLE_DEPTH
    hole = Part.makeCylinder(
        INSERT_HOLE_D / 2.0, INSERT_HOLE_DEPTH + 0.01, FreeCAD.Vector(mx, -my, insert_z)
    )
    case = case.cut(hole)

case = case.removeSplitter()

# ══════════════════════════════════════════
# EXPORT
# ══════════════════════════════════════════
doc = FreeCAD.newDocument("ChocofiCase")
part = doc.addObject("Part::Feature", "ChocofiBottomCase")
part.Shape = case
doc.recompute()

step_path = os.path.expanduser("~/chocofi_simple_case.step")
Part.export([part], step_path)
print(f"STEP -> {step_path}")

try:
    import Mesh

    stl_path = os.path.expanduser("~/chocofi_simple_case.stl")
    Mesh.export([part], stl_path)
    print(f"STL  -> {stl_path}")
except Exception as e:
    print(f"STL export failed: {e}")

bb = case.BoundBox
print(f"\nDone! Case: {bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f} mm")
print(f"  Floor: {FLOOR_THICKNESS} mm")
print(f"  Wall height: {WALL_HEIGHT} mm above floor")
print(f"  Wall thickness: {WALL_THICKNESS} mm")
print(
    f"  Standoffs: {STANDOFF_HEIGHT} mm, M2 insert holes ({INSERT_HOLE_D}mm x {INSERT_HOLE_DEPTH}mm blind)"
)
