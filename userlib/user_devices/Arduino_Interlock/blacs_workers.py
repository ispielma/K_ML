# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 12:04:05 2022

@author: rubidium

Defines the blacs worker class and functions for the Arduino_Interlock device
"""

import threading
import time
import numpy as np
import labscript_utils.h5_lock
import h5py

from blacs.tab_base_classes import Worker, define_state
from blacs.tab_base_classes import MODE_MANUAL, MODE_TRANSITION_TO_BUFFERED, MODE_TRANSITION_TO_MANUAL, MODE_BUFFERED  
import labscript_utils.properties


class Arduino_Interlock_Worker(Worker):
    def init(self):
        global Arduino_Interlock
        from .Arduino_Interlock import Arduino_Interlock
        
        global zprocess; import zprocess

        self.interlock = Arduino_Interlock(self.addr, termination=self.termination)
        print('Connected to Arduino_Interlock')
        
        self.stop_acquisition_timeout = None
        self.continuous_stop = threading.Event()
        self.continuous_thread = None
        self.continuous_interval = True
        self.shot_read = False
        self.restart_thread = False
        self.thread_standby = False
        
        # self.lastTemps = {}
        # self.lastSets = {}
        # self.lastStat = ""
        self.newTemps = {}
        self.newSets = {}
        self.newStat = []
        
        self.timeTag = 0
        
        
    
    def shutdown(self):
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
            #self.interlock.timeout = 1000 * self.interlock_params.get('timeout', 5)
        return {}


    def transition_to_manual(self):
        self.continuous_interval = True
        self.shot_read = False
        
        #Grab temperatures, interlock status, and interlock setpoints from the arduino
        self.timeTag = time.time()
        print('Downloading Temps and Status...')
        #temp_vals, intlock_stat = self.interlock.grab_full_packet()
        self.newTemps, self.newSets, self.newStat = self.interlock.grab_new_packet()
        temp_vals = self.newTemps
        intlock_stat = self.newStat[0]
        setpoint_vals = self.newSets
        self.interlock.call_plumber()     #to flush the serial
        downTime = time.time() - self.timeTag
        print('Took %s seconds' %(downTime)) 

        # Collect temp data in an array
        self.timeTag = time.time()
        data = np.empty([self.interlock.numSensors], dtype=float)
        for ch in temp_vals:
            chNum = int(ch)-1
            data[chNum] = temp_vals[ch]

        # Open the file after download, create an Arduino_Interlock folder, and save attributes there
        with h5py.File(self.h5file, 'r+') as hdf_file:
            grp = hdf_file['/devices/Arduino_Interlock']
            print('Saving attributes...')
            grp2 = hdf_file.create_group('/data/temps')
            dset = grp2.create_dataset(self.device_name, track_order= True, data=data)
            for ch in temp_vals:
                if len(ch) == 1: 
                    chNum = "channel_0"+str(ch)+"_temp"
                else:
                    chNum = "channel_"+str(ch)+"_temp"
                grp.attrs.create(chNum, temp_vals[ch])
                dset.attrs.create(chNum, temp_vals[ch])
            if intlock_stat == 'False':
                grp.attrs.create("interlock_trigger_status", 'False')
            elif intlock_stat[0:4] == 'True':
                grp.attrs.create("interlock_trigger_status", 'True')
            else:
                grp.attrs.create("interlock_trigger_status", intlock_stat)
            # for ch in setpoint_vals:
            #     if len(ch) == 1: 
            #         chName = "setpoint_channel_0"+str(ch)
            #     else:
            #         chName = "setpoint_channel_"+str(ch)
            #     grp.attrs.create(chName, setpoint_vals[ch])
        downTime2 = time.time() - self.timeTag
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

    
    def toggle_lock(self):
        print("Attempting to toggle digital lock...")
        locked_status = self.interlock.digital_lock(verbose=True)
        self.interlock.call_plumber()     #to flush the serial
        return locked_status
    
        
    def push_reset(self):
        print("Attempting to reset...")
        self.interlock.digital_reset(verbose=True)
        self.interlock.call_plumber()     #to flush the serial
    
    def initial_packet(self):
        self.newTemps, self.newSets, self.newStat = self.interlock.grab_init()
        print('Grabbed initial value packet')
        self.interlock.call_plumber()     #to flush the serial
        return self.newTemps, self.newSets, self.newStat
    
    def new_temps(self):
        print("Requesting new temperature values...")
        temps = self.interlock.get_temps(verbose=True)
        self.interlock.call_plumber()     #to flush the serial
        return temps
    
    
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
        
    
    def new_stat(self):
        print("Requesting new interlock status...")
        status = self.interlock.get_status()
        self.interlock.call_plumber()     #to flush the serial
        return status
    
    
    def stat_return(self):
        print("Calling latest interlock status...")
        status = self.interlock.check_status()
        return status
    
    
    def new_setpoints(self):
        print("Requesting the interlock setpoints...")
        setpoints = self.interlock.get_setpoints(verbose=True)
        self.interlock.call_plumber()     #to flush the serial
        return setpoints
    
    
    def set_setpoints(self, write_setpoints):
        print("Writing new interlock setpoints...")
        cur_setpoints = self.interlock.get_setpoints(verbose=False)
        self.interlock.call_plumber()     #to flush the serial
        
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
    
    
    def set_default_setpoints(self):
        print("Resetting interlock setpoints...")
        self.interlock.set_default_setpoints(verbose=False)
        self.interlock.call_plumber()     #to flush the serial
        self.interlock.arduino_save_setpoints(verbose=True)
        return
    
    def new_packet(self, verbose = True):
        if verbose:
            print("Requesting new temperature values and status...")
        self.newTemps, self.newSets, self.newStat = self.interlock.grab_new_packet()
        self.interlock.call_plumber()     #to flush the serial
        return self.newTemps, self.newSets, self.newStat
    
    
    def shot_check(self):
        #print("Checking for active shots...")
        shot = self.shot_read
        return shot
    

#These final three functions are likely defunct - will have to test    
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


    def start_continuous(self, interval=5):
        print("Starting automated temperature acquisition")
        #assert self.continuous_thread is None
        #interval = self.continuous_interval
        if self.thread_standby == False:
            self.continuous_thread = threading.Thread(
                target=self.continuous_loop, args=(), daemon=True
                )
            self.continuous_thread.start()
            self.thread_standby = True
        else:
            #self.restart_thread = True
            self.continuous_interval = True


    def stop_continuous(self, pause=False):
        assert self.continuous_thread is not None
        self.continuous_interval = False
        #self.restart_thread = False
        print("Continuous acquisition has been stopped")
       
           
           

         
