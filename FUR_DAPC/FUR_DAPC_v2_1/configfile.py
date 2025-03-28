# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 15:25:10 2024
@author: Hubert
"""
#COM communication settings as a list of tuples ('name', 'addr', 'baud', 'timeout')
#'name' and 'addr' are strings, 'baud' and 'timeout' are integers
#example: ('flomSer', 'COM12', 9600, 1)

#Writting the settings to the file
def writeConfig (fileName, serConnList, savingPeriod):
    with open(fileName, 'w') as file:
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

#Read COM settings, from line after lineNumber until lack of "End of COM settings"
def readComConf(filename):
    lineNumber = findLine(filename, "('name', 'addr', 'baud', 'timeout')")
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