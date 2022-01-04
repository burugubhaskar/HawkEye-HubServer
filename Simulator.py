########################################################################################################################
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
########################################################################################################################
class Simulator(QMainWindow):
    def __init__(self):
        super(Simulator, self).__init__()
        self.setFixedSize(800,600)
        self.setWindowTitle("Hub Simulator")

        font = QFont()
        font.setPointSize(12)

        self.hub = QLabel("Hub :",self)
        self.hub.setGeometry(50,50,100,30)
        self.hub.setFont(font)

        self.channel = QLabel("Channel :", self)
        self.channel.setGeometry(50, 90, 100, 30)
        self.channel.setFont(font)

        self.vibration_frequency = QLabel("Vibration \nFrequency :", self)
        self.vibration_frequency.setGeometry(50, 130, 110, 60)
        self.vibration_frequency.setFont(font)

        self.vibration_magnitude = QLabel("Vibration \nMagnitude :", self)
        self.vibration_magnitude.setGeometry(50, 190, 110, 60)
        self.vibration_magnitude.setFont(font)

        self.temperature = QLabel("Temperature :", self)
        self.temperature.setGeometry(50, 250, 130, 60)
        self.temperature.setFont(font)

        self.combo_hub=QComboBox(self)
        self.combo_hub.addItems(["HUB 1","HUB 2","HUB 3","HUB 4","HUB 5","HUB 6"])
        self.combo_hub.setGeometry(110,50,100,30)
        self.combo_hub.setFont(font)

        self.combo_channel = QComboBox(self)
        self.combo_channel.addItems(["Left","Right"])
        self.combo_channel.setFont(font)
        self.combo_channel.setGeometry(150,90,100,30)

        self.lineedit_vibration_frequency=QLineEdit(self)
        self.lineedit_vibration_frequency.setValidator(QIntValidator())
        self.lineedit_vibration_frequency.setGeometry(160,160,110,30)

        self.lineedit_vibration_magnitude = QLineEdit(self)
        self.lineedit_vibration_magnitude.setValidator(QIntValidator())
        self.lineedit_vibration_magnitude.setGeometry(170, 220, 110, 30)

        self.lineedit_temperature = QLineEdit(self)
        self.lineedit_temperature.setValidator(QIntValidator())
        self.lineedit_temperature.setGeometry(190, 265, 110, 30)

        self.magnetic_event = QCheckBox(self)
        self.magnetic_event.setGeometry(50,320,190,30)
        self.magnetic_event.setText("Magnetic Event")
        self.magnetic_event.setFont(font)

        self.PIR_Event = QCheckBox(self)
        self.PIR_Event.setGeometry(230, 320, 190, 30)
        self.PIR_Event.setText("PIR Event")
        self.PIR_Event.setFont(font)

        self.Save = QPushButton(self)
        self.Save.setText("Send")
        self.Save.setGeometry(200,390,100,30)
        self.Save.setFont(font)
        self.Save.clicked.connect(self.test)
    def test(self):
        print('Testr')
########################################################################################################################
if __name__ == '__main__':
    app=QApplication(sys.argv)
    sum=Simulator()
    sum.show()
    sys.exit(app.exec_())
########################################################################################################################