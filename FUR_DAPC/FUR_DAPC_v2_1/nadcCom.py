# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 17:48:44 2024

@author: Hubert

This function allows reading the state of NADC (Nitric Acid Dosing Controller),
in-house built device 

"""
#nadcCom.py


import time
#custom imports:
from readline import ReadLine
from events import stop_event

# Nitric Acid Dosing Controller
# Commands:
#   1 xxxx - postion of S1, HNO3/H2O valve (1166: H2O, 550: HNO3)
#   2 xxxx - position of S2,  reactor/prime valve (1600: prime, 900: reactor)
#   3 x    - state of P, peristaltic pump (0: OFF, 1: ON)
#   4      - status request (response: "S1: 1166; S2: 900; P: 0")

# Positions of servos are given in lenghts of impulses, in us (as the input for NADC Arduino program)
# they are claasified as 0 or 1 (S1: O - H2O, S1: 1 - HNO3, S2:0 - priming, S2:1 - reactor)
# Formating of a row  for saving to queue: [Timestamp, Servo1, Servo2, Peristaltic Pump]

#values of microseconds foe positioning the servo-controlled vales, preset:
s1_0 = 1166 #S1 H2O
s1_1 = 550  #S1 HNO3
s2_0 = 1600 #S2 Prime
s2_1 = 900  #S2 Reactor

def nadcStatusRead(serial_con, out_queue, sleep_time):
    rl = ReadLine(serial_con)
    row = []
    ask_stat = b'4\n'
    try:
        while not stop_event.is_set():
            try:
                serial_con.write(ask_stat)
                try: #read until receiving expected answer (NADC sends back received command)
                    raw_data = ''
                    i = 0
                    while len(raw_data) < 10 and i < 8:
                        raw_data = rl.readline()
                        i += 1
                except TimeoutError:
                    continue #skip the timeout error and continue
                except: #general exception
                    print("NADC - other error while receiving data")
                    continue
                try:
                    decoded_status = raw_data.decode('utf-8', errors='replace')  # Replace undecodable bytes                    
                except UnicodeDecodeError as e:
                    print(f"NADC receiving: Decoding error: {e}")
                except: #general exception
                    continue  # Skip this line if it can't be decoded
                if decoded_status:
                    try:
                        split_stat = decoded_status.split(';')
                        s1_us = int(split_stat[0].split(':')[1].strip())
                        s2_us = int(split_stat[1].split(':')[1].strip())
                        p = int(split_stat[2].split(':')[1].strip())

                        if s1_us == s1_0:
                            s1 = 0
                        elif s1_us == s1_1:
                            s1 = 1
                        if s2_us == s2_0:
                            s2 = 0
                        elif s2_us == s2_1:
                            s2 = 1
                        timestamp = int(time.time())
                        row = [timestamp, s1, s2, p]
                        #print(row)
                        out_queue.put(row)
                    except:
                        print("problem while splitting and formating raw data")
                    time.sleep(sleep_time)                 
            except TimeoutError:
                print('NADC communication problem - Timeout Error - inside while loop')
                continue
    except:
        print('NADC communication problem - outside the while loop, end of the nadcStatusRead function')
        pass
    finally:
        serial_con.close()

        
def nadcSendComand(serial_con, command):
    rl = ReadLine(serial_con)

    cmd = str(command).strip()
    if cmd == '1 0':
        message = "1 " + str(s1_0) + "\n"
    elif cmd == '1 1':
        message = "1 " + str(s1_1) + "\n"    
    elif cmd == '2 0':
        message = "2 " + str(s2_0) + "\n"            
    elif cmd == '2 1':
        message = "2 " + str(s2_1) + "\n" 
    elif cmd == '3 0':
        message = "3 0\n"    
    elif cmd == '3 1':
        message = "3 1\n"

    try:
        print("sending message:", message.encode('utf-8'))
        serial_con.write(message.encode('utf-8'))
        print(rl.readline())
        print(rl.readline())
    except TimeoutError:
        print("FSMCU: Timeout errorr occured while trying to write command")
    except:
        print ('FSMCU: Other error during sending command')

        
