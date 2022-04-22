#This script is meant to serve as a basic serial monitor for arduino
#STILL IN TESTING PHASE

#import serial

import pyvisa
from threading import Thread, Lock
import time

def get_next_line():
    rawOutput = my_instrument.read_bytes(50, chunk_size = None, break_on_termchar = True)
    try:
        output = rawOutput.decode('utf-8')
        time.sleep(0.05)   #in seconds
        print(output)
    except UnicodeDecodeError:
        print("******!! PYTHON ERROR: Could not decode!******")
        print(rawOutput)
    
def kill_check():     
    for _ in iter(int, 1): #creates an infinite loop, from which G.kill can break out to exit
        if G.kill:
            print("All lines were given - Goodbye")
            break
        elif G.commandStatus:
            write_line()
            G.commandStatus = False
        else:
            get_next_line()

def write_line():
    my_instrument.write(G.command, termination = None, encoding = 'utf-8')
    time.sleep(0.1)   #in seconds
   

        
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
        G.commandStatus = True
        return 1
    else:
        return 0    
    return 1


class globalVars():
    pass


#---------------------------------------------------------------------------------------------------------

# Define global variables to pass around
G = globalVars() #empty object to pass around global state
G.lock = Lock()
G.value = 0
G.kill = False
G.commandStatus = False


# Define the VISA protocol connection.
# Ensure the 'COM#' corresponds to what was seen in the Windows Device Manager
rm = pyvisa.ResourceManager()
rm.list_resources()       #defines possible addresses to check for connection, in list on next line
('ASRL1::INSTR', 'ASRL2::INSTR', 'GPIB0::14::INSTR', 'ASRL20::INSTR', 'ASRL25::INSTR')
my_instrument = rm.open_resource('ASRL20::INSTR')         #defines my_instrument as COM20 (arduino interlock)
print(my_instrument.query('*IDN?'))
my_instrument.read_termination = '\r\n'
my_instrument.write_termination = ',\r\n'


#Define and start the thread for serial monitoring
t = Thread(target=kill_check)
t.start()

#run the thread while the ask input displays
while ask_input():
    pass        

#Before exiting, make sure the thread stops 
G.kill = True
 