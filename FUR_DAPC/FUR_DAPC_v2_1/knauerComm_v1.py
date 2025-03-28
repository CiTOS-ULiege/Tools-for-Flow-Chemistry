# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 17:48:44 2024
@author: Hubert Hellwig, postdoctoral researcher at CiTOS

These functions allows communication with Knauer pumps (ex. Knauer Azurea P4.1S). 
Communication with Knauer pump through serial depends on sending commands to it and the
pump responds sending appropriate message. Information about communication can be found
in pump manual. The timing is bound by period of sending commands.
An issue withc communication was faced because this pump requires "\r" (carridge return)
symbol in the end of command and also messages send by the pump ends with this symbol, which
required modification of ReadLine function (changing line end symbol from "\n" to "\r").

Specified serial connection object is placed in function as "serial_con" from the main
program. Functions uses queues to transmit data to other threads in main program. Period
of operation is reduced by using "time_sleep", which is also transmitted from the main
program.
"""
#knauerComm_v1.py


import time
#custom imports:
from readline import ReadLine
from events import stop_event

#Knauer status put in queue:
#[1724229626, 0, 0.0, 0.0], expl: [timestamp, on/off, flowrate, pressure]
#[timestamp, flow rate,  pressure, on/off]  

def knauerStatusRead(serial_con, out_queue, sleep_time):
    rl = ReadLine(serial_con)
    row = []
    message = str('status?\n\r')
    try:
        while not stop_event.is_set():  # Check if stop signal is set
            try:
                serial_con.reset_input_buffer()
                serial_con.reset_output_buffer()
                serial_con.write(message.encode('utf_8')) 
                rawdata = rl.readline().strip()  # Read line from serial (using faster readline), strip whitespaces
            except TimeoutError:
                continue  # Ignore the timeout and continue the loop
            try:
                if len(rawdata) > 20:
                    decoded_data = rawdata.decode('utf-8', errors='replace')  # Replace undecodable bytes
            except UnicodeDecodeError as e:
                print(f"FLOM receiving: Decoding error: {e}")
            except: #general exception
                continue  # Skip this line if it can't be decoded
            if decoded_data: 
                timestamp = time.time()
                raw = decoded_data.split(',')
                #preparing row, dividing flow rate by 1000 and pressure by 10 to get ml/min and bar
                # timestamp, Px_Q (flow rate), Px_p (pressure), Px_s (status: 1:ON, 0:OFF)
                raw_2 = raw[0].split(':')
                row = [int(timestamp), float(raw[1])/1000, float(raw[2])/10, int(raw_2[1])]
                out_queue.put(row)
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        pass
    finally:
        serial_con.close()

#Knauer pump response to "status?" command:
#STATUS:0,5000,346,1,0,0,0,0,0,0

#modified flomSetFlowRate
def knauerSetFlowRate(serial_con, flow_rate):
    rl = ReadLine(serial_con)
    try:
        #flow_rate in uL/min, zfill(5) formats string - justify right, fills with zeroes
        flowStr = str(flow_rate) # in uL/min 
        serial_con.reset_input_buffer()
        serial_con.reset_output_buffer()
        message = f'flow {flowStr}\n\r' #command for flow prepared, flowStr 'xxxxx'
        serial_con.write(message.encode('utf_8'))
        print(rl.readline()) #print message being send back by the pump 
    except:
        print(f'Knauer pump: "{serial_con}": Error while trying to send flom command: "Set flowrate {flowStr}"')
          
def knauerPumpStart(serial_con):
    rl = ReadLine(serial_con)
    try:
        message = str('on\n\r')
        serial_con.reset_input_buffer()
        serial_con.reset_output_buffer()
        serial_con.write(message.encode('utf_8'))
        rl = ReadLine(serial_con)
        print(rl.readline()) #print message being send back by the pump 
    except:
        print('Knauer pump: "{serial_con}": Error while trying to send flom command: "Start Pump"')
        
def knauerPumpStop(serial_con):
    rl = ReadLine(serial_con)
    try:
        message = str('off\n\r')
        serial_con.reset_input_buffer()
        serial_con.reset_output_buffer()
        serial_con.write(message.encode('utf_8'))  
        rl = ReadLine(serial_con)
        print(rl.readline()) #print message being send back by the pump 
    except:
        print('Knauer pump: "{serial_con}"": Error while trying to send flom command: "Stop Pump"')

"""          
 After sending a command, pump sends back a response, confirmation or error. This response
 now is just printed "print(rl.readline())", bur could be placed on queue and processed
 later. Currently this functionality is not important, so it is omitted, because "status"
 gives enough information about the state of pump and reaction for commands.
"""
