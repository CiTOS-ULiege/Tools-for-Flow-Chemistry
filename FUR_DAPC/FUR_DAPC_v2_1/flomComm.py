# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 09:51:01 2024
@author: Hubert

These functions allows communication with FLOM pump (ex. FLOM UI-22-110DC). 
Communication with Flom pump through serial depends on sending commands to it and the
pump responds sending appropriate message. Information about communication can be found
in pump manual. The timing is bound by period of sending commands.

Specified serial connection object is placed in function as "serial_con" from the main
program. Functions uses queues to transmit data to other threads in main program. Period
of operation is reduced by using "time_sleep", which is also transmitted from the main
program.
28/08/2024 - added serial_con.reset_input_buffer, what allowed to receive current response
from Flom pump. Before the response was appearing with a big, increasing delay.
"""
import time
#custom imports:
from readline import ReadLine
from events import stop_event


#after sending: ';01,Q2\r\n' (status request)
#flom response: ';01,Q2,0,00,00000,000'
#flom splitted resp: [';01', 'Q2', '0', '00', '00000', '000']]
#flom row put in queue: [1724229626, 0, 0.0, 0.0], expl: [timestamp, on/off, flowrate, pressure]

def flomStatusRead(serial_con, out_queue, sleep_time):
    rl = ReadLine(serial_con)
    row = []
    message = str(';01,Q2\r\n')
    try:
        while not stop_event.is_set():  # Check if stop signal is set
            try:
                serial_con.reset_input_buffer()
                serial_con.write(message.encode('utf_8')) 
                rawdata = rl.readline().strip()  # Read line from serial (using faster readline), strip whitespaces
            except TimeoutError:
                continue  # Ignore the timeout and continue the loop
            try:
                if len(rawdata) > 18:
                    #print(rawdata) #for troubleshooting
                    decoded_data = rawdata.decode('utf-8', errors='replace')  # Replace undecodable bytes
            except UnicodeDecodeError as e:
                print(f"FLOM receiving: Decoding error: {e}")
            except: #general exception
                continue  # Skip this line if it can't be decoded
                print(rawdata)
                continue  # Skip
            if decoded_data: 
                try:
                    raw = decoded_data.split(',')
                    timestamp = time.time()
                    #preparing row, dividing flow rate by 1000 and pressure by 10 to get ml/min and bar
                    # timestamp, P1_Q (flow rate), P1_p (pressure), P1_s (status: 1:ON, 0:OFF)
                    row = [int(timestamp), float(raw[4])/1000, float(raw[5])/10, int(raw[2])]
                    out_queue.put(row)
                except:
                    print("Error occured while trying to split Flom status and save it to a new data row")
                    continue
                time.sleep(sleep_time)
    except KeyboardInterrupt:
        pass
    finally:
        serial_con.close()

def flomPumpStart(serial_con):
    rl = ReadLine(serial_con)
    try:
        message = str(';01,G1,1\r\n')
        serial_con.write(message.encode('utf_8'))
        print(rl.readline()) #print message being send back by the pump 
    except:
        print('FLOM: Error while trying to send flom command: "Start Pump"')
        
def flomPumpStop(serial_con):
    rl = ReadLine(serial_con)
    try:
        message = str(';01,G1,0\r\n')
        serial_con.write(message.encode('utf_8'))  
        print(rl.readline()) #print message being send back by the pump
    except:
        print('FLOM: Error while trying to send flom command: "Stop Pump"')

def flomSetFlowRate(serial_con, flow_rate):
    rl = ReadLine(serial_con)
    try:
        #flow_rate in uL/min, zfill(5) formats string - justify right, fills with zeroes
        flowStr = str(flow_rate).zfill(5) 
        message = f';01,S3,{flowStr}\r\n' #command for flow prepared, flowStr 'xxxxx'
        serial_con.write(message.encode('utf_8'))
        print(rl.readline()) #print message being send back by the pump
    except:
        print(f'FLOM: Error while trying to send flom command: "Set flowrate {flowStr}"')
        
"""          
 After sending a command, pump sends back a response, confirmation or error. This response
 now is just printed "print(rl.readline())", bur could be placed on queue and processed
 later. Currently this functionality is not important, so it is omitted, because "status"
 gives enough information about the state of pump and reaction for commands.
"""