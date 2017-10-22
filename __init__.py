# EMPTY!
from __future__ import print_function

try:
    import maya_ctrl as ctrl
except ImportError:
    raise RuntimeError("Software not currently supported.")

def main():
    ctrl.Window()
