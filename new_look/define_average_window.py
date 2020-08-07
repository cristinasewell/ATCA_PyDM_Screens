from pydm import Display
import json
import logging
import pyqtgraph as pg
from functools import partial
import scipy.signal.windows
from numbers import Number

import numpy as np
from pydm.widgets.pushbutton import PyDMPushButton

from qtpy.QtGui import QIntValidator
from qtpy.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)


class AverageWindow(Display):
    def __init__(self, parent=None, args=None, macros=None, ui_filename=None):
        super(AverageWindow, self).__init__(
            parent=parent, args=args, macros=macros)
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
        # self.ui.get_waveform_pb.clicked.connect(self.handle_show_curves)

    def define_complex_curves(self):
        try:
            device = self._macros['DEVICE']
            number = self._macros['N']

            if device and number:
                ioc = "ca://{}:".format(device)

                iq = [0, 1]
                iq_label = ['I', 'Q']
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
            self.ui.error_label.setText(
                "Something went wrong with the macro??...")
            logger.error(
                "You need to define a DEVICE macro ioc (-m 'DEVICE=MY_IOC')")

    def handle_show_curves(self):
        self.ui.average_window_wf.clear()
        curves = []
        if self._curves:
            for indx in self._curves:
                c_pv = json.dumps(self._curves[indx])
                curves.append(c_pv)
                logger.debug('plotting curve: {}'.format(c_pv))
            self.average_window_wf.setCurves(curves)

    def waveform_buttons_setup(self):
        self.real_button = PyDMPushButton()
        self.imm_button = PyDMPushButton()

        self.real_button.setStyleSheet("""
            QPushButton
            {
                background-color: #FF7596;
                border-color:
                rgb(225,185,202) rgb(176,0,42) rgb(176,0,42) rgb(255,185,202);
                border-style: outset;
                border-radius: 1px;
                border-width: 2px;
                padding: 4px;
                color: black;
            }
            QPushButton:hover
            {
                background-color: rgb(255,87,127);
            }
            QPushButton:pressed
            {
                background-color: rgb(225,185,202);
                border-style: inset;
                border-width: 2px;
                border-color:
                rgb(176,0,42) rgb(225,185,202) rgb(225,185,202) rgb(176,0,42);
            }
            """)
        self.imm_button.setStyleSheet("""
            QPushButton
            {
                background-color: #732DFF;
                border-color:
                rgb(224,209,255) rgb(37,0,112) rgb(37,0,112) rgb(224,209,255);
                border-style: outset;
                border-radius: 1px;
                border-width: 2px;
                padding: 4px;
                color: black;
            }
            QPushButton:hover
            {
                background-color: rgb(77,0,230);
            }
            QPushButton:pressed
            {
                background-color: rgb(224,209,255);
                border-style: inset;
                border-width: 2px;
                border-color:
                rgb(37,0,112) rgb(204,189,235) rgb(204,189,235) rgb(37,0,112);
            }
            """)

        self.real_button.setText("Write I PV")
        self.imm_button.setText("Write Q PV")
        self.ui.button_layout.addWidget(self.real_button)
        self.ui.button_layout.addWidget(self.imm_button)
        # send a value of 0 for i and 1 for q
        # to determine what pv should be sent
        self.real_button.clicked.connect(partial(self.write_to_pv, 0))
        self.imm_button.clicked.connect(partial(self.write_to_pv, 1))

        real_curve = self._curves[0]
        i_pv = real_curve["y_channel"]
        self.ui.real_button.channel = i_pv

        imm_curve = self._curves[1]
        q_pv = imm_curve["y_channel"]
        self.imm_button.channel = q_pv

    def edit_line_setup(self):
        self.ui.start_line_edit.textChanged.connect(
            self.start_on_text_changed)
        self.ui.end_line_edit.textChanged.connect(
            self.end_on_text_changed)
        self.ui.start_line_edit_q.textChanged.connect(
            self.start_on_text_changed_q)
        self.ui.end_line_edit_q.textChanged.connect(
            self.end_on_text_changed_q)

    def start_on_text_changed(self):
        self.ui.start_line_edit.setValidator(
            self.validate_input(self.ui.start_line_edit))
        self.ui.error_label.setText("")

    def end_on_text_changed(self):
        self.ui.end_line_edit.setValidator(
            self.validate_input(self.ui.end_line_edit))
        self.ui.error_label.setText("")

    def start_on_text_changed_q(self):
        self.ui.start_line_edit_q.setValidator(
            self.validate_input(self.ui.start_line_edit_q))
        self.ui.error_label.setText("")

    def end_on_text_changed_q(self):
        self.ui.end_line_edit_q.setValidator(
            self.validate_input(self.ui.end_line_edit_q))
        self.ui.error_label.setText("")

    def validate_input(self, to_validate):
        # use QIntValidator
        # might need more validation here?
        return QIntValidator(to_validate)

    def get_current_i_start(self):
        start = None
        str_value = str(self.ui.start_line_edit.text())
        if str_value:
            try:
                start = int(str_value)
            except ValueError:
                logger.error('Could not convert to int')
        return start

    def get_current_i_end(self):
        end = None
        str_value = str(self.ui.end_line_edit.text())
        if str_value:
            try:
                end = int(str_value)
            except ValueError:
                logger.error('Could not convert to int')
        return end

    def get_current_q_start(self):
        start = None
        str_value = str(self.ui.start_line_edit_q.text())
        if str_value:
            try:
                start = int(str_value)
            except ValueError:
                logger.error('Could not convert to int')
        return start

    def get_current_q_end(self):
        end = None
        str_value = str(self.ui.end_line_edit_q.text())
        if str_value:
            try:
                end = int(str_value)
            except ValueError:
                logger.error('Could not convert to int')
        return end

    def get_i_pv_size(self):
        size = None
        str_size = str(self.ui.get_pv_size_i.text())
        logger.debug('size-----: {}'.format(str_size))
        if str_size:
            try:
                size = int(str_size)
                logger.debug("Pv window size: {}".format(size))
            except ValueError:
                logger.error('Could not convert to int')
        return size

    def get_q_pv_size(self):
        size = None
        str_size = str(self.ui.get_pv_size_q.text())
        logger.debug('size-----: {}'.format(str_size))
        if str_size:
            try:
                size = int(str_size)
                logger.debug("Pv window size: {}".format(size))
            except:
                logger.error('Could not convert to int')
        return size

    def plot_data(self):
        i_start = self.get_current_i_start()
        i_end = self.get_current_i_end()
        i_size = self.get_i_pv_size()
        i_is_valid = False
        is_i_zeros = False

        if i_start == 0 and i_end == 0:
            is_i_zeros = True

        if (isinstance(i_start, Number) and
                isinstance(i_end, Number) and i_size):
            i_is_valid = True

        logger.debug('I start: {}, end: {}'.format(i_start, i_end))

        q_start = self.get_current_q_start()
        q_end = self.get_current_q_end()
        q_size = self.get_q_pv_size()
        q_is_valid = False
        is_q_zeros = False

        if (isinstance(q_start, Number) and
                isinstance(q_end, Number) and q_size):
            q_is_valid = True

        if q_start == 0 and q_end == 0:
            is_q_zeros = True

        logger.debug('Q start: {}, end: {}'.format(q_start, q_end))

        self.ui.average_window_wf.clear()

        i_pen = pg.mkPen(color=(255, 85, 127))
        q_pen = pg.mkPen(color=(85, 0, 255))

        if i_is_valid:
            if (i_start >= i_end and not is_i_zeros) or (i_end >= i_size):
                self.ui.error_label.setText(
                    "Not a valid I window size. Please make sure"
                    " the start < end, and end < pv_size, or both zeros"
                     )
            else:
                # set all the q_start spaces with 0s
                # set all (q_end - q_start) with 1s
                # set all (q_size - q_end) with 0s
                self.i_win = [0]*i_start + [1]*(i_end - i_start) + [0]*(i_size - i_end)
                self._curve_i = self.i_win
                self.ui.average_window_wf.plot(self.i_win, pen=i_pen)

        if q_is_valid:
            if (q_start >= q_end and not is_q_zeros) or (q_end >= q_size):
                self.ui.error_label.setText(
                    "Not a valid Q window size. Please make sure "
                    " the start < end, and end < pv_size, or both zeros"
                     )
            else:
                # set all the q_start spaces with 0s
                # set all (q_end - q_start) with 1s
                # set all (q_size - q_end) with 0s
                self.q_win = [0]*q_start + [1]*(q_end - q_start) + [0]*(q_size - q_end)
                self._curve_q = self.q_win
                self.ui.average_window_wf.plot(self.q_win, pen=q_pen)

        if not (i_is_valid or q_is_valid):
            self.ui.error_label.setText(
                "You must define start & end values")

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
        if self._curve_i:
            i_wave = np.array(self._curve_i)
            logger.debug('I ARRAY: {}'.format(i_wave))
            # self.real_button.releaseValue = i_wave
            self.ui.real_button.send_value_signal[np.ndarray].emit(i_wave)
        else:
            self.ui.error_label.setText("You must define a window first.")
        logger.debug("Writing to PV.....")

    def write_q_pv(self):
        if self._curve_q:
            q_wave = np.array(self.q_win)
            logger.debug('Q ARRAY: {}'.format(q_wave))
            # self.imm_button.releaseValue = q_wave
            self.ui.imm_button.send_value_signal[np.ndarray].emit(q_wave)
        else:
            self.ui.error_label.setText("You must define a window first.")
        logger.debug("Writing to PV.....")

    def ui_filename(self):
        return 'define_average_window.ui'
