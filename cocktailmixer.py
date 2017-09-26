import sys
import json
import time

from PyQt5.QtCore import Qt, pyqtSignal, QIODevice
from PyQt5.QtWidgets import QApplication, QProgressBar, QPushButton, QWidget, QStackedWidget, QStyleFactory, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QLabel, QSpacerItem, QListWidget, QListWidgetItem
from PyQt5.QtGui import QPainter, QPen, QColor, QMovie, QFont
from PyQt5.QtSerialPort import QSerialPort

class HeaderLayout(QHBoxLayout):

    def __init__(self, title, parent = None):
        super().__init__(parent)
        self.emg = EmergencyStopButton()
        self.label = QLabel(title)
        self.label.setStyleSheet("""
            QLabel {
                color: #FFB900;
                font: bold;
            }
        """)
        self.addWidget(self.label)
        self.addStretch()
        self.addWidget(self.emg)

class EmergencyStopButton(QPushButton):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setStyleSheet("""
            QPushButton {
                background-image: url("media/stop-sign.png");
                border-radius: 0px;
                height: 48px;
                width: 48px;
            }
            QPushButton:pressed {
                background-image: url("media/stop-sign-pressed.png");
            }
        """)

class StyledPushButton(QPushButton):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setMinimumWidth(10)
        self.setMinimumHeight(10)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("""
            StyledPushButton {
                background-color: #FFB900;
                border-radius: 5px;
                font: bold 14px;
            }
            StyledPushButton:pressed {
                background-color: #DB9E00;
            }
        """)

class StyledProgressBar(QProgressBar):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setStyleSheet("""
            QProgressBar {
                border: 1px solid #FFB900;
                border-radius: 5px;
                text-align: center;
                background-color: #FF0000;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #00FF00;
                margin: 0px;
                border-radius: 5px;
            }
        """)

class StyledStackedWidget(QStackedWidget):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(240, 320)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)

    # draw the orange border    
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        pen = QPen()
        pen.setWidth(1)
        pen.setColor(QColor("#FFB900"))
        painter.setPen(pen)
        painter.drawRect(0, 0, 239, 319)
        
class ClickableLabel(QLabel):

    label_pressed = pyqtSignal()
        
    def mousePressEvent(self, ev):
        self.label_pressed.emit()

class IntroMenu(QWidget):

    start_clicked = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(1, 1, 1, 1)

        self.container = ClickableLabel(self)
        self.intro = QMovie("media/party.gif")
        self.container.setMovie(self.intro)

        self.title1 = QLabel("COCKTAIL MACHINE")
        self.title2 = QLabel("TAP SCREEN TO START")
        self.title1.setAlignment(Qt.AlignCenter)
        self.title2.setAlignment(Qt.AlignCenter)
        self.title1.setStyleSheet("""
            QLabel {
                color: #FFB900;
                font: bold 20px;
            }
        """)
        self.title2.setStyleSheet("""
            QLabel {
                color: #FFB900;
                font: bold 18px;
            }
        """)
        
        self.container.label_pressed.connect(lambda: self.start_clicked.emit())

        self.layout.addStretch()
        self.layout.addWidget(self.title1)
        self.layout.addStretch()
        self.layout.addWidget(self.container)
        self.layout.addStretch()
        self.layout.addWidget(self.title2)
        self.layout.addStretch()
        self.intro.start()

class AlcoholMenu(QWidget):

    drink_clicked = pyqtSignal(bool)
    stop_clicked = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(9, 9, 9, 9)
        #self.layout.setContentsMargins(0, 0, 0, 0)
        #self.setStyleSheet(".QWidget{margin: 11px}")

        self.header = HeaderLayout("SELECT ALCOHOL")
        self.spacer = QSpacerItem(1, 169, QSizePolicy.Expanding, QSizePolicy.Expanding) # fine-tuned for the right size
        self.choice1 = StyledPushButton()
        self.choice1.setText("NON-\nALCOHOLIC")
        self.choice2 = StyledPushButton()
        self.choice2.setText("ALL\nCOCKTAILS")
        #self.choice3 = StyledPushButton()
        #self.choice4 = StyledPushButton()
        #self.choice5 = StyledPushButton()
        #self.choice6 = StyledPushButton()

        self.layout.addLayout(self.header, 0, 0, 1, 0)
        self.layout.addWidget(self.choice1, 1, 0)
        self.layout.addWidget(self.choice2, 1, 1)
        #self.layout.addWidget(self.choice3, 2, 0)
        #self.layout.addWidget(self.choice4, 2, 1)
        #self.layout.addWidget(self.choice5, 3, 0)
        #self.layout.addWidget(self.choice6, 3, 1)
        self.layout.addItem(self.spacer, 2, 0)
        #self.layout.addItem(self.spacer, 3, 0)
        
        self.choice1.pressed.connect(lambda: self.drink_clicked.emit(False))
        self.choice2.pressed.connect(lambda: self.drink_clicked.emit(True))
        self.header.emg.pressed.connect(lambda: self.stop_clicked.emit())

class ModeMenu(QWidget):

    stop_clicked = pyqtSignal()
    select_cocktail_clicked = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(9, 9, 9, 9)
        #self.layout.setContentsMargins(0, 0, 0, 0)
        #self.setStyleSheet(".QWidget{margin: 11px}")

        self.choice1 = StyledPushButton()
        self.choice1.setText("SELECT BY \nNAME")

        self.choice2 = StyledPushButton()
        self.choice2.setText("SELECT BY \nINGREDIENTS")

        self.choice3 = StyledPushButton()
        self.choice3.setText("RECENT \nCOCKTAILS")

        self.choice4 = StyledPushButton()
        self.choice4.setText("CUSTOM \nCOCKTAIL")

        self.choice5 = StyledPushButton()
        self.choice5.setText("RANDOM \nCOCKTAIL")

        self.choice6 = StyledPushButton()
        self.choice6.setText("RANDOM \nINGREDIENTS")

        self.header = HeaderLayout("SELECT MODE")
        self.layout.addLayout(self.header, 0, 0, 1, 0)

        self.layout.addWidget(self.choice1, 1, 0)
        self.layout.addWidget(self.choice2, 1, 1)
        self.layout.addWidget(self.choice3, 2, 0)
        self.layout.addWidget(self.choice4, 2, 1)
        self.layout.addWidget(self.choice5, 3, 0)
        self.layout.addWidget(self.choice6, 3, 1)

        # DONT REMOVE, progressbar example
        #self.pb = StyledProgressBar()
        #self.pb.setValue(50)
        #self.layout.addWidget(self.pb, 4, 0, 1, 2)
        
        self.header.emg.pressed.connect(lambda: self.stop_clicked.emit())
        self.choice1.pressed.connect(lambda: self.select_cocktail_clicked.emit())
        
class SelectCocktailMenu(QWidget):

    stop_clicked = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(9, 9, 9, 9)
        self.header = HeaderLayout("SELECT COCKTAIL")
        self.list = QListWidget(self)
        self.list.setStyleSheet("""
            QListWidget {
                background-color: #000000;
                color: #FFB900
            }
            QListWidget::item:selected {
                background-color: #FFB900;
                color: #000000;
                border-radius: 3px;
            }
            QScrollBar {
                width: 0px;
                height: 0px;
            }
        """)
        
        #self.list.addItem("Apricot Sling")

        #add a bold text item
        #self.myFont = QFont()
        #self.myFont.setBold(True)
        #self.testitem = QListWidgetItem("test")
        #self.testitem.setFont(self.myFont)
        #self.list.addItem(self.testitem)
        
        #self.list.scrollToTop()
        
        #self.list.setCurrentItem(self.testitem)
        
        self.layout.addLayout(self.header, 0, 0, 1, 0)
        self.layout.addWidget(self.list, 1, 0)
        
        self.header.emg.pressed.connect(lambda: self.stop_clicked.emit())
        
    def updateList(self, cocktails, alcoholic):
        print("> updating available cocktails")
        self.list.clear()
        if alcoholic == True:
            for p in cocktails["alcoholic"]:
                self.list.addItem(p)
        else:
            for p in cocktails["non-alcoholic"]:
                self.list.addItem(p)
                
class SizePriceMenu(QWidget):
    
    stop_clicked = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(9, 9, 9, 9)
        self.header = HeaderLayout("SELECT SIZE")
        
        self.layout.addLayout(self.header, 0, 0, 1, 0)
        #self.layout.addWidget(self.list, 1, 0)
        
        self.header.emg.pressed.connect(lambda: self.stop_clicked.emit())
        
class HardwareInterface():

    def __init__(self):
        # TODO: define port at a better location
        # TODO: check for port opening / writing exceptions
        self.serial = QSerialPort()
        self.serial.readyRead.connect(self.serialRead)
        self.serial.setPortName("COM8")
        self.serial.open(QIODevice.ReadWrite)
        self.serial.setBaudRate(115200)
        self.serial.setDataBits(8)
        self.serial.setParity(QSerialPort.NoParity)
        self.serial.setStopBits(1)
        self.serial.setFlowControl(QSerialPort.NoFlowControl)
        assert self.serial.error() == QSerialPort.NoError

        self.serial.clear(QSerialPort.Input)
        
        self.serial.write(b"DEBUG: serial write test")
        self.serial.flush()
        
    def serialRead(self):
        #print("DEBUG: serial received data: ", (bytes(self.serial.readAll()).decode('utf-8')))
        if self.serial.canReadLine():
            print("DEBUG: processing received serial data")
            self.serialProcess(self.serial.readLine())
            
    def serialProcess(self, rx_line):
        #print("DEBUG: reading line: MESSAGE:", (bytes(rx_line).decode('utf-8')).rstrip())
        serial_data = json.loads(bytes(rx_line).decode('utf-8'))
        if serial_data["command"] == "update":
            if serial_data["id"] == "encoder":
                print("DEBUG: " + serial_data["value"])
        
        
class Controller():
    
    def __init__(self):
        print("> starting controller...")
        
        print(">  - loading cocktail databases")
        # TODO: implement error handling and maybe close the file in the end?
        with open("data/cocktails.json") as cocktail_json_file:
            self.cocktail_data = json.load(cocktail_json_file)
            
        with open("data/ingredients.json") as ingredients_json_file:
            self.ingredients_data = json.load(ingredients_json_file)
            
        print(">  - connecting to hardware")
        self.hardware_interface = HardwareInterface()
            
        print(">  - loading GUI elements")
        # define the menus and window
        self.intro_menu = IntroMenu()
        self.alcohol_menu = AlcoholMenu()
        self.mode_menu = ModeMenu()
        self.select_cocktail_menu = SelectCocktailMenu()
        self.size_price_menu = SizePriceMenu()
        self.main_window = StyledStackedWidget()
        
        # add the menus to the window
        self.main_window.addWidget(self.intro_menu)
        self.main_window.addWidget(self.alcohol_menu)
        self.main_window.addWidget(self.mode_menu)
        self.main_window.addWidget(self.select_cocktail_menu)
        self.main_window.addWidget(self.size_price_menu)
        
        # connect the slots
        self.alcohol_menu.stop_clicked.connect(self.goto_intro)
        self.mode_menu.stop_clicked.connect(self.goto_intro)
        self.select_cocktail_menu.stop_clicked.connect(self.goto_intro)
        self.size_price_menu.stop_clicked.connect(self.goto_intro)
        self.intro_menu.start_clicked.connect(self.goto_alcohol)
        self.alcohol_menu.drink_clicked.connect(self.goto_select)
        self.mode_menu.select_cocktail_clicked.connect(self.goto_select_cocktail)
        
        print("> controller started")
        print("> enter intro menu")
        self.main_window.setCurrentWidget(self.intro_menu)
        self.main_window.show()
        
    def goto_alcohol(self):
        print("> enter alcohol menu")
        self.main_window.setCurrentWidget(self.alcohol_menu)
        
    def goto_select(self, alcohol):   # TODO: add default value = False?
        print("DEBUG: alcohol: " + str(alcohol))
        print("> enter mode menu")
        self.alcohol = alcohol
        self.main_window.setCurrentWidget(self.mode_menu)
        
    def goto_intro(self):
        print("> EMERGENCY STOP")
        print("> enter intro menu")
        self.main_window.setCurrentWidget(self.intro_menu)
        
    def goto_select_cocktail(self):
        # TODO: do the update directly after the non-alcoholic/all-cocktails selection in AlcoholMenu?
        self.select_cocktail_menu.updateList(self.cocktail_data, self.alcohol)
        print("> enter select cocktail menu")
        self.main_window.setCurrentWidget(self.select_cocktail_menu)
        
    def goto_size_price(self):
        print("> enter size price menu")
        self.main_window.setCurrentWidget(self.size_price_menu)

def main(args):
    app = QApplication(args)
    app.setStyle(QStyleFactory.create("Fusion"))
    
    controller = Controller()
    
    # TODO close serial port, files, etc?
    # TODO: add raspi shutdown function? or rather seperate script watching a GPIO-pin?
    sys.exit(app.exec_())
  
if __name__== "__main__":
    main( sys.argv )