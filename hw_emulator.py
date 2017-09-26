import sys
from PyQt5.QtCore import QIODevice, pyqtSignal
from PyQt5.QtWidgets import QApplication, QStyleFactory, QWidget, QGridLayout, QSpacerItem, QSizePolicy, QPushButton
from PyQt5.QtSerialPort import QSerialPort

# bridge COM ports COM8 and COM9 (using com0com), cocktailmixer controller listening on COM8

class Menu(QWidget):

    debug_clicked = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        layout = QGridLayout(self)
        debug_button = QPushButton()
        debug_button.setText("send DEBUG message")
        layout.addWidget(debug_button, 1, 0)
        
        debug_button.clicked.connect(lambda: self.debug_clicked.emit())
        
class Emulator():

    def __init__(self):
        menu = Menu()
        menu.show()
        
        menu.debug_clicked.connect(self.sendDebug)
        
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
        
        print("> EMU: emulator ready")
    
    def sendDebug(self):
        print("> EMU: sending debug")
        self.serial.write(b"DEBUG EMU: serial write test\n")

def main(args):

    app = QApplication(args)
    app.setStyle(QStyleFactory.create("Fusion"))
    
    emulator = Emulator()
    
    sys.exit(app.exec_())
  
if __name__== "__main__":
    main( sys.argv )