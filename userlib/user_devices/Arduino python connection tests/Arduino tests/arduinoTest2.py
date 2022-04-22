# -*- coding: utf-8 -*-


#This is meant to create a module necessary to connect labscript with an arduino device
#This module will (almost certainly) contain certain lines meant specifically for an arduino interlock
#Communication between python and the arduino will occur via serial connection

#This script is meant to serve as a basic serial monitor


import serial
from threading import Thread,Lock
import time

def GetNextLines():
    #grabs the next 100 lines before checking if the script should continue    
    for r in range(50):
        ser.open()           
        output = ser.readline()
        print(output)
        ser.close()          


# Define the serial port and baud rate.
# Ensure the 'COM#' corresponds to what was seen in the Windows Device Manager
ser = serial.Serial('COM20', 9600, dsrdtr = True)
ser.close()               

for x in range(100):
    GetNextLines()
    print("######################################################")
    Continue = input('Continue...? Type "Yes" or "No"')
    if Continue == "No":
        break
    else:
        continue
    
print("All lines were given - goodbye")

ser.close()     #Must do this so the serial port can be contacted again later
