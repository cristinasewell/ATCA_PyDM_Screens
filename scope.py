from pydm import Display
from os import path

class Scope(Display):
    def __init__(self, parent=None, args=None, macros=None, ui_filename=None):
        super(Scope, self).__init__(parent=parent, args=args, macros=macros)
        # for different channels
       # self._curves = {0: {}}
        self.setup_ui()

    def macros(self):
        is self._macros is None:
            return {}
        return self._macros

    def handle_show_curve(self):
        curves = []
        if self.ui.channel0_pb.isChecked():
            curves.append('{"y_channel": "ca://${DEVICE}:STR0:STREAM_SLOWSHORT0", "x_channel":""}')
        #self.ui.plot.setCurves(curves)
        self.waveformPlotBay0.plot.setCurves(curves)

    def setup_ui(self):
        self.ui.channel0_pb.clicked.connect(self.handle_show_curve)

    def ui_filename(self):
        return 'scope.ui'

    def ui_filepath(self):
        return path.join(path.dirname(path.relpath(__file__)), self.ui_filename())

    #    def show_curve():
