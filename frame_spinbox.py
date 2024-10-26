from PySide2.QtWidgets import QSpinBox

class FrameSpinbox(QSpinBox):
    def __init__(self, is_in_frame):

        super(FrameSpinbox, self).__init__()
        self.setRange(0, 10000)
        self.setValue(1001)

        self.prev_spinbox = None
        self.next_spinbox = None
        self.is_in_frame = is_in_frame

        # Possible background colours.
        self.red = "color: rgb(0,0,0); background-color: rgb(180, 125,125)"
        self.green = "color: rgb(0,0,0); background-color: rgb(125, 180, 125)"
        self.orange = "color: rgb(0,0,0); background-color: rgb(180, 180, 125)"
        self.grey = "color: rgb(0,0,0); background-color: rgb(125, 125, 125)"


    def update_colour(self):
        '''Update the background colour of the widget.'''

        green_potential = False

        # Needs to be red if in frame is greater than out, orange if gap between itself and prev is more than 1 frame.
        if self.is_in_frame:
            if self.prev_spinbox:
                if self.value() == self.prev_spinbox.value() + 1:
                    green_potential = True
            else:
                green_potential = True
            if self.next_spinbox:
                if self.value() <= self.next_spinbox.value():
                    if green_potential:
                        self.setStyleSheet(self.green)
                    else:
                        self.setStyleSheet(self.orange)
                else:
                    self.setStyleSheet(self.red)
        else:
            # Needs to be red if less than in frame, orange if gap between itself and next is more than 1 frame.
            if self.next_spinbox:
                if self.value() == self.next_spinbox.value() - 1:
                    green_potential = True
                if self.value() >= self.next_spinbox.value():
                    self.setStyleSheet(self.red)
                    return
            else:
                green_potential = True
            if self.prev_spinbox:
                if self.value() >= self.prev_spinbox.value():
                    if green_potential:
                        self.setStyleSheet(self.green)
                    else:
                        self.setStyleSheet(self.orange)
                else:
                    self.setStyleSheet(self.red)