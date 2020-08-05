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
from qtpy.QtGui import QRegExpValidator, QIntValidator
from qtpy.QtWidgets import QMessageBox, QGridLayout, QPushButton

logger = logging.getLogger(__name__)


class AverageWindow(Display):
    def __init__(self, parent=None, args=None, macros=None, ui_filename=None):
        super(AverageWindow, self).__init__(parent=parent, args=args, macros=macros)
        self._macros = macros
        self.start = None
        self.end = None
        self.end_edit_line_setup()
        self.start_edit_line_setup()
        self.setup_ui()
        self.imaginary_curves = None
        self.real_curves = None
        self.pv_size = 4096
        self.win = []
        self.current_window_selection = None
        self.waveform_button_setup()

        self.pv_combo_box_selection = {
            0: 'I Window 0 - ICPXWND0',
            1: 'I Window 1 - ICPXWND1',
            2: 'I Window 2 - ICPXWND2',
            3: 'Q Window 0 - QCPXWND0',
            4: 'Q Window 1 - QCPXWND1',
            5: 'Q Window 2 - QCPXWND2'
        }
        self.ui.display_pv_label.setText(
            "Current PV: {}".format(self.pv_combo_box_selection[0]))

    def waveform_button_setup(self):
        self.waveform_button = WaveformButton()
        # this will change based on the channel ....
        self.waveform_button.channel = 'ca://SIOC:B084:RFTEST:0:ICPXWND0'
       # wave = np.ones(10) #sends a ndarray of ones
       # waveform_button.pressValue = wave
        self.waveform_button.setStyleSheet("background-color: #bc5f6a")
        self.waveform_button.setText("Write")
        self.ui.button_layout.addWidget(self.waveform_button)
        self.waveform_button.clicked.connect(self.write_to_pv)


    def setup_ui(self):
        self.ui.draw_window_pb.clicked.connect(self.plot_data)
        self.ui.window_select_cb.currentIndexChanged.connect(
            self.window_selection_changed)

    def define_complex_curves(self):
       # try:
        device = self._macros['DEVICE']
    #    if device:
        #ioc = "ca://{}:".format(device)
        ioc = 'ca://SIOC:B084:RFTEST:0:ICPXWND0'
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
       # self.ui.start_line_edit.returnPressed.connect(self.start_on_return_pressed)
        self.ui.start_line_edit.textChanged.connect(self.start_on_text_changed)

    def end_edit_line_setup(self):
       # self.ui.end_line_edit.returnPressed.connect(self.end_on_return_pressed)
        self.ui.end_line_edit.textChanged.connect(self.end_on_text_changed)

    def start_on_text_changed(self):
        self.ui.start_line_edit.setValidator(self.validate_input(self.ui.start_line_edit))
        #self.ui.start_line_edit.setStyleSheet("QLineEdit { border: red }")
        self.ui.error_label.setText("")

    def end_on_text_changed(self):
        self.ui.end_line_edit.setValidator(self.validate_input(self.ui.end_line_edit))
        self.ui.error_label.setText("")
    
    def validate_input(self, to_validate):
        # validate +- values, up to 12 chars for now, and up to 6 values after the .
        #reg_ex = QRegExp("^[+-]?[0-9]{1,12}(?:\.[0-9]{1,6})?$")
        #return QRegExpValidator(reg_ex, to_validate)
        # use QIntValidator
        return QIntValidator(to_validate)

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
    
    def get_pv_size(self):
        size = None
        str_size = str(self.ui.get_pv_size_label.text())
        if str_size:
            size =  int(str_size)
            self.pv_size = size
            logger.info("Pv window size: {}".format(size))
        return size

    def window_selection_changed(self):
        index = self.ui.window_select_cb.currentIndex()
        text_label = self.pv_combo_box_selection[index]
        self.ui.display_pv_label.setText("Current PV: {}".format(text_label))

    def plot_data(self):
        start = self.get_current_start()
        end = self.get_current_end()
        self.ui.average_window_wf.clear()

        pen = pg.mkPen(color=(153,255,153))

        if end and start:
            logger.info(type(end))
            logger.info(type(start))
            self.win = [0]*start + [1]*(end - start) + [0]*(self.pv_size - end)
            logger.info(type(self.win))
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
        logger.info("Writing to PV.....")
        wave = np.ones(10) #sends a ndarray of ones
        waveform_button.pressValue = wave

    def ui_filename(self):
        return 'define_average_window.ui'


class WaveformButton(PyDMPushButton):
    """
    Button to allow sending a ndarray to a PV
    """
    @property
    def pressValue(self):
        return self._pressValue

    @pressValue.setter
    def pressValue(self, value):
        self._pressValue = value

    def sendValue(self):
        self.send_value_signal[np.ndarray].emit(self.pressValue)
