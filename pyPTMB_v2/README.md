# Software for Pressure & Temperature Data Acquisition
Developed by Hubert Hellwig	<sup>a</sup> under supervision of Jean-Christophe M. Monbaliu<sup>a,b</sup><br/><br/>
&nbsp; *a) Center for Integrated Technology and Organic Synthesis (CiTOS), MolSys Research Unit University of Liège,*<br/>
&nbsp; &nbsp; &nbsp; *B6a, Room 3/19, Allée du Six Août 13, 4000 Liège (Sart Tilman) (Belgium); webpage: https://www.citos.uliege.be*<br/>
&nbsp; *b)	WEL Research Institute, Avenue Pasteur 6, B-1300 Wavre (Belgium)*

&nbsp; *E-mail: hhellwig@uliege.be; jc.monbaliu@uliege.be*


### Python code for data acquisition from Pressure & Temperature Measurement Box (PTMB)
#### This program enables serial communication with the PTMB and records acquired pressure and temperature data to a file.

## Features
- Real-time data acquisition via serial communication
- Data logging to a text file with timestamps
- Configurable COM port, file output settings and data-saving interval
- Tested on **Windows 10 & 11** with **Python 3.9.10**

## Requirements
- Python 3.9 or later  
- A USB connection between PTMB and PC  
- Installed **pyserial** library (install via `pip install pyserial`) 

## Usage and configuration
- **Check the COM port number** of connected PTMB in your system's Device Manager
- **Open "*config.txt*"** and modify the following parameters: <br>
&nbsp; - **COM ports settings**: update `COM4` to match your system’s correct COM port<br>
&nbsp; - **File name**: change the filename (optional)<br>
&nbsp; - **Save file path**: change the directory path (optional)<br>
&nbsp; - **Data saving period**: modify the period (optional)<br>
- **Run the script** <br>
&nbsp; Script can be run via command line (type `python main_pyptmb.py`) or by double-clicking the file "*main_pyptmb.py*" <br>

After starting the program, a few seconds are required for the Arduino to restart (this is normal behavior), and then the serial communication will begin. Once the program runs, it will display the pressure and temperature values in the command line and create a text file with the current date in the filename. Example: "*PTMB1_2025-01-20_223613.txt*" The file will be updated continuously while the program is running, with a new data row created every *data-saving interval*. The created file can also be accessed in real-time by another program to process the data (e.g., to plot graphs). Real-time data plotting was tested with KST-2 software *Kst-2.0.8-win32.exe* (https://kst-plot.kde.org/ or https://sourceforge.net/projects/kst/files/Kst%202.0.8/Kst-2.0.8-win32.exe/download/). <br>

## Data Format
Each row in the output file follows this structure: <br>
`*timestamp,temperature,pressure*`  <br>
**timestamp** - UNIX format (number of seconds elapsed since January 1, 1970, 00:00:00 UTC)  <br>
**temperature** - °C  <br>
**pressure** - bar  <br>

Example output in the created text file <br>
`1737408977.7,21.31,1.2` <br>
`1737408979.0,21.31,1.2` <br>
`1737408980.4,21.5,1.19` <br>
