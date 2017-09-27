import sys
from PyQt5.QtCore import QIODevice, pyqtSignal
from PyQt5.QtWidgets import QApplication, QStyleFactory, QWidget, QGridLayout, QSpacerItem, QSizePolicy, QPushButton
from PyQt5.QtSerialPort import QSerialPort

# bridge COM ports COM8 and COM9 (using com0com), cocktailmixer controller listening on COM8

class Menu(QWidget):

    updated_encoder = pyqtSignal(int)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.resize(200, 200)
        layout = QGridLayout(self)
        scroll_up_button = QPushButton()
        scroll_down_button = QPushButton()
        scroll_up_button.setText("scroll up")
        scroll_down_button.setText("scroll down")
        layout.addWidget(scroll_up_button, 1, 0)
        layout.addWidget(scroll_down_button, 2, 0)
        
        scroll_up_button.clicked.connect(lambda: self.updated_encoder.emit(1))
        scroll_down_button.clicked.connect(lambda: self.updated_encoder.emit(-1))
        
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
        
        menu.updated_encoder.connect(self.update_encoder)
        
        print("> EMU: emulator ready")
    
    def update_encoder(self, counts):
        print("> EMU: sending update_encoder")
        self.serial.write(b'{"command": "update", "id": "encoder", "value": "%d", "checksum": "ABCD"}\n' % counts)
        
def main(args):

    app = QApplication(args)
    
    emulator = Emulator()
    
    sys.exit(app.exec_())
  
if __name__== "__main__":
    main( sys.argv )