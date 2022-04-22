# -*- coding: utf-8 -*-


#This is meant to create a module necessary to connect labscript with an arduino device
#This module will (almost certainly) contain certain lines meant specifically for an arduino interlock
#Communication between python and the arduino will occur via serial connection


import serial

# Define the serial port and baud rate.
# Ensure the 'COM#' corresponds to what was seen in the Windows Device Manager
ser = serial.Serial('COM20', 9600, dsrdtr = True)


#Really important note to self: Everytime the serial line is open, the arduino sketch restarts! FIXED BY SETTING "dsrdtr" TO "True"
#I cannot reliably open and close the serial port without resetting the interlock, unless I concieve a workaround
#However, I must close at the end or the serial port will be considered "in use" on the next iteration

#this is a test to ensure I can communicate with the arduino from python
#ser.write(b'@tsetpoint, 16, 17')
ser.close()               #CANNOT USE UNTIL END OF SCRIPT - Will restart sketch when ser.open() occurs

for r in range(50):
    ser.open()           #CANNOT USE when interlock is active!! Will restart sketch when ser.open() occurs
    output = ser.readline()
    print(output)
    ser.close()          #CANNOT USE UNTIL END OF SCRIPT - Will restart sketch when ser.open() occurs

#print()
#print("Here is a new setpoint")
#print()    

#ser.write(b'@SetPoint, 16, 17')

for r in range(200):
    ser.open()           #CANNOT USE when interlock is active!! Will restart sketch when ser.open() occurs
    output = ser.readline()
    print(output)
    ser.close()          #CANNOT USE UNTIL END OF SCRIPT - Will restart sketch when ser.open() occurs

    
print("The First 250 lines were given - goodbye")

ser.close()     #Must do this so the serial port can be contacted again later
