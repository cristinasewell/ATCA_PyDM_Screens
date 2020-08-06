from pydm import Display
import json
import logging
import sys
import pyqtgraph as pg
import epics
import re
from functools import partial

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

        self._curves = {}
        self.define_complex_curves()
        self.setup_ui()
        self.edit_line_setup()

        self.i_win = []
        self.q_win = []
        self._i_pv = None
        self._q_pv = None

        self._curve_i = None
        self._curve_q = None

        self.waveform_buttons_setup()

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
                colors = ["#ff557f", "#5500ff"]

                self._curves = {}
                for i_q, pv in enumerate(iq):
                    curves = {}
                    y_channel = "{}{}CPXWND{}".format(
                        ioc, iq_label[i_q], str(number)
                    )
                    name = "{}CPXWND{}".format(
                        iq_label[i_q], number)

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

    def waveform_buttons_setup(self):
        self.real_button = PyDMPushButton() #WaveformButton()
        self.imm_button = PyDMPushButton() #WaveformButton()
        self.real_button.setStyleSheet("background-color: #bc5f6a")
        self.imm_button.setStyleSheet("background-color: #bc5f6a")
        self.real_button.setText("Write I PV")
        self.imm_button.setText("Write Q PV")
        self.ui.button_layout.addWidget(self.real_button)
        self.ui.button_layout.addWidget(self.imm_button)
        # send a value of 0 for i and 1 for q
        # to determine what pv should be sent
        #self.real_button.clicked.connect(partial(self.write_to_pv, 0))
        #self.imm_button.clicked.connect(partial(self.write_to_pv, 1))
        #self.real_button.released.connect(partial(self.write_to_pv, 0))
        #self.imm_button.released.connect(partial(self.write_to_pv, 1))
        self.real_button.pressed.connect(self.write_i_pv)
        self.imm_button.pressed.connect(self.write_q_pv)

        real_curve = self._curves[0]    
        i_pv = real_curve["y_channel"]
        self.ui.real_button.channel = i_pv

        imm_curve = self._curves[1]
        q_pv = imm_curve["y_channel"]
        self.imm_button.channel = q_pv

    def edit_line_setup(self):
        self.ui.start_line_edit.textChanged.connect(self.start_on_text_changed)
        self.ui.end_line_edit.textChanged.connect(self.end_on_text_changed)
        self.ui.start_line_edit_q.textChanged.connect(self.start_on_text_changed_q)
        self.ui.end_line_edit_q.textChanged.connect(self.end_on_text_changed_q)

    def start_on_text_changed(self):
        self.ui.start_line_edit.setValidator(self.validate_input(self.ui.start_line_edit))
        self.ui.error_label.setText("")

    def end_on_text_changed(self):
        self.ui.end_line_edit.setValidator(self.validate_input(self.ui.end_line_edit))
        self.ui.error_label.setText("")

    def start_on_text_changed_q(self):
        self.ui.start_line_edit_q.setValidator(self.validate_input(self.ui.start_line_edit_q))
        self.ui.error_label.setText("")

    def end_on_text_changed_q(self):
        self.ui.end_line_edit_q.setValidator(self.validate_input(self.ui.end_line_edit_q))
        self.ui.error_label.setText("")
    
    def validate_input(self, to_validate):
        # use QIntValidator
        # might need more validation here?
        return QIntValidator(to_validate)

    def get_current_i_start(self):
        start = None
        str_value = str(self.ui.start_line_edit.text())
        if str_value:
            start = int(str_value)
        return start

    def get_current_i_end(self):
        end = None
        str_value = str(self.ui.end_line_edit.text())
        if str_value:
            end = int(str_value)
        return end

    def get_current_q_start(self):
        start = None
        str_value = str(self.ui.start_line_edit_q.text())
        if str_value:
            start = int(str_value)
        return start

    def get_current_q_end(self):
        end = None
        str_value = str(self.ui.end_line_edit_q.text())
        if str_value:
            end = int(str_value)
        return end
    
    def get_i_pv_size(self):
        size = None
        str_size = str(self.ui.get_pv_size_i.text())
        logger.info('size-----: {}'.format(str_size))
        if str_size:
            size =  int(str_size)
            logger.info("Pv window size: {}".format(size))
        return size
    
    def get_q_pv_size(self):
        size = None
        str_size = str(self.ui.get_pv_size_q.text())
        logger.info('size-----: {}'.format(str_size))
        if str_size:
            size =  int(str_size)
            logger.info("Pv window size: {}".format(size))
        return size

    def plot_data(self):
        i_start = self.get_current_i_start()
        i_end = self.get_current_i_end()
        i_size = self.get_i_pv_size()
        i_size = 4096

        logger.info('I start: {}, end: {}'.format(i_start, i_end))

        q_start = self.get_current_q_start()
        q_end = self.get_current_q_end()
        q_size = self.get_q_pv_size()
        q_size = 4096

        logger.info('Q start: {}, end: {}'.format(q_start, q_end))

        self.ui.average_window_wf.clear()

        i_pen = pg.mkPen(color=(255,85,127))
        q_pen = pg.mkPen(color=(85,0,255))

        if i_end and i_start and i_size:
            if (i_start >= i_end) or (i_end >= i_size):
                self.ui.error_label.setText(
                    "Not a valid window size."
                    "Please make sure the start < end, or end < pv_size"
                     )
            else:
                self.i_win = [0]*i_start + [1]*(i_end - i_start) + [0]*(i_size - i_end)
                self._curve_i = self.i_win
                self.ui.average_window_wf.plot(self.i_win, pen=i_pen)
              #  m = pg.transformToArray()[:2]
                #logger.info('the window.......'.format(self.i_win))
        else:
            self.ui.error_label.setText("You must define start and end values for I..")

        if q_end and q_start and q_size:
            if (q_start >= q_end) or (q_end >= q_size):
                self.ui.error_label.setText(
                    "Not a valid window size."
                    "Please make sure the start < end, or end < pv_size"
                     )
            else:
                self.q_win = [0]*q_start + [1]*(q_end - q_start) + [0]*(q_size - q_end)
                self._curve_q = self.q_win
                self.ui.average_window_wf.plot(self.q_win, pen=q_pen)
                logger.info('the window.......'.format(self.q_win))
        else:
            self.ui.error_label.setText("You must define start and end values for Q..")

    def write_to_pv(self, n):
        # n == 0 -> real pv
        if n == 0:
            write_message = QMessageBox.question(
                self, ' Writing I PV?', 'Write to I PV?',
                QMessageBox.Yes | QMessageBox.No)
            if write_message == QMessageBox.Yes:
                self.write_i_pv()
            else:
                pass
        # n == 1 -> imm pv
        elif n == 1:
            write_message = QMessageBox.question(
                self, ' Writing Q PV?', 'Write to Q PV?',
                QMessageBox.Yes | QMessageBox.No)
            if write_message == QMessageBox.Yes:
                self.write_q_pv()
            else:
                pass
    
    def write_i_pv(self):
        #real_curve = self._curves[0]    
       # i_pv = real_curve["y_channel"]
        #logger.info(i_pv)
        if self._curve_i:
           # self.ui.real_button.channel = i_pv
            i_wave = np.array(self._curve_i)
            logger.info('I ARRAY: {}'.format(i_wave))
            #self.real_button.releaseValue = i_wave
            self.ui.real_button.send_value_signal[np.ndarray].emit(i_wave)
        else:
            self.ui.error_label.setText("You must define a window first.")
        logger.info("Writing to PV.....")

    def write_q_pv(self):
        #imm_curve = self._curves[1]
        #q_pv = imm_curve["y_channel"]
        if self._curve_q:
           # self.imm_button.channel = q_pv
            q_wave = np.array(self.q_win)
            logger.info('Q ARRAY: {}'.format(q_wave))
            #self.imm_button.releaseValue = q_wave
            self.ui.imm_button.send_value_signal[np.ndarray].emit(q_wave)
        else:
            self.ui.error_label.setText("You must define a window first.")
        logger.info("Writing to PV.....")


    def ui_filename(self):
        return 'define_average_window.ui'


# class WaveformButton(PyDMPushButton):
#     """
#     Button to allow sending a ndarray to a PV
#     """
#     @property
#     def pressValue(self):
#         return self._pressValue

#     @pressValue.setter
#     def pressValue(self, value):
#         self._pressValue = value
    
#     @property
#     def releaseValue(self):
#         return self._releaseValue

#     @releaseValue.setter
#     def releaseValue(self, value):
#         self._releaseValue = value

#     def sendValue(self):
#         self.send_value_signal[np.ndarray].emit(self.releaseValue)

   # def button_released():
   #     my_button.send_value_signal[np.ndarray].emit(self.releaseValue)

