from pydm import Display
import json
import logging
import sys
import pyqtgraph as pg
import epics
import re

import numpy as np
from qtpy import QtCore, QtWidgets, QtGui
from pydm.widgets.pushbutton import PyDMPushButton

from qtpy.QtGui import QIntValidator
from qtpy.QtWidgets import QMessageBox, QGridLayout, QPushButton

logger = logging.getLogger(__name__)

class AverageWindow(Display):
    def __init__(self, parent=None, args=None, macros=None, ui_filename=None):
        super(AverageWindow, self).__init__(parent=parent, args=args, macros=macros)
        self._macros = macros
        self.start = None
        self.end = None
        self._curves = {}
        self.define_complex_curves()
        self.setup_ui()

        self.end_edit_line_setup()
        self.start_edit_line_setup()
        self.complex_curves = None
        self.pv_size = 4096
        self.win = []
        self.pv = None
        self.curve = None
        self.current_pv = None
        self.current_window_selection = None
        self.waveform_button_setup()


    def setup_ui(self):
        self.ui.draw_window_pb.clicked.connect(self.plot_data)
        self.ui.get_waveform_pb.clicked.connect(self.handle_show_curves)

    def define_complex_curves(self):
        try:
            device = self._macros['DEVICE']
            number = self._macros['N']

            if device and number:
                ioc = "ca://{}:".format(device)

                iq = [0, 1]
                iq_label =['I', 'Q']
                colors = ["#55ffff", "#5500ff"]

                self._curves = {}
                for i_q, pv in enumerate(iq):
                    curves = {}
                    y_channel = "{}{}CPXWND{}".format(
                        ioc, iq_label[i_q], number
                    )
                    name = "{}CPXWND{}".format(
                        iq_label[i_q], number)
                
                    style = {
                            "lineStyle": 1,
                            "lineWidth": 1,
                            "symbol": 0,
                            "symbolSize": 4,
                            "redraw_mode": 2
                            }

                    curves = {
                            "y_channel": y_channel,
                            "x_channel": None,
                            "name": name,
                            "color": colors[i_q],
                            "lineStyle": 1,
                            "lineWidth": 1,
                            "symbol": 0,
                            "symbolSize": 4,
                            "redraw_mode": 2
                            }
                    self._curves[i_q] = curves
                logger.info(self._curves)
        except:
            self.ui.error_label.setText("Something went wrong with the macro??...")
            logger.error("You need to define a DEVICE macro ioc  - ex: -m 'DEVICE=MY_IOC' ")
            # disble a button here - dissable the write button?

    def handle_show_curves(self):
        #self.ui.average_window_wf.clear()
        curves = []
        if self._curves:
            for indx in self._curves:
                c_pv = json.dumps(self._curves[indx])
                curves.append(c_pv)
                logger.info('plotting curve: {}'.format(c_pv))
            self.average_window_wf.setCurves(curves)

    def waveform_button_setup(self):
        self.waveform_button = WaveformButton()
        self.waveform_button.setStyleSheet("background-color: #bc5f6a")
        self.waveform_button.setText("Write")
        self.ui.button_layout.addWidget(self.waveform_button)
        self.waveform_button.clicked.connect(self.write_to_pv)

        if self.pv:
            self.waveform_button.channel = self.pv
            logger.info(self.pv)
            wave = np.array(self.win)
            self.waveform_button.pressValue = wave
        else:
            self.ui.error_label.setText("You must define a window first.")


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
        self.ui.average_window_wf.clear()

    def plot_data(self):
        start = self.get_current_start()
        end = self.get_current_end()
        self.ui.average_window_wf.clear()

        pen = pg.mkPen(color=(153,255,153))

        if end and start:
            self.win = [0]*start + [1]*(end - start) + [0]*(self.pv_size - end)
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
