import os
import sys

from pybattletank.__main__ import executable

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    os.chdir(sys._MEIPASS)

if __name__ == "__main__":
    executable()
