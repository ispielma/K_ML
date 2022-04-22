#This script is meant to serve as a basic serial monitor for arduino
#STILL IN TESTING PHASE

import serial
from threading import Thread, Lock
import time

def get_next_line():
    #grabs the next line before checking if the script should continue    
    ser.open()           
    rawOutput = ser.readline()
    
    #This prevents an error that would cause the program to quit and serial port to be busy 
    try:
        output = rawOutput.decode('utf-8')
        time.sleep(0.05)   #in seconds
        print(output)
    except UnicodeDecodeError:
        print("******!! PYTHON ERROR: Could not decode!******")
        rawOutput = ser.readline()
        time.sleep(0.5)   #in seconds
        print(rawOutput)
    
    ser.close()          
  
    
def write_line():
    #writes a line to serial   
    ser.open()           
    if G.Command1:    
        ser.write('@setpoint, 16, 60\r\n'.encode())
        time.sleep(0.05)   #in seconds
        G.Command1 = False
    elif G.Command2:    
        ser.write('@setpoint, 16, 95\r\n'.encode())
        time.sleep(0.05)   #in seconds
        G.Command2 = False
    else:
        ser.write(G.byte_str)
        time.sleep(0.05)   #in seconds
    ser.close() 
 
    
def kill_check():     
    for _ in iter(int, 1): #creates an infinite loop, from which G.kill can break out to exit
        if G.kill:
            print("All lines were given - Goodbye")
            ser.close()     #Must do this so the serial port can be contacted again later
            break
        elif G.commandStatus:
            write_line()
            G.commandStatus = False
        else:
            get_next_line()

        
def ask_input():
    choice = input('Enter the following :\n - "1": Will rerun thread\n - "2": Will kill the print-out of the monitor\n'
                   ' - "3": Will prompt for an arduino command\n - else: Any other input will exit\nInput: ')
    if choice == "1":
        G.kill = True
        time.sleep(0.5)   #in seconds
        G.kill = False
        t = Thread(target=kill_check)
        t.start()
        return 1
    elif choice == "2":
        G.kill = True
        return 1
    elif choice == "3":
        G.command = input('Provide arduino command:')
        if G.command == "1":
            G.Command1 = True
        elif G.command == "2":
            G.Command2 = True
        else:
            G.command += "\r\n" 
            G.byte_str = G.command.encode('utf-8')
        G.commandStatus = True
        return 1
    else:
        return 0    
    return 1

class globalVars():
    pass


#---------------------------------------------------------------------------------------------------------

#     # Define the serial port and baud rate.
#     # Ensure the 'COM#' corresponds to what was seen in the Windows Device Manager
ser = serial.Serial('COM20', baudrate = 9600, timeout = None, dsrdtr = True)
ser.close()         

G = globalVars() #empty object to pass around global state
G.lock = Lock()
G.value = 0
G.kill = False
G.commandStatus = False
G.Command1 = False
G.Command2 = False

#Define and start the thread for serial monitoring
t = Thread(target=kill_check)
t.start()

#run the thread while the ask input displays
while ask_input():
    pass        

#Before exiting, make sure the thread stops 
G.kill = True
 



