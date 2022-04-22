#This script is meant to serve as a basic serial monitor
#STILL IN TESTING PHASE

import serial
from threading import Thread, Lock

def get_next_line():
    #grabs the next line before checking if the script should continue    
    ser.open()           
    rawOutput = ser.readline()
    #output = rawOutput.decode('utf-8')
    #print(output)
    print(rawOutput)
    ser.close()          
  
    
def write_line():
    #writes a line to serial   
    ser.open()
    ser.write(G.bytestr)           
    #ser.write('@setpoint, 16, 60\r\n'.encode())
    ser.close() 
 
    
def kill_check():     
    n = G.count
    for i in range(n):
        if G.kill:
            print("All lines were given - Goodbye")
            ser.close()     #Must do this so the serial port can be contacted again later
            break
#        elif G.commandStatus:
#            t_lock.release()
            #            #ser.open()
#            #ser.write(b'@setpoint, 16, 60')
#            #ser.close()
#            write_line()
#            G.commandStatus = False
        else:
            get_next_line()


def write_to_serial():     
    if G.commandStatus:
        t2_lock.acquire() 
        write_line()
        print("Wrote to serial")
        G.commandStatus = False
        t2_lock.release()
    else:
        pass
        
def ask_input():
    choice = input('Enter the following :\n"1": Will rerun thread\n"2": Will kill the print-out of the monitor\n'
                   '"3": Will prompt for an arduino command\nelse: Any other input will exit\ninput: ')
    if choice == "1":
        G.kill = False
        t = Thread(target=kill_check)
        t.start()
        return 1
    elif choice == "2":
        G.kill = True
        return 1
    elif choice == "3":
        G.command = input('Provide arduino command:')
        G.command += "\r\n"
        print(G.command)
        G.commandStatus = True
        G.bytestr = G.command.encode('utf-8')
        print(G.bytestr)
        return 1
    else:
        return 0    
    return 1

class globalVars():
    pass


#---------------------------------------------------------------------------------------------------------

#     # Define the serial port and baud rate.
#     # Ensure the 'COM#' corresponds to what was seen in the Windows Device Manager
ser = serial.Serial('COM20', baudrate = 9600, timeout = None, dsrdtr = False)
#ser.write(b'@setpoint, 16, 60')
ser.close()         

G = globalVars() #empty object to pass around global state
G.lock = Lock()
G.value = 0
G.kill = False
G.commandStatus = False

G.count = 600

#Define and start the thread for serial monitoring
t = Thread(target=kill_check)
t_lock = Lock()
t2 = Thread(target=write_to_serial)
t2_lock = Lock()
t.start()
t2.start()

#run the thread while the ask input displays
while ask_input():
    pass        

#Before exiting, make sure the thread stops 
G.kill = True
 



