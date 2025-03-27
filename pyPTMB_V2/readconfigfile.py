# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 15:25:10 2024
@author: Hubert
"""
#COM communication settings as a list of tuples ('name', 'addr', 'baud', 'timeout')
#'name' and 'addr' are strings, 'baud' and 'timeout' are integers
#example: ('flomSer', 'COM12', 9600, 1)

#Writting the settings to the file
def writeConfig (filename, serConnList, savingPeriod):
    with open(filename, 'w') as file:
        file.write('DAPC - Data Acquisition Process Control - config file\n')
        file.write('\n')
        file.write('Device communication config\n')
        file.write('COM ports settings:\n')
        for i in serConnList:
            file.write(f'{i}\n')
        file.write('End of COM settings\n')
        file.write('\n')
        file.write('Other configurations\n')
        file.write('Data saving period [s]\n')
        file.write(str(savingPeriod))
        file.write('\n')
        file.write('End of configuration file')
        
#Search for line number where COM settings starts
def findLine(filename, searchString):
    with open(filename, 'r') as file:
        lines = file.readlines()
        lineNumb = 0
        for line in lines:
            lineNumb += 1
            #print(f"checking line {lineNumb}: {line.strip()}")
            if searchString.strip() in line.strip():
                return lineNumb            
    return None  

#Read COM settings, from line after lineNumber until "End of COM settings"
def readComConf(filename):
    lineNumber = findLine(filename, "'name', 'addr', 'baud', 'timeout'")
    list1 = list()
    with open(filename, 'r') as file:
        lines = file.readlines()
        a = 0
        b = 0
        for line in lines:
            if line == 'End of COM settings\n':
                break
            if a >= lineNumber:
                element = lines[a].replace('(', '').replace(')', '').strip().replace(' ', '').replace("'","").split(',')
                list1.insert(b, tuple(element))
                b += 1
            a += 1
    return list1      
    

#Read save-file settings to get file path, from line after lineNumber until "End of save file settings"
def readSaveFilePath(filename):
    pathLineNumber = findLine(filename, "Save file path:")
    with open(filename, 'r') as file:
        lines = file.readlines()
        a = 0
        for line in lines:
            if line == 'End of save file settings\n':
                break
            if a == pathLineNumber:
                file_path = lines[a].replace('(', '').replace(')', '').strip().replace("'","").split(',')
            a += 1
        saveFilePath = str(file_path[0])   
    return saveFilePath      
    
#Read save-file settings to get file name, from line after lineNumber until "End of save file settings"
def readSaveFileName(filename):
    nameLineNumber = findLine(filename, "File name:")
    with open(filename, 'r') as file:
        lines = file.readlines()
        a = 0
        for line in lines:
            if line == 'End of save file settings\n':
                break
            if a == nameLineNumber:
                file_name = lines[a].replace('(', '').replace(')', '').strip().replace(' ', '').replace("'","").split(',')
            a += 1                        
        saveFileName = str(file_name[0])   
    return saveFileName      
    
def readSavingPeriod(filename):
    savingPeriodLineNumber = findLine(filename, "Data saving period [s]:")
    with open(filename, 'r') as file:
        lines = file.readlines()
        a = 0
        for line in lines:
            if line == 'End of saving period settings\n':
                break
            if a == savingPeriodLineNumber:
                saving_period = lines[a].replace('(', '').replace(')', '').strip().replace(' ', '').replace("'","")
            a += 1
                        
    return float(saving_period)   