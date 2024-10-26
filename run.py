import sys
import maya.cmds as cmds


SCRIPT_PATH = 'C:/Users/mikey/PycharmProjects/animatic_cam_manager/'


if SCRIPT_PATH not in sys.path:
    sys.path.append()
cmds.refresh(scripts=True)

import anim_cam_manager

anim_cam_manager.create_new_window()
