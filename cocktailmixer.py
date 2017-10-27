import sys
import json
import time

from PyQt5.QtCore import Qt, pyqtSignal, QIODevice, QObject, QPoint, QRect
from PyQt5.QtWidgets import QApplication, QProgressBar, QPushButton, QWidget, QStackedWidget, QStyleFactory, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QLabel, QSpacerItem, QListWidget, QListWidgetItem, QCheckBox, QButtonGroup
from PyQt5.QtGui import QPainter, QPen, QColor, QMovie, QFont, QPainter, QPolygon
from PyQt5.QtSerialPort import QSerialPort

# TODO: use cool font like in airplanes with corners and crossed zeroes?

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
        # TODO: even darker shade of orange for pressed?
        self.setStyleSheet("""
            StyledPushButton {
                background-color: #FFB900;
                border-radius: 5px;
                font: bold 14px;
            }
            StyledPushButton:checked, StyledPushButton:pressed {
                background-color: #DB9E00;
            }
        """)

class CocktailProgressBar(QWidget):

    def __init__(self, parent = None):
        super().__init__(parent)
        # self.setStyleSheet("""
           # CocktailProgressBar {
               # border: 1px solid #FFB900;
               # border-radius: 5px;
               # text-align: center;
               # background-color: #FF0000;
               # font-weight: bold;
           # }
           # CocktailProgressBar::chunk {
               # background-color: #00FF00;
               # margin: 0px;
               # border-radius: 5px;
          # }
        # """)
    def paintEvent(self, e):
        # TODO: add ASCII drawing for the points
        # TODO: fill faster in thinner areas? (more realistic)
        # TODO: change from self.x()/.y() to self.size() size.width/.height
        # TODO: correctly map values for different widget heights (now 2x)
        # TODO: default value for setValue not called before first paint?
        # TODO: turn green at 100%?
        # TODO: filter values outside 0 - 100%
        # TODO: fix bug where value is wrong after too fast update, maybe in HardwareInterface?
        # TODO: maybe add some visual styles like borders or gradients?
        x_offset = self.x()                 # offset from widget to window
        y_offset = self.y()                 # offset from widget to window
        bowl_width = 140 / 2                # measured from model
        bowl_height = 92                    # measured from model
        stem_width = 12 / 2                 # measured from model
        stem_height = 100                   # measured from model
        base_width = 90 / 2                 # measured from model
        base_height = 8                     # measured from model
        x_symaxis = (240 / 2) - x_offset    # divide screen in half vertically, subtract offset
        y_spacing = 8                       # vertical positioning, trial and error
        
        a1 = QPoint(x_symaxis - bowl_width, y_spacing)
        a2 = QPoint(x_symaxis - stem_width, y_spacing + bowl_height)
        a3 = QPoint(x_symaxis - stem_width, y_spacing + bowl_height + stem_height)
        a4 = QPoint(x_symaxis - base_width, y_spacing + bowl_height + stem_height)
        a5 = QPoint(x_symaxis - base_width, y_spacing + bowl_height + stem_height + base_height)
        
        b1 = self.getSymPoint(a1, x_symaxis)
        b2 = self.getSymPoint(a2, x_symaxis)
        b3 = self.getSymPoint(a3, x_symaxis)
        b4 = self.getSymPoint(a4, x_symaxis)
        b5 = self.getSymPoint(a5, x_symaxis)
        
        qp = QPainter()
        qp.begin(self)
        qp.setPen(QColor("#FFB900"))
        font = QFont()
        font.setBold(True)
        qp.setFont(font)
        
        qp.drawPolyline(QPolygon([a1, a2, a3, a4, a5, b5, b4, b3, b2, b1, a1]))
        qp.drawText(QRect(a5.x(), a5.y(), 2 * base_width, 320 - a5.y() - y_offset), Qt.AlignCenter, str(self.value) + "%")
        
        # fill the Polyline
        fill_width = 0
        delta_x = a1.x() - a2.x()
        delta_y = a2.y() - a1.y()
        width_factor = delta_x / delta_y
        
        for i in range(2 * self.value):
            fill_height = a5.y() - i
            if fill_height >= a3.y():
                fill_width = base_width
            elif fill_height >= a2.y():
                fill_width = stem_width
            else:
                fill_width = width_factor * (fill_height - base_height - stem_height)
            qp.drawLine(x_symaxis - fill_width, fill_height, x_symaxis + fill_width, fill_height)
        
        qp.end()
        
    def setValue(self, value):
        self.value = value
        self.repaint()
        
    def getSymPoint(self, point, symaxis):
        return QPoint((2 * symaxis - point.x()), point.y())
        
class StyledLabel(QLabel):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setStyleSheet("""
            StyledLabel {
                color: #FFB900;
                font: bold;
            }
        """)
        
class StyledCheckBox(QCheckBox):

    def __init__(self, parent = None):
        super().__init__(parent)

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
        
        self.container.label_pressed.connect(self.start_clicked)

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
        self.header.emg.pressed.connect(self.stop_clicked)

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
        
        self.header.emg.pressed.connect(self.stop_clicked)
        self.choice1.pressed.connect(self.select_cocktail_clicked)
        
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
        self.list.setSortingEnabled(True)
        
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
        
        self.header.emg.pressed.connect(self.stop_clicked)
        
    def updateList(self, cocktails, alcoholic):
        # TODO: display only cocktails with all ingredients available
        print("> updating available cocktails")
        self.list.clear()
        for p in cocktails["non-alcoholic"]:
            self.list.addItem(p)
        if alcoholic:
            for p in cocktails["alcoholic"]:
                self.list.addItem(p)
        self.list.setCurrentRow(0)
                
    def scrollList(self, counts):
        print("DEBUG: scrolling list: " + str(counts))
        self.list.setCurrentRow((self.list.currentRow() - counts) % self.list.count())
                
class SizePriceMenu(QWidget):
    
    stop_clicked = pyqtSignal()
    start_clicked = pyqtSignal()
    size_clicked = pyqtSignal(int)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(9, 9, 9, 9)
        self.header = HeaderLayout("SELECT SIZE")
        self.group = QButtonGroup()
        self.group.setExclusive(True)
        
        # TODO: modify checkable buttons to activate on press, not click
        self.shot = StyledPushButton()
        self.shot.setText("SHOT\n2cl")
        self.shot.setCheckable(True)
        self.shot.setChecked(True)
        self.group.addButton(self.shot)
        self.medium = StyledPushButton()
        self.medium.setText("MEDIUM\n1dl")
        self.medium.setCheckable(True)
        self.group.addButton(self.medium)
        self.large = StyledPushButton()
        self.large.setText("LARGE\n2dl")
        self.large.setCheckable(True)
        self.group.addButton(self.large)
        self.spacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.price = StyledLabel()
        self.price.setText("CHF 6.42")
        self.price.setStyleSheet("""
            StyledLabel {
                font: bold 40px;
                color: #FFB900;
            }
        """)
        self.price.setAlignment(Qt.AlignCenter)
        self.glass_label = StyledLabel()
        self.glass_label.setText("Glass Status:")
        self.glass_label.setAlignment(Qt.AlignCenter)
        # TODO: style the checkbox in StyledCheckBox
        self.glass = StyledCheckBox()
        self.start = StyledPushButton()
        self.start.setText("START")
        
        self.layout.addLayout(self.header, 0, 0, 1, 3)
        self.layout.addWidget(self.shot, 1, 0)
        self.layout.addWidget(self.medium, 1, 1)
        self.layout.addWidget(self.large, 1, 2)
        ##self.layout.addItem(self.spacer, 2, 0, 1, 3)
        self.layout.addWidget(self.price, 2, 0, 1, 3)
        ##self.layout.addItem(self.spacer, 4, 0, 1, 3)
        self.layout.addWidget(self.glass_label, 3, 0, 1, 2)
        self.layout.addWidget(self.glass, 3, 2)
        #self.layout.addItem(self.spacer, 6, 0, 1, 3)
        self.layout.addWidget(self.start, 4, 0, 1, 3)
        
        # TODO: only activate start button after a glass is detected
        self.start.pressed.connect(self.start_clicked)
        self.shot.pressed.connect(lambda: self.size_clicked.emit(20))
        self.medium.pressed.connect(lambda: self.size_clicked.emit(100))
        self.large.pressed.connect(lambda: self.size_clicked.emit(200))
        self.header.emg.pressed.connect(self.stop_clicked)
        
class PouringMenu(QWidget):

    stop_clicked = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(9, 9, 9, 9)
        # TODO: change to "FINISHED!" when finished
        self.header = HeaderLayout("PLEASE WAIT...")
        
        self.progress = CocktailProgressBar()
        self.progress.setValue(0)
        
        self.layout.addLayout(self.header, 0, 0, 1, 3)
        self.layout.addWidget(self.progress, 1, 0, 1, 3)
        
        self.header.emg.pressed.connect(self.stop_clicked)
        
class HardwareInterface(QObject):

    encoder_changed = pyqtSignal(int)
    encoder_clicked = pyqtSignal()
    emergency_stop = pyqtSignal()
    scale_changed = pyqtSignal(int)

    def __init__(self, parent = None):
        super().__init__(parent)
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
        
        #self.serial.write(b"DEBUG: serial write test")
        #self.serial.flush()
        
    def serialRead(self):
        #print("DEBUG: serial received data: ", (bytes(self.serial.readAll()).decode('utf-8')))
        while self.serial.canReadLine():
            print("DEBUG: processing received serial data")
            self.serialProcess(self.serial.readLine())

    # TODO: implement checksum
    # TODO: implement ACK/NAK
    # TODO: implement exceptions to catch invalid command frames
    def serialProcess(self, serial_data):
        frame = json.loads(bytes(serial_data).decode('utf-8'))
        cmd = frame["command"]
        func = getattr(self, "command_" + cmd)
        func(frame["id"], frame["value"])
        
    def command_update(self, cmd_id, value):
        print("DEBUG: received: update " + cmd_id + " " + value)
        if cmd_id == "encoder":
            # TODO: check if really a number
            self.encoder_changed.emit(int(value))
        elif cmd_id == "encoder_button":
            # TODO: implement latching encoder button (check value)
            self.encoder_clicked.emit()
        elif cmd_id == "scale":
            # TODO: check if really a number
            self.scale_changed.emit(int(value))
        elif cmd_id == "emergency_stop":
            # TODO: implement latching emergency stop (check value)
            self.emergency_stop.emit()
        elif cmd_id == "coin_counter":
            pass
        elif cmd_id == "key_switch":
            pass
        
    def command_finished(self, cmd_id, value):
        print("DEBUG: received: finished " + cmd_id + " " + value)
        
    def command_get(self, cmd_id, value):
        pass
        
    def command_set(self, cmd_id, value):
        pass
        
    def command_pour(self, cmd_id, value):
        pass
        
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
        self.pouring_menu = PouringMenu()
        self.main_window = StyledStackedWidget()
        
        # add the menus to the window
        self.main_window.addWidget(self.intro_menu)
        self.main_window.addWidget(self.alcohol_menu)
        self.main_window.addWidget(self.mode_menu)
        self.main_window.addWidget(self.select_cocktail_menu)
        self.main_window.addWidget(self.size_price_menu)
        self.main_window.addWidget(self.pouring_menu)
        
        # connect the UI slots
        self.alcohol_menu.stop_clicked.connect(self.goto_intro)
        self.mode_menu.stop_clicked.connect(self.goto_intro)
        self.select_cocktail_menu.stop_clicked.connect(self.goto_intro)
        self.size_price_menu.stop_clicked.connect(self.goto_intro)
        self.pouring_menu.stop_clicked.connect(self.goto_intro)
        self.intro_menu.start_clicked.connect(self.goto_alcohol)
        self.alcohol_menu.drink_clicked.connect(self.goto_mode)
        self.mode_menu.select_cocktail_clicked.connect(self.goto_select_cocktail)
        self.size_price_menu.start_clicked.connect(self.goto_pouring_menu)
        self.size_price_menu.size_clicked.connect(self.handle_size_buttons)
        
        # connect the hardware interface command slots
        self.hardware_interface.encoder_changed.connect(self.handle_encoder_changed)
        self.hardware_interface.encoder_clicked.connect(self.handle_encoder_clicked)
        self.hardware_interface.emergency_stop.connect(self.goto_intro)
        self.hardware_interface.scale_changed.connect(self.pouring_menu.progress.setValue)
        
        print("> controller started")
        print("> enter intro menu")
        self.main_window.setCurrentWidget(self.intro_menu)
        self.main_window.show()
        
    def handle_encoder_changed(self, counts):
        if self.main_window.currentWidget() is self.select_cocktail_menu:
            self.select_cocktail_menu.scrollList(counts)
        
    def handle_encoder_clicked(self):
        if self.main_window.currentWidget() is self.select_cocktail_menu:
            self.goto_size_price()
            
    def handle_size_buttons(self, size):
        # TODO: collect this data for the pouring command
        if size == 20:
            print("DEBUG: shot button pressed")
        elif size == 100:
            print("DEBUG: medium button pressed")
        elif size == 200:
            print("DEBUG: large button pressed")
        self.size = size
        
    def start_pouring(self):
        # TODO: rather use and argument for this function instead of reading directly from the list?
        cocktail = self.select_cocktail_menu.list.currentItem().text()
        print("DEBUG: pouring " + cocktail + "...")
        
        # TODO: what if not found at all? should not happen in reality
        if cocktail in self.cocktail_data["non-alcoholic"]:
            recipe_volumes = self.cocktail_data["non-alcoholic"][cocktail]
        else:
            recipe_volumes = self.cocktail_data["alcoholic"][cocktail]
        
        # DEBUG
        #print(self.cocktail_data)
        
        print("DEBUG: recipe in original volumes: " + str(recipe_volumes))
        # FIXME: read correct norm. value from size pressed
        recipe_normalized_volumes = self.get_normalized_volumes(self.size, recipe_volumes)
        print("DEBUG: recipe in normalized volumes: " + str(recipe_normalized_volumes))
        recipe_masses = self.get_masses(recipe_normalized_volumes)
        print("DEBUG: recipe in normalized masses: " + str(recipe_masses))

        #mylist = [self.cocktail_data[k][cocktail] for k in self.cocktail_data]
        #print(mylist)
        
    def get_total_volume(self, volumes):
        volume = 0
        for ingredients in volumes:
            volume += ingredients[1]
        print("DEBUG: total volume: " + str(volume))
        return volume
        
    def get_normalized_volumes(self, normal_volume, volumes):
        normalized_volumes = []
        normalization_factor = normal_volume / self.get_total_volume(volumes)
        print("DEBUG: normalization_factor: " + str(round(normalization_factor, 3)))
        for ingredient in volumes:
            name = ingredient[0]
            mass = ingredient[1] * normalization_factor
            # TODO: remove? just to truncate the floats for DEBUG output
            mass = round(mass, 3)
            normalized_volumes.append([name, mass])
        return normalized_volumes
        
    def get_masses(self, volumes):
        masses = []
        for ingredient in volumes:
            name = ingredient[0]
            mass = ingredient[1] * self.ingredients_data[name]["density"]
            # TODO: remove? just to truncate the floats for DEBUG output
            mass = round(mass, 3)
            masses.append([name, mass])
        return masses
        
    def goto_alcohol(self):
        print("> enter alcohol menu")
        self.main_window.setCurrentWidget(self.alcohol_menu)
        
    def goto_mode(self, alcohol):   # TODO: add default value = False?
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
        # TODO: better way than to copy the whole list over?
        self.select_cocktail_menu.updateList(self.cocktail_data, self.alcohol)
        print("> enter select cocktail menu")
        self.main_window.setCurrentWidget(self.select_cocktail_menu)
        
    def goto_size_price(self):
        print("> enter size price menu")
        # default value 20ml if no size button pressed
        self.size = 20
        self.main_window.setCurrentWidget(self.size_price_menu)
        
    def goto_pouring_menu(self):
        print("> enter pouring menu")
        self.main_window.setCurrentWidget(self.pouring_menu)
        self.start_pouring()

def main(args):
    app = QApplication(args)
    app.setStyle(QStyleFactory.create("Fusion"))
    
    controller = Controller()
    
    # TODO close serial port, files, etc?
    # TODO: add raspi shutdown function? or rather seperate script watching a GPIO-pin?
    sys.exit(app.exec_())
  
if __name__== "__main__":
    main( sys.argv )