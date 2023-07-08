"""
This file is for pyinstaller.

Path of this file should be added to the "runtime_hooks" parameter of main.spce to run this file before the exe file.
"""

import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'libs'))
