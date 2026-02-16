"""
nice!nano STEP importer.
Loads nice-nano.step from the same directory as this script
and positions it at the KiCad footprint location.
"""

import os
import FreeCAD
import Part

DIR = os.path.dirname(os.path.abspath(__file__))
NICENANO_STEP = os.path.join(DIR, "nice-nano.step")
STEP_SCALE = 0.6755


def import_nice_nano(doc):
    """Import nice!nano STEP into the given FreeCAD document."""

    if os.path.isfile(NICENANO_STEP):
        print(f"  [+] Loading nice!nano from {NICENANO_STEP}...")
        nano_shape = Part.Shape()
        nano_shape.read(NICENANO_STEP)

        mat = FreeCAD.Matrix()
        mat.scale(STEP_SCALE, STEP_SCALE, STEP_SCALE)
        nano_shape = nano_shape.transformGeometry(mat)

        fp_x = 176.75
        fp_y = 71.77 - 0.76 - 0.28
        fp_rot = -90

        placement = FreeCAD.Placement()
        placement.move(FreeCAD.Vector(fp_x, -fp_y, -3.6))
        rot_z = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), fp_rot)
        rot_y = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 180)
        placement.Rotation = rot_y.multiply(rot_z)
        nano_shape.Placement = placement

        nano_obj = doc.addObject("Part::Feature", "NiceNano")
        nano_obj.Shape = nano_shape
        try:
            nano_obj.ViewObject.ShapeColor = (0.8, 0.2, 0.2)
            nano_obj.ViewObject.Transparency = 0
        except Exception:
            pass

        bb = nano_shape.BoundBox
        print(
            f"       nice!nano bbox: {bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f} mm"
        )
        print("       (adjust placement in build.py if it doesn't align)")
    else:
        print(f"  [!] No nice!nano STEP found. Place it at: {NICENANO_STEP}")
