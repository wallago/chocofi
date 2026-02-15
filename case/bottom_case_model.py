"""
Chocofi Bottom Case (tray).

Z layout:
  ridge top    = -PCB_THICKNESS + RIDGE_HEIGHT
  walls top    = -PCB_THICKNESS
  floor top    = -PCB_THICKNESS - BOTTOM_WALL_HEIGHT
  floor bottom = -PCB_THICKNESS - BOTTOM_WALL_HEIGHT - FLOOR_THICKNESS
"""

import FreeCAD
import Part
from params import (
    PCB_THICKNESS,
    TOLERANCE,
    WALL_THICKNESS,
    FLOOR_THICKNESS,
    BOTTOM_WALL_HEIGHT,
    STANDOFF_HEIGHT,
    STANDOFF_OUTER_R,
    INSERT_HOLE_D,
    INSERT_HOLE_DEPTH,
    RIDGE_WIDTH,
    RIDGE_HEIGHT,
    USB_WIDTH,
    USB_HEIGHT,
)
from pcb_data import MOUNTING_HOLES, MCU_Y_CENTER
from helpers import build_pcb_wire


def build_bottom_case():
    pcb_wire = build_pcb_wire()

    z_walls_top = -PCB_THICKNESS
    z_floor_top = z_walls_top - BOTTOM_WALL_HEIGHT
    z_floor_bottom = z_floor_top - FLOOR_THICKNESS

    inner_wire = pcb_wire.makeOffset2D(TOLERANCE)
    outer_wire = pcb_wire.makeOffset2D(TOLERANCE + WALL_THICKNESS)
    inner_face = Part.Face(inner_wire)
    outer_face = Part.Face(outer_wire)

    # Floor
    floor_solid = outer_face.extrude(FreeCAD.Vector(0, 0, FLOOR_THICKNESS))
    floor_solid.translate(FreeCAD.Vector(0, 0, z_floor_bottom))

    # Walls
    wall_face = outer_face.cut(inner_face)
    wall_solid = wall_face.extrude(FreeCAD.Vector(0, 0, BOTTOM_WALL_HEIGHT))
    wall_solid.translate(FreeCAD.Vector(0, 0, z_floor_top))

    case = floor_solid.fuse(wall_solid)

    # Ridge for top plate alignment
    ridge_inner_wire = pcb_wire.makeOffset2D(TOLERANCE + WALL_THICKNESS - RIDGE_WIDTH)
    ridge_inner_face = Part.Face(ridge_inner_wire)
    ridge_face = outer_face.cut(ridge_inner_face)
    ridge_solid = ridge_face.extrude(FreeCAD.Vector(0, 0, RIDGE_HEIGHT))
    ridge_solid.translate(FreeCAD.Vector(0, 0, z_walls_top))
    case = case.fuse(ridge_solid)

    # Standoffs + M2 heat-set insert holes
    posts = []
    holes = []
    for mx, my in MOUNTING_HOLES:
        pos = FreeCAD.Vector(mx, -my, z_floor_top)
        posts.append(Part.makeCylinder(STANDOFF_OUTER_R, STANDOFF_HEIGHT, pos))
        insert_z = z_floor_top + STANDOFF_HEIGHT - INSERT_HOLE_DEPTH
        holes.append(
            Part.makeCylinder(
                INSERT_HOLE_D / 2.0,
                INSERT_HOLE_DEPTH + 0.01,
                FreeCAD.Vector(mx, -my, insert_z),
            )
        )
    if posts:
        case = case.fuse(Part.Compound(posts))
    if holes:
        case = case.cut(Part.Compound(holes))

    # USB-C cutout on right wall
    bb = outer_wire.BoundBox
    usb_box = Part.makeBox(
        WALL_THICKNESS + TOLERANCE + 2,
        USB_WIDTH,
        USB_HEIGHT,
        FreeCAD.Vector(
            bb.XMax - WALL_THICKNESS - 1,
            -MCU_Y_CENTER - USB_WIDTH / 2.0,
            z_floor_top + BOTTOM_WALL_HEIGHT / 2.0 - USB_HEIGHT / 2.0,
        ),
    )
    case = case.cut(usb_box)

    return case.removeSplitter()
