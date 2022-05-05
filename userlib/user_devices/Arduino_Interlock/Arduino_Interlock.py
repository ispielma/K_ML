#Module for the Arduino_Interlock device
#Modeling from Tekscope device in labscript
#The Arduino_Interlock is in a beta development state at the moment
import pyvisa
import numpy as np
import time

class Arduino_Interlock:
    """"Class for connecting to the arduino interlock using PyVISA"""
    def __init__(self, addr='ASLR?*::INSTR', 
                 timeout=10, termination='\r\n'):
        rm = pyvisa.ResourceManager()
        devices = rm.list_resources(addr)
        assert len(devices), "pyvisa didn't find any connected devices matching " + addr
        self.device = rm.open_resource(devices[0])
        self.device.timeout = 1000 * timeout
        self.device.read_termination = termination
        #self.idn = self.device.query('*IDN?')             #Need to add a command to support this in the arduino first
        self.read = self.device.read
        self.write = self.device.write
        self.query = self.device.query
        self.flush = self.device.flush
        self.numSensors = 16
        
        self.temp_packet = ""
        self.setpoint_packet = ""
        self.status_packet = ""
        
        #empty lists/dictionaries to be used for storing values
        self.temperatures = []
        self.lastTemps = []
        self.setpoints = []
        self.lastSetpoints = []
        self.status = []
        self.lastStatus = []
        self.packet = []
        
        self.chan_temps = {}
        self.chan_lastTemps = {}
        self.chan_temperatures = {}
        self.chan_lastTemperatures = {}
        self.chan_setpoints = {}
        self.chan_lastSetpoints = {}
        self.this_dict = {}

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    def call_plumber(self, verbose=False):
         if verbose:
             print('Plumber is here - Time to flush')
         self.device.flush(pyvisa.constants.VI_READ_BUF_DISCARD)
         if verbose:
             print("Flush attempted")

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
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
    def send_call_num(self, verbose=False):
         if verbose:
             print('Generating call number...')
         call_num_gen = time.time()
         call_str = str(call_num_gen)[-4:]
         try:    
             call_int = int(call_str)
         except ValueError:
             print("Error: Call number not int()")
             call_str = '1000'
             call_int = int(call_str)
    
         if verbose:
            print('The call number being sent is %s' %(call_str))
         call_read = self.device.query('@callNum, '+call_str)
         expected_read ="Call Number received : "+str(call_int)
         if call_read == expected_read:
             if verbose:    
                 print(call_read)
         else:
             self.call_plumber()
             if verbose:
                 print('**!Call Error!**')
                 print(call_read)
                 print("Expected ",expected_read)
                 #self.call_plumber()
                 print('!! Cannot rectify call number !!')
                 #raise an error here someday
         return


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # def channel_names(self, all=True):
    #     """Return a dictionary of the channel names to correspond with each channel number, if such exist. """
    #     #***!!ARDUINO INTERLOCK DOES NOT CURRENTLY SUPPORT THIS FUNCTION!!***
    #     #will need arduino to list active channels (i.e. ones that are supposed to be connected to the thermocouples)
    #     #will most likely choose to include a way to discern between open circuit channels - have to think about practical safety / failures
        
    #     # #planning to use this to store the names of each channel with the assigned channel number as a dictionary
    #     # #all other info for a channel (current temp, last temp, interlock setpoint) will be stored as a list
        
    #     numSensors = self.numSensors
    #     responses = []
    #     chans = {}
        
    #     self.send_call_num()
        
    #     # # determine the device's channel name assignment for the channel number
    #     self.device.write('@names,')
        
    #     for n in range(numSensors):
    #         rawOutput = self.device.read_bytes(50, chunk_size = None, break_on_termchar = True)
    #         try:
    #             output = rawOutput.decode('utf-8')
    #             responses.append(output)
    #         except UnicodeDecodeError:
    #             print("******!! PYTHON ERROR for channel_names: Could not decode!******")
    #             print(rawOutput)

    #     # # create a dict from the responses to store actual channel names, like MOT_QUAD_I, etc.            
    #     for n in range(numSensors):    
    #         respon = responses[n]
    #         name, val = respon.rsplit(';',1)
    #         chans[val] = {name}

    #     return chans    

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def interlock_setpoints(self, all=True):
        """Return a list of the channel interlock setpoints, in order of channel number. """
        #will need arduino to list setpoints of channels (Probably based on active channels) - include in degrees Celcius     
        
        self.send_call_num()
        
        numSensors = self.numSensors
        self.setpoints = []
        # # determine the device's channel name assignment for the channel number
        self.device.write('@chanSetpoints,')
        
        for n in range(numSensors):
            rawOutput = self.device.read_bytes(75, chunk_size = None, break_on_termchar = True)
            try:
                output = rawOutput.decode('utf-8')
                self.setpoints.append(output)
            except UnicodeDecodeError:
                print("******!! PYTHON ERROR for channel_names: Could not decode!******")
                print(rawOutput)

        return self.setpoints

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def channel_temperatures(self, all=True):
            """Return a list of the channel interlock setpoints, in order of channel number. """
            #will need arduino to list setpoints of channels (Probably based on active channels) - include in degrees Celcius
            
            self.send_call_num()
            
            numSensors = self.numSensors
            self.temperatures = []
            # # determine the device's channel name assignment for the channel number
            self.device.write('@temps,')
            #time.sleep(0.05)
            
            for n in range(numSensors):
                rawOutput = self.device.read_bytes(75, chunk_size = None, break_on_termchar = True)
                try:
                    output = rawOutput.decode('utf-8')
                    self.temperatures.append(output)
                except UnicodeDecodeError:
                    print("******!! PYTHON ERROR for channel_names: Could not decode!******")
                    print(rawOutput)

            return self.temperatures

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def channel_last_temps(self, all=True):
            """Return a list of the channel last temperatures, in order of channel number. """
            #creates a list to be used for storing the last temperatures of the channels
            
            self.send_call_num()
            
            numChan = self.numSensors
            
            # This will be stored on the python side as a list
            self.lastTemps = []
            #populate the list with placeholder values for channel temps
            for n in numChan:
                self.lastTemps.insert(n, 0.0)
            
            return self.lastTemps

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def grab_init(self, all=True):
            """Return full dictionaries of the channel temperatures, channel setpoints, and status. """
            #creates a list to be used for storing the last temperatures of the channels
            
            self.send_call_num()
            
            self.device.write('@init,')
            time.sleep(1)
            rawOutput = self.device.read_bytes(500, chunk_size = None, break_on_termchar = True)
            output = rawOutput.decode('utf-8')
            #print(output)

            # This will be stored on the python side as a list and then dictionary 
            #      of all the packet info (should be 16 channel temps, 16 setpoints, and the status)
            self.temp_packet, self.setpoint_packet, self.status_packet, junk = output.split('#')
            
            self.temperatures = self.temp_packet[:-1].split(",")
            #print(self.temperatures)
            self.chan_temperatures = self.convert_to_dict(self.temperatures)
            self.chan_lastTemperatures = self.chan_temperatures
            
            self.setpoints = self.setpoint_packet[:-1].split(",")
            #print(self.setpoints)
            self.chan_setpoints = self.convert_to_dict(self.setpoints)
            self.chan_lastSetpoints = self.chan_setpoints
            
            self.status = self.status_packet[:-1].split(",")
            self.lastStatus = self.status
            #print(self.lastStatus)
            
            return self.chan_temperatures, self.chan_setpoints, self.status     

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def grab_new_packet(self, all=True):
            """Return updates to channel temperatures, channel setpoints, and status. """
            #creates a list to be used for storing the last temperatures of the channels
            
            self.send_call_num()
            
            self.device.write('@pack,')
            
            rawOutput = self.device.read_bytes(500, chunk_size = None, break_on_termchar = True)
            output = rawOutput.decode('utf-8')

            # This will be stored on the python side as a list and then dictionary 
            #      of all the packet info (should be 16 channel temps, 16 setpoints, and the status)
            self.temp_packet, self.setpoint_packet, self.status_packet, junk = output.split('#')
            #print(self.temp_packet)
            if self.temp_packet:
                self.temperatures = self.temp_packet[:-1].split(",")
                self.chan_temperatures = self.convert_to_dict(self.temperatures)
                for ch in self.chan_temperatures:
                    self.chan_lastTemperatures[ch] = self.chan_temperatures[ch]
            
            #print(self.setpoint_packet)
            if self.setpoint_packet:    
                self.setpoints = self.setpoint_packet[:-1].split(",")
                self.chan_setpoints = self.convert_to_dict(self.setpoints)
                for ch in self.chan_setpoints:
                    self.chan_lastSetpoints[ch] = self.chan_setpoints[ch]
            
            #print(self.status_packet)
            if self.status_packet:
                self.status = self.status_packet[:-1].split(",")
                if self.status[0] == 'True':
                    self.status_trig = self.status[1]
                self.lastStatus = self.status
            
            return self.chan_lastTemperatures, self.chan_lastSetpoints, self.lastStatus
  
    
  
#-----------------------------------------------------------------
    #have to check to ensure temperatures are received and stored properly    
    def get_temps(self, verbose=False):
        if verbose:
            print('Grabbing thermocouple temperatures...')
        now_temps = self.channel_temperatures()
        self.chan_temperatures = self.convert_to_dict(now_temps)
        return self.chan_temperatures

#-----------------------------------------------------------------   
    def check_temps(self, verbose=False):
        if verbose:
            print('Sending latest temperatures...')
        latest_temps = self.chan_temperatures
        return latest_temps
    
#-----------------------------------------------------------------    
    def store_last_temps(self, verbose=False):
        numSensors = self.numSensors
        if verbose:
            print('Storing last temperatures...')
        for n in numSensors:
            tempTemp = self.temperatures[n]
            if (self.lastTemps[n] != tempTemp) and (tempTemp != 0.0):
                self.lastTemps[n] = tempTemp
        self.chan_lastTemps = self.convert_to_dict(self.lastTemps)
        return self.chan_lastTemps
    
#-----------------------------------------------------------------   
    #note that setpoints should only change if set_setpoint is used
    def get_setpoints(self, verbose=False):
        if verbose:
            print('Grabbing interlock setpoints...')
        int_set = self.interlock_setpoints()
        self.chan_setpoints = self.convert_to_dict(int_set)
        return self.chan_setpoints

#-----------------------------------------------------------------
    def set_setpoint(self, n, v, verbose=False):
        self.send_call_num()
        chanPos = n
        setVal = v
        if verbose:
            #chanName = chans{chanPos}
            print('Sending new setpoint for channel...')
        self.device.write('@setpoint, %s, %s,'%(chanPos, setVal))
        rawOutput = self.device.read_bytes(75, chunk_size = None, break_on_termchar = True)
        output = rawOutput.decode('utf-8')
        print(output)

#-----------------------------------------------------------------
    def set_default_setpoints(self, verbose=False):
        self.send_call_num()
        if verbose:
            print('Requesting default setpoints...')
        rawOutput = self.device.query('@default,')
        try:
            output = rawOutput.decode('utf-8')
            print(output)
        except AttributeError:
            #print("******!! PYTHON ERROR: Could not decode!******")
            print(rawOutput)
    
#-----------------------------------------------------------------    
    def arduino_save_setpoints(self, verbose=False):
        self.send_call_num() 
        if verbose:
             print('Saving interlock setpoints to Arduino EEPROM...')
        self.device.write('@SV,')
        return

#-----------------------------------------------------------------    
    def digital_lock(self, verbose=False):
        self.send_call_num() 
        if verbose:
             print('Toggling the interlock digital lock trigger')
        resp = self.device.query('@Lock,')
        print(resp)
        return resp
    
#-----------------------------------------------------------------    
    def digital_reset(self, verbose=False):
        self.send_call_num() 
        if verbose:
             print('Sending the digital reset command')
        reset = self.device.query('@push,')
        print(reset)
        return
    
#-----------------------------------------------------------------    
    def get_status(self, verbose=False):
        self.send_call_num() 
        if verbose:
             print('Sending the digital reset command')
        self.status = self.device.query('@status,')
        if verbose:
            print(self.status)
        return self.status
        
#-----------------------------------------------------------------   
    def check_status(self, verbose=False):
        if verbose:
            print('Sending latest interlock status...')
        latest_stat = self.status
        return latest_stat
    
#----------------------------------------------------------------- 
    #meant to be used by BLACS / labscript during shutdown procedures
    def close(self):
        self.device.close()



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# # This has gone beyond the length of a reasonable test script - oops
if __name__ == '__main__':
    arduino = Arduino_Interlock(addr='ASRL20::INSTR', timeout=10)
    Test = input('Choose a Test:\n - "1" : Test temperature grabbing\n - "2" : Test setpoint grabbing\n - "3" : Test setting setpoint'
                 '\n - "4" : Test call number creation\n - "5" : Test temp grab anf setpoint grab together\n - else : Will exit.\n Enter Choice:')
    if Test == "1":     #Test get_temps()
        print("Test 1 selected!")
        for r in range(5):
            temperature_store = arduino.get_temps()
            print(temperature_store)
            arduino.get_status()
            time.sleep(8)
            arduino.call_plumber(verbose = False)
    elif Test == "2":     #Test get_setpoints()
        print("Test 2 selected!")
        time.sleep(2)
        for r in range(5):
            interlocks = arduino.get_setpoints(verbose = True)
            print(interlocks)
            arduino.get_status()
            time.sleep(3)
            arduino.call_plumber(verbose = False)
            #arduino.flush(pyvisa.constants.VI_READ_BUF_DISCARD)
        #interlocks = arduino.get_setpoints(verbose = True)
        #print(interlocks)
    elif Test == "3":     #test set_setpoint()
        print("Test 3 selected!")
        time.sleep(2)
        command = input("Give a channel number and temperature setpoint in the format:"
                        "'[CHAN#];[VALUE]'\nCommand: ")
        name, val = command.rsplit(';',1)
        arduino.set_setpoint(name, val, verbose=True)
        time.sleep(2)
        arduino.call_plumber()
        interlocks = arduino.get_setpoints()
        print(interlocks)
    elif Test == "4":     #Test send_call_num() -> call numbers for call-response
        print("Test 4 selected!")
        time.sleep(2)
        arduino.send_call_num()
    elif Test == "5":     #Test for serial overflow errors - Should be solved with call_plumber()
        print("Test 5 selected!")
        time.sleep(2)
        for r in range(3):
            arduino.get_status()
            temperature_store = arduino.get_temps()
            print(temperature_store)
            time.sleep(3)
            interlocks = arduino.get_setpoints(verbose = True)
            print(interlocks)
            time.sleep(3)
    elif Test == "6":      #Test serial flushing - i.e. call_plumber()
         print("Test 6 selected!")
         time.sleep(2)
         arduino.call_plumber(True)
         print("The flush has occurred (hopefully)")
    elif Test == "7":
         print("Test 7 selected!")     #Test convert_to_dict() - this is now inserted into get_temps
         time.sleep(2)
         temperature_store = arduino.get_temps()
         #storedTemps = arduino.convert_to_dict(temperature_store)
         print(temperature_store)
    elif Test == "8":     #Test digital_lock() and digital_reset()
         print("Test 8 selected!")
         time.sleep(2)
         lockStat = arduino.digital_lock()
         print(lockStat)
         lockSet = input("Update lock and reset?")
         if lockSet == 'yes':
             lockStat2 = arduino.digital_lock()
             print(lockStat2)
             lockRestart = arduino.digital_reset()
             print(lockRestart)
             time.sleep(3)
             arduino.call_plumber()
    elif Test == "9":     #Test get_status()
         print("Test 9 selected!")
         time.sleep(2)
         arduino.get_status()
         time.sleep(2)
         lockStat = arduino.digital_lock()
         print(lockStat)
         arduino.get_status()
         time.sleep(2)
         lockStat2 = arduino.digital_lock()
         print(lockStat2)
         arduino.get_status()
         time.sleep(2)
         lockRestart = arduino.digital_reset()
         print(lockRestart)
         time.sleep(3)
         arduino.get_status()
    elif Test == "10":      #Test check_temps()
         print("Test 10 selected!")
         time.sleep(2)
         arduino.get_temps()
         cur_temps = arduino.check_temps()
         time.sleep(2)
         print(cur_temps)
         cur_temps = arduino.check_temps()
         time.sleep(2)
         print(cur_temps)
         time.sleep(2)
         arduino.get_temps()
         cur_temps = arduino.check_temps()
         time.sleep(2)
         print(cur_temps)
    elif Test == "11":      #Test check_temps()
         print("Test 11 selected!")
         time.sleep(2)
         new_packet = arduino.grab_init()
         #time.sleep(2)
         print(new_packet)
         #time.sleep(2)
         new_packet = arduino.grab_new_packet()
         #time.sleep(2)
         print(new_packet)
    else:
        print("No test selected")
    print("That's all for now")
    arduino.close()
