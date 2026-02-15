"""
Chocofi Top Case (switch plate).

Z layout:
  plate top    = Z = TOP_PLATE_THICKNESS
  plate bottom = Z = 0  (sits on PCB top)
  lip bottom   = Z = -TOP_LIP_HEIGHT
"""

import FreeCAD
import Part
from params import (
    TOLERANCE,
    WALL_THICKNESS,
    TOP_PLATE_THICKNESS,
    TOP_LIP_HEIGHT,
    SWITCH_PLATE_CUTOUT,
    SCREW_CLEARANCE_D,
)
from pcb_data import SWITCH_POSITIONS, MOUNTING_HOLES
from helpers import build_pcb_wire, make_plate_cutout, make_hole


def build_top_case():
    pcb_wire = build_pcb_wire()

    outer_wire = pcb_wire.makeOffset2D(TOLERANCE + WALL_THICKNESS)
    inner_wire = pcb_wire.makeOffset2D(TOLERANCE)
    outer_face = Part.Face(outer_wire)
    inner_face = Part.Face(inner_wire)

    # Plate
    plate = outer_face.extrude(FreeCAD.Vector(0, 0, TOP_PLATE_THICKNESS))

    # Lip going down inside bottom case walls
    lip_face = outer_face.cut(inner_face)
    lip = lip_face.extrude(FreeCAD.Vector(0, 0, -TOP_LIP_HEIGHT))

    top_case = plate.fuse(lip)

    # Switch plate cutouts (13.8mm squares)
    for sx, sy, rot in SWITCH_POSITIONS:
        top_case = top_case.cut(
            make_plate_cutout(
                sx,
                sy,
                rot,
                0,
                TOP_PLATE_THICKNESS,
                SWITCH_PLATE_CUTOUT,
            )
        )

    # Screw clearance holes
    for mx, my in MOUNTING_HOLES:
        top_case = top_case.cut(
            make_hole(
                mx,
                my,
                0,
                TOP_PLATE_THICKNESS,
                SCREW_CLEARANCE_D,
            )
        )

    return top_case.removeSplitter()
