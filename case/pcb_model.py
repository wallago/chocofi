"""
Chocofi PCB model.
Flat board with actual through-holes from KiCad:
  - Switch NPTH holes (stem, pins, hotswap sockets)
  - nice!nano header pin holes
  - Mounting holes (M2)

NO switch plate cutouts on the PCB — those go on the top case only.

Z layout: top = 0, bottom = -PCB_THICKNESS
"""

import FreeCAD
import Part
from params import PCB_THICKNESS
from pcb_data import (
    SWITCH_POSITIONS,
    SWITCH_NPTH_HOLES,
    SWITCH_CENTER_HOLE,
    MOUNTING_HOLES,
    MOUNTING_HOLE_DRILL,
    NICENANO_HEADERS,
    NICENANO_PAD_DRILL,
)
from helpers import build_pcb_wire, make_hole, transform_local_to_global


def build_pcb():
    wire = build_pcb_wire()
    face = Part.Face(wire)
    pcb = face.extrude(FreeCAD.Vector(0, 0, -PCB_THICKNESS))

    holes = []

    # ── Switch holes (NPTH + center plated hole per switch) ──
    for sx, sy, rot in SWITCH_POSITIONS:
        # NPTH holes (stem, pins, hotswap sockets)
        for lx, ly, drill in SWITCH_NPTH_HOLES:
            gx, gy = transform_local_to_global(lx, ly, sx, sy, rot)
            holes.append(make_hole(gx, gy, -PCB_THICKNESS, PCB_THICKNESS, drill))

        # Center plated through-hole
        cx, cy, cd = SWITCH_CENTER_HOLE
        gx, gy = transform_local_to_global(cx, cy, sx, sy, rot)
        holes.append(make_hole(gx, gy, -PCB_THICKNESS, PCB_THICKNESS, cd))

    # ── nice!nano header holes ──
    for fp_x, fp_y, fp_rot, pads in NICENANO_HEADERS:
        for lx, ly in pads:
            gx, gy = transform_local_to_global(lx, ly, fp_x, fp_y, fp_rot)
            holes.append(
                make_hole(gx, gy, -PCB_THICKNESS, PCB_THICKNESS, NICENANO_PAD_DRILL)
            )

    # ── Mounting holes ──
    for mx, my in MOUNTING_HOLES:
        holes.append(
            make_hole(mx, my, -PCB_THICKNESS, PCB_THICKNESS, MOUNTING_HOLE_DRILL)
        )

    # Cut all holes at once
    if holes:
        pcb = pcb.cut(Part.Compound(holes))

    return pcb.removeSplitter()
