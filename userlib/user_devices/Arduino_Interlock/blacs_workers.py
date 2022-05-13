# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 12:04:05 2022
Last Updated on Mon May 09 15:31:37 2022

@author: rubidium

Defines the blacs worker class and functions for the Arduino_Interlock device
"""

import threading
import time
import numpy as np
import labscript_utils.h5_lock
import h5py

from blacs.tab_base_classes import Worker
import labscript_utils.properties


class Arduino_Interlock_Worker(Worker):
    #Defined for blacs functionality (spot to connect ot device, set initial variables, etc.)
    def init(self):
        #import these here for reinitialization purposes
        global Arduino_Interlock
        from .Arduino_Interlock import Arduino_Interlock
        
        global zprocess; import zprocess

        #connect to the interlock class as self.interlock
        self.interlock = Arduino_Interlock(self.addr, termination=self.termination)
        print('Connected to Arduino_Interlock')
        
        #variables for later use  
        self.shot_read = False          #intended to mark when shots are running - currently does not work
        self.timeTag = 0 #used later for tracking time to complete a shot
        
        #dictionaries and list to store temperature values, setpoints, and status 
        self.newTemps = {}
        self.newSets = {}
        self.newStat = []
        
    
    #Defined for blacs functionality - function necessary to shutdown the tab
    def shutdown(self):
        self.interlock.close()

    #May not be necessary - will check
    def restart(self, args, kargs):
        self.interlock.close()

    #Defined for blacs functionality - when blacs stat is transition to buffered mode (before a shot), minimal required preparation
    #           for the h5 file (and if necessry, halt any extraneous processes)
    def transition_to_buffered(self, device_name, h5file, front_panel_values, refresh):
        self.shot_read = True        #Not currently working as intended (so sort of useless)
        self.h5file = h5file        #define h5 for reference
        self.device_name = 'Arduino_Interlock'          #device name to be called upon later
        #very quickly add the device to the h5 and then return (don't save anything yet)
        with h5py.File(h5file, 'r') as hdf5_file:           
            print('\n' + h5file)
            self.interlock_params = labscript_utils.properties.get(
                hdf5_file, device_name, 'device_properties'
            )
        return {}

    #Defined for blacs functionality - when blacs stat is transition to manual mode (after a shot), collect appropriate
    #           device data for the h5 file and reactivate any important manual mode functionalities that were halted (if any)
    def transition_to_manual(self):
        self.shot_read = False   #!! May not use this anymore!
        
        #Grab temperatures, interlock status, and interlock setpoints from the arduino
        self.timeTag = time.time()      #set to current time
        print('Downloading Temps and Status...')
        
        #grab a new packet of the latest temperatures, setpoints, and status update 
        self.newTemps, self.newSets, self.newStat = self.interlock.grab_new_packet()
        temp_vals = self.newTemps       #local dictionary for easy use
        intlock_stat = self.newStat[0]      #local string for easy use
        self.interlock.call_plumber()     #to flush the serial
        downTime = time.time() - self.timeTag   #calculate how much time was spent getting and setting the packet
        print('Took %s seconds' %(downTime)) 

        # Collect temp data in an array
        self.timeTag = time.time()       #reuse timeTag (for time it takes to write to h5)
        
        #Create a numpy array to serve as the dataset for latest temperature values and fill
        data = np.empty([self.interlock.numSensors, 2], dtype=float)
        for ch in temp_vals:        #add each channel to the array
            chNum = int(ch)-1
            data[chNum, 0] = chNum+1 
            data[chNum, 1] = temp_vals[ch]

        # Open the h5 file after download, create an Arduino_Interlock folder, and save attributes/ data
        with h5py.File(self.h5file, 'r+') as hdf_file:
            grp = hdf_file['/devices/Arduino_Interlock']  #directs use of "grp" to an Arduino_Interlock device folder
            print('Saving attributes and data...')
            grp2 = hdf_file.create_group('/data/temps') #directs use of "grp2" to a temps folder in data
            dset = grp2.create_dataset(self.device_name, track_order= True, data=data)  #creates a dataset for grp2 (from the array "data")
            for ch in temp_vals:
                if len(ch) == 1: 
                    chNum = "channel_0"+str(ch)+"_temp"
                else:
                    chNum = "channel_"+str(ch)+"_temp"
                dset.attrs.create(chNum, temp_vals[ch])  #creates an attribute to go with the dataset array
            #This sets interlock trigger status as an attribute in the Arduino_interlock folder with appropriate indication
            if intlock_stat == 'False':
                grp.attrs.create("interlock_trigger_status", 'False')
            elif intlock_stat[0:4] == 'True':
                grp.attrs.create("interlock_trigger_status", 'True')
            else:
                grp.attrs.create("interlock_trigger_status", intlock_stat)
        downTime2 = time.time() - self.timeTag  #calculate time it takes to open and set the values in the h5
        print('Done!')
        print('Took %s seconds' %(downTime2)) 
        return True

    #Define for blacs
    def program_manual(self, values):        
        return values

    #Define for blacs to control the device during an abort
    def abort(self):
        print('aborting!')
        return True

    #Define for blacs to abort during buffered mode (while taking shots)
    def abort_buffered(self):
        print('abort_buffered: ...')
        return self.abort()

    #Define for blacs to abort during transition to buffered mode (right before taking shots)
    def abort_transition_to_buffered(self):
        print('abort_transition_to_buffered: ...')
        return self.abort()



#The following functions talk to the arduino

    #Activates the self.interlock.digital_lock function for digitally locking and unlocking the interlock
    def toggle_lock(self):
        print("Attempting to toggle digital lock...")
        locked_status = self.interlock.digital_lock(verbose=True)       #Activate interlock class "digital lock" function
        self.interlock.call_plumber()     #to flush the serial
        return locked_status
    
    
    #Activates the self.digital_reset function for digitally pushing the reset button    
    def push_reset(self):
        print("Attempting to reset...")
        self.interlock.digital_reset(verbose=True)      #Activate interlock class "digital_reset" function
        self.interlock.call_plumber()     #to flush the serial
    
    
    #Grabs an entirely new packet from the arduino, including all channel temperatures, channel setpoints, and the interlock status
    def initial_packet(self):
        self.newTemps, self.newSets, self.newStat = self.interlock.grab_init()
        print('Grabbed initial value packet')
        self.interlock.call_plumber()     #to flush the serial
        return self.newTemps, self.newSets, self.newStat
    

    #Requests a packet for any changed values (as compared to the last request)
    def new_packet(self, verbose = True):
        if verbose:
            print("Requesting new temperature values and status...")
        self.newTemps, self.newSets, self.newStat = self.interlock.grab_new_packet()
        self.interlock.call_plumber()     #to flush the serial
        return self.newTemps, self.newSets, self.newStat

    
    #Grabs a full call of only the channel temperatures  (!!may be ignored now)
    def new_temps(self):
        print("Requesting new temperature values...")
        self.newTemps, self.newSets, self.newStat = self.interlock.grab_new_packet()
        self.interlock.call_plumber()     #to flush the serial
        return self.newTemps
    
    
    #Performs a check for temperature values and then grabs, unless there are no temperatures which forces a full new temp grab
    def temp_return(self):
        print("Calling latest received temperature values...")
        if self.interlock.chan_temperatures:
            tempers = self.interlock.check_temps(verbose=True)
            self.interlock.call_plumber()     #to flush the serial
            return tempers
        else:
            self.interlock.get_temps()
            tempers = self.interlock.check_temps(verbose=True)
            self.interlock.call_plumber()     #to flush the serial
            return tempers
        
    
    #Grabs the new status of the interlock
    def new_stat(self):
        print("Requesting new interlock status...")
        self.newTemps, self.newSets, self.newStat = self.interlock.grab_new_packet()
        self.interlock.call_plumber()     #to flush the serial
        return self.newStat
  
    
    #Performs a check of the latest called interlock status and returns that status
    def stat_return(self):
        print("Calling latest interlock status...")
        status = self.interlock.check_status()
        return status
    
    
    #Grabs a full call of only the channel setpoints (!! may be ignored now)
    def new_setpoints(self):
        print("Requesting the interlock setpoints...")
        self.newTemps, self.newSets, self.newStat = self.interlock.grab_new_packet()
        self.interlock.call_plumber()     #to flush the serial
        return self.newSets
    
    
    #Accepts setpoint ch# and value dict, and then sends a setpoint write command for any changed setpoint values
    def set_setpoints(self, write_setpoints):
        print("Writing new interlock setpoints...")
        cur_setpoints = self.interlock.get_setpoints(verbose=False)  #calls current setpoints for reference
        self.interlock.call_plumber()     #to flush the serial
        
        #writes a new setpoint for a particular channel after verifying that that channel's setpoint has changed value
        for ch in range(self.interlock.numSensors):
            chNum = ch+1
            chVal = write_setpoints[ch]
            cur_ch_setpoint = cur_setpoints[str(chNum)]
            #checks current setpoints and only writes a new one if there is a change (this saves time/ error potential)
            if write_setpoints[ch] != cur_ch_setpoint:
                new_setpoint = self.interlock.set_setpoint(n=chNum,v=chVal)
                self.interlock.call_plumber()     #to flush the serial
                print(new_setpoint)
            else:
                pass
        #this save the setpoints in the arduino EEPROM memory so that they will remain even if the device is restarted/ reset
        self.interlock.arduino_save_setpoints(verbose=True)
        return
    
    
    #Sends the command to return the setpoint values to the default programmed values in the arduino
    def set_default_setpoints(self):
        print("Resetting interlock setpoints...")
        self.interlock.set_default_setpoints(verbose=False)
        self.interlock.call_plumber()     #to flush the serial
        self.interlock.arduino_save_setpoints(verbose=True)
        return
    
    

#This function had intended functionality for checking for active shots (and is still referenced by the blacs_tab),
#       but it doesn't really do anything useful at this time    
    #Checks to see if a shot is being read (npt properly working at this time)
    def shot_check(self):
        shot = self.shot_read
        return shot
    

##These final three functions are only here for printouts now - not super necessary anymore but they are here for now
    #signifies the acquisition of a new packet
    def continuous_loop(self, verbose = True):
        if verbose:
            print("Acquiring...")
 

    #Prints a continuous acquisition start message in the terminal output
    def start_continuous(self, verbose = True):
        if verbose:
            print("Starting automated temperature acquisition")


    #Prints a continuous acquisition stop message in the terminal output
    def stop_continuous(self, verbose = True):
        if verbose:
            print("Continuous acquisition has been stopped")
 
        
 
    
 
    