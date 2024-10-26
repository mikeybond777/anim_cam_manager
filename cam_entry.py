from PySide2.QtGui import QFont
from PySide2.QtWidgets import QCheckBox, QLabel

from anim_cam_manager_utils import get_camera_name, get_keyframes
from frame_spinbox import FrameSpinbox


class CameraEntry():
    def __init__(self, camera_full_name):

        self.camera_full_name = camera_full_name
        self.camera_name = get_camera_name(camera_full_name)
        self.camera_path = self.get_camera_path()
        self.camera_num = self.get_camera_number()
        self.keys = list()

        # WIDGETS
        self.widgets = list()

        # Cam name label.
        self.camera_name_la = QLabel(self.camera_name)
        bold_font = QFont()
        bold_font.setBold(True)
        self.camera_name_la.setFont(bold_font)

        self.in_frame_sb = FrameSpinbox(True)
        self.out_frame_sb = FrameSpinbox(False)
        self.to_include_cb = QCheckBox()
        self.to_include_cb.setChecked(True)
        self.to_include_cb.stateChanged.connect(lambda: self.set_widgets_state())

        self.set_def_frame_range()
        self.set_default_widgets()


    def set_widgets_state(self):
        '''Update the widget states when changing the checkbox.'''

        widget_state = self.to_include_cb.isChecked()

        self.in_frame_sb.setEnabled(widget_state)
        self.out_frame_sb.setEnabled(widget_state)

        if not widget_state:
            self.in_frame_sb.setStyleSheet(self.in_frame_sb.grey)
            self.out_frame_sb.setStyleSheet(self.out_frame_sb.grey)


    def get_camera_number(self):
        '''Get the camera number.'''

        num_list = list()

        for char in self.camera_name:
            if char.isdigit():
                num_list.append(char)

        camera_number = int(''.join(num_list))

        return camera_number


    def get_camera_path(self):
        '''Get the path of the camera, not including shape.'''

        cam_path_split = self.camera_full_name.split('|')
        cam_path = ''

        for i, cam_path_piece in enumerate(cam_path_split):
            if i != len(cam_path_split)-1:
                cam_path += cam_path_piece

        return cam_path


    def set_def_frame_range(self):
        '''Set the default cam frame range.'''

        cam_keyframes = get_keyframes(self.camera_path)

        if cam_keyframes:
            self.in_frame_sb.setValue(min(cam_keyframes))
            self.out_frame_sb.setValue(max(cam_keyframes))


    def set_default_widgets(self):
        '''Append widgets to widgets param.'''

        # Reset widgets.
        self.widgets = list()

        self.widgets.append(self.camera_name_la)
        self.widgets.append(self.in_frame_sb)
        self.widgets.append(self.out_frame_sb)
        self.widgets.append(self.to_include_cb)
