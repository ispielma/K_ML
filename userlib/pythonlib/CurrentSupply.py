#####################################################################
#                                                                   #
# linear_coil_driver.py                                             #
#                                                                   #
# Copyright 2013, Monash University                                 #
#                                                                   #
# This file is part of the labscript suite (see                     #
# http://labscriptsuite.org) and is licensed under the Simplified   #
# BSD License. See the license.txt file in the root of the project  #
# for the full license.                                             #
#                                                                   #
#####################################################################
from labscript_utils.unitconversions.UnitConversionBase import UnitConversion
import numpy as np

class CurrentSupply(UnitConversion):
    base_unit = 'V'

    def __init__(self, calibration_parameters=None):
        
        # To support subclassing better
        try:
            self.derived_units.append('A')
        except:
            self.derived_units = ['A']
        
        if calibration_parameters is None:
            calibration_parameters = {}
        self.parameters = calibration_parameters
        

        self.parameters.setdefault('A_per_V', 1) # A/V
        self.parameters.setdefault('V_0', 0) # V
        
        UnitConversion.__init__(self,self.parameters)


    def A_to_base(self, amps):

        volts = amps / self.parameters['A_per_V'] + self.parameters['V_0']
        return volts
        
    def A_from_base(self,volts):

        amps = (volts - self.parameters['V_0']) * self.parameters['A_per_V']
        return amps 
    
class CurrentSupplyBias(CurrentSupply):
    
    def __init__(self, calibration_parameters=None):
        try:
            self.derived_units.append('G')
        except:
            self.derived_units = ['G']
            
        if calibration_parameters is None:
            calibration_parameters = {}
            
        self.parameters = calibration_parameters
        

        self.parameters.setdefault('G_per_V', 1) # G/V
        
        CurrentSupply.__init__(self,self.parameters)


    def G_to_base(self, gauss):

        volts = gauss / self.parameters['G_per_V'] + self.parameters['V_0']
        return volts
        
    def G_from_base(self, volts):

        gauss = (volts - self.parameters['V_0']) * self.parameters['G_per_V']
        return gauss 

class CurrentSupplyGradient(CurrentSupply):

    def __init__(self, calibration_parameters=None):
        try:
            self.derived_units.append('G_per_cm')
        except:
            self.derived_units = ['G_per_cm']
            
        if calibration_parameters is None:
            calibration_parameters = {}
        self.parameters = calibration_parameters
        
        self.parameters.setdefault('G_per_cm_per_V', 1) # (G/cm)/V
        
        CurrentSupply.__init__(self,self.parameters) 
    
    def G_per_cm_to_base(self, gauss_per_cm):

        volts = gauss_per_cm / self.parameters['G_per_cm_per_V'] + self.parameters['V_0']
        return volts
        
    def G_per_cm_from_base(self,volts):

        gauss_per_cm = (volts - self.parameters['V_0']) * self.parameters['G_per_cm_per_V']
        return gauss_per_cm