# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 17:48:44 2024

@author: Hubert

28/08/2024 - added 'serial_con.reset_input_buffer()' to prevent outdated data being received
"""

#fsmCom.py
#FSMCU data format:
#FSM_HS1, FSM_HS2, FSM_HS3, FSM_HS4, FSM_p, FSM_sep_v, FSM_byp_v, FSM_serv_v1, FSM_serv_2, FSM_serv_v3, FSM_flt_mod, FSM_sep_mod


import time
#custom imports:
from readline import ReadLine
from events import stop_event

def fsmcuCom(serial_con, out_queue, sleep_time):
    rl = ReadLine(serial_con)
    row = []
    try:
        while not stop_event.is_set():  # Check if stop signal is set
            try:
                rawdata = rl.readline().strip()  # Read line from serial (using faster readline), strip whitespaces
                serial_con.reset_input_buffer()
                #print(rawdata)
            except TimeoutError:
                continue  # Ignore the timeout and continue the loop
            try:
                decoded_data = rawdata.decode('utf-8', errors='replace')  # Replace undecodable bytes
            except UnicodeDecodeError as e:
                print(f"FSMCU receiving: Decoding error: {e}")
                continue  # Skip this line if it can't be decoded
            if decoded_data:
                try:
                    splt = decoded_data.split(',')
                    timestamp = time.time()
                    if len(splt) > 5:
                        row = [int(timestamp), int(splt[0]), int(splt[1]),int(splt[2]),
                               int(splt[3]), float(splt[4]), int(splt[5]), int(splt[6]),
                               int(splt[7]), int(splt[8]), int(splt[9]), int(splt[10]),
                               int(splt[11])]
                        out_queue.put(row)
                except:
                    print("FSMCU data parsing: error while splitting and saving formated data to queue")
                    continue
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        pass
    finally:
        serial_con.close()
        
def fsmcuSendComand(serial_con, command):
    try:
        serial_con.write(command.encode('utf-8'))
    except TimeoutError:
        print("FSMCU: Timeout errorr occured while trying to write command")
    except:
        print ('FSMCU: Other error during sending command')


        
