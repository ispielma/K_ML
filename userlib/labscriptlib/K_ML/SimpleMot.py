# -*- coding: utf-8 -*-
"""
This file loads a MOT in the KML lab and takes a picture of it.
"""

import numpy as np

import labscript as ls
from labscript import ns, us, ms, s, Hz, kHz, MHz, GHz
from  labscript_utils import import_or_reload
from labscript_devices.PulseBlasterUSB import PulseBlasterUSB
from labscript_devices.NI_DAQmx.labscript_devices import NI_PCI_6733, NI_USB_6229, NI_USB_6343
from labscript_devices.NovaTechDDS9M import NovaTechDDS9M
from labscript_devices.IMAQdxCamera.labscript_devices import IMAQdxCamera
import_or_reload('labscriptlib.K_ML.connection_table')

def SetDefaults(t):
    """
    Here we  set the default starting and ending state for the experiment.

    Note that we use a keep warm protocol for the high power AOMs

    """
    ScopeTrigger.go_low(t)

    # The TTL like for the satspec lock (repumper): needs to be always high
    D2_Lock_DO.go_high(t)

    # NI_PCI_01
    UV_DO.go_low(t)

    ni_pci_01_ao0.constant(t, 1.0)
    ni_pci_01_ao0.constant(t+1e-3, 0.0)

    # NI_PCI_02
    D2_Repump_AO.constant(t, D2_Repump_Volts)
    D2_Repump_FM.constant(t, D2_Repump_Default_Shift, units='MHz')
    D2_Cooling_AO.constant(t, D2_Cooling_Volts)
    D2_Probe_OP_AO.constant(t, 0.0)

    D2_Repump_DO.go_high(t)
    D2_Repump_Sh.go_low(t)
    D2_Cooling_DO.go_high(t)
    D2_Cooling_Sh.go_low(t)
    D2_Probe_OP_DO.go_low(t)
    D2_Probe_1_Sh.go_low(t)
    D2_Probe_2_Sh.go_low(t)
    D2_OP_Sh.go_low(t)

    # NI_USB_01
    MOT_y_Bias.constant(t, MOT_y_Bias_0)
    MOT_x_z_Bias.constant(t, MOT_x_z_Bias_0)
    MOT_x_mz_Bias.constant(t, MOT_x_mz_Bias_0)
    MOT_Quad.constant(t, 0.0)

    MOT_y_Bias_Disable.go_high(t)
    MOT_x_z_Bias_Disable.go_high(t)
    MOT_x_mz_Bias_Disable.go_high(t)
    MOT_Quad_Disable.go_high(t)

    # NI_USB_02
    ni_usb_02_do0.go_high(t)
    ni_usb_02_do0.go_low(t+0.001)
    ni_usb_02_ao0.constant(t, 1.0)
    ni_usb_02_ao0.constant(t+0.001, 0.0)

    # NT_1
    D2_Lock_DDS.setfreq(t, D2_Lock_Freq_MOT)
    D2_Lock_DDS.setamp(t, 1.0) # -80dBm

def PrepMOT(t,
            MOT_y_Bias_Prep,
            MOT_x_z_Bias_Prep,
            MOT_x_mz_Bias_Prep,
            MOT_Quad_Prep,
            D2_Lock_Freq_Prep,
            D2_Repump_Default_Shift_Prep):

    MOT_y_Bias.constant(t, MOT_y_Bias_Prep + MOT_y_Bias_0)
    MOT_x_z_Bias.constant(t, MOT_x_z_Bias_Prep + MOT_x_z_Bias_0)
    MOT_x_mz_Bias.constant(t, MOT_x_mz_Bias_Prep + MOT_x_mz_Bias_0)
    MOT_Quad.constant(t, MOT_Quad_Prep)

    MOT_y_Bias_Disable.go_low(t)
    MOT_x_z_Bias_Disable.go_low(t)
    MOT_x_mz_Bias_Disable.go_low(t)
    MOT_Quad_Disable.go_low(t)

    D2_Lock_DDS.setfreq(t, D2_Lock_Freq_Prep)
    D2_Repump_FM.constant(t, D2_Repump_Default_Shift_Prep, units='MHz')

    return Time_MOT

def cMOT(t):

    MOT_y_Bias.ramp(t, Time_cMOT, MOT_y_Bias_cMOT_Start + MOT_y_Bias_0, 
                    MOT_y_Bias_cMOT_Stop + MOT_y_Bias_0, RampRate_cMOT)
    MOT_x_z_Bias.ramp(t, Time_cMOT, MOT_x_z_Bias_cMOT_Start + MOT_x_z_Bias_0,  
                      MOT_x_z_Bias_cMOT_Stop + MOT_x_z_Bias_0, RampRate_cMOT)
    MOT_x_mz_Bias.ramp(t, Time_cMOT, MOT_x_mz_Bias_cMOT_Start + MOT_x_mz_Bias_0, 
                       MOT_x_mz_Bias_cMOT_Stop + MOT_x_mz_Bias_0, RampRate_cMOT)
    
    MOT_Quad.constant(t, MOT_Quad_cMOT)

    D2_Repump_FM.constant(t, D2_Repump_Default_Shift_cMOT, units='MHz')

    # Cooling Detuning ramp
    D2_Lock_DDS.frequency.ramp(t, Time_cMOT, D2_Lock_Freq_cMOT_Start, D2_Lock_Freq_cMOT_Stop, RampRate_cMOT)

    # Repump intensity ramp
    D2_Repump_AO.ramp(t, Time_cMOT, D2_Repump_Volts_cMOT_Start, D2_Repump_Volts_cMOT_Start, RampRate_cMOT)


    return Time_cMOT

def Molasses(t):

    MOT_y_Bias.constant(t, MOT_y_Bias_Mol + MOT_y_Bias_0)
    MOT_x_z_Bias.constant(t, MOT_x_z_Bias_Mol + MOT_x_z_Bias_0)
    MOT_x_mz_Bias.constant(t,MOT_x_mz_Bias_Mol + MOT_x_mz_Bias_0)
    MOT_Quad.constant(t, 0)

    # Cooling Detuning ramp
    D2_Lock_DDS.frequency.ramp(t, Time_Mol, D2_Lock_Freq_Mol_Start, D2_Lock_Freq_Mol_Stop, RampRate_Mol)

    # Cooling intensity ramp
    D2_Cooling_AO.ramp(t, Time_Mol, D2_Cooling_Volts_Mol_Start, D2_Cooling_Volts_Mol_Stop, RampRate_Mol)

    # Repump Detuning ramp
    D2_Repump_FM.ramp(t, Time_Mol, D2_Repump_Default_Shift_Mol_Start, D2_Repump_Default_Shift_Mol_Stop, RampRate_Mol, units='MHz')

    # Repump intensity ramp
    D2_Repump_AO.ramp(t, Time_Mol, D2_Repump_Volts_Mol_Start, D2_Repump_Volts_Mol_Start, RampRate_Mol)



    return Time_Mol

t = 0
ls.start()

#
# Set Dafault state
#

SetDefaults(t)
t += 10*ms

#
# Get all MOT stuff on except fields (should be a function!)
#

PrepMOT(t,
        MOT_y_Bias_Prep=MOT_y_Bias_MOT,
        MOT_x_z_Bias_Prep=MOT_x_z_Bias_MOT,
        MOT_x_mz_Bias_Prep=MOT_x_mz_Bias_MOT,
        MOT_Quad_Prep=0,
        D2_Lock_Freq_Prep=D2_Lock_Freq_MOT,
        D2_Repump_Default_Shift_Prep=D2_Repump_Default_Shift)

# Turn on MOT beam.
D2_Repump_DO.go_low(t)
D2_Cooling_DO.go_low(t)
D2_Repump_Sh.go_high(t)
D2_Cooling_Sh.go_high(t)

t += 10e-3

D2_Repump_DO.go_high(t)
D2_Cooling_DO.go_high(t)

t += 10e-3

#
# Snap a dark frame
#
ls.add_time_marker(t, "Snap dark frame", verbose=True)
ScopeTrigger.go_high(t)
ScopeTrigger.go_low(t+1*ms)
MOT_x.expose(t, 'fluorescence', frametype='dark', trigger_duration=MOT_Fl_Exposure)
t += 10*ms

t += PrepMOT(t,
        MOT_y_Bias_Prep=MOT_y_Bias_MOT,
        MOT_x_z_Bias_Prep=MOT_x_z_Bias_MOT,
        MOT_x_mz_Bias_Prep=MOT_x_mz_Bias_MOT,
        MOT_Quad_Prep=MOT_Quad_MOT,
        D2_Lock_Freq_Prep=D2_Lock_Freq_MOT,
        D2_Repump_Default_Shift_Prep=D2_Repump_Default_Shift)

#
# Apply UV
#
# ls.add_time_marker(t, "UV on", verbose=True)
# UV_DO.go_high(t)
# UV_DO.go_low(t)

#
# cMOT
#

t += cMOT(t)

#
# Optical Molassas (sub Doppler cooling!)
#

# t += Molasses(t)


# Fl imaging
D2_Repump_DO.go_low(t)
D2_Cooling_DO.go_low(t)

PrepMOT(t,
        MOT_y_Bias_Prep=MOT_y_Bias_0,
        MOT_x_z_Bias_Prep=MOT_x_z_Bias_0,
        MOT_x_mz_Bias_Prep=MOT_x_mz_Bias_0,
        MOT_Quad_Prep=0,
        D2_Lock_Freq_Prep=D2_Lock_Freq_MOT,
        D2_Repump_Default_Shift_Prep=D2_Repump_Default_Shift)

# # TOF!
t += TOF_Time

# Image!
D2_Repump_DO.go_high(t)
D2_Cooling_DO.go_high(t)
D2_Repump_AO.constant(t, D2_Repump_Volts)
D2_Cooling_AO.constant(t, D2_Cooling_Volts)

MOT_x.expose(t, 'fluorescence', frametype='bright', trigger_duration=MOT_Fl_Exposure)
t+= 1*ms

#
# Set Dafault state
#
SetDefaults(t)

# Stop the experiment shot with stop()
t += 10*ms
ls.stop(t)
