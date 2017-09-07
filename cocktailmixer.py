import sys
import json
import time

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QProgressBar, QPushButton, QWidget, QStackedWidget, QStyleFactory, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QLabel, QSpacerItem
from PyQt5.QtGui import QPainter, QPen, QColor, QMovie
# FIXME: why choose QtSerialPort over PySerial?
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

class IntroMenu(QWidget):

    start_clicked = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        #layout.setSpacing(8)
        layout.setContentsMargins(1, 1, 1, 1)

        container = QLabel()
        intro = QMovie("media/party.gif")
        container.setMovie(intro)

        title1 = QLabel("COCKTAIL")
        title2 = QLabel("MACHINE")
        title1.setAlignment(Qt.AlignCenter)
        title2.setAlignment(Qt.AlignCenter)
        title1.setStyleSheet("""
            QLabel {
                color: #FFB900;
                font: bold 36px;
            }
        """)
        title2.setStyleSheet("""
            QLabel {
                color: #FFB900;
                font: bold 36px;
            }
        """)
        
        #intro.clicked.connect(start_clicked.emit)

        layout.addStretch()
        layout.addWidget(title1)
        layout.addStretch()
        layout.addWidget(container)
        layout.addStretch()
        layout.addWidget(title2)
        layout.addStretch()
        intro.start()

class AlcoholMenu(QWidget):

    drink_clicked = pyqtSignal(bool)
    stop_clicked = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(9, 9, 9, 9)
        #layout.setContentsMargins(0, 0, 0, 0)
        #self.setStyleSheet(".QWidget{margin: 11px}")

        self.header = HeaderLayout("1. SELECT ALCOHOL")
        self.spacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.choice1 = StyledPushButton()
        self.choice1.setText("NON-\nALCOHOLIC")
        #choice1.pressed.connect(lambda: self.changeForm.emit(2))
        self.choice2 = StyledPushButton()
        self.choice2.setText("ALL DRINKS")
        #choice2.pressed.connect(lambda: self.changeForm.emit(2))

        self.layout.addLayout(self.header, 0, 0, 1, 0)
        self.layout.addWidget(self.choice1, 1, 0)
        self.layout.addWidget(self.choice2, 1, 1)
        self.layout.addItem(self.spacer, 2, 0)
        self.layout.addItem(self.spacer, 3, 0)
        #layout.addStretch()
        #button = EmergencyStopButton()
        #layout.addWidget(button, 1, 0)
        
        self.choice1.pressed.connect(lambda: self.drink_clicked.emit(True))
        self.choice2.pressed.connect(lambda: self.drink_clicked.emit(False))
        self.header.emg.pressed.connect(lambda: self.stop_clicked.emit())

class SelectMenu(QWidget):

    changeForm = pyqtSignal(int)

    def __init__(self, parent = None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(9, 9, 9, 9)
        #layout.setContentsMargins(0, 0, 0, 0)
        #self.setStyleSheet(".QWidget{margin: 11px}")

        choice1 = StyledPushButton()
        choice1.setText("SEARCH BY \nNAME")
        #choice1.pressed.connect(lambda: self.changeForm.emit(1))

        choice2 = StyledPushButton()
        choice2.setText("SEARCH BY \nINGREDIENTS")

        choice3 = StyledPushButton()
        choice3.setText("RECENT \nDRINKS")

        choice4 = StyledPushButton()
        choice4.setText("CUSTOM \nDRINK")

        choice5 = StyledPushButton()
        choice5.setText("RANDOM \nDRINK")

        choice6 = StyledPushButton()
        choice6.setText("RANDOM \nINGREDIENTS")

        header = HeaderLayout("2. SELECT MODE")
        layout.addLayout(header, 0, 0, 1, 0)

        layout.addWidget(choice1, 1, 0)
        layout.addWidget(choice2, 1, 1)
        layout.addWidget(choice3, 2, 0)
        layout.addWidget(choice4, 2, 1)
        layout.addWidget(choice5, 3, 0)
        layout.addWidget(choice6, 3, 1)

        pb = StyledProgressBar()
        pb.setValue(50)
        layout.addWidget(pb, 4, 0, 1, 2)
        
class Controller:
    def __init__(self):
        print(">entered controller instance")
        
        self.alcohol_menu = AlcoholMenu()
        self.select_menu = SelectMenu()
        self.main_window = StyledStackedWidget()
        self.main_window.addWidget(self.alcohol_menu)
        self.main_window.addWidget(self.select_menu)
        
        self.main_window.setCurrentWidget(self.alcohol_menu)
        self.main_window.show()
        self.alcohol_menu.drink_clicked.connect(self.select_alcohol)
        self.alcohol_menu.stop_clicked.connect(self.emg_stop)
        
    def select_alcohol(self, alcohol):   #TODO: add default value = False?
        print("select alcohol: " + str(alcohol))
        self.alcohol = alcohol
        self.main_window.setCurrentWidget(self.select_menu)
        
    def emg_stop(self):
        print("STOPPED")

def main(args):
    app = QApplication(args)
    app.setStyle(QStyleFactory.create("Fusion"))

    # define the windows
    #window0 = IntroMenu()
    #window1 = AlcoholMenu()
    #window2 = SelectMenu()
    #mainWindow = StyledStackedWidget()

    # set up the slots
    #window1.changeForm.connect(mainWindow.setCurrentIndex)

    # add the windows
    #mainWindow.addWidget(window0)
    #mainWindow.addWidget(window1)
    #mainWindow.addWidget(window2)

    # set window to be displayed
    #mainWindow.setCurrentIndex(1)

    #mainWindow.show()
    
    # do something here?
    controller = Controller()
    
    sys.exit(app.exec_())
  
if __name__== "__main__":
    main( sys.argv )