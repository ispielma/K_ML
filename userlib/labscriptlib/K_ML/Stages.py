# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 11:04:54 2022

@author: rubidium
"""

from labscriptlib.common.utilities import stage

def SetDefaults(t, mode='Startup', **kwargs):
    """
    Here we  set the default starting and ending state for the experiment.

    Note that we use a keep warm protocol for the high power AOMs
    """

    # NI_PCI_01
    ScopeTrigger.go_low(t)

    # The TTL like for the satspec lock (repumper): needs to be always high
    D2_Lock_DO.go_high(t)

    UV_DO.go_low(t)
    
    # This is a workaround to be sure that this set out outputs is triggered
    # at all
    if mode=='Startup':
        ni_pci_01_ao0.constant(t, 1.0)
    else:
        ni_pci_01_ao0.constant(t, 0)

    # NI_PCI_02
    D2_Repump_AO.constant(t, D2_Repump_Volts)
    D2_Repump_FM.constant(t, D2_Repump_Freq, units='MHz')
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
    MOT_y_Bias.constant(t, 0, units='A')
    MOT_x_z_Bias.constant(t, 0, units='A')
    MOT_x_mz_Bias.constant(t, 0, units='A')
    MOT_Quad.constant(t, 0, units='A')

    MOT_y_Bias_Disable.go_high(t)
    MOT_x_z_Bias_Disable.go_high(t)
    MOT_x_mz_Bias_Disable.go_high(t)
    MOT_Quad_Disable.go_high(t)

    # NI_USB_02
    if mode == 'startup':
        ni_usb_02_do0.go_high(t)
        ni_usb_02_ao0.constant(t, 1.0)
    else:
        ni_usb_02_do0.go_low(t)
        ni_usb_02_ao0.constant(t, 0)        

    # NT_1
    D2_Lock_DDS.setfreq(t, D2_Lock_Freq_MOT)
    D2_Lock_DDS.setamp(t, 1.0) # -80dBm
    nt1_1.frequency.constant(t, 1e3)
    nt1_1.amplitude.constant(t, 1.0)
    
    return 101e-6

@stage
def MOT(t, duration,
            y_Bias,
            x_z_Bias,
            x_mz_Bias,
            Quad,
            D2_Lock_Freq,
            D2_Repump_Freq,
            UV=False,
            DelayLight=0,
            **kwargs):
    """
    This function will run a basic MOT with a range of settings
    """
    
    # Set Fields and frequencies
    MOT_y_Bias.constant(t, y_Bias, units='A')
    MOT_x_z_Bias.constant(t, x_z_Bias, units='A')
    MOT_x_mz_Bias.constant(t, x_mz_Bias, units='A')
    MOT_Quad.constant(t, Quad, units='A')

    MOT_y_Bias_Disable.go_low(t)
    MOT_x_z_Bias_Disable.go_low(t)
    MOT_x_mz_Bias_Disable.go_low(t)
    MOT_Quad_Disable.go_low(t)

    D2_Lock_DDS.setfreq(t, D2_Lock_Freq)
    D2_Repump_FM.constant(t, D2_Repump_Freq, units='MHz')
    
    if UV:
        UV_DO.go_high(t)
        UV_DO.go_low(t + duration)
        
    if DelayLight > duration:
        raise ValueError('In MOT DelayLight > duration')
        
    t += DelayLight

    # Turn on MOT beams
    D2_Repump_Sh.go_high(t)
    D2_Cooling_Sh.go_high(t)    

    return duration

@stage
def cMOT(t, **kwargs):

    MOT_y_Bias.ramp(t, Time_cMOT, 
                    MOT_y_Bias_cMOT_Start, 
                    MOT_y_Bias_cMOT_Stop, RampRate_cMOT, units='A')
    MOT_x_z_Bias.ramp(t, Time_cMOT, 
                      MOT_x_z_Bias_cMOT_Start,  
                      MOT_x_z_Bias_cMOT_Stop, RampRate_cMOT, units='A')
    MOT_x_mz_Bias.ramp(t, Time_cMOT, 
                       MOT_x_mz_Bias_cMOT_Start, 
                       MOT_x_mz_Bias_cMOT_Stop, RampRate_cMOT, units='A')
    
    MOT_Quad.ramp(t, Time_cMOT,
                  MOT_Quad_cMOT_Start,
                  MOT_Quad_cMOT_Stop,
                  RampRate_cMOT, units='A')

    D2_Repump_FM.ramp(t, Time_cMOT, 
                      D2_Repump_Freq_cMOT_Start, 
                      D2_Repump_Freq_cMOT_Stop, 
                      RampRate_cMOT, units='MHz')

    # Cooling Detuning ramp
    D2_Lock_DDS.frequency.ramp(t, Time_cMOT,
                               D2_Lock_Freq_cMOT_Start, 
                               D2_Lock_Freq_cMOT_Stop, 
                               RampRate_cMOT)

    # Repump intensity ramp
    D2_Repump_AO.ramp(t, Time_cMOT, 
                      D2_Repump_Volts_cMOT_Start, 
                      D2_Repump_Volts_cMOT_Stop, 
                      RampRate_cMOT)


    return Time_cMOT

@stage
def Molasses(t, **kwargs):

    MOT_y_Bias.constant(t, MOT_y_Bias_Mol, units='A')
    MOT_x_z_Bias.constant(t, MOT_x_z_Bias_Mol, units='A')
    MOT_x_mz_Bias.constant(t,MOT_x_mz_Bias_Mol, units='A')
    MOT_Quad.ramp(t, Time_Mol/10, MOT_Quad_cMOT_Stop, 
                  0, RampRate_Mol, units='A')
    # MOT_Quad_Disable.go_high(t+Time_Mol/10)

    # Cooling Detuning ramp
    D2_Lock_DDS.frequency.ramp(t, Time_Mol, 
                               D2_Lock_Freq_Mol_Start, 
                               D2_Lock_Freq_Mol_Stop, 
                               RampRate_Mol)

    # Cooling intensity ramp
    D2_Cooling_AO.ramp(t, Time_Mol, 
                       D2_Cooling_Volts_Mol_Start, 
                       D2_Cooling_Volts_Mol_Stop,
                       RampRate_Mol)

    # Repump Detuning ramp
    D2_Repump_FM.ramp(t, Time_Mol, 
                      D2_Repump_Freq_Mol_Start,
                      D2_Repump_Freq_Mol_Stop, RampRate_Mol, units='MHz')

    # Repump intensity ramp
    D2_Repump_AO.ramp(t, Time_Mol,
                      D2_Repump_Volts_Mol_Start,
                      D2_Repump_Volts_Mol_Stop, 
                      RampRate_Mol)

    return Time_Mol

@stage
def OpticalPump(t, **kwargs):
    """
    Optical pumping between Molasses and magnetic trapping
    """
    D2_Repump_AO.constant(t, D2_Repump_Volts)
    D2_Cooling_AO.constant(t, 0)
    return Time_OP

@stage
def MagneticTrapCapture(t, **kwargs):
    MOT_Quad_Disable.go_low(t)
    MOT_Quad.constant(t, MOT_Quad_Capture, units='A')
    
    D2_Repump_DO.go_low(t)
    D2_Repump_AO.constant(t, 0.0)
    D2_Repump_Sh.go_low(t)
    
    D2_Cooling_DO.go_low(t)
    D2_Cooling_AO.constant(t, 0.0)
    D2_Cooling_Sh.go_low(t)

    return Capture_Hold_Time

@stage
def MOT_Cell_TOF(t, **kwargs):

    # Get fields ready for TOF
    MOT_y_Bias.constant(t, MOT_y_Bias_Imaging, units='A')
    MOT_x_z_Bias.constant(t, MOT_x_z_Bias_Imaging, units='A')
    MOT_x_mz_Bias.constant(t, MOT_x_mz_Bias_Imaging, units='A')    
    MOT_Quad_Disable.go_high(t)
    MOT_Quad.constant(t, 0, units='A')
    
    # Frequencies
    D2_Lock_DDS.setfreq(t, D2_Lock_Freq_Imaging)
    D2_Repump_FM.constant(t, D2_Repump_Freq_Imaging, units='MHz')
    
    # Turn off lasers
    D2_Repump_DO.go_low(t)
    D2_Repump_AO.constant(t, 0.0)
    D2_Cooling_DO.go_low(t)
    D2_Cooling_AO.constant(t, 0.0)
 
    return TOF_Time

@stage 
def SimpleImage(t,
                cameras,
                trigger_duration,
                download_time,
                ShutterDevices=[],
                DigitalDevices=[],
                AnalogDevices=[],
                AnalogValues=[],
                CloseShutters=True,
                mode='fluorescence',
                frametype='bright',
                **kwargs):
    """
    General use function for simple imaging
    
    In many cases set CloseShutters=False until the last image.
    """
    
    for Device in ShutterDevices:
        Device.go_high(t-5e-3)
    
    for Device in DigitalDevices:
        Device.go_high(t)
        
    for (Device, Value) in zip(AnalogDevices, AnalogValues):
        Device.constant(t, Value)
    
    for camera in cameras:
        camera.expose(t, mode, 
                      frametype=frametype, 
                      trigger_duration=trigger_duration)
        
    t += trigger_duration
    
    if CloseShutters:
        for Device in ShutterDevices:
            Device.go_high(t-5e-3)
    
    for Device in DigitalDevices:
        Device.go_low(t)
        
    for Device in AnalogDevices:
        Device.constant(t, 0)
    
    t += download_time
    
    return trigger_duration + download_time




