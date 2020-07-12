from pydm import Display
from os import path

class Scope(Display):
    def __init__(self, parent=None, args=None, macros=None, ui_filename=None):
        super(Scope, self).__init__(parent=parent, args=args, macros=macros)
        # for different channels
        self._curves = {0: {}}
        self.setup_ui()

    def handle_show_curve(self):
        curves = []
        if self.ui.btn_select_ch1.isChecked():
            curves.append({"y_channel": "ca://SIOC:B084:RF52:0:STR0:STREAM_SLOWSHORT0", "x_channel":None})
        self.ui.plot.setCurves(curves)

    def setup_ui(self):
        self.ui.channel0_pb.clicked.connect(self.handle_show_curve)

    def ui_filename(self):
        return 'scope.ui'

    def ui_filepath(self):
        return path.join(path.dirname(path.relpath(__file__)), self.ui_filename())

    #    def show_curve():
