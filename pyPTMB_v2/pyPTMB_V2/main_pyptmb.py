"""
Created on 20 Jan 2025
@author: Hubert Hellwig, CiTOS, Liege, Belgium
Modified code from function used in furfural nitration platform.
Configuration of COM settings and saving file done by 'config.txt' file localized in the script directory.

"""
import time
from datetime import datetime, date
import re
import serial
from pathlib import Path
#custom imports:
from readline import ReadLine
from readconfigfile import readComConf, readSaveFilePath, readSaveFileName, readSavingPeriod

def file_path(file_name):
   script_dir = Path(__file__).resolve().parent
   file_path = script_dir / file_name
   return(file_path)
   
# Function for reading temperature from 4-channel in-house made PTMB (Pressure and Temperature Measurement Box) based on Arduino Uno
# These devices are sending data in preset frequncy (typical around 2 Hz)
def ptmbCom(serial_con, period, sleep_time, saveFile):
    rl = ReadLine(serial_con)
    row = [0,0,0]
    decoded_data = ''
    previous_timestamp = time.time()
    try:
        while True:  # Continuous loop
            try:
                #print("Reading serial")
                rawdata = rl.readline().strip()  # Read line from serial (using faster readline), strip whitespaces
                #serial_con.reset_input_buffer()  # This causes problem with missing data fragments... Reset input buffer to ensure up to date data being read in next loop
                #print("raw data:", rawdata)
            except TimeoutError:
                print("timeout error while trying to read serial")
                continue  # Ignore the timeout and continue the loop
            if rawdata:
                try:
                    decoded_data = rawdata.decode('utf-8', errors='replace')  # Replace undecodable bytes
                except UnicodeDecodeError as e:
                    print(f"Decoding error: {e}")
                    continue  # Skip this line if it can't be decoded
            if decoded_data: 
                # Searches for everything after 'Thermocouple:' until space and 'Pressure:' until space
                temp = re.search(r'(?<=Thermocouple: )[^\s]*', decoded_data)
                press = re.search(r'(?<=Pressure: )[^\s]*', decoded_data)
                   
                if temp:
                    temp = temp.group()                    
                    row[1] = float(temp)
                if press:
                    press = press.group()                    
                    row[2] = float(press)
 
                timestamp = time.time()
                if timestamp > (previous_timestamp + period): #increment of 'period' [s]
                    decoded_data = ''
                    row[0] = round(float(timestamp), 1)                   
                    print('\r', row, "                   ", end='')
                    previous_timestamp = timestamp
                    with open (saveFile, 'a+') as sf:
                        try:
                            line = str(row[0]) + ',' + str(row[1]) + ',' + str(row[2]) + '\n'
                            sf.write(line)
                        except TimeoutError:
                            print("File saving timeout error")
                    
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        pass
    finally:
        serial_con.close()
        print("Serial connetion closed")
        
        
def main():
    configFileName = 'config.txt'                  # the name of the config file
    configFile = file_path(configFileName)         # find the config file path for reading it later
    saveFilePath = readSaveFilePath(configFile)    # find the save file path in the condig file 
    saveFileName = readSaveFileName(configFile)    # find the save file name in the condig file 
   
    saveFileDir = Path(saveFilePath)                    # Convert saveFilePath to a Path object
    saveFileDir.mkdir(parents=True, exist_ok=True)      # Ensure the directory exists, create it if not
    # Create the full file path with the name and timestamp
    saveFile = saveFileDir / (saveFileName + '_' + str(date.today()) + '_' + time.strftime("%H%M%S", time.localtime()) + ".txt")
    
    print("PTMB  - Pressure & Temperature Measurement Box")
    print("Built in CiTOS, Center For Integrated Technology and Organic Synthesis; author: Hubert Hellwig")
    print("This program provides serial communication with the PTMB and recording of acquired data to a file")
    print("Data being saved to:")
    print(saveFile)   # Print the localisation and name of the save file
    print("") 
    
    # Read the saving period from the file
    saving_period = readSavingPeriod(configFile)
    #saving_period = 1
    print("Saving period:", saving_period, "s")
    print("")
    print("To terminate the program, press: 'CTRL+C'")
    print("")
    
    #Set the serial port configuration, using data from config file`
    a = 0 #only one serial object freom the readComConf, '0' is the index of the config (just one line)
    serial1 = serial.Serial(port = readComConf(configFile)[a][1], baudrate = readComConf(configFile)[a][2],
                            timeout = int(readComConf(configFile)[a][3]), parity='N', stopbits=1, bytesize=8)
   
    try:
        if serial1:
            print("Serial connection open")
            print("[Timestamp(s), TC(°C),  p(bar)")
            time.sleep(0.2)
            serial1.reset_input_buffer()  # Flush the buffer to ensure the up-to date data
            time.sleep(0.2)
            ptmbCom(serial1, saving_period, 0.05, saveFile)     # Start the function which reads the serial connection and saves it to the file
    except KeyboardInterrupt:
        pass
    #except:
    #    print("Problem with serial connection")
    
main()      # start the main function