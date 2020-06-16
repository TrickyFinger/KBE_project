import os.path

_module_dir = os.path.dirname(__file__)
AIRFOIL_DIR = os.path.join(_module_dir, 'airfoil_library', '')

from .airfoil import Airfoil
from .ref_frame import Frame

