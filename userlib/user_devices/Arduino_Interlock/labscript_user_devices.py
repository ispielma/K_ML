# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 11:28:34 2022

@author: rubidium
"""

from labscript import Device, LabscriptError, set_passed_properties

class Arduino_Interlock(Device):
    """A labscript_device for the Arduino_interlock using a visa interface.
          connection_table_properties (set once)
          termination: character signalling end of response

          device_properties (set per shot)
          timeout: in seconds for response to queries over visa interface 
    """
    description = 'Arduino Interlock Monitor'

    @set_passed_properties(
        property_names = {
            'connection_table_properties': ['termination'],
            'device_properties': ['timeout']}
        )
    def __init__(self, name, addr, 
                 termination='\r\n',
                 timeout=5,
                 **kwargs):
        Device.__init__(self, name, None, addr, **kwargs)
        self.name = name
        self.BLACS_connection = addr
        self.termination = termination

    def generate_code(self, hdf5_file):
        # group = self.init_device_name(hdf5_file)
        #Device.generate_code(self, hdf5_file)
        pass