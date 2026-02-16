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
from helpers import build_pcb_wire, make_plate_cutout, make_hole

NICE_VIEW_W = 36.5
NICE_VIEW_H = 14.5
NICE_VIEW_T = 1.6


def build_nice_view():
    view_box = Part.makeBox(NICE_VIEW_H, NICE_VIEW_W, NICE_VIEW_T)
    target_x = 177.75
    target_y = -74

    view_box.translate(
        FreeCAD.Vector(
            target_x - (NICE_VIEW_H / 2.0), target_y - (NICE_VIEW_W / 2.0), 2
        )
    )
    return view_box
