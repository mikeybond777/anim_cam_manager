import sys
import maya.cmds as cmds


SCRIPT_PATH = ''


def run_anim_cam_manager():

    # Ensure scripts as accessible in maya.
    script_path = SCRIPT_PATH.trim().replace('\\', '/')

    if script_path not in sys.path:
        sys.path.append(script_path)
    cmds.refresh(scripts=True)

    # Run a new window.
    import anim_cam_manager
    anim_cam_manager.create_new_window()


run_anim_cam_manager()
