########################################################################################################################
import datetime
import json
from datetime import datetime
import socket,selectors,types
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
import pandas as pd

########################################################################################################################
class HubServer(QtCore.QThread):
    # Create a counter thread
    posteventdata = QtCore.pyqtSignal(str)
    change_value = QtCore.pyqtSignal(str)
    posthealthdata = QtCore.pyqtSignal(str)
   # postevent = QtCore.pyqtSignal(dict)
   # posthealthevent = QtCore.pyqtSignal(dict)
    ####################################################################################################################
    def __init__(self):
        super().__init__()
        self.StopFlag = False

        self.HEADER_INDEX = 0
        self.CHANNEL_INDEX = 1
        self.IPADDR_INDEX = 2
        self.RTID_INDEX = 6
        self.VIBFRQ_INDEX = 8
        self.VIBMAG_INDEX = 10
        self.TEMP_INDEX = 14
        self.MAGN_INDEX = 17
       # self.CAM_DWELL_TIME = 10
       # self.CAM_HOLD_TIME = 10


        try:
            self.pd_sensorconfig = pd.read_csv('sensorconfiginfo.csv')
        except:
            print('sensorconfiginfo.csv file missing')
            self.change_value.emit('sensorconfiginfo.csv file missing')
        #print(self.pd_sensorconfig)
        try:
            self.pd_TempTable = pd.read_csv('Temperature.csv')
            # print(pd_HubIPConfig)
        except:
            print('Temperature.csv file missing')
            self.change_value.emit('Temperature.csv file missing')
            #exit(0)
        try:
            self.pd_Event_Thresholds = pd.read_csv('EventThresholds.csv')
            # print(pd_HubIPConfig)
        except:
            print('EventThresholds.csv file missing')
            self.change_value.emit('EventThresholds.csv file missing')

        self.ServerIP = 'localhost'
        self.Port   = 5555
    ####################################################################################################################
    def Extract_Engg_Values(self,data):
        if (len(data) >= 22):
            hub_id = str(data[self.IPADDR_INDEX]) + '.' + str(data[self.IPADDR_INDEX + 1]) + '.' + str(
                data[self.IPADDR_INDEX + 2]) + '.' + str(data[self.IPADDR_INDEX + 3])

            RT_ID = ((data[self.RTID_INDEX] & 0x0f) << 4) + (data[self.RTID_INDEX + 1] & 0x0f)

            VibFreq = ((data[self.VIBFRQ_INDEX] & 0x0f) << 4) + (data[self.VIBFRQ_INDEX + 1] & 0x0f)

            VibMag = ((data[self.VIBMAG_INDEX] & 0x0f) << 12) + ((data[self.VIBMAG_INDEX + 1] & 0x0f) << 8) + (
                    (data[self.VIBMAG_INDEX + 2] & 0x0f) << 4) + (data[self.VIBMAG_INDEX + 3] & 0x0f)

            ADC = ((data[self.TEMP_INDEX] & 0x0f) << 8) + ((data[self.TEMP_INDEX + 1] & 0x0f) << 4) + (
                        data[self.TEMP_INDEX + 2] & 0x0f)

            Magnetic = True if ((data[self.MAGN_INDEX]  == 0xBF) or (data[self.MAGN_INDEX]  == 0xB3))  else False
            PIR  = True if (data[self.MAGN_INDEX]  == 0xBC) else False

            channel = 'Right' if data[1] == 1 else 'Left'

            try:
                sensitivity = self.pd_sensorconfig.loc[((self.pd_sensorconfig['channel']==channel) &
                                                      (self.pd_sensorconfig['hub']==hub_id) &
                                                      (self.pd_sensorconfig['sensorid']==RT_ID),'sensitivity')].values[0] #(self.sensorconfig['']=hub_id,hub_channel=channel, sensor_id=RT_ID)
            except:
                errormsg = f'Invalid Sensor Mapping: \n\tHub Id : {hub_id}\n\tChannel : {channel}\n\tSensor Id : {RT_ID}'
                status = False
                return status, None, errormsg

            try:
                Temp = self.pd_TempTable.loc[(self.pd_TempTable['ADC'] == ADC), 'Temperature'].values[0]
            except:
                print('*** Invalid Temperature Count Value ****')
                return False, None, 'Invalid Temperature'
           # sensitivity = sensor_details['sensitivity'][0]
            Event = {
                        'date'                      :  datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                        'hub_id'                    :  '192.168.1.100',
                        'hub_channel'               :  channel,
                        'sensor_id'                 :  RT_ID,
                        'event'                     :  'Vibration',
                    }
            try:
                VibrationFrqthreshold = self.pd_Event_Thresholds.loc[
                    (self.pd_Event_Thresholds['Parameter'] == sensitivity), 'Threshold'].values[0]
                VibrationMgnthreshold = self.pd_Event_Thresholds.loc[
                    (self.pd_Event_Thresholds['Parameter'] == sensitivity), 'Width'].values[0]
                Temperaturethreshold = self.pd_Event_Thresholds.loc[
                    (self.pd_Event_Thresholds['Parameter'] == 'Temperature'), 'Threshold'].values[0]
            except:
                print('Invalid Sensitivity')
                return False, None, 'Invalid Sensitivity'
            #Temperaturethreshold = 60 #sensor_details['fire_trigger'][0]
            print('Read Temperature',Temp)
            print('Threshold',Temperaturethreshold)
            if Temp >= Temperaturethreshold:
                Event['event'] = 'fire'
            elif Magnetic == True:
                Event['event'] = 'smart_patrol'
            elif PIR == True:
                Event['event'] = 'early_warning'
            elif (VibFreq >= VibrationFrqthreshold):
                #elif (VibFreq >= VibrationFrqthreshold) and (VibMag > VibrationMgnthreshold):
                Event['event'] = 'vibration'
            else:
                Event['event'] = None
            #if VibFreq !=0:
         #   print('********************************************************************************************')
         #   print(Event)
         #   print('*********************************************************************************************')
            status = False
            if Event['event'] is not None:
                status = True

        return status,Event,None
    ####################################################################################################################
    def group(L=[]):
        first = last = L[0]
        bins = []
        for n in L[1:]:
            if n - 1 <= last:  # Part of the group, bump the end
                last = n
            else:  # Not part of the group, yield current group and start a new
                #yield first, last
                bins.append((first,last))
                first = last = n
        #yield first, last  # Yield the last group
        return bins
    ####################################################################################################################
    def group_sensors(self,sensorlist=[]):
        #x = self.group(L=sensorlist)
        first = last = sensorlist[0]
        bins = []
        for n in sensorlist[1:]:
            if n - 1 <= last:  # Part of the group, bump the end
                last = n
            else:  # Not part of the group, yield current group and start a new
                #yield first, last
                bins.append((first,last))
                first = last = n
        bins.append((first,last))
        #bins = self.group(L=sensorlist)
    #    width = [bins[i][1] - bins[i][0] + 1 for i in range(len(bins))]

        inactive_sensors = []
    ##    for i in range(0, len(bins)):
    #        sensorid = f'{bins[i][0]}-{bins[i][1]}' if width[i] > 1 else f'{bins[i][0]}'
    #        inactive_sensors.append(sensorid)
        return f'{bins}'
    ####################################################################################################################
    def Exctract_Health_Status(self,HealthData, StartRT=1, EndRT=150):
        if len(HealthData) < 37 :
            return False, None
        HealthEvent = {
                        "hubid": "192.168.1.100",
                        "channel": "Right",
                        'inactivesensorlist': []
                      }
        # print(type(StartRT),type(EndRT))
        IPAddress = f'{HealthData[1]}.{HealthData[2]}.{HealthData[3]}.{HealthData[4]}'

        healthdata = HealthData[5:37]
        bytes_as_bits = ''.join(format(byte, '08b')[::-1] for byte in healthdata)
        #print('***********************8',HealthData[0])
        if HealthData[0] == 0xFD:
            HealthEvent['channel'] = 'Right'
        else:
            HealthEvent['channel'] = 'Left'

        hub_id = self.hubdb.GetHupIpMappingInfo(ipaddress=IPAddress)
        if hub_id == None:
            return False, HealthEvent
        HealthEvent['hubid'] = hub_id
        ConfigSensorList = self.sensorconfigdb.GetSensorList(hub_id=HealthEvent['hubid'], hub_channel=HealthEvent['channel'])
        SensorHealthStatus = list(bytes_as_bits)
      #  print('List of Configured Sensors:',ConfigSensorList)
        FaultySensorList = []
        for i in range(len(SensorHealthStatus)):
            if SensorHealthStatus[i] == '1':
                FaultySensorList.append(i)
        faultlist = [x for x in FaultySensorList if x in ConfigSensorList]
        # print('#################### Health Event ###################################')
        # print('Hub ID :',HealthEvent['Hub ID'])
        # print('Channel:',HealthEvent['Channel'])
        # print('List of non responding Sensors',faultlist)
        # print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        if len(faultlist) == 0:
            HealthEvent['inactivesensorlist'] = []
        else:
            HealthEvent['inactivesensorlist'] = self.group_sensors(faultlist)
        #  print(HealthEvent)

        return True,HealthEvent
    # Exctract_Health_Status(healthdata)
    ####################################################################################################################
    def run(self):
        GUI_CONNECT = b'Command Controller'
        GUI_Client_Conn_Status = False
        GUI_sock = None
        sel = selectors.DefaultSelector()
        # host = '192.168.1.150'  # Standard loopback interface address (localhost)
        # host = 'DESKTOP-E9LCLCN'  # Standard loopback interface address (localhost)
        port = self.Port  # Port to listen on (non-privileged ports are > 1023)
        # host = socket.gethostname()
        #IPAddr = socket.gethostbyname(host)
        IPAddr = self.ServerIP
        #print('********',self.ServerIP)
        # self.change_value.emit("Your Computer Name is:" + host)
        # self.change_value.emit("Your Computer IP Address is:" + IPAddr)
        try:
            lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            lsock.settimeout(1)
            lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            lsock.bind((IPAddr, port))
            lsock.listen()
            self.change_value.emit(f'{datetime.now().today().strftime("%d-%m-%Y %H:%M:%S")} HUB Server listening on : ({self.ServerIP},{port})')
            # print('listening on', (host, port))
            lsock.setblocking(False)
            sel.register(lsock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=None)
        except:
            self.change_value.emit(f'LAN inactive or set IP Address of Computer to {IPAddr}')
            return
        ################################################################################################################
        def accept_wrapper(sock):
            # print('trying for connection')
            conn, addr = sock.accept()  # Should be ready to read
            self.change_value.emit(f'{datetime.now().today().strftime("%d-%m-%Y %H:%M:%S")} Hub Server accepted connection from :' + str(addr))
            # print('accepted connection from', addr)
            conn.setblocking(False)
            data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
            sel.register(conn, events, data=data)
            return conn, addr
        ################################################################################################################
        activesocklist = []
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        while self.StopFlag == False:
            try:
                events = sel.select(timeout=1)
            except:
                print("error")
            for key, mask in events:
                try:
                    if key.data is None:
                        # print('if condition')
                        # print(key.fileobj)
                        conn, addr1 = accept_wrapper(key.fileobj)
                        #    print(conn,addr1)
                        activesocklist.append(conn)
                    else:
                        sock = key.fileobj
                        data = key.data
                        # data = service_connection(key, mask)
                        if mask & selectors.EVENT_READ:
                            recv_data = sock.recv(1024)  # Should be ready to read
                            if recv_data:
                                data.inb = recv_data
                                if (recv_data[0] == 0xfa):
                                    for i in range(len(recv_data) // 22):
                                    #for i in range(0,1):
                                        status,Event,errormsg = self.Extract_Engg_Values(recv_data[i * 22:])
                                        if status == True:
                                            self.change_value.emit(f'{Event}')
                                            if GUI_Client_Conn_Status == True:
                                                GUI_sock.send(bytes(json.dumps(Event),encoding="utf-8"))
                                elif (recv_data[0] == 0xfd) or (recv_data[0] == 0xfe):
                                    pass
                                    #HealthStatus, HealthEvent = self.Exctract_Health_Status(recv_data)
                                    #if self.SensorHealthDataUpdateFlag == True:
                                    #    self.posthealthdata.emit(str(HealthEvent))
                                    '''
                                    HS_dict = {'date': datetime.datetime.now(),
                                              'channel': 'left',
                                              'inactivesensorlist': [1, 9, 4, 8]
                                              }
                                    self.pidsdb.InsertintoHealthEventDBTable(HS_dict)
                                    self.pidsdb.GetFromHealthEventDBTable(datetime.datetime.now() - datetime.timedelta(hours=1),
                                                                 datetime.datetime.now())
                                    print(self.pidsdb.CurDbTable)
                                    '''
                                elif recv_data == GUI_CONNECT:
                                    if (GUI_Client_Conn_Status == False):
                                    #if ((GUI_Client_Conn_Status == False) or (data.addr == GUI_IPAddr)):
                                        self.change_value.emit('Connected to GUI :' + str(data.addr))
                                        #self.change_value.emit('######  GUI Link Up  #######\n')
                                        GUI_Client_Conn_Status = True
                                        GUI_IPAddr = data.addr
                                        print(GUI_IPAddr)
                                        GUI_sock = sock
                                        # GUI_sock(b'Connection Established')
                                        # GUI_Port = data.addr[1]
                                        # print(data.addr,GUI_IPAddr,GUI_Port)
                                    else:
                                        self.change_value.emit(
                                            'GUI Client Already Connected.\nRejecting Connection Request from :' + str(
                                                data.addr))
                                        sel.unregister(sock)
                                        sock.close()
                                        GUI_Client_Conn_Status = False
                                else:
                                  #  self.change_value.emit ('######  GUI Link Down  #######\n')
                                    #print('Link Down')
                                    pass
                            else:
                                self.change_value.emit('closing connection to :' + str(data.addr))
                               # GUI_Client_Conn_Status = False
                                # print('GUI',GUI_IPAddr,GUI_Port)
                                # print('closing connection to', data.addr)
                                # if (data.addr == GUI_IPAddr) :
                                #    self.change_value.emit('GUI_Client Closed' )
                                sel.unregister(sock)
                                sock.close()
                                activesocklist.remove(sock)
                                print('sock' + str(sock))
                except:
                    print('If Error')
                    print(key.fileobj)
                    s1 = key.fileobj
                    sel.unregister(s1)
                    s1.close()
                    activesocklist.remove(s1)
                    print('Socket Closed')
        print('Number of Active Sockets', len(activesocklist))
        for s1 in activesocklist:
            sel.unregister(s1)
            s1.close()
            print(s1)
        # activesocklist.remove(sock)
        sel.unregister(lsock)
        lsock.close()
    ####################################################################################################################