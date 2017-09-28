import sys
from PyQt5.QtCore import QIODevice, pyqtSignal
from PyQt5.QtWidgets import QApplication, QStyleFactory, QWidget, QGridLayout, QSizePolicy, QPushButton, QLabel
from PyQt5.QtSerialPort import QSerialPort

# bridge COM ports COM8 and COM9 (using com0com), cocktailmixer controller listening on COM8

class Menu(QWidget):

    encoder_update = pyqtSignal(int)
    encoder_click = pyqtSignal()
    emergency_stop = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.resize(640, 240)
        self.setWindowTitle("Cocktailmixer Hardware Emulator")
        layout = QGridLayout(self)
        encoder_label = QLabel()
        emergency_stop_label = QLabel()
        encoder_up_button = QPushButton()
        encoder_down_button = QPushButton()
        encoder_click_button = QPushButton()
        emergency_stop_button = QPushButton()
        encoder_label.setText("Encoder")
        emergency_stop_label.setText("Emergency Stop")
        encoder_up_button.setText("scroll up")
        encoder_down_button.setText("scroll down")
        encoder_click_button.setText("select")
        emergency_stop_button.setText("STOP")
        layout.addWidget(encoder_label, 0, 0)
        layout.addWidget(emergency_stop_label, 0, 1)
        layout.addWidget(encoder_up_button, 1, 0)
        layout.addWidget(encoder_down_button, 2, 0)
        layout.addWidget(encoder_click_button, 3, 0)
        layout.addWidget(emergency_stop_button, 1, 1)
        
        encoder_up_button.clicked.connect(lambda: self.encoder_update.emit(1))
        encoder_down_button.clicked.connect(lambda: self.encoder_update.emit(-1))
        encoder_click_button.clicked.connect(self.encoder_click)
        emergency_stop_button.clicked.connect(self.emergency_stop)
        
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
        
def main(args):

    app = QApplication(args)
    
    emulator = Emulator()
    
    sys.exit(app.exec_())
  
if __name__== "__main__":
    main( sys.argv )