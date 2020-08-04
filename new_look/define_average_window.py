from pydm import Display
from os import path
import json
import logging
import sys
import pyqtgraph as pg
import epics
import re

from qtpy.QtCore import QRegExp
from qtpy.QtGui import QRegExpValidator, QDoubleValidator
from qtpy.QtWidgets import QMessageBox
#from qtpy.QtCore import Qt, QTimer, Slot, QSize, QLibraryInfo

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

    def start_edit_line_setup(self):
        self.ui.start_line_edit.returnPressed.connect(self.start_on_return_pressed)
        self.ui.start_line_edit.textChanged.connect(self.start_on_text_changed)

    def end_edit_line_setup(self):
        self.ui.end_line_edit.returnPressed.connect(self.end_on_return_pressed)
        self.ui.end_line_edit.textChanged.connect(self.end_on_text_changed)

    def start_on_text_changed(self):
        self.ui.start_line_edit.setValidator(self.validate_input(self.ui.start_line_edit))
        #self.ui.start_line_edit.setStyleSheet("QLineEdit { border: red }")

    def end_on_text_changed(self):
        self.ui.end_line_edit.setValidator(self.validate_input(self.ui.end_line_edit))

    def start_on_return_pressed(self):
        """
        Slot to capture the input for the Start value.
        Called when return pressed
        """
        if self.ui.start_line_edit.text():
            str_value = str(self.ui.start_line_edit.text())
            self.start = float(str_value)

    def end_on_return_pressed(self):
        """
        Slot to capture the input for the End value.
        Called when return pressed
        """
        if self.ui.end_line_edit.text():
            str_value = str(self.ui.end_line_edit.text())
            self.end = float(str_value)
    
    def validate_input(self, to_validate):
        # validate +- values, up to 12 chars for now, and up to 6 values after the .
        reg_ex = QRegExp("^[+-]?[0-9]{1,12}(?:\.[0-9]{1,6})?$")
        return QRegExpValidator(reg_ex, to_validate)

    def set_window_size(self, start, stop):
        #self.ui.average_window_wf.plotItem.getViewBox().setYRange(start, stop, padding=0)
        pass

    def plot_data(self):
       # y_values = [20, 40, 60]
       # self.ui.average_window_wf.plotItem.getViewBox().addCurve(y_values)
        pass

    def write_to_pv(self, checked):
        write_message = QMessageBox.question(
            self, ' Writing PV?', 'Write to PV?',
            QMessageBox.Yes | QMessageBox.No)
        if write_message == QMessageBox.Yes:
            self.write()
        else:
            pass
    
    def write(self):
        self.plot_data()
        logger.info("Writing to PV.....")
        pass

    def ui_filename(self):
        return 'define_average_window.ui'
