from pydm import Display
from os import path
import json
import logging
import sys
import pyqtgraph as pg

logger = logging.getLogger(__name__)

class Scope(Display):
    def __init__(self, parent=None, args=None, macros=None, ui_filename=None):
        super(Scope, self).__init__(parent=parent, args=args, macros=macros)
        self._macros = macros
        self._curves = None
        self._dotted_curves = None
        self.define_curves()
        self.define_dotted_curves()

        self.setup_ui()
     #   self.ui.bay0Mode0_rb.setChecked(True)
      #  self.ui.bay1Mode0_rb.setChecked(True)
        
        self.bay0_dotted = True
        self.bay1_dotted = True
        self.bay0_line= False
        self.bay1_line = False

    def macros(self):
        if self._macros is None:
            return {}
        return self._macros

    def define_dotted_curves(self):
        try:
            device = self._macros["DEVICE"]
            if device:
                ioc = "ca://{}:".format(device)
        
                self._dotted_curves = {
                    0: {"y_channel": ioc+"STR0:STREAM_SLOWSHORT0",
                        "x_channel": None, "name": "CH 0", "color": "#55ffff",
                        "lineStyle": 0, "lineWidth": 1, "symbol": 0,
                        "symbolSize": 4, "redraw_mode": 2},

                    1: {"y_channel": ioc+"STR0:STREAM_SLOWSHORT1",
                        "x_channel": None, "name": "CH 1", "color": "#55ff7f",
                        "lineStyle": 0, "lineWidth": 1, "symbol": 0,
                        "symbolSize": 4, "redraw_mode": 2},

                    2: {"y_channel": ioc+"STR0:STREAM_SLOWSHORT2",
                        "x_channel": None, "name": "CH 2", "color": "#ffff7f",
                        "lineStyle": 0, "lineWidth": 1, "symbol": 0,
                        "symbolSize": 4, "redraw_mode": 2},

                    3: {"y_channel": ioc+"STR0:STREAM_SLOWSHORT3",
                        "x_channel": None, "name": "CH 3", "color": "#ffaa7f",
                        "lineStyle": 0, "lineWidth": 1, "symbol": 0, 
                        "symbolSize": 4, "redraw_mode": 2}, 
                    
                    4: {"y_channel": ioc+"STR1:STREAM_SLOWSHORT0",
                        "x_channel": None, "name": "CH 0", "color": "#55ffff",
                        "lineStyle": 0, "lineWidth": 1, "symbol": 0,
                        "symbolSize": 4, "redraw_mode": 2},

                    5: {"y_channel": ioc+"STR1:STREAM_SLOWSHORT1",
                        "x_channel": None, "name": "CH 1", "color": "#55ff7f",
                        "lineStyle": 0, "lineWidth": 1, "symbol": 0,
                        "symbolSize": 4, "redraw_mode": 2},

                    6: {"y_channel": ioc+"STR1:STREAM_SLOWSHORT2",
                        "x_channel": None, "name": "CH 2", "color": "#ffff7f",
                        "lineStyle": 0, "lineWidth": 1, "symbol": 0,
                        "symbolSize": 4, "redraw_mode": 2},

                    7: {"y_channel": ioc+"STR1:STREAM_SLOWSHORT3",
                        "x_channel": None, "name": "CH 3", "color": "#ffaa7f",
                        "lineStyle": 0, "lineWidth": 1, "symbol": 0, 
                        "symbolSize": 4, "redraw_mode": 2}}    
        except:
            logger.error("You need to define a DEVICE macro ioc  - ex: -m 'DEVICE=MY_IOC' ")
            sys.exit(1)

    def define_curves(self):
        try:
            device = self._macros["DEVICE"]
            if device:
                ioc = "ca://{}:".format(device)
        
                self._curves = {
                    0: {"y_channel": ioc+"STR0:STREAM_SLOWSHORT0",
                        "x_channel": None, "name": "CH 0", "color": "#55ffff",
                        "lineStyle": 1, "lineWidth": 1, "symbol": 0,
                        "symbolSize": 4, "redraw_mode": 2},

                    1: {"y_channel": ioc+"STR0:STREAM_SLOWSHORT1",
                        "x_channel": None, "name": "CH 1", "color": "#55ff7f",
                        "lineStyle": 1, "lineWidth": 1, "symbol": 0,
                        "symbolSize": 4, "redraw_mode": 2},

                    2: {"y_channel": ioc+"STR0:STREAM_SLOWSHORT2",
                        "x_channel": None, "name": "CH 2", "color": "#ffff7f",
                        "lineStyle": 1, "lineWidth": 1, "symbol": 0,
                        "symbolSize": 4, "redraw_mode": 2},

                    3: {"y_channel": ioc+"STR0:STREAM_SLOWSHORT3",
                        "x_channel": None, "name": "CH 3", "color": "#ffaa7f",
                        "lineStyle": 1, "lineWidth": 1, "symbol": 0, 
                        "symbolSize": 4, "redraw_mode": 2}, 
                    
                    4: {"y_channel": ioc+"STR1:STREAM_SLOWSHORT0",
                        "x_channel": None, "name": "CH 0", "color": "#55ffff",
                        "lineStyle": 1, "lineWidth": 1, "symbol": 0,
                        "symbolSize": 4, "redraw_mode": 2},

                    5: {"y_channel": ioc+"STR1:STREAM_SLOWSHORT1",
                        "x_channel": None, "name": "CH 1", "color": "#55ff7f",
                        "lineStyle": 1, "lineWidth": 1, "symbol": 0,
                        "symbolSize": 4, "redraw_mode": 2},

                    6: {"y_channel": ioc+"STR1:STREAM_SLOWSHORT2",
                        "x_channel": None, "name": "CH 2", "color": "#ffff7f",
                        "lineStyle": 1, "lineWidth": 1, "symbol": 0,
                        "symbolSize": 4, "redraw_mode": 2},

                    7: {"y_channel": ioc+"STR1:STREAM_SLOWSHORT3",
                        "x_channel": None, "name": "CH 3", "color": "#ffaa7f",
                        "lineStyle": 1, "lineWidth": 1, "symbol": 0, 
                        "symbolSize": 4, "redraw_mode": 2}}    
        except:
            logger.error("You need to define a DEVICE macro ioc  - ex: -m 'DEVICE=MY_IOC' ")
            sys.exit(1)

    def handle_show_curve(self):
        # bay 0
        b0_curves = []
        if self._curves:
            if self.ui.b0_channel0_pb.isChecked():
                if self.bay0_line:
                    ch = json.dumps(self._curves.get(0))
                    b0_curves.append(ch)
                else:
                    ch = json.dumps(self._dotted_curves.get(0))
                    b0_curves.append(ch)
            if self.ui.b0_channel1_pb.isChecked():
                if self.bay0_line:
                    ch = json.dumps(self._curves.get(1))
                    b0_curves.append(ch)
                else:
                    ch = json.dumps(self._dotted_curves.get(1))
                    b0_curves.append(ch)
            if self.ui.b0_channel2_pb.isChecked():
                if self.bay0_line:
                    ch = json.dumps(self._curves.get(2))
                    b0_curves.append(ch)
                else:
                    ch = json.dumps(self._dotted_curves.get(2))
                    b0_curves.append(ch)
            if self.ui.b0_channel3_pb.isChecked():
                if self.bay0_line:
                    ch = json.dumps(self._curves.get(3))
                    b0_curves.append(ch)
                else:
                    ch = json.dumps(self._dotted_curves.get(3))
                    b0_curves.append(ch)

            self.waveformPlotBay0.setCurves(b0_curves)
            
        # bay 1
        b1_curves = []
        # if curves...
        if self.ui.b1_channel0_pb.isChecked():
            if self.bay1_line:        
                ch = json.dumps(self._curves.get(4))
                b1_curves.append(ch)
            else:
                ch = json.dumps(self._dotted_curves.get(4))
                b1_curves.append(ch)
        if self.ui.b1_channel1_pb.isChecked():
            if self.bay1_line:
                ch = json.dumps(self._curves.get(5))
                b1_curves.append(ch)
            else:
                ch = json.dumps(self._dotted_curves.get(5))
                b1_curves.append(ch)
        if self.ui.b1_channel2_pb.isChecked():
            if self.bay1_line:
                ch = json.dumps(self._curves.get(6))
                b1_curves.append(ch)
            else:
                ch = json.dumps(self._dotted_curves.get(6))
                b1_curves.append(ch)
        if self.ui.b1_channel3_pb.isChecked():
            if self.bay1_line:
                ch = json.dumps(self._curves.get(7))
                b1_curves.append(ch)
            else:
                ch = json.dumps(self._dotted_curves.get(7))
                b1_curves.append(ch)
        self.waveformPlotBay1.setCurves(b1_curves)
    
    def setup_curve_selection_mode(self):
        self.waveform0Ch0.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)
        self.waveform0Ch1.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)
        self.waveform0Ch2.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)
        self.waveform0Ch3.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)
        self.waveform1Ch0.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)
        self.waveform1Ch1.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)
        self.waveform1Ch2.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)
        self.waveform1Ch3.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)
        self.waveformPlotBay0.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)
        self.waveformPlotBay1.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)

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
        # modes
        self.ui.bay0Mode0_rb.clicked.connect(self.setup_mode)
        self.ui.bay0Mode1_rb.clicked.connect(self.setup_mode)
        self.ui.bay1Mode0_rb.clicked.connect(self.setup_mode)
        self.ui.bay1Mode1_rb.clicked.connect(self.setup_mode)

    def setup_mode(self):
        if self.ui.bay0Mode0_rb.isChecked():
            self.bay0_dotted = True
            self.bay0_line = False
        elif self.ui.bay0Mode1_rb.isChecked():
            self.bay0_line = True
            self.bay0_dotted = False

        if self.ui.bay1Mode0_rb.isChecked():
            self.bay1_dotted = True
            self.bay1_line = False
        elif self.ui.bay1Mode1_rb.isChecked():
            self.bay1_line = True
            self.bay1_dotted = False

    def ui_filename(self):
        try:
            device = self._macros["DEVICE"]
            if device:
                return 'scope.ui'
        except:
            logger.error("Please provide a valid macro for the IOC - ex: 'DEVICE=MY_IOC' ")
            sys.exit(1)

    def ui_filepath(self):
        return path.join(path.dirname(path.relpath(__file__)), self.ui_filename())
