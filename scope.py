from pydm import Display
from os import path
import json
import logging

logger = logging.getLogger(__name__)

class Scope(Display):
    def __init__(self, parent=None, args=None, macros=None, ui_filename=None):
        super(Scope, self).__init__(parent=parent, args=args, macros=macros)
        self._macros = macros
        self._curves = self.define_curves()
        self.setup_ui()

    def macros(self):
        if self._macros is None:
            return {}
        return self._macros

    def define_curves(self):
        try:
            device = self._macros.get("DEVICE")
            if device is not None:
                ioc = "ca://{}:".format(device)
        
                curves = {
                    0: {"y_channel": ioc+"STR0:STREAM_SLOWSHORT0",
                        "x_channel": None, "name": "CH 0", "color": "#55ffff",
                        "lineStyle": 1, "lineWidth": 1, "symbol": None,
                        "symbolSize": 10, "redraw_mode": 2},

                    1: {"y_channel": ioc+"STR0:STREAM_SLOWSHORT1",
                        "x_channel": None, "name": "CH 1", "color": "#55ff7f",
                        "lineStyle": 1, "lineWidth": 1, "symbol": None,
                        "symbolSize": 10, "redraw_mode": 2},

                    2: {"y_channel": ioc+"STR0:STREAM_SLOWSHORT2",
                        "x_channel": None, "name": "CH 2", "color": "#ffff7f",
                        "lineStyle": 1, "lineWidth": 1, "symbol": None,
                        "symbolSize": 10, "redraw_mode": 2},

                    3: {"y_channel": ioc+"STR0:STREAM_SLOWSHORT3",
                        "x_channel": None, "name": "CH 3", "color": "#ffaa7f",
                        "lineStyle": 1, "lineWidth": 1, "symbol": None, 
                        "symbolSize": 10, "redraw_mode": 2}, 
                    
                    4: {"y_channel": ioc+"STR1:STREAM_SLOWSHORT0",
                        "x_channel": None, "name": "CH 0", "color": "#55ffff",
                        "lineStyle": 1, "lineWidth": 1, "symbol": None,
                        "symbolSize": 10, "redraw_mode": 2},

                    5: {"y_channel": ioc+"STR1:STREAM_SLOWSHORT1",
                        "x_channel": None, "name": "CH 1", "color": "#55ff7f",
                        "lineStyle": 1, "lineWidth": 1, "symbol": None,
                        "symbolSize": 10, "redraw_mode": 2},

                    6: {"y_channel": ioc+"STR1:STREAM_SLOWSHORT2",
                        "x_channel": None, "name": "CH 2", "color": "#ffff7f",
                        "lineStyle": 1, "lineWidth": 1, "symbol": None,
                        "symbolSize": 10, "redraw_mode": 2},

                    7: {"y_channel": ioc+"STR1:STREAM_SLOWSHORT3",
                        "x_channel": None, "name": "CH 3", "color": "#ffaa7f",
                        "lineStyle": 1, "lineWidth": 1, "symbol": None, 
                        "symbolSize": 10, "redraw_mode": 2}}
                return curves    
        except:
            logger.error("You need to define a DEVICE ioc!")
            return

    def handle_show_curve(self):
        # put them in the correct json format
        for curve in self._curves:
            self._curves[curve] = json.dumps(self._curves.get(curve))

        # bay 0
        if self.ui.b0_channel0_pb.isChecked():
            self.waveformPlotBay0.setCurves(self._curves.get(0))
        if self.ui.b0_channel1_pb.isChecked():
            self.waveformPlotBay0.setCurves(self._curves.get(1))
        if self.ui.b0_channel2_pb.isChecked():
            self.waveformPlotBay0.setCurves(self._curves.get(2))
        if self.ui.b0_channel3_pb.isChecked():
            self.waveformPlotBay0.setCurves(self._curves.get(3))
        # bay 1
        if self.ui.b1_channel0_pb.isChecked():
            self.waveformPlotBay0.setCurves(self._curves.get(4))
        if self.ui.b1_channel1_pb.isChecked():
            self.waveformPlotBay0.setCurves(self._curves.get(5))
        if self.ui.b1_channel2_pb.isChecked():
            self.waveformPlotBay0.setCurves(self._curves.get(6))
        if self.ui.b1_channel3_pb.isChecked():
            self.waveformPlotBay0.setCurves(self._curves.get(7))

    def setup_ui(self):
        # bay 0
        self.ui.b0_channel0_pb.clicked.connect(self.handle_show_curve)
        self.ui.b0_channel1_pb.clicked.connect(self.handle_show_curve)
        self.ui.b0_channel2_pb.clicked.connect(self.handle_show_curve)
        self.ui.b0_channel3_pb.clicked.connect(self.handle_show_curve)
        # bay 1
        self.ui.b1_channel0_pb.clicked.connect(self.handle_show_curve)
        self.ui.b1_channel1_pb.clicked.connect(self.handle_show_curve)
        self.ui.b1_channel2_pb.clicked.connect(self.handle_show_curve)
        self.ui.b1_channel3_pb.clicked.connect(self.handle_show_curve)

    def ui_filename(self):
        return 'scope.ui'

    def ui_filepath(self):
        return path.join(path.dirname(path.relpath(__file__)), self.ui_filename())
