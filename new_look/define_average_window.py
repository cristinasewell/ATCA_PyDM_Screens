from pydm import Display
from os import path
import json
import logging
import sys
import pyqtgraph as pg
import epics
import re

import numpy as np
from qtpy import QtCore, QtWidgets, QtGui
from pydm.widgets.pushbutton import PyDMPushButton

from qtpy.QtCore import QRegExp
from qtpy.QtGui import QRegExpValidator, QDoubleValidator
from qtpy.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)


class AverageWindow(Display):
    def __init__(self, parent=None, args=None, macros=None, ui_filename=None):
        super(AverageWindow, self).__init__(parent=parent, args=args, macros=macros)
        self._macros = macros
        self.start = None
        self.end = None
        self.end_edit_line_setup()
        self.start_edit_line_setup()
        self.ui.write_pb.clicked.connect(self.write_to_pv)
        self.ui.draw_window_pb.clicked.connect(self.plot_data)
        self.imaginary_curves = None
        self.real_curves = None
        logger.info(macros)
        self.pv_size = 4096
        self.win = []

    def define_complex_curves(self):
       # try:
        device = self._macros['DEVICE']
    #    if device:
        ioc = "ca://{}:".format(device)
        # avg window[0..2]
        # cmplx window[0..2]
        channels = [0, 1, 2]
        # 2 colors, one for imaginary one for real part
        colors = ["#55ffff", "#55ff7f"]
        imaginary_curves = {}
        real_curves = {}

        # real windows
        for ch in channels:  
            y_channel = "{}ICPXWND{}".format(
                ioc, ch)
            name = "ICPXWND{}".format(ch)

            real_curves[ch] = {
                "y_channel": y_channel,
                "x_channel": None,
                "name": name,
                "color": colors[0]
            }
        self.real_curves = real_curves
        # imaginary windows
        for ch in channels:  
            y_channel = "{}QCPXWND{}".format(
                ioc, ch)
            name = "QCPXWND{}".format(ch)

            imaginary_curves[ch] = {
                "y_channel": y_channel,
                "x_channel": None,
                "name": name,
                "color": colors[1]
            }
        self.imaginary_curves = imaginary_curves
        return imaginary_curves, real_curves
       # except:
        #    self.ui.error_label.setText("Something went wrong with the macro??...")
        #    logger.error("something went wrong...")
            #logger.error("You need to define a DEVICE macro ioc  - ex: -m 'DEVICE=MY_IOC' ")
            #sys.exit(1)
            # disble a button here - dissable the write button?

    def start_edit_line_setup(self):
        self.ui.start_line_edit.returnPressed.connect(self.start_on_return_pressed)
        self.ui.start_line_edit.textChanged.connect(self.start_on_text_changed)

    def end_edit_line_setup(self):
        self.ui.end_line_edit.returnPressed.connect(self.end_on_return_pressed)
        self.ui.end_line_edit.textChanged.connect(self.end_on_text_changed)

    def start_on_text_changed(self):
        self.ui.start_line_edit.setValidator(self.validate_input(self.ui.start_line_edit))
        #self.ui.start_line_edit.setStyleSheet("QLineEdit { border: red }")
        self.ui.error_label.setText("")

    def end_on_text_changed(self):
        self.ui.end_line_edit.setValidator(self.validate_input(self.ui.end_line_edit))
        self.ui.error_label.setText("")

    def start_on_return_pressed(self):
        """
        Slot to capture the input for the Start value.
        Called when return pressed
        """
        if self.ui.start_line_edit.text():
            str_value = str(self.ui.start_line_edit.text())
            self.start = int(str_value)

    def end_on_return_pressed(self):
        """
        Slot to capture the input for the End value.
        Called when return pressed
        """
        if self.ui.end_line_edit.text():
            str_value = str(self.ui.end_line_edit.text())
            self.end = int(str_value)
    
    def validate_input(self, to_validate):
        # validate +- values, up to 12 chars for now, and up to 6 values after the .
        reg_ex = QRegExp("^[+-]?[0-9]{1,12}(?:\.[0-9]{1,6})?$")
        return QRegExpValidator(reg_ex, to_validate)

    def set_window_size(self, start, stop):
        #self.ui.average_window_wf.plotItem.getViewBox().setYRange(start, stop, padding=0)
        pass

    def get_current_start(self):
        start = None
        str_value = str(self.ui.start_line_edit.text())
        if str_value:
            start = int(str_value)
        return start

    def get_current_end(self):
        end = None
        str_value = str(self.ui.end_line_edit.text())
        if str_value:
            end = int(str_value)
        return end

    def plot_data(self):
        start = self.get_current_start()
        end = self.get_current_end()
        self.ui.average_window_wf.clear()

        pen = pg.mkPen(color=(153,255,153))

        if end and start:
            logger.info(type(end))
            logger.info(type(start))
            self.win = [0]*start + [1]*(end-start) + [0]*(self.pv_size-end)
            self.ui.average_window_wf.plot(self.win, pen=pen)
        else:
            self.ui.error_label.setText("You must define start and end values..")

    def write_to_pv(self, checked):
        write_message = QMessageBox.question(
            self, ' Writing PV?', 'Write to PV?',
            QMessageBox.Yes | QMessageBox.No)
        if write_message == QMessageBox.Yes:
            self.write()
        else:
            pass
    
    def write(self):
        #self.plot_data()
        pass

        logger.info("Writing to PV.....")


    def ui_filename(self):
        return 'define_average_window.ui'

# app = QtWidgets.QApplication([])
# class WaveformButton(PyDMPushButton):
#     @property
#     def pressValue(self):
#         return self._pressValue
#     @pressValue.setter
#     def pressValue(self, value):
#         self._pressValue = value
#     def sendValue(self):
#         self.send_value_signal[np.ndarray].emit(self.pressValue)
# widget = WaveformButton()
# widget.channel = 'ca://MTEST:Waveform'
# wave = np.ones(10)
# widget.pressValue = wave
# #widget.show()
# #app.exec_()