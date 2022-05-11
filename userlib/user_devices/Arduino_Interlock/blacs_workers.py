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
    def init(self):
        global Arduino_Interlock
        from .Arduino_Interlock import Arduino_Interlock
        
        global zprocess; import zprocess

        self.interlock = Arduino_Interlock(self.addr, termination=self.termination)
        print('Connected to Arduino_Interlock')
        
        #variables for later use  
        self.stop_acquisition_timeout = None
        self.continuous_stop = threading.Event()
        self.continuous_thread = None
        self.continuous_interval = True
        self.shot_read = False
        self.restart_thread = False
        self.thread_standby = False
        
        #dictionaries and list to store temperature values, setpoints, and status 
        self.newTemps = {}
        self.newSets = {}
        self.newStat = []
        
        self.timeTag = 0 #used later for tracking time to complete a shot
        
    
    def shutdown(self):
        self.interlock.close()

    def restart(self, args, kargs):
        self.interlock.close()

    def transition_to_buffered(self, device_name, h5file, front_panel_values, refresh):
        self.continuous_interval = False
        self.shot_read = True
        self.h5file = h5file 
        self.device_name = 'Arduino_Interlock'
        with h5py.File(h5file, 'r') as hdf5_file:
            print('\n' + h5file)
            self.interlock_params = labscript_utils.properties.get(
                hdf5_file, device_name, 'device_properties'
            )
        return {}


    def transition_to_manual(self):
        self.continuous_interval = True
        self.shot_read = False   #!! May not use this anymore!
        
        #Grab temperatures, interlock status, and interlock setpoints from the arduino
        self.timeTag = time.time()      #set to current time
        print('Downloading Temps and Status...')
        
        #grab a new packet of the latest temperatures, setpoints, and status update 
        self.newTemps, self.newSets, self.newStat = self.interlock.grab_new_packet()
        temp_vals = self.newTemps
        intlock_stat = self.newStat[0]
        self.interlock.call_plumber()     #to flush the serial
        downTime = time.time() - self.timeTag   #calculate how much time was spent getting and setting the packet
        print('Took %s seconds' %(downTime)) 

        # Collect temp data in an array
        self.timeTag = time.time()       #reuse timeTag (for time it takes to write to h5)
        
        #Create a numpy array to serve as the dataset for latest temperature values and fill
        data = np.empty([self.interlock.numSensors, 2], dtype=float)
        for ch in temp_vals:
            chNum = int(ch)-1
            data[chNum, 0] = chNum+1 
            data[chNum, 1] = temp_vals[ch]

        # Open the h5 file after download, create an Arduino_Interlock folder, and save attributes there
        with h5py.File(self.h5file, 'r+') as hdf_file:
            grp = hdf_file['/devices/Arduino_Interlock']  #directs use of "grp" to an Arduino_Interlock device folder
            print('Saving attributes...')
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


    def program_manual(self, values):        
        return values


    def abort(self):
        print('aborting!')
        return True


    def abort_buffered(self):
        print('abort_buffered: ...')
        return self.abort()


    def abort_transition_to_buffered(self):
        print('abort_transition_to_buffered: ...')
        return self.abort()


    #Activates the self.interlock.digital_lock function for digitally locking and unlocking the interlock
    def toggle_lock(self):
        print("Attempting to toggle digital lock...")
        locked_status = self.interlock.digital_lock(verbose=True)
        self.interlock.call_plumber()     #to flush the serial
        return locked_status
    
    
    #Activates the self.digital_reset function for digitally pushing the reset button    
    def push_reset(self):
        print("Attempting to reset...")
        self.interlock.digital_reset(verbose=True)
        self.interlock.call_plumber()     #to flush the serial
    
    
    #Grabs an entirely new packet from the arduino, including all channel temperatures, channel setpoints, and the interlock status
    def initial_packet(self):
        self.newTemps, self.newSets, self.newStat = self.interlock.grab_init()
        print('Grabbed initial value packet')
        self.interlock.call_plumber()     #to flush the serial
        return self.newTemps, self.newSets, self.newStat
    
    
    #Grabs a full call of only the channel temperatures  (!!may be ignored now)
    def new_temps(self):
        print("Requesting new temperature values...")
        temps = self.interlock.get_temps(verbose=True)
        self.interlock.call_plumber()     #to flush the serial
        return temps
    
    
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
        status = self.interlock.get_status()
        self.interlock.call_plumber()     #to flush the serial
        return status
    
    
    #Performs a check of the latest called interlock status and returns that status
    def stat_return(self):
        print("Calling latest interlock status...")
        status = self.interlock.check_status()
        return status
    
    #Grabs a full call of only the channel setpoints (!! may be ignored now)
    def new_setpoints(self):
        print("Requesting the interlock setpoints...")
        setpoints = self.interlock.get_setpoints(verbose=True)
        self.interlock.call_plumber()     #to flush the serial
        return setpoints
    
    
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
            if write_setpoints[ch] != cur_ch_setpoint:
                new_setpoint = self.interlock.set_setpoint(n=chNum,v=chVal)
                self.interlock.call_plumber()     #to flush the serial
                print(new_setpoint)
            else:
                pass
        self.interlock.arduino_save_setpoints(verbose=True)
        return
    
    
    #Sends the command to return the setpoint values to the default programmed values in the arduino
    def set_default_setpoints(self):
        print("Resetting interlock setpoints...")
        self.interlock.set_default_setpoints(verbose=False)
        self.interlock.call_plumber()     #to flush the serial
        self.interlock.arduino_save_setpoints(verbose=True)
        return
    
    
    #Requests a packet for any changed values (as compared to the last request)
    def new_packet(self, verbose = True):
        if verbose:
            print("Requesting new temperature values and status...")
        self.newTemps, self.newSets, self.newStat = self.interlock.grab_new_packet()
        self.interlock.call_plumber()     #to flush the serial
        return self.newTemps, self.newSets, self.newStat
    
    
    #Checks to see if a shot is being read (I cannot recall if this actually has proper use)
    def shot_check(self):
        #print("Checking for active shots...")
        shot = self.shot_read
        return shot
    

##These final three functions are defunct (the thread is not necessary)  - may keep for printouts 
    #signifies the start of a continuous loop (formerly created a continuous call loop, but the implementation was changed)
    def continuous_loop(self):
        print("Acquiring...")
        # interval=5
        # while True:
        #     # if self.continuous_interval:
        #     #     # self.interlock.get_status()
        #     #     # self.interlock.call_plumber()     #to flush the serial
        #     #     # self.interlock.get_temps(verbose=True)
        #     #     # self.interlock.call_plumber()     #to flush the serial        
        #     #     time.sleep(interval)
        #     # else:
        #         pass

    #Begins an automatic loop thread if none exists, or otherwise indicates that the auto loop should continue acquiring values
    # (!! I believe this thread no longer does anything)
    def start_continuous(self, interval=5):
        print("Starting automated temperature acquisition")
        #assert self.continuous_thread is None
        #interval = self.continuous_interval
        # if self.thread_standby == False:
        #     self.continuous_thread = threading.Thread(
        #         target=self.continuous_loop, args=(), daemon=True
        #         )
        #     self.continuous_thread.start()
        #     self.thread_standby = True
        # else:
        #     #self.restart_thread = True
        #     self.continuous_interval = True

    #Stops auto-acquisition from the loop thread by setting the continuous_interval to false
    def stop_continuous(self, pause=False):
        # assert self.continuous_thread is not None
        # self.continuous_interval = False
        #self.restart_thread = False
        print("Continuous acquisition has been stopped")
       
           
           

         
