"""
Chocofi Top Plate
=================
Run in FreeCAD: Macro > Macros... > browse to this file > Execute

Features:
- Kailh Choc low-profile switch cutouts (13.8mm square)
- USB-C slot that fits both nice!nano positions
- Nice!view display window
- Matching groove to snap onto bottom case ridge
"""

import FreeCAD
import Part
import math
import os

# ══════════════════════════════════════════
# PARAMETERS
# ══════════════════════════════════════════
PLATE_THICKNESS = 1.6  # mm - top plate thickness (matches PCB)
GROOVE_DEPTH = 2.0  # mm - matches bottom case RIDGE_HEIGHT
GROOVE_WIDTH = 1.2  # mm - matches bottom case RIDGE_WIDTH
GROOVE_TOLERANCE = 0.2  # mm - gap so it slides on easily
BORDER_WIDTH = 2.2  # mm - matches bottom case WALL_THICKNESS
TOLERANCE = 0.5  # mm - matches bottom case TOLERANCE

# Switch cutout
CHOC_CUTOUT = 13.8  # mm - Kailh Choc plate cutout (square)
CHOC_TOLERANCE = 0.1  # mm - extra per side for easier insertion
CHOC_HOLE = CHOC_CUTOUT + CHOC_TOLERANCE * 2  # final cutout size

# USB-C port
USBC_WIDTH = 10.0  # mm - wide enough for both nano positions
USBC_HEIGHT = 4.0  # mm - USB-C connector height + clearance
USBC_SLOT_EXTRA = 3.0  # mm - extra width to cover both nano placements

# Nice!view display
NICEVIEW_WINDOW_W = 25.0  # mm - display visible area width + margin
NICEVIEW_WINDOW_H = 13.0  # mm - display visible area height + margin
NICEVIEW_SURROUND = 0.5  # mm - lip around window to hold the display

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

# Switch positions from KiCad (Kailh Choc hotswap)
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
    (134.010, 112.990, 0.0),  # thumb 1 - 180° is same as 0° for square
    (154.060, 115.580, 15.0),  # thumb 2 - 15° tilt
    (174.660, 118.790, -60.0),  # thumb 3 - -60° tilt
]

# Nice!nano positions (both at -90° rotation)
# Nano #1 (front):  (176.75, 71.77), USB-C center at Y ≈ 56.27
# Nano #2 (back):   (178.75, 73.02), USB-C center at Y ≈ 57.52

# Nice!view sits on top of nice!nano, near the USB end
# With -90° rotation, display long axis is along global Y
# Center roughly at X=177.75, Y=65 (between USB and middle of nano)
NICEVIEW_CENTER_X = 177.75
NICEVIEW_CENTER_Y = 67.0

# USB-C slot - needs to go through the top plate wall on the top edge
# Covers both nano positions
USBC_CENTER_X = 177.75
# USB-C faces the top edge of PCB (low Y), the connector sits around Y=54-58
# The wall is at the PCB edge, so the slot goes through the plate border
USBC_CENTER_Y = 54.0  # roughly at the PCB edge where the wall is

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
# BUILD TOP PLATE
# ══════════════════════════════════════════

# The top plate outer edge matches the bottom case outer wall
outer_wire = pcb_wire.makeOffset2D(TOLERANCE + BORDER_WIDTH)
outer_face = Part.Face(outer_wire)

# Main plate body
plate = outer_face.extrude(FreeCAD.Vector(0, 0, PLATE_THICKNESS))

# ── GROOVE on the underside ──
# The groove wraps around the inside of the plate border.
# It matches the ridge on the bottom case:
#   Ridge sits on outer half of bottom wall, width=RIDGE_WIDTH
#   Groove needs to be slightly wider (GROOVE_TOLERANCE) to slide over it
#
# Bottom case ridge outer edge = outer_wire (same as plate outer)
# Bottom case ridge inner edge = TOLERANCE + BORDER_WIDTH - RIDGE_WIDTH from PCB
# Groove outer = same as ridge outer (plate outer edge)
# Groove inner = ridge inner - GROOVE_TOLERANCE

groove_outer_wire = pcb_wire.makeOffset2D(TOLERANCE + BORDER_WIDTH)
groove_inner_wire = pcb_wire.makeOffset2D(
    TOLERANCE + BORDER_WIDTH - GROOVE_WIDTH - GROOVE_TOLERANCE
)

groove_outer_face = Part.Face(groove_outer_wire)
groove_inner_face = Part.Face(groove_inner_wire)
groove_ring = groove_outer_face.cut(groove_inner_face)

groove_solid = groove_ring.extrude(FreeCAD.Vector(0, 0, GROOVE_DEPTH))
# Groove goes downward from plate bottom (z=0 going negative)
groove_solid.translate(FreeCAD.Vector(0, 0, -GROOVE_DEPTH))

# The groove is a pocket cut into a skirt that hangs below the plate
# First make the skirt (full ring going down)
skirt_ring = groove_outer_face.cut(Part.Face(pcb_wire.makeOffset2D(TOLERANCE)))
skirt = skirt_ring.extrude(FreeCAD.Vector(0, 0, GROOVE_DEPTH))
skirt.translate(FreeCAD.Vector(0, 0, -GROOVE_DEPTH))

plate = plate.fuse(skirt)

# Now cut the groove channel into the skirt
plate = plate.cut(groove_solid)

# ── SWITCH CUTOUTS ──
for sx, sy, rot in SWITCHES:
    half = CHOC_HOLE / 2.0
    r = math.radians(rot)

    # 4 corners of the square cutout in local coords
    corners_local = [(-half, -half), (half, -half), (half, half), (-half, half)]

    # Rotate and place in FreeCAD coords (Y flipped)
    corners_global = []
    for lx, ly in corners_local:
        gx = sx + lx * math.cos(r) - ly * math.sin(r)
        gy = -(sy + lx * math.sin(r) + ly * math.cos(r))
        corners_global.append(FreeCAD.Vector(gx, gy, 0))

    # Make wire and face
    cut_edges = []
    for i in range(4):
        j = (i + 1) % 4
        cut_edges.append(Part.makeLine(corners_global[i], corners_global[j]))
    cut_wire = Part.Wire(cut_edges)
    cut_face = Part.Face(cut_wire)

    # Cut through entire plate + skirt
    cut_solid = cut_face.extrude(
        FreeCAD.Vector(0, 0, PLATE_THICKNESS + GROOVE_DEPTH + 2)
    )
    cut_solid.translate(FreeCAD.Vector(0, 0, -GROOVE_DEPTH - 1))
    plate = plate.cut(cut_solid)

# ══════════════════════════════════════════
# NICE!VIEW TOWER
# ══════════════════════════════════════════

import math

# Tower dimensions (same as standalone that fits)
TOWER_WALL = 1.6
TOWER_TOL = 0.4
NV_PCB_H = 14.0
NV_PCB_W = 36.0

CAVITY_X = NV_PCB_H + TOWER_TOL * 2  # 14.8mm (nice!view guide width)
CAVITY_Y = NV_PCB_W + TOWER_TOL * 2  # 36.8mm
HOLE_X = 20.0  # mm - wider hole for nice!nano access
OUTER_X = HOLE_X + TOWER_WALL * 2  # 23.2mm
OUTER_Y = CAVITY_Y + TOWER_WALL * 2  # 40.0mm

TOWER_BASE_H = 1.0
TOWER_HEIGHT = 2.0
TOWER_TOTAL = TOWER_BASE_H + TOWER_HEIGHT  # 5.0mm

# Position: flush with top plate outer border
TOWER_CX = 177.75
TOWER_FRONT_Y = 51.05  # KiCad Y - flush with plate outer edge + 0.75mm back
TOWER_CY = TOWER_FRONT_Y + OUTER_Y / 2

# No gap - tower sits directly on the plate
NANO_CLEARANCE = 0.0

# Screen window (from datasheet)
# Nice!view rotated 180°: pin header faces FRONT (low Y), connector faces BACK
NV_SCR_INSET_PIN = 5.0  # pin header side = now FRONT
NV_SCR_INSET_CON = 4.0  # connector side = now BACK
NV_SCR_INSET_SIDE = 1.6  # top/bottom edges
NV_SCREEN_DISP_W = NV_PCB_W - NV_SCR_INSET_PIN - NV_SCR_INSET_CON  # 27mm along Y
NV_SCREEN_DISP_H = NV_PCB_H - NV_SCR_INSET_SIDE * 2  # 10.8mm along X
# Screen shifted toward back (pin header takes more space at front)
SCREEN_CY = TOWER_CY + (NV_SCR_INSET_PIN - NV_SCR_INSET_CON) / 2.0

# USB-C hole
USBC_W = 11.0
USBC_H = 3.26
USBC_R = 0.8

# Z base of tower
tower_z_base = PLATE_THICKNESS + NANO_CLEARANCE
tower_top_z = tower_z_base + TOWER_TOTAL


# ── Helper ──
def make_rect_face(cx, cy, w, h):
    """Rectangle centered at (cx, -cy) in FreeCAD coords."""
    c = [
        FreeCAD.Vector(cx - w / 2, -(cy - h / 2), 0),
        FreeCAD.Vector(cx + w / 2, -(cy - h / 2), 0),
        FreeCAD.Vector(cx + w / 2, -(cy + h / 2), 0),
        FreeCAD.Vector(cx - w / 2, -(cy + h / 2), 0),
    ]
    edges = [Part.makeLine(c[i], c[(i + 1) % 4]) for i in range(4)]
    return Part.Face(Part.Wire(edges))


# ── 1) Tower outer box with rounded corners ──
# Extend right side to be flush with plate outer edge
TOWER_LEFT = TOWER_CX - OUTER_X / 2  # 166.15
TOWER_RIGHT = 190.7  # flush with plate outer edge
TOWER_ACTUAL_W = TOWER_RIGHT - TOWER_LEFT
TOWER_ACTUAL_CX = (TOWER_LEFT + TOWER_RIGHT) / 2.0

TOWER_CORNER_R = 3.2  # mm radius - matches plate outer corner arcs

# Build rounded rectangle for tower outer shape
tr_hw = TOWER_ACTUAL_W / 2.0
tr_hh = OUTER_Y / 2.0
tr_r = TOWER_CORNER_R
tr_cx = TOWER_ACTUAL_CX
tr_cy_fc = -TOWER_CY  # FreeCAD Y

cos45_t = 0.7071

# Corner centers
t_tl = (tr_cx - tr_hw + tr_r, tr_cy_fc + tr_hh - tr_r)
t_tr = (tr_cx + tr_hw - tr_r, tr_cy_fc + tr_hh - tr_r)
t_br = (tr_cx + tr_hw - tr_r, tr_cy_fc - tr_hh + tr_r)
t_bl = (tr_cx - tr_hw + tr_r, tr_cy_fc - tr_hh + tr_r)


def tv(x, y):
    return FreeCAD.Vector(x, y, 0)


tower_edges = [
    # Top edge
    Part.makeLine(tv(t_tl[0], t_tl[1] + tr_r), tv(t_tr[0], t_tr[1] + tr_r)),
    # Top-right arc
    Part.Arc(
        tv(t_tr[0], t_tr[1] + tr_r),
        tv(t_tr[0] + tr_r * cos45_t, t_tr[1] + tr_r * cos45_t),
        tv(t_tr[0] + tr_r, t_tr[1]),
    ).toShape(),
    # Right edge
    Part.makeLine(tv(t_tr[0] + tr_r, t_tr[1]), tv(t_br[0] + tr_r, t_br[1])),
    # Bottom-right arc
    Part.Arc(
        tv(t_br[0] + tr_r, t_br[1]),
        tv(t_br[0] + tr_r * cos45_t, t_br[1] - tr_r * cos45_t),
        tv(t_br[0], t_br[1] - tr_r),
    ).toShape(),
    # Bottom edge
    Part.makeLine(tv(t_br[0], t_br[1] - tr_r), tv(t_bl[0], t_bl[1] - tr_r)),
    # Bottom-left arc
    Part.Arc(
        tv(t_bl[0], t_bl[1] - tr_r),
        tv(t_bl[0] - tr_r * cos45_t, t_bl[1] - tr_r * cos45_t),
        tv(t_bl[0] - tr_r, t_bl[1]),
    ).toShape(),
    # Left edge
    Part.makeLine(tv(t_bl[0] - tr_r, t_bl[1]), tv(t_tl[0] - tr_r, t_tl[1])),
    # Top-left arc
    Part.Arc(
        tv(t_tl[0] - tr_r, t_tl[1]),
        tv(t_tl[0] - tr_r * cos45_t, t_tl[1] + tr_r * cos45_t),
        tv(t_tl[0], t_tl[1] + tr_r),
    ).toShape(),
]

tower_wire = Part.Wire(tower_edges)
tower_face = Part.Face(tower_wire)
tower_solid = tower_face.extrude(FreeCAD.Vector(0, 0, TOWER_TOTAL))
tower_solid.translate(FreeCAD.Vector(0, 0, tower_z_base))

# Trim tower to plate outline for the right side arcs
plate_outer_face = Part.Face(pcb_wire.makeOffset2D(TOLERANCE + BORDER_WIDTH))
plate_boundary = plate_outer_face.extrude(
    FreeCAD.Vector(0, 0, TOWER_TOTAL + PLATE_THICKNESS + 10)
)
plate_boundary.translate(FreeCAD.Vector(0, 0, -5))
tower_solid = tower_solid.common(plate_boundary)

plate = plate.fuse(tower_solid)

# ── 2) Hollow out inside with 20mm wide hole (open from bottom, lid on top) ──
tower_inner_wide = make_rect_face(TOWER_CX, TOWER_CY, HOLE_X, CAVITY_Y)
cavity = tower_inner_wide.extrude(FreeCAD.Vector(0, 0, TOWER_TOTAL - TOWER_WALL))
cavity.translate(FreeCAD.Vector(0, 0, tower_z_base - 0.01))
plate = plate.cut(cavity)

# ── 3) Open the plate underneath the tower (20mm wide) ──
# Only cut through the plate itself, NOT the skirt below
plate_hole = tower_inner_wide.extrude(FreeCAD.Vector(0, 0, PLATE_THICKNESS + 0.02))
plate_hole.translate(FreeCAD.Vector(0, 0, -0.01))
plate = plate.cut(plate_hole)

# ── 4) Screen window on top with PCB guide ledge ──
# Center screen between left and right tower walls
SCREEN_CX = TOWER_CX + 0.675

# First: cut a shallow PCB-sized recess into the lid (guide for gluing)
# Nice!view PCB is 36x14mm, at -90° that's 14mm in X, 36mm in Y
NV_PCB_RECESS_X = NV_PCB_H + TOWER_TOL * 2  # 14.8mm
NV_PCB_RECESS_Y = NV_PCB_W + TOWER_TOL * 2  # 36.8mm
NV_RECESS_DEPTH = 1.0  # mm - PCB thickness

recess_face = make_rect_face(SCREEN_CX, SCREEN_CY, NV_PCB_RECESS_X, NV_PCB_RECESS_Y)
recess_cut = recess_face.extrude(FreeCAD.Vector(0, 0, NV_RECESS_DEPTH + 0.01))
recess_cut.translate(FreeCAD.Vector(0, 0, tower_top_z - TOWER_WALL - NV_RECESS_DEPTH))
plate = plate.cut(recess_cut)

# Then: cut the screen window through the remaining lid
screen_face = make_rect_face(SCREEN_CX, SCREEN_CY, NV_SCREEN_DISP_H, NV_SCREEN_DISP_W)
screen_cut = screen_face.extrude(FreeCAD.Vector(0, 0, TOWER_WALL + 2))
screen_cut.translate(FreeCAD.Vector(0, 0, tower_top_z - TOWER_WALL - 1))
plate = plate.cut(screen_cut)

# ── 5) USB-C notch on front wall ──
# Rounded top (arc), open bottom - U-shape / notch
# Lowered 2.47mm from center, bottom completely open
tower_front_fc_y = -TOWER_FRONT_Y
usb_z_center = tower_z_base + TOWER_TOTAL / 2.0 - 2.47

usb_hw = USBC_W / 2.0
usb_hh = USBC_H / 2.0
r = USBC_R
cos45 = math.cos(math.pi / 4)

# Top of the USB-C shape (rounded rect top half + sides going all the way down)
# The notch goes from below the plate (z=-5) up to usb_z_center + usb_hh
usb_top_z = usb_z_center + usb_hh
usb_bottom_z = -5.0  # well below everything

# Top-left and top-right corner centers (only top corners have arcs)
c_tl = (TOWER_CX - usb_hw + r, usb_top_z - r)
c_tr = (TOWER_CX + usb_hw - r, usb_top_z - r)


def uv(x, z):
    return FreeCAD.Vector(x, tower_front_fc_y, z)


# Build U-shape: left side up, arc top-left, top straight, arc top-right, right side down
usb_edges = [
    # Left side (bottom to top)
    Part.makeLine(uv(TOWER_CX - usb_hw, usb_bottom_z), uv(TOWER_CX - usb_hw, c_tl[1])),
    # Top-left arc
    Part.Arc(
        uv(c_tl[0] - r, c_tl[1]),
        uv(c_tl[0] - r * cos45, c_tl[1] + r * cos45),
        uv(c_tl[0], c_tl[1] + r),
    ).toShape(),
    # Top straight
    Part.makeLine(uv(c_tl[0], c_tl[1] + r), uv(c_tr[0], c_tr[1] + r)),
    # Top-right arc
    Part.Arc(
        uv(c_tr[0], c_tr[1] + r),
        uv(c_tr[0] + r * cos45, c_tr[1] + r * cos45),
        uv(c_tr[0] + r, c_tr[1]),
    ).toShape(),
    # Right side (top to bottom)
    Part.makeLine(uv(TOWER_CX + usb_hw, c_tr[1]), uv(TOWER_CX + usb_hw, usb_bottom_z)),
    # Bottom (close the shape)
    Part.makeLine(
        uv(TOWER_CX + usb_hw, usb_bottom_z), uv(TOWER_CX - usb_hw, usb_bottom_z)
    ),
]

usb_wire = Part.Wire(usb_edges)
usb_face = Part.Face(usb_wire)
usb_cut = usb_face.extrude(FreeCAD.Vector(0, -(TOWER_WALL + 2), 0))
usb_cut.translate(FreeCAD.Vector(0, 1, 0))
plate = plate.cut(usb_cut)

# ── 5b) Reinforce inner skirt near USB-C ──
# The skirt is thin near the USB-C notch. Add 0.60mm to the inner face
# of the skirt, 4.50mm wide on each side of the notch, 3.27mm tall
# hanging down from the skirt top (z=0).
REINFORCE_THICK = 0.60
REINFORCE_H = 3.27
REINFORCE_W = 4.50

# Skirt inner face is at the PCB outline + TOLERANCE inward
# The reinforcement goes on the inside (toward center), so it's offset
# further inward from the skirt inner edge
# At the tower front, Y ≈ 51.05 (KiCad), the skirt follows the PCB edge
# The skirt inner face Y in FreeCAD ≈ -(pcb_edge_y + TOLERANCE)
# Reinforcement is on the inside = toward more negative FreeCAD Y (higher KiCad Y)

skirt_inner_fc_y = -(
    TOWER_FRONT_Y - BORDER_WIDTH + TOLERANCE
)  # approximate inner skirt Y

# Left strip (left of USB-C notch)
left_reinf = Part.makeBox(
    REINFORCE_W,
    REINFORCE_THICK,
    REINFORCE_H,
    FreeCAD.Vector(
        TOWER_CX - usb_hw - REINFORCE_W,
        skirt_inner_fc_y - REINFORCE_THICK - 3.30,
        -REINFORCE_H + 3.26,
    ),
)
plate = plate.fuse(left_reinf)

# Right strip (right of USB-C notch)
right_reinf = Part.makeBox(
    REINFORCE_W,
    REINFORCE_THICK,
    REINFORCE_H,
    FreeCAD.Vector(
        TOWER_CX + usb_hw,
        skirt_inner_fc_y - REINFORCE_THICK - 3.30,
        -REINFORCE_H + 3.26,
    ),
)
plate = plate.fuse(right_reinf)

# Clean up
plate = plate.removeSplitter()

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
print(
    f"  Tower: {OUTER_X:.1f} x {OUTER_Y:.1f} x {TOWER_TOTAL:.1f} mm (raised {NANO_CLEARANCE}mm)"
)
print(f"  Screen window: {NV_SCREEN_DISP_H:.1f} x {NV_SCREEN_DISP_W:.1f} mm")
print(f"  Pin header at back, USB-C on front")
