"""
Chocofi Top Plate
=================
Run in FreeCAD: exec(open("/path/to/chocofi_top_plate.py").read())

Features:
- Kailh Choc low-profile switch cutouts
- Snap-fit groove for bottom case
- Nice!view tower with screen window, PCB guide recess, USB-C notch
- Rounded tower corners matching plate outline
"""

import FreeCAD
import Part
import math
import os

# ══════════════════════════════════════════
# PARAMETERS
# ══════════════════════════════════════════

# ── Plate ──
PLATE_THICKNESS = 1.6  # mm
BORDER_WIDTH = 2.2  # mm (matches bottom case wall)
TOLERANCE = 0.5  # mm (gap around PCB)

# ── Groove (snap-fit onto bottom case ridge) ──
GROOVE_DEPTH = 2.0  # mm (matches ridge height)
GROOVE_WIDTH = 1.2  # mm (matches ridge width)
GROOVE_TOLERANCE = 0.2  # mm

# ── Switch cutouts ──
CHOC_CUTOUT = 13.8  # mm (Kailh Choc spec)
CHOC_TOLERANCE = 0.1  # mm per side
CHOC_HOLE = CHOC_CUTOUT + CHOC_TOLERANCE * 2

# ── Nice!view (from datasheet) ──
NV_PCB_W = 36.0  # mm (long side)
NV_PCB_H = 14.0  # mm (short side)
NV_PCB_THICK = 1.0  # mm
NV_SCREEN_THICK = 0.9  # mm
NV_SCR_INSET_PIN = 5.0  # mm (pin header side)
NV_SCR_INSET_CON = 4.0  # mm (connector side)
NV_SCR_INSET_SIDE = 1.6  # mm (top/bottom)
NV_SCREEN_W = NV_PCB_W - NV_SCR_INSET_PIN - NV_SCR_INSET_CON  # 27.0mm
NV_SCREEN_H = NV_PCB_H - NV_SCR_INSET_SIDE * 2  # 10.8mm

# ── Tower ──
TOWER_WALL = 1.6  # mm
TOWER_TOL = 0.4  # mm (around nice!view PCB)
TOWER_HEIGHT = 7.0  # mm total above plate

CAVITY_X = NV_PCB_H + TOWER_TOL * 2  # 14.8mm (X, nice!view short side)
CAVITY_Y = NV_PCB_W + TOWER_TOL * 2  # 36.8mm (Y, nice!view long side)
HOLE_X = 20.0  # mm (wider for nice!nano access)
OUTER_X = HOLE_X + TOWER_WALL * 2  # 23.2mm
OUTER_Y = CAVITY_Y + TOWER_WALL * 2  # 40.0mm

TOWER_CX = 177.75
TOWER_FRONT_Y = 51.05  # KiCad Y of front outer face
TOWER_CY = TOWER_FRONT_Y + OUTER_Y / 2.0
TOWER_CORNER_R = 3.2  # mm (matches plate corner arcs)

# Tower right side flush with plate outer edge, left side pulled in 1.5mm to clear keycaps
TOWER_LEFT = TOWER_CX - OUTER_X / 2.0 + 1.5  # 167.65 (was 166.15)
TOWER_RIGHT = 190.7

# Nice!view recess: 2mm border around screen window
NV_BORDER = 2.0  # mm ledge width around screen
NV_RECESS_DEPTH = 1.0  # mm

# Screen center: nice!view rotated 180° → pin header at front
SCREEN_CY = TOWER_CY + (NV_SCR_INSET_PIN - NV_SCR_INSET_CON) / 2.0
SCREEN_CX = (TOWER_LEFT + TOWER_RIGHT) / 2.0  # centered in actual tower box

# ── USB-C notch ──
USBC_W = 11.0  # mm (standard 8.94 + 2mm)
USBC_H = 3.26  # mm (standard height)
USBC_R = 0.8  # mm (corner radius)
USBC_Z_DROP = 2.47  # mm below tower center

# ── Skirt reinforcement near USB-C ──
REINFORCE_THICK = 0.60  # mm
REINFORCE_H = 3.27  # mm
REINFORCE_W = 4.50  # mm
REINFORCE_Y_BACK = 3.30  # mm backward offset
REINFORCE_Z_UP = 3.26  # mm upward offset

# ══════════════════════════════════════════
# PCB OUTLINE (KiCad Edge.Cuts)
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

SWITCHES = [
    (121.910, 52.400, 0.0),
    (103.910, 58.400, 0.0),
    (139.910, 59.020, 0.0),
    (157.910, 61.400, 0.0),
    (121.910, 69.400, 0.0),
    (85.910, 70.400, 0.0),
    (103.910, 75.400, 0.0),
    (139.910, 76.020, 0.0),
    (157.910, 78.400, 0.0),
    (121.910, 86.400, 0.0),
    (85.910, 87.400, 0.0),
    (103.910, 92.400, 0.0),
    (139.910, 93.025, 0.0),
    (157.910, 95.400, 0.0),
    (85.910, 104.400, 0.0),
    (134.010, 112.990, 0.0),
    (154.060, 115.580, 15.0),
    (174.660, 118.790, -60.0),
]

# ══════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════


def build_pcb_wire():
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


def make_rect_face(cx, cy, w, h):
    pts = [
        FreeCAD.Vector(cx - w / 2, -(cy - h / 2), 0),
        FreeCAD.Vector(cx + w / 2, -(cy - h / 2), 0),
        FreeCAD.Vector(cx + w / 2, -(cy + h / 2), 0),
        FreeCAD.Vector(cx - w / 2, -(cy + h / 2), 0),
    ]
    edges = [Part.makeLine(pts[i], pts[(i + 1) % 4]) for i in range(4)]
    return Part.Face(Part.Wire(edges))


def make_rounded_rect_face(cx_fc, cy_fc, hw, hh, r):
    c45 = math.cos(math.pi / 4)
    tl = (cx_fc - hw + r, cy_fc + hh - r)
    tr = (cx_fc + hw - r, cy_fc + hh - r)
    br = (cx_fc + hw - r, cy_fc - hh + r)
    bl = (cx_fc - hw + r, cy_fc - hh + r)

    def v(x, y):
        return FreeCAD.Vector(x, y, 0)

    edges = [
        Part.makeLine(v(tl[0], tl[1] + r), v(tr[0], tr[1] + r)),
        Part.Arc(
            v(tr[0], tr[1] + r),
            v(tr[0] + r * c45, tr[1] + r * c45),
            v(tr[0] + r, tr[1]),
        ).toShape(),
        Part.makeLine(v(tr[0] + r, tr[1]), v(br[0] + r, br[1])),
        Part.Arc(
            v(br[0] + r, br[1]),
            v(br[0] + r * c45, br[1] - r * c45),
            v(br[0], br[1] - r),
        ).toShape(),
        Part.makeLine(v(br[0], br[1] - r), v(bl[0], bl[1] - r)),
        Part.Arc(
            v(bl[0], bl[1] - r),
            v(bl[0] - r * c45, bl[1] - r * c45),
            v(bl[0] - r, bl[1]),
        ).toShape(),
        Part.makeLine(v(bl[0] - r, bl[1]), v(tl[0] - r, tl[1])),
        Part.Arc(
            v(tl[0] - r, tl[1]),
            v(tl[0] - r * c45, tl[1] + r * c45),
            v(tl[0], tl[1] + r),
        ).toShape(),
    ]
    return Part.Face(Part.Wire(edges))


def make_usbc_notch_face(cx, fc_y, z_top, hw, r):
    c45 = math.cos(math.pi / 4)
    z_bot = -10.0
    ctl = (cx - hw + r, z_top - r)
    ctr = (cx + hw - r, z_top - r)

    def v(x, z):
        return FreeCAD.Vector(x, fc_y, z)

    edges = [
        Part.makeLine(v(cx - hw, z_bot), v(cx - hw, ctl[1])),
        Part.Arc(
            v(ctl[0] - r, ctl[1]),
            v(ctl[0] - r * c45, ctl[1] + r * c45),
            v(ctl[0], ctl[1] + r),
        ).toShape(),
        Part.makeLine(v(ctl[0], ctl[1] + r), v(ctr[0], ctr[1] + r)),
        Part.Arc(
            v(ctr[0], ctr[1] + r),
            v(ctr[0] + r * c45, ctr[1] + r * c45),
            v(ctr[0] + r, ctr[1]),
        ).toShape(),
        Part.makeLine(v(cx + hw, ctr[1]), v(cx + hw, z_bot)),
        Part.makeLine(v(cx + hw, z_bot), v(cx - hw, z_bot)),
    ]
    return Part.Face(Part.Wire(edges))


# ══════════════════════════════════════════
# BUILD
# ══════════════════════════════════════════
pcb_wire = build_pcb_wire()

outer_offset = TOLERANCE + BORDER_WIDTH
outer_wire = pcb_wire.makeOffset2D(outer_offset)
outer_face = Part.Face(outer_wire)

# ── 1. Plate body ──
plate = outer_face.extrude(FreeCAD.Vector(0, 0, PLATE_THICKNESS))

# ── 2. Skirt + groove ──
groove_outer_face = Part.Face(pcb_wire.makeOffset2D(outer_offset))
groove_inner_face = Part.Face(
    pcb_wire.makeOffset2D(outer_offset - GROOVE_WIDTH - GROOVE_TOLERANCE)
)
skirt_inner_face = Part.Face(pcb_wire.makeOffset2D(TOLERANCE))

skirt = groove_outer_face.cut(skirt_inner_face).extrude(
    FreeCAD.Vector(0, 0, GROOVE_DEPTH)
)
skirt.translate(FreeCAD.Vector(0, 0, -GROOVE_DEPTH))
plate = plate.fuse(skirt)

groove = groove_outer_face.cut(groove_inner_face).extrude(
    FreeCAD.Vector(0, 0, GROOVE_DEPTH)
)
groove.translate(FreeCAD.Vector(0, 0, -GROOVE_DEPTH))
plate = plate.cut(groove)

# ── 3. Switch cutouts ──
for sx, sy, rot in SWITCHES:
    half = CHOC_HOLE / 2.0
    rad = math.radians(rot)
    corners = []
    for lx, ly in [(-half, -half), (half, -half), (half, half), (-half, half)]:
        gx = sx + lx * math.cos(rad) - ly * math.sin(rad)
        gy = -(sy + lx * math.sin(rad) + ly * math.cos(rad))
        corners.append(FreeCAD.Vector(gx, gy, 0))
    cut_edges = [Part.makeLine(corners[i], corners[(i + 1) % 4]) for i in range(4)]
    cut_face = Part.Face(Part.Wire(cut_edges))
    cut_solid = cut_face.extrude(
        FreeCAD.Vector(0, 0, PLATE_THICKNESS + GROOVE_DEPTH + 2)
    )
    cut_solid.translate(FreeCAD.Vector(0, 0, -GROOVE_DEPTH - 1))
    plate = plate.cut(cut_solid)

# ══════════════════════════════════════════
# NICE!VIEW TOWER
# ══════════════════════════════════════════

tower_z_base = PLATE_THICKNESS
tower_top_z = tower_z_base + TOWER_HEIGHT

# ── 4. Tower shell (rounded corners, right flush with plate) ──
tower_actual_w = TOWER_RIGHT - TOWER_LEFT
tower_actual_cx = (TOWER_LEFT + TOWER_RIGHT) / 2.0

# Left wall is thin, so use smaller radius for left corners
# Right corners match plate arcs (3.2mm)
R_LEFT = 1.0  # small radius for thin left wall
R_RIGHT = TOWER_CORNER_R  # 3.2mm for right (matches plate)

hw = tower_actual_w / 2.0
hh = OUTER_Y / 2.0
cx_fc = tower_actual_cx
cy_fc = -TOWER_CY
c45 = math.cos(math.pi / 4)

# Corner centers with different radii
tl = (cx_fc - hw + R_LEFT, cy_fc + hh - R_LEFT)  # top-left
tr = (cx_fc + hw - R_RIGHT, cy_fc + hh - R_RIGHT)  # top-right
br = (cx_fc + hw - R_RIGHT, cy_fc - hh + R_RIGHT)  # bottom-right
bl = (cx_fc - hw + R_LEFT, cy_fc - hh + R_LEFT)  # bottom-left


def tv(x, y):
    return FreeCAD.Vector(x, y, 0)


tower_edges = [
    # Top edge
    Part.makeLine(tv(tl[0], tl[1] + R_LEFT), tv(tr[0], tr[1] + R_RIGHT)),
    # Top-right arc
    Part.Arc(
        tv(tr[0], tr[1] + R_RIGHT),
        tv(tr[0] + R_RIGHT * c45, tr[1] + R_RIGHT * c45),
        tv(tr[0] + R_RIGHT, tr[1]),
    ).toShape(),
    # Right edge
    Part.makeLine(tv(tr[0] + R_RIGHT, tr[1]), tv(br[0] + R_RIGHT, br[1])),
    # Bottom-right arc
    Part.Arc(
        tv(br[0] + R_RIGHT, br[1]),
        tv(br[0] + R_RIGHT * c45, br[1] - R_RIGHT * c45),
        tv(br[0], br[1] - R_RIGHT),
    ).toShape(),
    # Bottom edge
    Part.makeLine(tv(br[0], br[1] - R_RIGHT), tv(bl[0], bl[1] - R_LEFT)),
    # Bottom-left arc
    Part.Arc(
        tv(bl[0], bl[1] - R_LEFT),
        tv(bl[0] - R_LEFT * c45, bl[1] - R_LEFT * c45),
        tv(bl[0] - R_LEFT, bl[1]),
    ).toShape(),
    # Left edge
    Part.makeLine(tv(bl[0] - R_LEFT, bl[1]), tv(tl[0] - R_LEFT, tl[1])),
    # Top-left arc
    Part.Arc(
        tv(tl[0] - R_LEFT, tl[1]),
        tv(tl[0] - R_LEFT * c45, tl[1] + R_LEFT * c45),
        tv(tl[0], tl[1] + R_LEFT),
    ).toShape(),
]

tower_face = Part.Face(Part.Wire(tower_edges))
tower_solid = tower_face.extrude(FreeCAD.Vector(0, 0, TOWER_HEIGHT))
tower_solid.translate(FreeCAD.Vector(0, 0, tower_z_base))

# Trim to plate outline
plate_boundary = outer_face.extrude(FreeCAD.Vector(0, 0, 50))
plate_boundary.translate(FreeCAD.Vector(0, 0, -10))
tower_solid = tower_solid.common(plate_boundary)
plate = plate.fuse(tower_solid)

# ── 5. Tower cavity ──
tower_inner = make_rect_face(TOWER_CX, TOWER_CY, HOLE_X, CAVITY_Y)
cavity = tower_inner.extrude(FreeCAD.Vector(0, 0, TOWER_HEIGHT - TOWER_WALL))
cavity.translate(FreeCAD.Vector(0, 0, tower_z_base - 0.01))
plate = plate.cut(cavity)

# ── 6. Open plate under tower ──
plate_hole = tower_inner.extrude(FreeCAD.Vector(0, 0, PLATE_THICKNESS + 0.02))
plate_hole.translate(FreeCAD.Vector(0, 0, -0.01))
plate = plate.cut(plate_hole)

# ── 7a. Inner guide walls for nice!view positioning ──
# 1.5mm tall ridges on both sides (left/right in X)
# At screen center ± (5tower_inner.4mm screen half + 1.6mm PCB inset) = ±7.0mm
GUIDE_WALL_H = TOWER_HEIGHT - TOWER_WALL - 1.4  # full cavity height, flush with lid
GUIDE_WALL_THICK = 1.6  # mm thick (X direction)
GUIDE_OFFSET = 5.4 + 1.7  # 7.1mm from screen center to wall inner edge

# Left guide wall (lower X) - extends to cavity left edge
left_wall_inner = SCREEN_CX - GUIDE_OFFSET  # inner edge aligned with nice!view PCB
left_wall_outer = TOWER_CX - HOLE_X / 2.0  # extend to cavity left edge
left_wall_w = left_wall_inner - left_wall_outer
left_wall_cx = (left_wall_inner + left_wall_outer) / 2.0
left_wall = make_rect_face(left_wall_cx, TOWER_CY, left_wall_w, CAVITY_Y)
lw = left_wall.extrude(FreeCAD.Vector(0, 0, GUIDE_WALL_H))
lw.translate(FreeCAD.Vector(0, 0, tower_z_base + 3))
plate = plate.fuse(lw)

# Right guide wall (higher X)
right_wall_cx = SCREEN_CX + GUIDE_OFFSET + GUIDE_WALL_THICK / 2.0
right_wall = make_rect_face(right_wall_cx, TOWER_CY, GUIDE_WALL_THICK, CAVITY_Y)
rw = right_wall.extrude(FreeCAD.Vector(0, 0, GUIDE_WALL_H))
rw.translate(FreeCAD.Vector(0, 0, tower_z_base + 3))
plate = plate.fuse(rw)

# ── 7b. Screen window ──
screen_face = make_rect_face(SCREEN_CX, SCREEN_CY, NV_SCREEN_H, NV_SCREEN_W)
screen_cut = screen_face.extrude(FreeCAD.Vector(0, 0, TOWER_WALL + 2))
screen_cut.translate(FreeCAD.Vector(0, 0, tower_top_z - TOWER_WALL - 1))
plate = plate.cut(screen_cut)

# ── 9. USB-C notch ──
# Fixed absolute position (doesn't move with tower height)
usb_z_top = 2.26  # absolute Z, preserved from original 3mm tower height
usb_face = make_usbc_notch_face(
    TOWER_CX, -TOWER_FRONT_Y, usb_z_top, USBC_W / 2.0, USBC_R
)
usb_cut = usb_face.extrude(FreeCAD.Vector(0, -(TOWER_WALL + 2), 0))
usb_cut.translate(FreeCAD.Vector(0, 1, 0))
plate = plate.cut(usb_cut)

# ── 10. Skirt reinforcement ──
skirt_inner_fc_y = -(TOWER_FRONT_Y - BORDER_WIDTH + TOLERANCE)
usb_hw = USBC_W / 2.0

for x_start in [TOWER_CX - usb_hw - REINFORCE_W, TOWER_CX + usb_hw]:
    reinf = Part.makeBox(
        REINFORCE_W,
        REINFORCE_THICK,
        REINFORCE_H,
        FreeCAD.Vector(
            x_start,
            skirt_inner_fc_y - REINFORCE_THICK - REINFORCE_Y_BACK,
            -REINFORCE_H + REINFORCE_Z_UP,
        ),
    )
    plate = plate.fuse(reinf)

# ── Cleanup ──
plate = plate.removeSplitter()

# ── 11. M2 countersunk screw holes (matching bottom case standoffs) ──
M2_THROUGH = 2.2  # mm - M2 screw clearance hole
M2_HEAD_D = 4.0  # mm - M2 DIN 7991 dk max from datasheet
# 90° cone angle: depth = (head_d - through_d) / 2
M2_HEAD_DEPTH = (M2_HEAD_D - M2_THROUGH) / 2.0  # 0.9mm
M2_HEX_S = 1.3  # mm - hex socket width (Allen key size for M2)
M2_HEX_DEPTH = 0.5  # mm - hex socket recess depth into plate top

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
    # Through hole (full depth: plate + skirt)
    hole = Part.makeCylinder(
        M2_THROUGH / 2.0,
        PLATE_THICKNESS + GROOVE_DEPTH + 2,
        FreeCAD.Vector(mx, -my, -GROOVE_DEPTH - 1),
    )
    plate = plate.cut(hole)
    # Chamfered countersink (90° cone for DIN 7991 flat head)
    cone = Part.makeCone(
        M2_HEAD_D / 2.0,
        M2_THROUGH / 2.0,
        M2_HEAD_DEPTH,
        FreeCAD.Vector(mx, -my, PLATE_THICKNESS - M2_HEAD_DEPTH),
    )
    plate = plate.cut(cone)
    # Hex socket recess at the top surface
    hex_socket = Part.makeCylinder(
        M2_HEX_S, M2_HEX_DEPTH, FreeCAD.Vector(mx, -my, PLATE_THICKNESS - M2_HEX_DEPTH)
    )
    plate = plate.cut(hex_socket)

# ══════════════════════════════════════════
# EXPORT
# ══════════════════════════════════════════
doc = FreeCAD.newDocument("ChocofiTopPlate")
part = doc.addObject("Part::Feature", "ChocofiTopPlate")
part.Shape = plate
doc.recompute()

step_path = os.path.expanduser("~/chocofi_top_plate.step")
Part.export([part], step_path)
print(f"STEP -> {step_path}")

try:
    import Mesh

    stl_path = os.path.expanduser("~/chocofi_top_plate.stl")
    Mesh.export([part], stl_path)
    print(f"STL  -> {stl_path}")
except Exception as e:
    print(f"STL export failed: {e}")

bb = plate.BoundBox
print(f"\nDone! Top plate: {bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f} mm")
print(f"  Tower: {tower_actual_w:.1f} x {OUTER_Y:.1f} x {TOWER_HEIGHT:.1f} mm")
print(f"  Screen: {NV_SCREEN_H:.1f} x {NV_SCREEN_W:.1f} mm")
print(f"  USB-C: {USBC_W} x {USBC_H} mm (notch)")
print(f"  M2 countersunk holes: {len(MOUNTING_HOLES)}")
