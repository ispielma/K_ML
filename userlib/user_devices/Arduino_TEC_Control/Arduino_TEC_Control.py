#Module for the Arduino_TEC_Control device
#Modeling from Tekscope device in labscript
#The Arduino_TEC_Device is in alpha
import pyvisa
import numpy as np
import time

class Arduino_TEC_Control:
    """"Class for connecting to the arduino TEC Controller using PyVISA"""
    def __init__(self, addr='ASLR?*::INSTR', 
                 timeout=10, termination='\r\n'):
        rm = pyvisa.ResourceManager()
        devices = rm.list_resources(addr)
        assert len(devices), "pyvisa didn't find any connected devices matching " + addr
        self.device = rm.open_resource(devices[0])
        self.device.timeout = 1000 * timeout
        self.device.read_termination = termination
        
        #The arduino has no IDN command and functions perfectly fine without it, but it could be added
        #               as a standardizing initial component in the future, if necessary
        #self.idn = self.device.query('*IDN?')  
        
        #These are standard requests to make over VISA
        self.read = self.device.read
        self.write = self.device.write
        self.query = self.device.query
        self.flush = self.device.flush
        
        #These are defined for particular data about the TEC device
        self.temp_reading_packet = ""  #(the packet strings are left empty)
        self.out_voltage_packet = ""
        self.setpoint_packet = ""
        self.Kcrit_packet = ""
        self.Tcrit_packet = ""
        self.Kp_packet = ""
        self.Ki_packet = ""
        self.Kd_packet = ""
        
        #empty variables to be used for storing various values/strings of information
        #the strings may be unncessary with a list approach - will determine after testing
        self.temp_reading = ""
        self.last_temp_reading = ""
        self.out_voltage = ""
        self.last_out_voltage = ""
        self.setpoint = ""
        self.last_setpoint = ""
        self.Kcrit = ""
        self.last_Kcrit = ""
        self.Tcrit = ""
        self.last_Tcrit = ""
        self.Kp = ""
        self.last_Kp = ""
        self.Ki = ""
        self.last_Ki = ""
        self.Kd = ""
        self.last_Kd = ""
        self.ref_volt = ""
        self.last_ref_volt = ""
        
        self.packet = []
        self.last_packet = []
        
        self.this_dict = {}



#The following functions are internally referred to by other functions in the Arduino_TEC_Control class
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    #Activates a flush of the serial buffer to prevent inaccurate line-reading
    def call_plumber(self, verbose=False):
         if verbose:
             print('Plumber is here - Time to flush')
         self.device.flush(pyvisa.constants.VI_READ_BUF_DISCARD)
         if verbose:
             print("Flush attempted")


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    #Converts lists into dictionaries for convienient reference    
    def convert_to_dict(self, this_list):
        self.this_dict = {}
        for item in range(len(this_list)):
            this_string = this_list[item]
            name, valRaw = this_string.rsplit(';',1)
            val_str = ""
            for m in valRaw:
                if m.isdigit():
                    val_str = val_str + m
                elif m=='.':
                    val_str = val_str + m
            val = float(val_str)
            self.this_dict[name] = val
        return self.this_dict


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    #Sends a call number to the arduino to verify that the serial is clear and the arduino is ready for a call    
    def send_call_num(self, verbose=False):
         if verbose:
             print('Generating call number...')
         
         #Generates a random 4 digit number using time.time() 
         call_num_gen = time.time()
         call_str = str(call_num_gen)[-4:]
         try:                                     
             call_int = int(call_str)    #try to convert to an interger
         except ValueError:
             print("Error: Call number not int()")   #if string has a decimal, just send call number 1000
             call_str = '1000'
             call_int = int(call_str)
        
         #send a call number and read response from the arduino
         if verbose:
            print('The call number being sent is %s' %(call_str))
         call_read = self.device.query('@callNum, '+call_str)
         expected_read ="Call Number received : "+str(call_int)
         if call_read == expected_read:
             if verbose:    
                 print(call_read)
         else:
             self.call_plumber()
             print('**!Call Error!**')
             if verbose:
                 print(call_read)
                 print("Expected ",expected_read)
                 #self.call_plumber()
                 print('!! Cannot rectify call number !!')
                 #raise an error here someday
         return


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #Grabs the full interlock packet which contains all channel temperatures, all channel setpoints, and interlock status
    def grab_init(self, all=True):
            """Return full packet of values for temp, voltage, setpoint, and PID shares. """
            
            self.update = []
            
            self.send_call_num()
            
            self.device.write('@init,')
            time.sleep(1)
            rawOutput = self.device.read_bytes(250, chunk_size = None, break_on_termchar = True)
            output = rawOutput.decode('utf-8')

            # This will be stored on the python side as a list and then dictionary 
            #      of all the packet info (should be 16 channel temps, 16 setpoints, and the status)
            self.temp_reading_packet, self.out_voltage_packet, self.setpoint_packet, self.Kcrit_packet, self.Tcrit_packet, self.Kp_packet, self.Ki_packet, self.Kd_packet, self.ref_volt_packet, junk = output.split('#')

            self.temp_reading = self.temp_reading_packet
            #self.last_temp_reading = self.temp_reading
            self.packet.append(self.temp_reading)
            self.last_packet.append(self.temp_reading)
            
            self.out_voltage = self.out_voltage_packet
            #self.last_out_voltage = self.out_voltage
            self.packet.append(self.out_voltage)
            self.last_packet.append(self.out_voltage)
            
            self.setpoint = self.setpoint_packet
            #self.last_setpoint = self.setpoint
            self.packet.append(self.setpoint)
            self.last_packet.append(self.setpoint)
            
            self.Kcrit = self.Kcrit_packet
            #self.last_Kcrit = self.Kcrit
            self.packet.append(self.Kcrit)
            self.last_packet.append(self.Kcrit)
            
            self.Tcrit = self.Tcrit_packet
            #self.last_Tcrit = self.Tcrit
            self.packet.append(self.Tcrit)
            self.last_packet.append(self.Tcrit)
            
            self.Kp = self.Kp_packet
            #self.last_Kp = self.Kp
            self.packet.append(self.Kp)
            self.last_packet.append(self.Kp)
            
            self.Ki = self.Ki_packet
            #self.last_Ki = self.Ki
            self.packet.append(self.Ki)
            self.last_packet.append(self.Ki)
            
            self.Kd = self.Kd_packet
            #self.last_Kd = self.Kd
            self.packet.append(self.Kd)
            self.last_packet.append(self.Kd)
            
            self.ref_volt = self.ref_volt_packet
            #self.last_ref_volt = self.ref_volt
            self.packet.append(self.ref_volt)
            self.last_packet.append(self.ref_volt)
            
            #ignore junk!
            
            return self.packet     


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #Grabs a new packet which contains only changed channel temperatures, all channel setpoints, and/or interlock status
    def grab_new_packet(self, all=True):
            """Return updates to temp, voltage, setpoint, and PID shares. """
            
            self.send_call_num()
            
            self.device.write('@pack,')
            
            rawOutput = self.device.read_bytes(250, chunk_size = None, break_on_termchar = True)
            output = rawOutput.decode('utf-8')

            # Read the packet and split into the appropriate variables
            self.temp_reading_packet, self.out_voltage_packet, self.setpoint_packet, self.Kcrit_packet, self.Tcrit_packet, self.Kp_packet, self.Ki_packet, self.Kd_packet, self.ref_volt_packet, junk = output.split('#')

            #update the temperature reading if a new one exists
            if self.temp_reading_packet:
                self.packet[0] = self.temp_reading_packet
                #self.last_packet[0] = self.temp_reading_packet
                
            #update the out voltage if a new one exists
            if self.out_voltage_packet:
                self.packet[1] = self.out_voltage_packet

            #update the setpoint if a new one exists
            if self.setpoint_packet:
                self.packet[2] = self.setpoint_packet
            
            #update the K critical if a new one exists
            if self.Kcrit_packet:
                self.packet[3] = self.Kcrit_packet
            
            #update the T critical if a new one exists
            if self.Tcrit_packet:
                self.packet[4] = self.Tcrit_packet
            
            #update the Kp share if a new one exists
            if self.Kp_packet:
                self.packet[5] = self.Kp_packet
            
            #update the Ki share if a new one exists
            if self.Ki_packet:
                self.packet[6] = self.Ki_packet
                
            #update the Kd share if a new one exists
            if self.Kd_packet:
                self.packet[7] = self.Kd_packet
        
            #update the out voltage if a new one exists
            if self.ref_volt_packet:
                self.packet[8] = self.ref_volt_packet
        
            return self.packet
  
    
  

#These functions are called directly by the blacs_worker and may refer to those above   
#-----------------------------------------------------------------
    #Send command to set a new setpoint value for a particular channel, given as n for ch# and v for value
    def set_setpoint(self, v, verbose=False):
        self.send_call_num()
        setVal = v
        if verbose:
            print('Sending new temperature setpoint...')
        self.device.write('@tempSetPoint, %s,'%(setVal))
        rawOutput = self.device.read_bytes(75, chunk_size = None, break_on_termchar = True)
        output = rawOutput.decode('utf-8')
        print(output)


#-----------------------------------------------------------------
    #Send command to set a new setpoint value for a particular channel, given as n for ch# and v for value
    def set_Kp(self, v, verbose=False):
        self.send_call_num()
        setVal = v
        if verbose:
            print('Sending new proportional (Kp) share...')
        self.device.write('@Kp, %s,'%(setVal))
        rawOutput = self.device.read_bytes(75, chunk_size = None, break_on_termchar = True)
        output = rawOutput.decode('utf-8')
        print(output)


#-----------------------------------------------------------------
    #Send command to set a new setpoint value for a particular channel, given as n for ch# and v for value
    def set_Ki(self, v, verbose=False):
        self.send_call_num()
        setVal = v
        if verbose:
            print('Sending new integral (Ki) share...')
        self.device.write('@Ki, %s,'%(setVal))
        rawOutput = self.device.read_bytes(75, chunk_size = None, break_on_termchar = True)
        output = rawOutput.decode('utf-8')
        print(output)


#-----------------------------------------------------------------
    #Send command to set a new setpoint value for a particular channel, given as n for ch# and v for value
    def set_Kd(self, v, verbose=False):
        self.send_call_num()
        setVal = v
        if verbose:
            print('Sending new derivative (Kd) share...')
        self.device.write('@Kd, %s,'%(setVal))
        rawOutput = self.device.read_bytes(75, chunk_size = None, break_on_termchar = True)
        output = rawOutput.decode('utf-8')
        print(output)


#-----------------------------------------------------------------
    #Send command to set a new setpoint value for a particular channel, given as n for ch# and v for value
    def set_ref_volt(self, v, verbose=False):
        self.send_call_num()
        setVal = v
        if verbose:
            print('Sending new reference voltage...')
        self.device.write('@setRefVolt, %s,'%(setVal))
        rawOutput = self.device.read_bytes(75, chunk_size = None, break_on_termchar = True)
        output = rawOutput.decode('utf-8')
        print(output)
        

#-----------------------------------------------------------------
    #Send command for the arduino to return all setpoints to the default values stored in the arduino sketch
    def set_default_settings(self, verbose=False):
        self.send_call_num()
        if verbose:
            print('Requesting default settings...')
        #due to an error with default on the arduino end, I am manually defining the defaults here for now
        # rawOutput = self.device.query('@default,')
        # try:
        #     output = rawOutput.decode('utf-8')
        #     print(output)
        # except AttributeError:
        #     #print("******!! PYTHON ERROR: Could not decode!******")
        #     print(rawOutput)
        
        #These are temporary default values, but they will be used for now
        self.set_setpoint(40)
        self.call_plumber()
        self.set_Kp(1.5)
        self.call_plumber()
        self.set_Ki(1.0)
        self.call_plumber()
        self.set_Kd(0.075)


#-----------------------------------------------------------------
    #Send command for the arduino to return the PID setpoints to the default values
    def set_default_PID(self, verbose=False):
        self.send_call_num()
        if verbose:
            print('Requesting default PID settings...')
        
        #These are temporary default values, but they will be used for now
        self.set_Kp(65)
        self.call_plumber()
        self.set_Ki(0.01)
        self.call_plumber()
        self.set_Kd(10)
        self.call_plumber()
        
        
#-----------------------------------------------------------------
    #Send command for the arduino to return temperature setpoint to the default value
    def set_default_temp(self, verbose=False):
        self.send_call_num()
        if verbose:
            print('Requesting default temperature setpoint...')
        
        #These are temporary default values, but they will be used for now
        self.set_setpoint(40)
        self.call_plumber()
        
        
#----------------------------------------------------------------- 
    #Meant to be used by BLACS / labscript during shutdown procedures (ensures device is disconnected from serial properly)
    def close(self):
        self.device.close()



#This is a test script to verify that a given individual function of the Arduino_TEC_Control class is working properly
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
if __name__ == '__main__':
    arduino = Arduino_TEC_Control(addr='ASRL9::INSTR', timeout=10)
    Test = input('Choose a Test:\n - "1" : Test packet grabbing\n'
                 ' - "2" : Test setting setpoint\n'
                 ' - "3" : Test setting Kp share\n'
                 ' - "4" : Test setting defaults\n'
                 ' - else : Will exit.\n Enter Choice:')
    if Test == "1":     #Test grab_init() and Grab_new_packet()
        print("Test 1 selected!")
        time.sleep(2)
        initial = arduino.grab_init()
        print(initial)
        for r in range(5):
            packet = arduino.grab_new_packet()
            print(packet)
            time.sleep(4)
            arduino.call_plumber(verbose = False)
    elif Test == "2":     #Test set_setpoint()
        print("Test 2 selected!")
        initial = arduino.grab_init()
        print(initial)
        time.sleep(2)
        command = input("Give a temperature setpoint in the format:"
                        "'[VALUE]'\nCommand: ")
        arduino.set_setpoint(command, verbose=True)
        for r in range(2):
            time.sleep(2)
            arduino.call_plumber()
            packet = arduino.grab_new_packet()
            print(packet)
    elif Test == "3":     #test set_Kp()
        print("Test 3 selected!")
        initial = arduino.grab_init()
        print(initial)
        time.sleep(2)
        command = input("Give a Kp share (to the nearest 0.01) in the format:"
                        "'[VALUE]'\nCommand: ")
        arduino.set_Kp(command, verbose=True)
        for r in range(2):
            time.sleep(2)
            arduino.call_plumber()
            packet = arduino.grab_new_packet()
            print(packet)
    elif Test == "4":     #Test set_default_settings
        print("Test 4 selected!")
        initial = arduino.grab_init()
        print(initial)
        time.sleep(2)
        command = input("Give a temperature setpoint in the format:"
                        "'[VALUE]'\nCommand: ")
        arduino.set_setpoint(command, verbose=True)
        time.sleep(2)
        arduino.call_plumber()
        packet = arduino.grab_new_packet()
        print(packet)
        arduino.call_plumber()
        time.sleep(2)
        arduino.set_default_settings()
        arduino.call_plumber()
        time.sleep(2)
        packet = arduino.grab_new_packet()
        print(packet)
    else:
        print("No test selected")
    print("That's all for now")
    arduino.close()
