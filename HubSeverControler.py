########################################################################################################################
import json
import os
import sys
import time
from datetime import datetime

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap

import json
from uuid import getnode
#from Encrypt1 import File_Encrypter
#from Decrypt import decrypt_JSON
from HubServerThread import HubServer
import pandas as pd
########################################################################################################################
class Server_Config(QtWidgets.QDialog):
    def __init__(self):
        super(Server_Config, self).__init__()
        self.setWindowTitle("Server Config")
        self.setFixedWidth(400)
        self.setFixedHeight(200)

        self.label_ServerIP = QtWidgets.QLabel("Server IP",self)
        self.label_ServerIP.setGeometry(40,50,100,30)
        self.label_ServerIP.setText("Server IP")
        font = QtGui.QFont()
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(12)
        font.setPointSize(10)
        self.label_ServerIP.setFont(font)

        self.label_port_number = QtWidgets.QLabel("Port Number",self)
        self.label_port_number.setGeometry(20,50,100,150)
        font = QtGui.QFont()
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(12)
        font.setPointSize(10)
        self.label_port_number.setFont(font)

        self.lineedit_ServerIP = QtWidgets.QLineEdit(self)
        self.lineedit_ServerIP.setGeometry(130,50,200,30)
        self.lineedit_ServerIP.setPlaceholderText("Enter Server IP Addres")

        self.lineedit_portnumber = QtWidgets.QLineEdit(self)
        self.lineedit_portnumber.setGeometry(130, 110, 200, 30)
        self.lineedit_portnumber.setPlaceholderText("Enter Port Number")
########################################################################################################################
class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.Launch()
########################################################################################################################
    def Launch(self):
        App.aboutToQuit.connect(self.Exit)
        # self.Path="Site_Info/"
        self.FolderPath = 'Site_Info'
        # self.Path = self.FolderPath
        self.setWindowTitle(self.tr("ITS-999 PIDS HUB Server"))
        self.setFixedSize(650, 900)
        self.Widgets()
        self.setWindowIcon(QtGui.QIcon('Resources/HubServer.ico'))
        self.dialogs = list()  # to open modelless camera popup

    ####################################################################################################################
    def Widgets(self):
        self.ClearDispCount = 0
        self.Tab_Show = False

        '''
        self.view = QtWebEngineWidgets.QWebEngineView(self)
        self.view.setGeometry(QtCore.QRect(0, 0, 800, 890))
        self.view.setAutoFillBackground(True)
        '''

        self.TextServer = QtWidgets.QTextEdit(self)
        self.TextServer.setGeometry(QtCore.QRect(25, 50, 600, 820))
        self.TextServer.setReadOnly(False)
        self.TextServer.hide()
        # self.TextServer.setStyleSheet("text-color: rgb(0,255,255);")

        self.ToolBar = QtWidgets.QToolBar(self)
        self.ToolBar.setGeometry(QtCore.QRect(25, 0, 600, 50))
        self.ToolBar.setIconSize(QtCore.QSize(65, 35))
        self.ToolBar.setMovable(True)
        # self.ToolBar.setStyleSheet("{background-color:rgba(255,255,255,0);}")

        self.Health_Data = QtWidgets.QAction(self)
        self.Health_Data.setText("Show Health Event")
        self.Health_Data.setIcon(QtGui.QIcon('Resources/Healthgreen.png'))
        self.Health_Data.triggered.connect(self.SensorHealthDataUpdate)
        self.ToolBar.addAction(self.Health_Data)

        self.Clear_All_Events = QtWidgets.QAction(self)
        self.Clear_All_Events.setText("Clear All Events")
        self.Clear_All_Events.setIcon(QtGui.QIcon('Resources/Clear.png'))
        self.Clear_All_Events.triggered.connect(self.Clear)
        self.ToolBar.addAction(self.Clear_All_Events)
        '''
        self.Start_Server = QtWidgets.QAction(self)
        self.Start_Server.setText("Start Server")
        self.Start_Server.setIcon(QtGui.QIcon('Resources/startserver.png'))
        self.Start_Server.setDisabled(True)
        self.Start_Server.triggered.connect(self.Server_Start)
        self.ToolBar.addAction(self.Start_Server)

        self.Stop_Server = QtWidgets.QAction(self)
        self.Stop_Server.setText("Stop Server")
        self.Stop_Server.setIcon(QtGui.QIcon('Resources/StopServer.png'))
        self.Stop_Server.triggered.connect(self.Server_Stop)
        self.ToolBar.addAction(self.Stop_Server)
        
        self.Reports = QtWidgets.QAction(self)
        self.Reports.setText("Reports")
        self.Reports.setIcon(QtGui.QIcon('Resources/Reports.png'))
        self.Reports.triggered.connect(self.Reportsmenu)
        self.ToolBar.addAction(self.Reports)
        
        self.Settings = QtWidgets.QAction(self)
        self.Settings.setText("Settings")
        self.Settings.setIcon(QtGui.QIcon('Resources/Settings-icon.png'))
        self.Settings.triggered.connect(self.Setting)
        self.Settings.setShortcut('S')
        self.ToolBar.addAction(self.Settings)
        '''
        self.About = QtWidgets.QAction(self)
        self.About.setText("Developer")
        self.About.setIcon(QtGui.QIcon('Resources/About.png'))
        self.About.triggered.connect(self.Developer)
        self.ToolBar.addAction(self.About)

        '''
        self.dbthread = myDataBaseThread()
        if not self.dbthread.pidsdb.connection:
            QtWidgets.QMessageBox.warning(self, "Warning !!!", "Filed to connect with Database")
        # dbthread = myDataBaseThread()
        if self.dbthread.pidsdb.connection:
            self.dbthread.start()
        '''
        self.Server_Start()
        self.DatabaseFlag = False
        self.SensorHealthDataUpdateFlag = False
        ########################################################################################################################

        self.FirstTimeFlag = True
        # [time.time() - 60 for _ in range(self.pd_SensConfig.shape[0])]
        # print(self.pd_HubChannels)
        # print(self.pd_HubChannels.shape)
        #self.TextServer.hide()

        self.label_licensed = QtWidgets.QLabel(self)
        self.label_licensed.setGeometry(QtCore.QRect(100, 280, 300, 20))
        #self.label_licensed.setText('Licensed to:')
        font = QtGui.QFont()
        font.setItalic(True)
        font.setUnderline(True)
        font.setWeight(12)
        font.setPointSize(10)
        self.label_licensed.setFont(font)

        self.label_licensed.setVisible(False)

        self.label_custlogo = QtWidgets.QLabel(self)
        with open('Site_Info/AppLogoConfig.json') as f:
            self.LogoCongig = json.load(f)

        self.X_axis = 400
        self.Y_axis = 300
        self.Width = 400
        self.Height = 300
        self.label_custlogo.setGeometry(QtCore.QRect(200,350,self.Width,self.Height))
        self.pixmap = QPixmap('Resources/AppLogo.png')
        self.label_custlogo.setPixmap(self.pixmap)
    ####################################################################################################################
    # Author : Burugu Aditya
    # Centers the Map
    ####################################################################################################################
    def SensorHealthDataUpdate(self):
        if self.SensorHealthDataUpdateFlag == True:
            self.SensorHealthDataUpdateFlag = False
            self.Health_Data.setIcon(QtGui.QIcon('Resources/Healthgreen.png'))
            self.Health_Data.setToolTip('Show Health Event')
            self.label_licensed.show()
            self.label_custlogo.show()
            self.TextServer.hide()
        else:
            self.SensorHealthDataUpdateFlag = True
            self.TextServer.show()
            self.label_licensed.hide()
            self.label_custlogo.hide()
            self.Health_Data.setToolTip('Hide Health Event')
            self.Health_Data.setIcon(QtGui.QIcon('Resources/Health.png'))
    ################################################################################################################
    def Reportsmenu(self):
        '''
        self.dbthread.pidsdb.DropHealthDataBaseTable()
        self.dbthread.pidsdb.DropVibrationDataBaseTable()
        self.dbthread.pidsdb.GetTemperatureEventTable()
        self.dbthread.pidsdb.DropMagnDataBaseTable()
        '''
       # self.reports = Reports()
       # self.reports.show()

    def Table_Visible(self):
        if self.Tab_Show == False:
            self.tableWidget.show()
            self.dock.show()
            # self.tableWidget.setDisabled(True)
            self.Tab_Show = True
        else:
            self.tableWidget.hide()
            self.dock.hide()
            self.Tab_Show = False
    ####################################################################################################################
    def reload(self):
        self.view.reload()
    ####################################################################################################################
    def Server_Start(self):
        self.TextServer.append("Server Started")
        #  self.button.setEnabled(False)
        #  self.button1.setEnabled(True)
#        self.Stop_Server.setEnabled(True)
 #       self.Start_Server.setEnabled(False)
        # self.Text.append("Server Started")
        self.thread = HubServer()
        try:
            with open('Site_Info/ServerConfigInfo.JSON') as f:
                ServerConfigDict = json.load(f)
            print(ServerConfigDict['HUBServerIP'])
            self.thread.ServerIP = ServerConfigDict['HUBServerIP']
            self.thread.Port = ServerConfigDict['HubServerPort']
        except:
            #print('SensorConfigInfo file missing')
            reply = QtWidgets.QMessageBox.question(self, "ServerConfigInfo File Missing?",
                                           f'''ServerConfigInfo.JSON File is not found in\n {os.getcwd()}\nDo you want to continue Hubserver with localhost''')
            if reply == QtWidgets.QMessageBox.Yes:
                self.thread.ServerIP = '0.0.0.0'
            else:
                exit(0)

        self.thread.change_value.connect(self.setProgressVal)
        self.thread.StopFlag = False
        self.thread.start()
    ####################################################################################################################
    def Server_Stop(self):
        self.thread.StopFlag = True
        self.Stop_Server.setEnabled(False)
        self.Start_Server.setEnabled(True)
        # self.TextServer.append("Server Disconnected")
        # self.thread.exit()
        # self.ServerStopFlag = True
    ####################################################################################################################
    def setProgressVal(self, val):
        if (self.ClearDispCount > 50):
            self.ClearDispCount = 0
            self.TextServer.clear()
            # self.TextServer.setText(val)
        else:
            # pass
            self.TextServer.append(val)
        self.ClearDispCount = self.ClearDispCount + 1
        # self.Text.setText(val)
        # print(val)
    ####################################################################################################################
    def Exit(self):
        #self.dbthread.DataBaseEnableFlag = False
        #self.dbthread.pidsdb.close()
        self.thread.StopFlag=True
        print('exit')
    ####################################################################################################################
    def Clear_ServerText(self):
        self.TextServer.clear()
    ####################################################################################################################
    def Clear(self):
        self.TextServer.clear()
    ####################################################################################################################
    def Developer(self):
        Dialog = QtWidgets.QDialog()
        ui = Ui_Dialog()
        ui.setupUi(Dialog)
        Dialog.exec_()
    ####################################################################################################################
    def Setting(self):
        self.ServerApp=Server_Config()
        self.ServerApp.show()
        print('Settings')
    ####################################################################################################################
class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        Dialog.setWindowOpacity(1.0)
        Dialog.setWindowTitle("Developer's Info")
        Dialog.setWindowIcon(QtGui.QIcon('About.png'))

        Developer_Details = QtWidgets.QLabel(Dialog)
        Developer_Details.setText('Developed by:\n    I Square Systems,Hyderabad')
       # Developer_Details.setAlignment(QtCore.Qt.AlignCenter)
        Developer_Details.setGeometry(QtCore.QRect(180,130,200,100))
        font = QtGui.QFont()
        font.setItalic(True)
        font.setWeight(6)
        font.setPointSize(6)
        Developer_Details.setFont(font)
       # self.setWindowIcon(QtGui.QIcon('Resources/Platinum.png'))
        label_Image = QtWidgets.QLabel(Dialog)

        label_Image.setGeometry(QtCore.QRect(40,0,250,300))
        pixmap = QPixmap('Resources/AppLogoSmall.png')
        label_Image.setPixmap(pixmap)
    ####################################################################################################################
if __name__ == "__main__":
    App = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec())
########################################################################################################################