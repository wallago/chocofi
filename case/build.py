"""
Chocofi Keyboard Case - Build Script
=====================================
Creates 3 objects in the document tree:
  - Chocofi_PCB          (green)
  - Chocofi_TopCase      (blue)
  - Chocofi_BottomCase   (orange)
"""

import os
import sys
import importlib

if "__file__" in dir():
    _dir = os.path.dirname(os.path.abspath(__file__))
elif "f" in dir() and isinstance(f, str) and f.endswith(".py"):
    _dir = os.path.dirname(os.path.abspath(f))
else:
    _dir = os.getcwd()

if _dir not in sys.path:
    sys.path.insert(0, _dir)

# ── Force reload all modules (avoids stale cache between exec() runs) ──
import params
import pcb_data
import helpers
import pcb_model
import top_case_model
import bottom_case_model

for mod in [params, pcb_data, helpers, pcb_model, top_case_model, bottom_case_model]:
    importlib.reload(mod)

import FreeCAD
import Part

from pcb_model import build_pcb
from top_case_model import build_top_case
from bottom_case_model import build_bottom_case

# ── Build ──
print("Building Chocofi case...")
doc = FreeCAD.newDocument("ChocofiCase")

parts = [
    ("Chocofi_PCB", build_pcb, (0.10, 0.55, 0.15), 0),
    ("Chocofi_TopCase", build_top_case, (0.30, 0.50, 0.85), 30),
    ("Chocofi_BottomCase", build_bottom_case, (0.85, 0.50, 0.20), 30),
]

for i, (name, builder, color, transparency) in enumerate(parts, 1):
    print(f"  [{i}/3] {name}...")
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = builder()
    try:
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.Transparency = transparency
    except Exception:
        pass  # headless mode

doc.recompute()

# ── Export STEP ──
output_dir = _dir
for obj in doc.Objects:
    step_path = os.path.join(output_dir, f"{obj.Name}.step")
    Part.export([obj], step_path)
    print(f"  STEP -> {step_path}")

# ── Summary ──
bb = doc.getObject("Chocofi_BottomCase").Shape.BoundBox
print(f"\nDone! 3 objects in document 'ChocofiCase'")
print(f"  Bottom case bbox: {bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f} mm")
