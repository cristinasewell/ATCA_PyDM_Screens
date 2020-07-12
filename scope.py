from pydm import Display
from os import path
import json

class Scope(Display):
    def __init__(self, parent=None, args=None, macros=None, ui_filename=None):
        super(Scope, self).__init__(parent=parent, args=args, macros=macros)
        # for different channels
        device = self._macros.get("DEVICE")
        if device is not None:
            ioc = "ca://{}:".format(device)
        self._curves_bay0 = {0: {"y_channel": ioc+"STR0:STREAM_SLOWSHORT0", "x_channel": None, "name": "MyName", "color": "#55ffff", "lineStyle": 1, "lineWidth": 1, "symbol": None, "symbolSize": 10, "redraw_mode": 2}, 
                1: {"y_channel": ioc, "x_channel": None, "name": "MyName", "color": "#55ffff", "lineStyle": 1, "lineWidth": 1, "symbol": None, "symbolSize": 10, "redraw_mode": 2},
                2: {"y_channel": ioc, "x_channel": None, "name": "MyName", "color": "#55ffff", "lineStyle": 1, "lineWidth": 1, "symbol": None, "symbolSize": 10, "redraw_mode": 2}, 
                3: {"y_channel": ioc, "x_channel": None, "name": "MyName", "color": "#55ffff", "lineStyle": 1, "lineWidth": 1, "symbol": None, "symbolSize": 10, "redraw_mode": 2}}

        self._macros = macros
        self.setup_ui()
        #self.my_ch = {"y_channel": None, "x_channel": None, "name": "MyName", "color": "#55ffff", "lineStyle": 1, "lineWidth": 1, "symbol": None, "symbolSize": 10, "redraw_mode": 2}

    def macros(self):
        if self._macros is None:
            return {}
        return self._macros

    def handle_show_curve(self):
        curves = []
        channel = {}

        device = self._macros.get("DEVICE")
        if device is not None:
            ioc = "ca://{}:STR0:STREAM_SLOWSHORT0".format(device)

        #ioc = "ca://{}:STR0:STREAM_SLOWSHORT0".format(device)
        #self.my_ch["y_channel"] = ioc
        #self.my_ch["x_channel"] = ""
        #ch = json.dumps(self.my_ch)

        ch = json.dumps(self._curves_bay0.get(0))
        print("ioc ", ch)
        if self.ui.channel0_pb.isChecked():
            curves.append(ch)
            print(curves)
        #self.ui.plot.setCurves(curves)
        self.waveformPlotBay0.setCurves(curves)

    def setup_ui(self):
        self.ui.channel0_pb.clicked.connect(self.handle_show_curve)

    def ui_filename(self):
        return 'scope.ui'

    def ui_filepath(self):
        return path.join(path.dirname(path.relpath(__file__)), self.ui_filename())

    #    def show_curve():
