# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 17:48:44 2024
@author: Hubert

These functions are responsible for reading data from serial devices which are sending
data periodically (PTMB, Pressure Temperature Measuring Box and KERN balance). There is no
need for sending commands to these devices (they even can not receive commands).

28/08/2024 - added 'bal_ser.reset_input_buffer()' to prevent outdated data being received
"""
#comReceivers.py

import time
import re
#custom imports:
from readline import ReadLine
from events import stop_event


# Function for reading temperature and pressure from in-house made PTMBs based on Arduino Uno
# These devices are sending data in preset frequncy (typical around 2 Hz)
def ptmbCom(serial_con, out_queue, sleep_time):
    rl = ReadLine(serial_con)
    row = []
    try:
        while not stop_event.is_set():  # Check if stop signal is set
            try:
                rawdata = rl.readline().strip()  # Read line from serial (using faster readline), strip whitespaces
            except TimeoutError:
                continue  # Ignore the timeout and continue the loop
            try:
                decoded_data = rawdata.decode('utf-8', errors='replace')  # Replace undecodable bytes
            except UnicodeDecodeError as e:
                print(f"Decoding error: {e}")
                continue  # Skip this line if it can't be decoded
            if decoded_data: 
                timestamp = time.time()
                # Searches for everything after 'Thermocouple :' until space and similar for 'Pressure: '
                temp1 = re.search(r'(?<=Thermocouple: )[^\s]*', decoded_data)
                press1 = re.search(r'(?<=Pressure: )[^\s]*', decoded_data)
                if temp1 and press1:
                    temp2 = temp1.group()
                    press2 = press1.group()
                    splitted_temp = temp2.partition('.')
                    splitted_press = press2.partition('.')
                    temp3 = splitted_temp[0] + '.' + splitted_temp[2][0:2]
                    press3 = splitted_press[0] + '.' + splitted_press[2][0:2]
                    row = [int(timestamp), float(temp3), float(press3)]
                    out_queue.put(row)
                else:
                    print("Data format error: Could not parse temperature or pressure.")
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        pass
    finally:
        serial_con.close()
        
# Function for reading mass from KERN balance, includes taking a mean from readouts collected
# during given time period, for example 1 s (the balance is sending data with frequency higher than 1 Hz)
def balanceCom(bal_ser, out_queue, sleep_time):
    rl = ReadLine(bal_ser)
    tuple1 =()
    timing1 = time.time()
    row = []
    try:
        while not stop_event.is_set():  # Check if stop signal is set
            try:
                bal_ser.reset_input_buffer()
                rawdata = rl.readline().strip()  # Read until '\r\n' and remove leading/trailing whitespace
            except TimeoutError:
                continue  # Ignore the timeout and continue the loop
            # checking if there are alphabetic charaters
            #print(f'balance: {rawdata}')
            if rawdata[2:6].isalpha():
                print('Balance: Not a number', rawdata)
                out_queue.put('NaN')
            else: #if not alphabetic, then continue to acquire data                   
                try:
                    decoded_data = rawdata.decode('utf-8', errors='replace')  # Replace undecodable bytes
                except UnicodeDecodeError as e:
                    print(f"Balance: Decoding error: {e}")
                    continue  # Skip this line if it can't be decoded
                if decoded_data and len(decoded_data) > 10:
                    try:
                        splitted = rawdata.decode('utf-8').partition('.')
                        if splitted[0][0] == "-":
                            mass = float((splitted[0][1:5] + '.' + splitted[2][0:3]).strip())
                            mass = -mass
                        else:
                            mass = float((splitted[0] + '.' + splitted[2][0:3]).strip())
                        tuple1 = tuple1 + (mass,)
                        if (time.time() - timing1) > 1: #time period for removing data from tuple
                            timing1 = time.time()
                            value=sum(tuple1)/len(tuple1)
                            tuple1 = ()
                            row = [int(time.time()), round(value, 3)]
                            out_queue.put(row)
                    except:
                        print("Balance: other error while splitting and formating data")
                        continue
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        pass
    finally:
        bal_ser.close()