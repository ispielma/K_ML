# -*- coding: utf-8 -*-
"""
Created on Wed May 18 15:20:21 2022
Last Updated on Wed May 18 11:39:32 2022

@author: rubidium

Defines the blacs worker class and functions for the Arduino_TEC_Control device
"""

import threading
import time
import numpy as np
import labscript_utils.h5_lock
import h5py

from blacs.tab_base_classes import Worker
import labscript_utils.properties


class Arduino_TEC_Control_Worker(Worker):
    #Defined for blacs functionality (spot to connect ot device, set initial variables, etc.)
    def init(self):
        #import these here for reinitialization purposes
        global Arduino_TEC_Control
        from .Arduino_TEC_Control import Arduino_TEC_Control
        
        global zprocess; import zprocess

        #connect to the TEC control class as self.controller
        self.controller = Arduino_TEC_Control(self.addr, termination=self.termination)
        print('Connected to Arduino_TEC_Control')
        
        # #variables for later use  

        self.timeTag = 0           #used later for tracking time to complete a shot
        
        self.temp = 0
        self.out_volt = 0
        self.setpoint = 0
        self.Kcrit = 0
        self.Tcrit = 0
        self.Kp = 0
        self.Ki = 0
        self.Kd = 0
        
        self.full_pack = []        #used to store the packet of values, including temperature, voltage, setpoint, and PID shares
        self.last_pack = []        #used for the last packet of values (may not need)
        
        self.save_pack = {} 
    
    #Defined for blacs functionality - function necessary to shutdown the tab
    def shutdown(self):
        self.controller.close()


    #Defined for blacs functionality - when blacs stat is transition to buffered mode (before a shot), minimal required preparation
    #           for the h5 file (and if necessry, halt any extraneous processes)
    def transition_to_buffered(self, device_name, h5file, front_panel_values, refresh):
        self.h5file = h5file        #define h5 for reference
        self.device_name = 'Arduino_TEC_Control'          #device name to be called upon later
        #very quickly add the device to the h5 and then return (don't save anything yet)
        with h5py.File(h5file, 'r') as hdf5_file:           
            print('\n' + h5file)
            self.controller_params = labscript_utils.properties.get(
                hdf5_file, device_name, 'device_properties'
            )
        return {}


    #Defined for blacs functionality - when blacs stat is transition to manual mode (after a shot), collect appropriate
    #           device data for the h5 file and reactivate any important manual mode functionalities that were halted (if any)
    def transition_to_manual(self):
        
        #start timer for how long a save takes during a shot
        self.timeTag = time.time()      #set to current time
        print('Downloading temperature and changes...')
        
        #grab a new packet of the latest temperature, setpoint, out voltage, and PID shares 
        self.full_pack = self.controller.grab_new_packet()
        self.controller.call_plumber()     #to flush the serial
        
        self.update_values()   #updates all of the individual variables using the latest full packet
        # self.temp = self.full_pack[0]
        # self.setpoint = self.full_pack[2]
        # self.Kp = self.full_pack[5]
        # self.Ki = self.full_pack[6]
        # self.Kd = self.full_pack[7]
        
        self.save_pack['temp'] = self.temp
        self.save_pack['setpoint'] = self.setpoint
        self.save_pack['Kp'] = self.Kp
        self.save_pack['Ki'] = self.Ki
        self.save_pack['Kd'] = self.Kd
        
        downTime = time.time() - self.timeTag   #calculate how much time was spent getting and setting the packet
        print('Took %s seconds' %(downTime)) 

        # Collect temp data in an array
        self.timeTag = time.time()       #reuse timeTag (for time it takes to write to h5)
        
        #Create a numpy array to serve as the dataset for latest temperature values and fill
        data = np.empty([1, 1], dtype=float)
        data[0,0] = self.temp

        # Open the h5 file after download, create an Arduino_TEC_Control folder, and save attributes/ data
        with h5py.File(self.h5file, 'r+') as hdf_file:
            print('Saving attributes and data...')
            grp = hdf_file['/devices/Arduino_TEC_Control']  #directs use of "grp" to an Arduino_TEC_Control device folder
            for item in self.save_pack:
                grp.attrs.create(item, self.save_pack[item])  #creates an attribute to go with the dataset array
                
            grp2 = hdf_file.create_group('/data/temps') #directs use of "grp2" to a temps folder in data
            dset = grp2.create_dataset(self.device_name, track_order= True, data=data)  #creates a dataset for grp2 (from the array "data")
            dset.attrs.create('temp', self.save_pack['temp'])
            
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


    #Grabs an entirely new packet from the arduino, including the temperature, out voltage, setpoint, and PID shares
    def update_values(self):
        self.temp = self.full_pack[0]
        self.out_volt = self.full_pack[1]
        self.setpoint = self.full_pack[2]
        self.Kcrit = self.full_pack[3]
        self.Tcrit = self.full_pack[4]
        self.Kp = self.full_pack[5]
        self.Ki = self.full_pack[6]
        self.Kd = self.full_pack[7]
        return 



#The following functions talk to the arduino   
    
    #Grabs an entirely new packet from the arduino, including the temperature, out voltage, setpoint, and PID shares
    def initial_packet(self):
        self.full_pack = self.controller.grab_init()
        print('Grabbed initial value packet')
        self.controller.call_plumber()     #to flush the serial
        self.update_values()   #updates all of the individual variables using the latest full packet
        return self.full_pack
    

    #Requests a packet for any changed values (as compared to the last request)
    def new_packet(self, verbose = False):
        if verbose:
            print("Requesting new temperature and shares...")
        self.full_pack = self.controller.grab_new_packet()
        self.controller.call_plumber()     #to flush the serial
        self.update_values()   #updates all of the individual variables using the latest full packet
        return self.full_pack


    #Performs a check of the latest called packet and returns the packet
    def packet_return(self):
        print("Calling latest packet...")
        return self.full_pack
    
    
    #Accepts setpoint, and then sends a setpoint write command for a changed setpoint value
    def set_setpoint(self, write_setpoint):
        print("Writing new temperature setpoint...")
        if write_setpoint != self.setpoint:
            new = self.controller.set_setpoint(write_setpoint)
            self.controller.call_plumber()     #to flush the serial
            #self.full_packet = self.controller.grab_new_packet()
            #self.update_values()   #updates all of the individual variables using the latest full packet
            #self.controller.call_plumber()     #to flush the serial
            print(new)
        else:
            pass
        return


    #Accepts Kp share, and then sends a Kp write command for a changed Kp value
    def set_Kp(self, write_Kp):
        print("Writing new Kp share...")
        if write_Kp != self.Kp:
            new = self.controller.set_Kp(write_Kp)
            self.controller.call_plumber()     #to flush the serial
            print(new)
        else:
            pass
        return


    #Accepts Ki share, and then sends a Ki write command for a changed Ki value
    def set_Ki(self, write_Ki):
        print("Writing new Ki share...")
        if write_Ki != self.Ki:
            new = self.controller.set_Ki(write_Ki)
            self.controller.call_plumber()     #to flush the serial
            print(new)
        else:
            pass
        return


    #Accepts Kd share, and then sends a Kd write command for a changed Kd value
    def set_Kd(self, write_Kd):
        print("Writing new Kd share...")
        if write_Kd != self.Kd:
            new = self.controller.set_Kd(write_Kd)
            self.controller.call_plumber()     #to flush the serial
            print(new)
        else:
            pass
        return

    
    #Accepts Kp share, and then sends a Kp write command for a changed Kp value
    def set_defaults(self):
        print("Resetting to default values...")
        self.controller.set_default_settings()
        self.controller.call_plumber()     #to flush the serial
        self.full_pack = self.controller.grab_new_packet()
        self.update_values()   #updates all of the individual variables using the latest full packet
        self.controller.call_plumber()     #to flush the serial
        return self.full_pack
    


##These final three functions are only here for printouts
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
 
        
 
    