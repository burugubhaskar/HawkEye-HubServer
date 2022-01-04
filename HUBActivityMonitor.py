########################################################################################################################
import socket
from time import sleep
import sys
import random
from PyQt5.QtCore import QTimer
########################################################################################################################
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtWidgets import QMainWindow, QLabel, QComboBox, QLineEdit, QCheckBox, QPushButton, QApplication
########################################################################################################################
class Simulator(QMainWindow):
    def __init__(self):
        super(Simulator, self).__init__()
        self.setFixedSize(800,600)
        self.setWindowTitle("Hub Health Monitoring System")

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
        self.HubList = ["HUB 01","HUB 02","HUB 03"]
       # self.HubList = ["HUB 1", "HUB 2"]
        self.combo_hub.addItems(self.HubList)
        self.combo_hub.setGeometry(110,50,200,31)
        self.combo_hub.setFont(font)

        self.combo_channel = QComboBox(self)
        self.combo_channel.addItems(["Left","Right"])
        self.combo_channel.setFont(font)
        self.combo_channel.setGeometry(150,90,100,30)

        self.sensor = QLabel("Sensor :", self)
        self.sensor.setGeometry(50, 360, 130, 60)
        self.sensor.setFont(font)

        self.lineedit_sensor = QLineEdit(self)
        self.lineedit_sensor.setValidator(QIntValidator())
        self.lineedit_sensor.setGeometry(190,380,110,30)

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
        self.Save.setText("Capture")
        self.Save.setGeometry(200,430,100,30)
        self.Save.setFont(font)
        self.Save.clicked.connect(self.BuildEventPacket)

        self.server_connect = QPushButton(self)
        self.server_connect.setText("Connect")
        self.server_connect.setGeometry(320,430,200,30)
        self.server_connect.setFont(font)

        self.SendHealthEvent = QPushButton(self)
        self.SendHealthEvent.setText("Health Event")
        self.SendHealthEvent.setGeometry(300,500,200,30)
        self.SendHealthEvent.setFont(font)
        self.SendHealthEvent.clicked.connect(self.BuildHealthPackets)

        self.magnetic_event.setChecked(False)
        self.server_connect.clicked.connect(self.ConnectToServer)
        self.ServerConnectionStatus = False
       # self.PIR_Event.setChecked(True)
        self.lineedit_temperature.setText('1000')
        self.lineedit_vibration_frequency.setText('10')
        self.lineedit_vibration_magnitude.setText('10000')
        self.lineedit_sensor.setText('34')
        self.Timer = QTimer()
        self.TimeOut = 60*10*1000
        self.GenRandomEvent()
      #  self.Timer.timeout.connect(self.GenRandomEvent)
        self.Timer.startTimer(self.TimeOut)
       # self.hide()
        ################################################################################################################
    #def BuildEventPacket(self,HubID = 'HUB 1',Channel = 'Right', RTNumber = 1, VibFreq = 10, VibMag = 10000,Temp = 20,MagneticEvent = True,PIREvent = True):
    def ConnectToServer(self):
        if self.ServerConnectionStatus == False:
            try:
                self.sock = socket.socket()
                self.sock.connect(('localhost',5555))
              #  self.sock.connect(('192.168.1.150', 5555))
                self.server_connect.setText('Close')
                self.ServerConnectionStatus = True
            except:
                print('unable to connect to server')
        else:
            try:
                self.sock.close()
            except:
                print('error in closing port')
            self.server_connect.setText('Connect')
            self.ServerConnectionStatus = False

        ##########################################################################################################
    def GenRandomEvent(self):
       # self.ConnectToServer()
        self.combo_channel.setCurrentText(random.choice(["Left","Right"]))
        self.combo_hub.setCurrentText(random.choice(self.HubList))
        self.lineedit_sensor.setText(f'{random.randint(1,250)}')
        self.lineedit_vibration_frequency.setText(f'{random.randint(3,20)}')
        self.lineedit_vibration_magnitude.setText(f'{random.randint(5000,50000)}')
        #print(random.randint(1,250))
        self.Timer.start(self.TimeOut)
        try:
            self.sock = socket.socket()
           # self.sock.connect(('192.168.1.150', 5555))
            self.sock.connect(('localhost', 5555))
            self.server_connect.setText('Close')
            self.ServerConnectionStatus = True
            self.BuildEventPacket()
            self.sock.close()
        except:
            print('unable to connect to server')
        ##########################################################################################################
    def BuildHealthPackets(self):
        Channel = self.combo_channel.currentText()
        RTNumber = int(self.lineedit_sensor.text())
        #HubID = self.combo_hub.currentText()
        Packet =[]
        if Channel == 'Left' :
            Packet.append(0xFE)
        elif Channel == 'Right':
            Packet.append(0xFD)
        Packet.append(0xC0)
        Packet.append(0xA8)
        Packet.append(0x01)
        Packet.append(0x64+self.combo_hub.currentIndex())
        for _ in range(0,5):
            Packet.append(0x00)
        for _ in range(5, 10):
            Packet.append(0xFF)
        for _ in range(10, 15):
            Packet.append(0x00)

        for _ in range(15,38):
            Packet.append(0xFF)
        #Packet = b'bhaskar'
        print(bytes(Packet))
        try:
            self.sock.send(bytes(Packet))
        except:
            print('Tansmission Failed')
        ##########################################################################################################
    def BuildEventPacket(self):
        Channel = self.combo_channel.currentText()
        HubID = self.combo_hub.currentText()
        RTNumber = int(self.lineedit_sensor.text())
        VibFreq = int(self.lineedit_vibration_frequency.text())
        VibMag = int(self.lineedit_vibration_magnitude.text())
        Temp = int(self.lineedit_temperature.text())

        MagneticEvent = 1 if self.magnetic_event.isChecked() else 0
        PIREvent = 1 if self.PIR_Event.isChecked() else 0
        print(Channel)
        print(HubID)
        print(RTNumber)
        print(VibFreq)
        print(VibMag)
        print(Temp)
        print(MagneticEvent)
        print(PIREvent)
        Packet = []
        Packet.append(0xFA)
        if Channel == 'Right':
            Packet.append(0x01)
        elif Channel == 'Left':
            Packet.append(0x02)
        Packet.append(0xC0)
        Packet.append(0xA8)
        Packet.append(0x01)
        Packet.append(0x64+self.combo_hub.currentIndex())
        '''
        if HubID == 'HUB 1':
            Packet.append(0x64)
        elif HubID == 'HUB 2':
            Packet.append(0x65)
        elif HubID == 'HUB 3':
            Packet.append(0x66)
        elif HubID == 'HUB 4':
            Packet.append(0x67)
        elif HubID == 'HUB 5':
            Packet.append(0x68)
        elif HubID == 'HUB 6':
            Packet.append(0x69)
        '''
        ########### RT Number #############
        Packet.append(((RTNumber & 0xF0)>>4) + 0x00)
        Packet.append((RTNumber & 0x0F) + 0x10)
        ######### Vib Freq Number #########
        Packet.append(((VibFreq & 0xF0)>>4) + 0x20)
        Packet.append((VibFreq & 0x0F) + 0x30)
        ######### Vib Mag Number ##########
        Packet.append(((VibMag & 0xF000)>>12) + 0x40)
        Packet.append(((VibMag & 0x0F00)>>8) + 0x50)
        Packet.append(((VibMag & 0x00F0)>> 4) + 0x60)
        Packet.append((VibMag & 0x000F) + 0x70)
        ######### Temperature #############
        Packet.append(((Temp & 0x0F00)>>8) + 0x80)
        Packet.append(((Temp & 0x00F0)>> 4) + 0x90)
        Packet.append((Temp & 0x000F) + 0xA0)
        ######### Magnetic and PIR #########
        if (MagneticEvent == True) and (PIREvent == True):
            Packet.append(0xB3)
        elif (MagneticEvent == True) and (PIREvent == False):
            Packet.append(0xBF)
        elif (MagneticEvent == False) and (PIREvent == True):
            Packet.append(0xBC)
        else:
            Packet.append(0xB0)
        Packet.append(0xC0)
        Packet.append(0xD0)
        Packet.append(0xE0)
        Packet.append(0xFB)
        #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#
        #Packet = b'bhaskar'
        print(bytes(Packet))
        try:
            self.sock.send(bytes(Packet))
        except:
            print('Tansmission Failed')
########################################################################################################################
if __name__ == "__main__":
    #BuildEventPacket(HubID='HUB 1',Channel='Right',RTNumber=16,VibFreq=95,VibMag=10000,Temp=40,MagneticEvent = True, PIREvent = False)
    app=QApplication(sys.argv)
    sum=Simulator()
    sum.show()
    sys.exit(app.exec_())
########################################################################################################################