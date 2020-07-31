
from pydm import Display
from os import path
import json
import logging
import sys
import pyqtgraph as pg

logger = logging.getLogger(__name__)

class Rtm(Display):
    def __init__(self, parent=None, args=None, macros=None, ui_filename=None):
        super(Rtm, self).__init__(parent=parent, args=args, macros=macros)
        self.setup_waveforms()
        self.set_y_range()

    def setup_waveforms(self):
        self.ui.beam_current_waveform.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)
        self.ui.beam_voltage_waveform.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)
        self.ui.rf_power_waveform.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)

    def set_y_range(self):
        self.ui.beam_current_waveform.plotItem.getViewBox().setAutoVisible()
        self.ui.beam_voltage_waveform.plotItem.getViewBox().setAutoVisible()
        self.ui.rf_power_waveform.plotItem.getViewBox().setAutoVisible()
        self.ui.beam_current_waveform.plotItem.getViewBox().setAutoPan(False, True)
        self.ui.beam_voltage_waveform.plotItem.getViewBox().setAutoPan(False, True)
        self.ui.rf_power_waveform.plotItem.getViewBox().setAutoPan(False, True)

        #pg.ViewBox.updateAutoRange
        #self.ui.beam_voltage_waveform.plotItem.getViewBox().setAutoRange(padding=0.2)
        #logger.info(self.ui.beam_current_waveform.pltItem.y_address())
        #self.waveformPlotBay1.plotItem.getViewBox().setMouseMode(pg.ViewBox.RectMode)


    def ui_filename(self):
        return 'rtm.ui'