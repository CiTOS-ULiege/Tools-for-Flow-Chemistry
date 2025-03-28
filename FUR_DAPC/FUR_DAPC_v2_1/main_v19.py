# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 23:46:50 2024

@author: Hubert
This prgoram reads data through serial connection from several devices used in the continuous
furfural nitration platform. The program allows also sending commands to some of these devices
(pumps and in-house made Arduino based modules like Filtration and Separation Module Control
Unit (FSMCU) or Nitric Acid Dosing Controller (NADC)).

This program uses multiple threads and queues to allow simultaneous communication with multiple
serial devices. 
Data is dequeud from apropriate queues obtained from subroutins for all devices. Each value
(for example pressure from P1) is placed in apropriate place of dictionary. Positoning of values
in current version is preset in the code (which could be actualized in future versions of the
program). All the data are placed in single dictionary with a current timestampe (UNIX time)
and then concatenated to a pandas Data Frame, which is then saved in real time to a file. The
Data Frame is also kept in memory, allowing plotting it in real time using Python matplotlib or
other libraries (this functionality is not present yet in current version).
Data is dequeued with higer frequecy than the frequency of data being enqueued, what prevents
saving outdated values. This dequeuing frequency depends on time.sleep() commands. Transferring
to the new line for being saved in the Data Frame occurs with 1 Hz frequency, dictated by the
presence of change in the timestamp (UNIX).

Serial configurations for all devices are in the file "configFile.txt", which is read when the
program is started and serial configurations are configured. All serial objects are stored in a
list which is later used for transmitting them to appropriate subroutines. Program uses multiple
custom-made functions saved in separate files.

The current version of program does not contain GUI (Graphical User Interface) and is operated
in the command line. The human-interface in current version is realised by writing commands
using the command line.



Devices:
    balance, ptmb02, ptmb03, 


"""

import serial
import time
from datetime import date#, datetime
import threading
import numpy as np
import pandas as pd
import sys
from queue import Queue, Empty

#custom files:
from events import stop_event
from configfile import readComConf 
from comReceivers_v3 import balanceCom, ptmbCom
from flomComm import flomStatusRead, flomPumpStart, flomPumpStop, flomSetFlowRate
from knauerComm_v1 import knauerStatusRead, knauerPumpStart, knauerPumpStop, knauerSetFlowRate
from fsmcuCom_v2 import fsmcuCom, fsmcuSendComand
from nadcCom import nadcStatusRead, nadcSendComand

#configuration of filenames and pathway
path1 = r'C:\DATA\FUR_Project\Software\FUR_DAPC_v2_1_cmd_07102024\\' # Where is configuration file
configFile = path1 + 'config.txt'

path2 = r'C:\DATA\FUR_Project\LB_amine_low_temp_10102024\\'  # Where to save data frame. Double backslash to escape the backslash
df_save_f = path2 + r"EXP_DF_" + str(date.today()) + '_' + time.strftime("%H%M%S", time.localtime()) + ".txt" # Add date and time to the file

# Below is info to be displayed in the command line interface
menu_cmd_print = "Main menu: \n"\
    +"Type: 'p1'   - to enter P1, Flom pump menu \n"\
    +"Type: 'p4'   - to enter P4, Knauer pump menu \n"\
    +"Type: 'p5'   - to enter P5, Knauer pump menu \n"\
    +"Type: 'p9'   - to enter P9, Knauer pump menu \n"\
    +"Type: 'fsm'  - to enter FSMCU control menu \n"\
    +"Type: 'nadc' - to enter NADC control menu \n"\
    +"Type: 'stat' - to display status of the pumps \n"\
    +"Type: 'end'  - to terminate the program \n"\

fsmcu_commands_print = "Filtration and Separation Module Control Unit (FSMCU)\n"\
    + "Commands: \n" \
    + "Type: '1 x'     : Manual Sep Valve control, x=0:OFF, x=1:ON \n" \
    + "Type: '2'       : AUTO sep valve control \n"\
    + "Type: '3 x'     : Manual Bypass Valve control, x=0:OFF, x=1:ON \n" \
    + "Type: '4 x y z' : Manual Servo Valves control, x,y,z can be 0 or 1 (OFF or ON) \n" \
    + "Type: '5 x y'   : Semi-Auto Servo Valves control, x - filter choice \n" \
    + "          x=0: filter 1, x=1: filter 2, y: washing vavlve control \n" \
    + "          y=0: wash input 1, y=1:wash input 2 \n"\
    +  "Type 'e' to return to previous menu \n"

nadc_commands_print = "Nitric Acid Dosing Controller (NADC)\n"\
    + "Commands: \n"\
    + "Type: '1 x' - postion of S1, HNO3/H2O valve (0: H2O, 1: HNO3) \n"\
    + "Type: '2 x' - position of S2,  reactor/prime valve (0: prime, 1: reactor) \n"\
    + "Type: '3 x' - state of P, peristaltic pump (0: OFF, 1: ON) \n"\
    + "Type: 'e' to return to previous menu \n"

#Pumps menu
pump_options_print = "Options: \n"\
    +  "Type: '0' to switch the pump OFF \n"\
    +  "Type: '1' to switch the pump ON \n"\
    +  "Type: 'f xxxx' to change the flowrate of the pump \n"\
    +  "(Flow rate value in μL/min) \n"\
    +  "Type 'e' to return to previous menu \n"

#Column names placed below can be later placed in a file and loaded as other seetings
#Flom pump data format header:
flom_header = ['P1_Q', 'P1_p', 'P1_s']
#Balance data
    # Single data point
#Other pumps:
    #
#PTMBs data format headers
ptmb02_header = ['PTMB02_T', 'PTMB02_p']
ptmb03_header = ['PTMB03_T', 'PTMB03_p']
#FSMCU data format header:
fsmcu_header = ['FSM_HS1', 'FSM_HS2', 'FSM_HS3', 'FSM_HS4', 'FSM_p',
                'FSM_sep_v', 'FSM_byp_v', 'FSM_serv_v1', 'FSM_serv_2',
                'FSM_serv_v3', 'FSM_flt_mod', 'FSM_sep_mod']
#Knauer pumps
knaP4_header = ['P4_Q', 'P4_p', 'P4_s']  # Knauer P4, 6 M KOH
knaP5_header = ['P5_Q', 'P5_p', 'P5_s']  # Knauer P5, MeTHF
knaP9_header = ['P9_Q', 'P9_p', 'P9_s']  # Knauer P9, washing of FSM
#NADC Nitric Acid Dosing Controler
nadc_header = ['NADC_S1', 'NADC_S2', 'NADC_PP'] #Servo1, Servo2 and Peristaltic Pump


#Creating a list with names of all columns
column_names = ['timestamp'] + flom_header + ['bal.'] + ptmb02_header + ptmb03_header + fsmcu_header + knaP4_header\
    + knaP5_header + knaP9_header + nadc_header
df1 = pd.DataFrame(columns=column_names) 
        
def dataReceiving1(column_names, que1, que2, que3, que4, que5, que6, que7, que8, que9):
    c_n = column_names #this is used for placing data in correct places of dictionary new_row
    new_row = {}
    timing = int(time.time())
    previous_timing = int(time.time())
    #while loop checking if stop_even was not set, if yes then it stops executing
    while not stop_event.is_set():
        #timeloop, using time.time and comparing timestamp
        if timing == previous_timing:
            previous_timing = int(time.time())
            
            try:   # Check data queue1, ptmb02
                data1 = que1.get_nowait()
                if data1: #saving col.5: ptmb02_T and col.6: ptmb02_p
                    new_row.update({c_n[5]: data1[1], c_n[6]: data1[2]})
            except Empty:
                pass  # No data received, continue checking in_queue2
            
            try: # Check data from queue2, ptmb03
                data2 = que2.get_nowait()    
                if data2: #saving col.7: ptmb03_T and col.8: ptmb03_p       
                    new_row.update({c_n[7]: data2[1],c_n[8]: data2[2]})
            except Empty:
                pass  # No data received
            
            try:  #Check data from queue3, ballance
                data3 = que3.get_nowait()    
                if data3: #saving col.4: bal.   
                    new_row.update({c_n[4]: data3[1]})
            except Empty:
                 pass  # No data received
            
            try:  #Check data from queue4, flom pump
                data4 = que4.get_nowait()    
                if data4 :#saving col.1: P1_Q, col.2: P1_p and col.3: P1_s   
                    new_row.update({c_n[1]: data4[1], c_n[2]: data4[2], c_n[3]: data4[3]})                
            except Empty:
                 pass  # No data received   
            
            try:  #Check data from queue5, FSMCU
                data5 = que5.get_nowait()    
                if data5 :#saving col.9 to col.20, FSMCU data from queue5
                    #start of FSMCU datapoints in c_n is row no.9, the number of datapoitns is 12
                    i=0
                    for i in range(9,21):
                        new_row.update({c_n[i]: data5[i-8]})                
            except Empty:
                 pass  # No data received                    
            
            try:  #Check data from queue6, Knauer P4 pump
                data6 = que6.get_nowait() 
                if data6:#saving col.21: P4_Q, col.22: P4_p and col.23: P4_s   
                    new_row.update({c_n[21]: data6[1], c_n[22]: data6[2], c_n[23]: data6[3]})                
            except Empty:
                 pass  # No data received   

            try:  #Check data from queue7, Knauer P5 pump
                data7 = que7.get_nowait() 
                if data7:#saving col.24: P5_Q, col.25: P5_p and col.26: P5_s   
                    new_row.update({c_n[24]: data7[1], c_n[25]: data7[2], c_n[26]: data7[3]})                
            except Empty:
                 pass  # No data received                    

            try:  #Check data from queue8, Knauer P9 pump
                data8 = que8.get_nowait() 
                if data8:#saving col.27: P9_Q, col.28: P9_p and col.29: P9_s   
                    new_row.update({c_n[27]: data8[1], c_n[28]: data8[2], c_n[29]: data8[3]})                
            except Empty:
                 pass  # No data received     
                         
            try:  #Check data from queue9, NADC mdoule
                data9 = que9.get_nowait() 
                if data9: #saving col.30: NADC_S1, col.31: NADC_S2 and col.32: NADC_PP   
                    new_row.update({c_n[30]: data9[1], c_n[31]: data9[2], c_n[32]: data9[3]})                
            except Empty:
                 pass  # No data received                   
                 
            time.sleep(0.1)
        else:     
            # after timing loop, add timestamp
            #previous_timing = time.time()
            timing = int(time.time())  
            new_row.update({'timestamp': [int(time.time())]})
            addingToDF(new_row)
            time.sleep(0.05)
            for element in column_names:
                new_row = {element: [np.nan]}

def addingToDF(new_row):
    global df1
    #Create new rof for data concatenation, as DataFreame from dictionary        
    df_new_row = pd.DataFrame.from_dict(new_row)
    # Identify missing columns in df_new_row that are present in df1
    missing_columns = set(df1.columns) - set(df_new_row.columns)
    #print(missing_columns)
    # Add missing columns with default values (e.g., NaN or any other value)
    for col in missing_columns:
        df_new_row[col] = np.nan  # Using NaN ensures consistent dtype across column
    # Ensure the order of columns is the same
    df_new_row = df_new_row[df1.columns]            
    df1 = pd.concat([df1, df_new_row], ignore_index = True)
    #print(df1)    
         
def savingDFtoFile(save_file, sleep):
    global df1
    df_line = pd.DataFrame(columns=column_names)
    while not stop_event.is_set():            
        #comparing with the last line (dataframe.iloc[-1:]), df1.equals(df2) used   
        if not df_line['timestamp'].equals(df1['timestamp'].iloc[-1:]):
            df_line = df1.iloc[-1:]                       
            with open(save_file, 'ab') as s_f:   #appending last line to file
                df_line.to_csv(s_f, mode='a', index=False, header=False, lineterminator='\n')        
        time.sleep(sleep)
        
    
#Function allowing gentle termination of all threads and closing all serail objects in ser_conns list
def termination():
    print("Terminating program...")
    stop_event.set()  # Signal the threads to stop
    thread1.join()
    thread2.join()
    thread3.join()
    thread5.join()
    thread6.join()
    thread7.join()
    thread8.join()
    thread9.join()
    thread10.join()
    thread11.join()
    thread12.join()
    i = 0
    #closing all serial connections
    for i in range(len(ser_conns)):
        #Check if list element is serial instance and close it 
        if isinstance(ser_conns[i], serial.Serial):
            ser_conns[i].close()
        i =+ 1
    sys.exit(0)

                                        
#Function which configures serial connections, using configFile. Serial objects are stored in a list
def settingSerial(ser_no, serial_conns, configFile):
    a = ser_no #choice of setting for serial connection in config file
    serial_conns[a] = serial.Serial(port = readComConf(configFile)[a][1], baudrate = readComConf(configFile)[a][2],
                                timeout = int(readComConf(configFile)[a][3]), parity='N', stopbits=1, bytesize=8)

#This function is for interacting with the user, checks of responsivity: 'e'+enter should terminate program 

def printPumpStat(pump, column_names, p_q, p_p, p_s):
    global df
    cn = column_names    
    print(f"P{pump}_Q:{df1[cn[p_q]].values[-1]:8.3f}, P{pump}_p: {df1[cn[p_p]].values[-1]:4.1f}, "\
          + f"P{pump}_s: {df1[cn[p_s]].values[-1]}")

def check_input():
    global df1
    cn = column_names
    knaPumps = {'4': 6, '5': 7, '9': 8}
    while not stop_event.is_set():
        try:
            #print(menu_cmd_print)
            a = input(menu_cmd_print + "\nGive a keyboard input:")
            if a == 'end':
                termination()
                
            # Print current status of pumps
            elif a == 'stat':
                while True:
                    print("STATUS")
                    printPumpStat(1, cn, 1, 2, 3)
                    printPumpStat(4, cn, 21, 22, 23)
                    printPumpStat(5, cn, 24, 25, 26)
                    printPumpStat(9, cn, 27, 28, 29)
                    print()
                    b = input("Press 'e' to return to the previous menu \n")
                    if b == "e":
                        break
                
            elif a == 'fsm':
                while True:
                    print(fsmcu_commands_print)
                    command = input("Give commmand for FSMCU:")
                    if command[0].isnumeric():
                        fsmcuSendComand(ser_conns[5],command)
                    elif command == 'e':
                        break
                    else:
                        print('Incorrect FSMCU command')
            
            # Pumps control menu
            elif a and a[0] == 'p' and len(a) > 1:
                if a[1] == '1' or a[1] == '4' or a[1] == '5' or a[1] == '9':
                    pump = a[1]     
                    print(f"Pump P{pump} menu")
                    print(pump_options_print)
                    while True:
                        b = input(f'Give input for P{pump}: ')
                        if b == '0':
                            if a[1] == '1':
                                flomPumpStop(ser_conns[1])
                                print(f'Flom P{pump} pump STOP')
                            else:
                                #print("trying to stop knauer pump")
                                #print(pump)
                                #print(ser_conns[knaPumps[pump]])
                                knauerPumpStop(ser_conns[knaPumps[pump]])
                                print(f'Knauer P{pump} pump STOP')
                        elif b == '1':
                            if a[1] == '1':
                                flomPumpStart(ser_conns[1])
                                print(f'Flom P{pump} pump START')
                            else:
                                knauerPumpStart(ser_conns[knaPumps[pump]])
                                print(f'Knauer P{pump} pump START')
                        elif len(b) > 1 and b[0] == 'f':
                            flowrate = (b[2:6])
                            print(flowrate)
                            if flowrate.isnumeric():
                                if int(flowrate) >= 0 and int(flowrate) < 10000:
                                    if a[1] == '1':
                                        flomSetFlowRate(ser_conns[1], flowrate)
                                        print(f'Flom P{pump} flow rate set to: {flowrate} μL/min')
                                    else:    
                                        knauerSetFlowRate(ser_conns[knaPumps[pump]], flowrate)
                                        print(f'Knauer P{pump} flow rate set to: {flowrate} μL/min')
                                else:
                                    print('Incorrect flow rate value')                    
                        elif b == 'e':
                            break
            
            elif a == "nadc":
                while True:
                    print(nadc_commands_print)
                    print("Press 'e' to exit to previous menu")
                    b = input("Give commmand for NADC:")
                    if b[0].isnumeric() and len(b) < 4 and len(b) >= 1:
                        nadcSendComand(ser_conns[0], b)
                    elif command == 'e':
                        break
                    else:
                        print('Incorrect FSMCU command')
            else:
                print(f"You pressed: {a}")
        except:
            print("Error occured in user input function")
            continue

def main_loop():    
    check_input_thread.start()
    check_input_thread.join()
    time.sleep(0.02)

#setting serial connections
ser_conns = ['0','1' ,'2' ,'3' ,'4' ,'5', '6', '7', '8', '9'] #set elements in the serial conns list to avoid problems when iterating
set_serials = [0,1,2,3,4,5,6,7,8] #these numbers correlate to serial connection parameters in config file
#start all serial connections
try:
    for a in set_serials:
        settingSerial(a, ser_conns, configFile)
except:
    print(f'Problem with opening serial no.{a}')

#for conn in ser_conns: # display all serial connnections
#    print(conn)

#defining queues
queue1 = Queue()
queue2 = Queue()
queue3 = Queue()
queue4 = Queue()
queue5 = Queue()
queue6 = Queue()
queue7 = Queue()
queue8 = Queue()
queue9 = Queue()

# defining threads
thread1 = threading.Thread(target = balanceCom, args = (ser_conns[2], queue3, 0.02,), daemon = True)
thread2 = threading.Thread(target = ptmbCom, args = (ser_conns[3], queue1, 0.1,), daemon = True)
thread3 = threading.Thread(target = ptmbCom, args = (ser_conns[4], queue2, 0.1,), daemon = True)
check_input_thread = threading.Thread(target=check_input)
main_thread = threading.Thread(target=main_loop, daemon = True)
thread5 = threading.Thread(target = dataReceiving1, args = (column_names, queue1, queue2, queue3, queue4,\
                                                            queue5, queue6, queue7, queue8, queue9), daemon = True)
thread6 = threading.Thread(target = savingDFtoFile, args = (df_save_f, 0.5,), daemon = True)
thread7 = threading.Thread(target = flomStatusRead, args = (ser_conns[1], queue4, 0.4,), daemon = True)
thread8 = threading.Thread(target = fsmcuCom, args = (ser_conns[5], queue5, 0.1), daemon = True)
thread9 = threading.Thread(target = knauerStatusRead, args = (ser_conns[6], queue6, 0.4,), daemon = True)
thread10 = threading.Thread(target = knauerStatusRead, args = (ser_conns[7], queue7, 0.4,), daemon = True)
thread11 = threading.Thread(target = knauerStatusRead, args = (ser_conns[8], queue8, 0.4,), daemon = True)
thread12 = threading.Thread(target = nadcStatusRead, args = (ser_conns[0], queue9, 0.5,), daemon = True)


#starting threads
thread1.start()
thread2.start()
thread3.start()
main_thread.start()
thread5.start()
thread6.start()
thread7.start()
thread8.start()
thread9.start()
thread10.start()
thread11.start()
thread12.start()

try:
    main_thread.join()
except KeyboardInterrupt:
    termination()

