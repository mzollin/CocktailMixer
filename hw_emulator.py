# Copyright 2017 Marco Zollinger <marco@freelabs.space>
#
# This file is part of CocktailMixer.
#
# CocktailMixer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CocktailMixer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CocktailMixer.  If not, see <http://www.gnu.org/licenses/>.

import sys
from PyQt5.QtCore import QIODevice, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QStyleFactory, QWidget, QGridLayout, QSizePolicy, QPushButton, QLabel, QScrollBar
from PyQt5.QtSerialPort import QSerialPort

# bridge COM ports COM8 and COM9 (using com0com), cocktailmixer controller listening on COM8

class Menu(QWidget):

    encoder_update = pyqtSignal(int)
    encoder_click = pyqtSignal()
    emergency_stop = pyqtSignal()
    scale_update = pyqtSignal(int)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.resize(640, 240)
        self.setWindowTitle("Cocktailmixer Hardware Emulator")
        layout = QGridLayout(self)
        encoder_label = QLabel()
        emergency_stop_label = QLabel()
        scale_label = QLabel()
        encoder_up_button = QPushButton()
        encoder_down_button = QPushButton()
        encoder_click_button = QPushButton()
        emergency_stop_button = QPushButton()
        scale_scroller = QScrollBar(Qt.Horizontal)
        scale_scroller.setMaximum(100)
        scale_value = QLabel()
        encoder_label.setText("Encoder")
        emergency_stop_label.setText("Emergency Stop")
        encoder_up_button.setText("scroll up")
        encoder_down_button.setText("scroll down")
        encoder_click_button.setText("select")
        emergency_stop_button.setText("STOP")
        scale_label.setText("Scale Value")
        scale_value.setText(str(0))
        layout.addWidget(encoder_label, 0, 0)
        layout.addWidget(emergency_stop_label, 0, 1)
        layout.addWidget(scale_label, 0, 2)
        layout.addWidget(encoder_up_button, 1, 0)
        layout.addWidget(encoder_down_button, 2, 0)
        layout.addWidget(encoder_click_button, 3, 0)
        layout.addWidget(emergency_stop_button, 1, 1)
        layout.addWidget(scale_scroller, 1, 2)
        layout.addWidget(scale_value, 2, 2)
        
        encoder_up_button.clicked.connect(lambda: self.encoder_update.emit(1))
        encoder_down_button.clicked.connect(lambda: self.encoder_update.emit(-1))
        encoder_click_button.clicked.connect(self.encoder_click)
        emergency_stop_button.clicked.connect(self.emergency_stop)
        scale_scroller.valueChanged.connect(lambda: self.scale_update.emit(scale_scroller.value()))
        scale_scroller.valueChanged.connect(lambda: scale_value.setText(str(scale_scroller.value())))
        
class Emulator():

    def __init__(self):
        menu = Menu()
        menu.show()
        
        # TODO: define port at a better location
        # TODO: check for port opening / writing exceptions
        self.serial = QSerialPort()
        self.serial.setPortName("COM9")
        self.serial.open(QIODevice.ReadWrite)
        self.serial.setBaudRate(115200)
        self.serial.setDataBits(8)
        self.serial.setParity(QSerialPort.NoParity)
        self.serial.setStopBits(1)
        self.serial.setFlowControl(QSerialPort.NoFlowControl)
        assert self.serial.error() == QSerialPort.NoError
        
        menu.encoder_update.connect(self.update_encoder)
        menu.encoder_click.connect(self.click_encoder)
        menu.emergency_stop.connect(self.update_emergency_stop)
        menu.scale_update.connect(self.update_scale)
        
        print("> EMU: emulator ready")
    
    def update_encoder(self, counts):
        print("> EMU: sending update_encoder")
        self.serial.write(b'{"command": "update", "id": "encoder", "value": "%d", "checksum": "ABCD"}\n' % counts)
        
    def click_encoder(self):
        print("> EMU: sending update_encoder_button")
        self.serial.write(b'{"command": "update", "id": "encoder_button", "value": "1", "checksum": "ABCD"}\n')
        
    def update_emergency_stop(self):
        print("> EMU: sending update_emergency_stop")
        self.serial.write(b'{"command": "update", "id": "emergency_stop", "value": "1", "checksum": "ABCD"}\n')
        
    def update_scale(self, value):
        print("> EMU: sending update_scale")
        self.serial.write(b'{"command": "update", "id": "scale", "value": "%d", "checksum": "ABCD"}\n' % value)
        
def main(args):

    app = QApplication(args)
    
    emulator = Emulator()
    
    sys.exit(app.exec_())
  
if __name__== "__main__":
    main( sys.argv )
