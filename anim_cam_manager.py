import maya.cmds as cmds
from PySide2.QtWidgets import QCheckBox, QGroupBox, QVBoxLayout, QLabel, QLineEdit, QGridLayout, QSpinBox, QWidget, \
    QPushButton

from anim_cam_manager_utils import extend_keyframe, duplicate_camera, set_keyframe_all_attr, copy_keyframes, \
    get_camera_name
from cam_entry import CameraEntry
from frame_spinbox import FrameSpinbox


class AnimaticCamManager(QWidget):
    def __init__(self, scale):

        super(AnimaticCamManager, self).__init__()

        ## PARAMETERS ##
        self.scale = scale
        self.setWindowTitle("Animatic Camera Window")
        self.warnings = []
        self.uber_cam = None

        # Params concerning the board.
        self.camera_entries = list()
        self.spinbox_widgets = list()
        self.cam_name_le = QLineEdit('UberCam')
        self.bake_cb = QCheckBox()
        # Don't create camera entries for default cameras.
        self.cameras_to_avoid = ['top', 'front', 'side', 'persp']

        # Create the camera entries
        self.set_camera_entries()

        # Create the window layout.
        self.init_gui()


    def init_gui(self):
        '''Create and add widgets to the window.'''

        self.setContentsMargins(5 * self.scale, 5 * self.scale, 5 * self.scale, 5 * self.scale)
        self.window_main_layout = QVBoxLayout()

        # Layout setup.
        settings_layout = QGridLayout()

        # Add widgets to the board
        if self.camera_entries:
            settings_layout.addWidget(QLabel("Camera To Create:"), 0, 0)
            settings_layout.addWidget(self.cam_name_le, 0, 1)

            settings_layout.addWidget(QLabel("Camera Name:"), 1, 0)
            settings_layout.addWidget(QLabel("In Frame:"), 1, 1)
            settings_layout.addWidget(QLabel("Out Frame:"), 1, 2)
            settings_layout.addWidget(QLabel("Include Cam:"), 1, 3)

        i = 0
        if not self.camera_entries:
            settings_layout.addWidget(QLabel("No cameras other than defaults in the scene."), 2, 0)
        else:
            for i, camera_entry in enumerate(self.camera_entries):
                for j, widget in enumerate(camera_entry.widgets):
                    settings_layout.addWidget(widget, i + 2, j)

                    # Connect widgets on the camera entries to affect all others when their state is changed.
                    if isinstance(widget, QCheckBox):
                        widget.stateChanged.connect(lambda: self.reset_widget_colours())
                    if isinstance(widget, FrameSpinbox):
                        widget.valueChanged.connect(lambda: self.reset_widget_colours())

            # Resets the spinboxes and updates colours respective of neighbouring boxes.
            self.reset_widget_colours()

            self.bake_cb.setChecked(True)
            settings_layout.addWidget(QLabel("Bake and extend frames?"), i + 3, 0)
            settings_layout.addWidget(self.bake_cb, i + 3, 1)

        settings_box = QGroupBox()
        settings_box.setLayout(settings_layout)

        # BOTTOM BUTTONS
        bottom_buttons_layout = QGridLayout()
        bottom_buttons_layout.setColumnMinimumWidth(0, 225 * self.scale)
        bottom_buttons_layout.setColumnMinimumWidth(1, 225 * self.scale)

        bottom_buttons_box = QGroupBox("", self)

        self.create_uber_cam_bt = QPushButton("Build Uber Camera", self)
        self.create_uber_cam_bt.clicked.connect(lambda: self.create_uber_cam())

        if not self.camera_entries:
            self.create_uber_cam_bt.setEnabled(False)

        self.refresh_window_bt = QPushButton("Refresh Window", self)
        self.refresh_window_bt.clicked.connect(lambda: self.refresh_window())

        bottom_buttons_layout.addWidget(self.create_uber_cam_bt, 0, 0)
        bottom_buttons_layout.addWidget(self.refresh_window_bt, 0, 1)

        bottom_buttons_box.setLayout(bottom_buttons_layout)

        # Add everything to the board
        self.setLayout(self.window_main_layout)
        self.window_main_layout.addWidget(settings_box)
        self.window_main_layout.addWidget(bottom_buttons_box)


    def reset_widget_colours(self):
        '''Update the widget colours, called by changes to the ui.'''

        # Reset the list.
        self.spinbox_widgets = list()

        for camera_entry in self.camera_entries:
            if camera_entry.to_include_cb.isChecked():
                for widget in camera_entry.widgets:
                    # Add function to track the colour if the widget is a QSpinBox.
                    if isinstance(widget, FrameSpinbox):
                        self.spinbox_widgets.append(widget)

        self.track_colour()

        for widget in self.spinbox_widgets:
            widget.update_colour()


    def track_colour(self):
        '''Set the prev and next spinboxes relative to the current one to correctly track the colour.'''

        for k, spinbox in enumerate(self.spinbox_widgets):

            # Reset spinboxes
            spinbox.prev_spinbox, spinbox.next_spinbox = None, None

            if len(self.spinbox_widgets) == 1:
                break
            if k != 0:
                spinbox.prev_spinbox = self.spinbox_widgets[k-1]
            if k != len(self.spinbox_widgets)-1:
                spinbox.next_spinbox = self.spinbox_widgets[k+1]


    def set_camera_entries(self):
        '''Create the camera entry classes.'''

        camera_entries = list()

        # List through the cameras in maya and classes containing camera info and widgets.
        for camera_name in self.get_cameras():
            camera_entries.append(CameraEntry(camera_name))

        self.camera_entries = camera_entries


    def get_cameras(self):
        '''Get the full maya camera name paths.'''

        scene_camera_full_names = cmds.ls(type=('camera'), l=True)
        camera_full_names = list()

        # Remove cameras to avoid from the list.
        for camera_full_name in scene_camera_full_names:
            camera_name = get_camera_name(camera_full_name)

            if camera_name not in self.cameras_to_avoid:
                camera_full_names.append(camera_full_name)

        return camera_full_names


    def filter_cameras(self):
        '''Filter out the cameras to include based on checkboxes and whether frame ranges will disrupt tool.'''

        cams_to_include = list()

        # Filter out cameras that are not checked in ui, or whose frame ranges conflict.
        for scene_camera in self.camera_entries:
            if not scene_camera.to_include_cb.isChecked():
                continue
            if scene_camera.in_frame_sb.value() > scene_camera.out_frame_sb.value():
                self.warnings.append(f"Ignoring {scene_camera.camera_name} as in frame greater than out frame.")
                continue
            cams_to_include.append(scene_camera)

        # Filter out cameras whose frame overlaps with the next.
        new_cams_to_include = list()

        # Filter out cameras whose frames overlap.
        for i, scene_camera in enumerate(cams_to_include):
            if not i == len(cams_to_include) - 1:
                next_cam = cams_to_include[i + 1]
                if scene_camera.out_frame_sb.value() >= next_cam.in_frame_sb.value():
                    self.warnings.append(f"Ignoring {scene_camera.camera_name} as out frame overlaps with next camera.")
                    continue
            new_cams_to_include.append(scene_camera)

        return new_cams_to_include


    def create_uber_cam(self):
        '''Create the uber cam based on the GUI inputs and camera entries.'''

        # Filter out the cameras from the camera entries to just the ones we need.
        cams_to_include = self.filter_cameras()

        # Simply duplicate the only camera as the uber camera if there is only one cam to include.
        if len(cams_to_include) == 1:
            new_cam_path = duplicate_camera(cams_to_include[0].camera_path)
            cmds.rename(new_cam_path, 'UberCam')
            return

        self.uber_cam = cmds.camera(name=self.cam_name_le.text())

        # Loop through the cameras and copy keyframes, add a warning if there are gaps in frame ranges between cameras.
        for i, scene_camera in enumerate(cams_to_include):
            if i == len(cams_to_include) - 1:
                self.copy_cam_keyframes(scene_camera, None)
            else:
                next_cam = cams_to_include[i + 1]
                # Append warning if the out frame of this camera is not the frame before in frame of the next.
                if scene_camera.out_frame_sb.value() + 1 != next_cam.in_frame_sb.value():
                    warning = "On at lease one occasion," \
                              " there are gaps of more than one frame between out frame and next in frame."
                    if warning not in self.warnings:
                        self.warnings.append(warning)
                self.copy_cam_keyframes(scene_camera, next_cam)

        # Display warnings if any.
        if self.warnings:
            warning_dialog = UberCamWarning(self.scale, self.warnings)
            warning_dialog.show()
            # Reset warnings.
            self.warnings = []

        self.close()


    def copy_cam_keyframes(self, scene_camera, next_cam):
        '''Copy the camera keyframes from the scene_camera to the uber_cam.'''

        # Duplicate cam as to not add keyframes to existing cam.
        new_cam_path = duplicate_camera(scene_camera.camera_path)
        set_keyframe_all_attr(new_cam_path, 0, False)

        start_time = scene_camera.in_frame_sb.value()
        end_time = scene_camera.out_frame_sb.value()

        # Insert keyframe at the start and end of the ui time.
        set_keyframe_all_attr(new_cam_path, start_time, True)
        set_keyframe_all_attr(new_cam_path, end_time, True)

        # If bake every frame is checked.
        if self.bake_cb.isChecked():
            # Insert keyframes for every frame in the ui range.
            for current_time in range(start_time, end_time):
                set_keyframe_all_attr(new_cam_path, current_time, True)
            # Extend the end of the cam animation to the beginning of the next camera.
            if next_cam:
                extend_keyframe(new_cam_path, end_time, next_cam.in_frame_sb.value() - end_time)
                copy_keyframes(new_cam_path, self.uber_cam[0], start_time, next_cam.in_frame_sb.value())
            else:
                copy_keyframes(new_cam_path, self.uber_cam[0], start_time, end_time)
        else:
            # Copy keyframes to uber.
            copy_keyframes(new_cam_path, self.uber_cam[0], start_time, end_time)

        # Delete the duplicate camera when we are done.
        cmds.delete(new_cam_path)


    def refresh_window(self):
        """Refresh the current window."""

        self.close()
        create_new_window()


class UberCamWarning(QWidget):
    def __init__(self, scale, warnings):
        '''List warnings.'''

        super(UberCamWarning, self).__init__()

        self.scale = scale
        self.setWindowTitle("Uber Cam Warning")

        self.setContentsMargins(5 * self.scale, 5 * self.scale, 5 * self.scale, 5 * self.scale)
        self.window_main_layout = QVBoxLayout()

        settings_layout = QGridLayout()
        settings_layout.setColumnMinimumWidth(0, 300 * self.scale)

        # Add warnings to board.
        i = 0
        for i, warning in enumerate(warnings):
            settings_layout.addWidget(QLabel(warning), i, 0)

        self.close_bt = QPushButton("Close", self)
        self.close_bt.clicked.connect(lambda: self.close_window())
        settings_layout.addWidget(self.close_bt, i+1, 0)

        # Window setup.
        settings_box = QGroupBox()
        settings_box.setLayout(settings_layout)
        self.setLayout(self.window_main_layout)
        self.window_main_layout.addWidget(settings_box)


    def close_window(self):
        """Close the current window."""

        self.close()


def create_new_window():
    new_window = AnimaticCamManager(0.5)
    new_window.show()

    return new_window


if __name__ == "__main__":
    create_new_window()
