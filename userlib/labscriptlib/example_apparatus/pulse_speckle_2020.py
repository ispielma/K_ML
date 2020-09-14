from __future__ import division, print_function

from labscript_utils import import_or_reload
from labscript import *
from labscript import *
from labscriptlib.common.functions import *

import_or_reload('labscriptlib.rb_chip_mainline.connectiontable')     


def stage(func):
    """A decorator for functions that represent stages of the experiment.
    
    Assumes first argument to function is the stage's start time, and return value is
    its duration (which is a convention we normally follow throughout labscript).
    
    The resulting decorated function simply prints the name of the stage and its start and end
    times when the function is called."""
    import functools
    @functools.wraps(func)
    def f(t, *args, **kwargs):
        duration = func(t, *args, **kwargs)
        try:
            float(duration)
        except Exception:
            raise TypeError("Stage function %s must return its duration, even if zero"%func.__name__)
        print('%s: %s sec to %s sec'%(func.__name__, str(t), str(t + duration)))
        add_time_marker(t, label=func.__name__)
        return duration
    return f
    
    
@stage
def prep(t):
    """
    Define initial state of system.  All settable Hardware should be set here. 
    no exceptions.
    """

    # UV Soak -- heep the UV on the whole time
    if UVSoak:
        UV_LED.go_high(t)
    else:
        UV_LED.go_low(t)
    
    # pulseblaster_0 outputs:
    AOM_MOT_repump.go_high(t) # high
    shutter_MOT_repump.go_high(t)
    camera_trigger_0.go_high(t)    
    AOM_MOT_cooling.go_high(t)
    shutter_MOT_cooling.go_high(t)
    AOM_probe_2.go_high(t)
    camera_trigger_1.go_high(t)
    camera_trigger_2.go_high(t)
    camera_trigger_3.go_high(t)
       
    # ni_usb_6343_1 digital outputs:
    # Both on: bottom bias
    # 0 off & 1 on: top bias
    # other combinations: Both bias off
    kepco_enable_0.go_high(t) # Select bottom (high is bottom, low is top)
    kepco_enable_1.go_high(t) # 
    
    # ni_pci_6733_0 analog outputs:
    MOT_repump.constant(t,  UVMOTRepump)
    MOT_cooling.constant(t, UVMOTAmplitude)
    probe_2.constant(t,     ProbeInt)
   
    #long_trap.constant(t, -0.5)
    
    # Setup agilent supplies
    curent_supply_1_enable.go_low(t)
    curent_supply_2_enable.go_high(t)
    curent_supply_3_enable.go_low(t)
    curent_supply_4_enable.go_low(t)
    
    # Select mot currents
    curent_supply_2_select_line0.go_low(t)
    curent_supply_2_select_line1.go_low(t)    
    
    # ni_usb_6343_0 analog outputs:
    transport_current_1.constant(t, 0, units='A')
    transport_current_2.constant(t, UVMOTCurrent, units='A')
    transport_current_3.constant(t, 0, units='A')
    transport_current_4.constant(t, 0, units='A')
    
    
    # ni_usb_6343_1 analog outputs:
    x_bias.constant(t, 2.11*UVxShim, units='A')
    y_bias.constant(t,      UVyShim, units='A')
    z_bias.constant(t, -0.8*UVzShim, units='A')
    offset.constant(t, 0.0)
    
    # ni_usb_6343_2 outputs:
    # mixer_raman_1.constant(t, 0.0)#mixer_raman_1.constant(t, 0.31)
    # mixer_raman_2.constant(t, 0.0)
    shutter_greenbeam.go_low(t)
    green_beam.go_low(t)
    AOM_green_beam.constant(t, green_beam_off_V)
    green_servo_trigger.go_low(t)
    long_trap_switch.go_low(t)

    # shutter_greenbeam.go_high(t)#07/15/19 added for Yuchen to be able to carry out alignment while I am running.
    # green_beam.go_high(t)
    # AOM_green_beam.constant(t, 0.5)
    
    # novatechdds9m_0 channel outputs:
    MOT_lock.setfreq(t,  (ResFreq + UVMOTFreq)*MHz)
    MOT_lock.setamp(t,  0.7077) # 0 dBm
    
    RF_evap.setfreq(t,  StartRF, units='MHz')
    RF_evap.setamp(t, 0.000) 
    
    #FPGA_ao.constant(t, 0.2)
    
    RF_mixer1.constant(t, 0)
    RF_switch_0.go_low(t)
    #RF_mixer2.constant(t, 0)
    #RF_mixer3.constant(t, 0)
    
    #AOM_Raman_1.setfreq(t, raman_freq, units='MHz')
    #AOM_Raman_1.setamp(t, 0.0)
    
    
    #ni_pci_6733_1 analog outputs:
    microwave_attenuator.constant(t, 6.0)
    # novatechdds9m_1 channel outputs:
    uwave1.setfreq(t, 100*MHz)
    uwave1.setamp(t, 0.0) # -80dBm
    uWave_switch_0.go_low(t)
    
    fluxgate_trig.go_low(t)
    
    dipole_switch.go_low(t)
    dipole_intensity.constant(t, InitialDipoleInt)
    
    return 30*ms

@stage
def small_MOT(t):
    MOT_repump.constant(t, 0.5)
    MOT_cooling.constant(t, 0.5)
    kepco_enable_0.go_low(t) #Moving bias control to bottom?
    
    # TODO: why do we load a small MOT for 1 sec?
    return 1.0


@stage
def MOT_image_1(t):
    # pulseblaster_0 outputs: 
    YZ_2_Flea3.expose(t-30e-6, 'shot1', 'atoms1')
    return TimeImage
 
    
@stage  
def download_MOT_image_1(t):
    # pulseblaster_0 outputs:
    AOM_MOT_repump.go_low(t)
    AOM_MOT_cooling.go_low(t)
    
    
    return TimeDownloadImage    
    
@stage
def MOT_image_2(t):
    # pulseblaster_0 outputs: 
    YZ_2_Flea3.expose(t-30e-6, 'shot2', 'dark')
    return TimeImage
 
    
@stage  
def download_MOT_image_2(t):
    AOM_MOT_repump.go_high(t)
    AOM_MOT_cooling.go_high(t)
    
    kepco_enable_0.go_high(t) # TODO: why am I here?
    
    return TimeDownloadImage        

@stage
def MOT_image_3(t):
    # pulseblaster_0 outputs: 
    YZ_2_Flea3.expose(t-30e-6, 'shot3', 'atoms2')
    return TimeImage
 
@stage  
def download_MOT_image_3(t):
    MOT_repump.constant(t, UVMOTRepump)
    MOT_cooling.constant(t, UVMOTAmplitude)
    
    return TimeDownloadImage       
    
      
    
@stage    
def UVMOT(t):
    # ni_pci_6733_0 digital outputs:
    if not UVSoak:
        UV_LED.go_high(t)
        
    return UV_MOT_time    

@stage    
def cMOT(t):
    # ni_pci_6733_0 digital outputs:
    
    # UV Soak -- keep the UV on the whole time
    if not UVSoak:
        UV_LED.go_low(t)
   
    # ni_pci_6733_0 analog outputs:
    MOT_repump.customramp(t,  CMOT_time, HalfGaussRamp, RepumpMOT, RepumpCMOT, CMOTCaptureWidth, samplerate=1/step_cMOT)
    MOT_cooling.constant(t,   MOTAmplitude)
        
    # ni_usb_6343_0 analog outputs:
    transport_current_2.customramp(t, CMOT_time, HalfGaussRamp, MOTCurrent, CMOTCurrent, CMOTCaptureWidth, samplerate=1/step_cMOT, units='A')
    
    # ni_usb_6343_1 analog outputs:
    x_bias.constant(t, 2.11*MOTxShim, units='A')
    y_bias.constant(t,      MOTyShim, units='A')
    z_bias.constant(t, -0.8*MOTzShim, units='A')

    # novatechdds9m_0 channel outputs:
    MOT_lock.frequency.customramp(t,  CMOT_time, HalfGaussRamp, MOTFreq + ResFreq, CMOTFreq + ResFreq, CMOTCaptureWidth, samplerate=1/step_cMOT, units='MHz')
     
    return CMOT_time
    

@stage
def molasses(t):
# Turn off quadrupole field to nearly zero to allow polarization gradient cooling. 
    # pulseblaster_0 outputs:
    shutter_optical_pumping.go_high(t)
    
    # ni_usb_6343_0 digital outputs:
    curent_supply_2_enable.go_low(t)
    
    # ni_pci_6733_0 analog outputs:
    MOT_repump.constant(t, RepumpMol)
    
    # ni_usb_6343_0 analog outputs:
    transport_current_2.constant(t, MOTCurrent, units='A')
    
    # ni_usb_6343_1 analog outputs:
    x_bias.constant(t, 2.11*MolXBias, units='A')
    y_bias.constant(t, MolYBias, units='A')
    z_bias.constant(t, -0.8*MolZBias, units='A')
    
    # novatechdds9m_0 channel outputs:
    #fluxgate_trig.go_high(t)#-1*ms
    #fluxgate_trig.go_low(t+1.*ms)#-1*ms-1*ms+1e-3
    #MOT_lock.setamp(t,  0.8) 
    
    MOT_lock.frequency.customramp(t, TimeMol, ExpRamp, StartFreqMol + ResFreq , EndFreqMol + ResFreq , TimeMol/fractionTau , samplerate=1/step_molasses, units='MHz')
    return TimeMol
    

    
@stage
def optical_pump_1(t):
    # pulseblaster_0 outputs:
    AOM_MOT_repump.go_low(t)
    AOM_MOT_cooling.go_low(t)
    shutter_MOT_cooling.go_low(t)

    # ni_pci_6733_0 analog outputs:
    MOT_repump.constant(t, RepumpOpPump)
    MOT_cooling.constant(t, 0)
    optical_pumping.constant(t, OpPumpAmplitude)
    
    # ni_usb_6343_1 analog outputs:
    x_bias.constant(t, 2.11*OpxShim, units='A')
    y_bias.constant(t, OpyShim, units='A')
    z_bias.constant(t, -0.8*OpzShim, units='A')
    
    # novatechdds9m_0 channel outputs:
    # Redundant: already set in previous stage (is final value of ramp). Leaving in anyway:
    
    #MOT_lock.frequency.constant(t, ResFreq + EndFreqMol, units='MHz')
    MOT_lock.frequency.constant(t, ResFreq + EndFreqOpPump, units='MHz')
    
    return TimePrePump

    
@stage
def optical_pump_2(t):

# Pump atoms to the low field seeking F=2, mf=2 state. 
    # pulseblaster_0 outputs:
    AOM_MOT_repump.go_high(t)
    AOM_optical_pumping.go_high(t)
    
    return TimePump
    

@stage
def magnetic_trap(t):
    # pulseblaster_0 outputs:
    AOM_MOT_repump.go_low(t)
    shutter_MOT_repump.go_low(t)
    AOM_optical_pumping.go_low(t) # this is normally a cold one - so optimize injection while cold
    shutter_optical_pumping.go_low(t)
    AOM_probe_2.go_low(t)
    
    # ni_usb_6343_0 digital outputs:
    curent_supply_2_enable.go_high(t)
    curent_supply_3_enable.go_high(t)
    
    # ni_pci_6733_0 analog outputs:
    MOT_repump.constant(t, 0)
    optical_pumping.constant(t, 0)
    
    # ni_usb_6343_0 analog outputs:
    transport_current_2.customramp(t, TrapTime,  HalfGaussRamp, MOTCaptureCurrent, IM, TrapTime/MTrap_capture_fraction, samplerate=1/step_magnetic_trap, units='A')
    
    # ni_usb_6343_1 analog outputs:
    x_bias.customramp(t, TrapTime, HalfGaussRamp,  2.11*CapxShim, 2.11*MolXBias, TrapTime/MTrap_capture_fraction, samplerate=1/step_magnetic_trap, units='A')
    y_bias.customramp(t, TrapTime, HalfGaussRamp,  CapyShim, MolYBias,           TrapTime/MTrap_capture_fraction, samplerate=1/step_magnetic_trap, units='A')
    z_bias.customramp(t, TrapTime, HalfGaussRamp, -0.8*CapzShim, -0.8*MolZBias, TrapTime/MTrap_capture_fraction, samplerate=1/step_magnetic_trap, units='A')
    
    
    
    return TrapTime
 

    
@stage
def move_1(t):
    """
    
    """
    # pulseblaster_0 outputs:
    AOM_MOT_repump.go_high(t) #
    AOM_probe_1.go_high(t) #
    
    
    # ni_pci_6733_0 analog outputs:
    MOT_repump.constant(t, 0.8) #

    # ni_usb_6343_0 digital outputs:
    curent_supply_4_enable.go_high(t)

    
    # ni_usb_6343_0 analog outputs:
    transport_current_1.customramp(t, TimeMove01, Poly4Asymmetric, IPM, WidthPM, SkewPM, 1, Cf=[Cf5, AccelFrac, 0, Vel0], samplerate=1/step_magnetic_transport, units='A')
    transport_current_2.customramp(t, TimeMove01, PolyHalf2, 0, IM, WidthM, SkewM,          Cf=[Cf5, AccelFrac, 0, Vel0], samplerate=1/step_magnetic_transport, units='A')
    transport_current_3.customramp(t, TimeMove01, Poly4,     0, IMB, WidthMB, SkewMB,       Cf=[Cf5, AccelFrac, 0, Vel0], samplerate=1/step_magnetic_transport, units='A')                               
    
    # ni_usb_6343_1 analog outputs:
    #x_bias.constant(t,  2.11*MolXBias, units='A')
    #y_bias.constant(t,  MolYBias, units='A')
    #z_bias.constant(t, -0.8*MolZBias, units='A')                               
    
    
    return TimeMove01


@stage
def move_2(t):
    # ni_usb_6343_0 digital outputs:
    curent_supply_1_select_line0.go_high(t)
    curent_supply_1_enable.go_high(t)
    
    # ni_usb_6343_0 analog outputs:
    transport_current_1.constant(t, 0, units='A')
    transport_current_2.customramp(t, TimeMove02, PolyHalf2, 1, IM, WidthM, SkewM,       Cf=[Cf2, d1, Vel0, Vel1], samplerate=1/step_magnetic_transport, units='A')
    transport_current_3.customramp(t, TimeMove02, Poly4,     1, IMB, WidthMB, SkewMB,    Cf=[Cf2, d1, Vel0, Vel1], samplerate=1/step_magnetic_transport, units='A')
    transport_current_4.customramp(t, TimeMove02, PolyExp,   0, IL, WidthL, SkewL, ExpL, Cf=[Cf2, d1, Vel0, Vel1], samplerate=1/step_magnetic_transport, units='A')
    
    return TimeMove02
    
    
@stage
def move_3(t):
    # ni_usb_6343_0 digital outputs:
    curent_supply_2_select_line0.go_high(t)
    
    # ni_usb_6343_0 analog outputs:
    transport_current_1.customramp(t, TimeMove03, PolyExp, 0, IB, WidthB, SkewB, ExpB, Cf=[Cf2, d1, Vel1, Vel2], samplerate=1/step_magnetic_transport, units='A')
    transport_current_2.constant(t, 0, units='A')
    transport_current_3.customramp(t, TimeMove03, Poly4,   2, IMB, WidthMB, SkewMB,    Cf=[Cf2, d1, Vel1, Vel2], samplerate=1/step_magnetic_transport, units='A')
    transport_current_4.customramp(t, TimeMove03, PolyExp, 1, IL, WidthL, SkewL, ExpL, Cf=[Cf2, d1, Vel1, Vel2], samplerate=1/step_magnetic_transport, units='A')

    return TimeMove03
    

@stage
def move_4(t):
    # ni_usb_6343_0 digital outputs:
    curent_supply_3_select_line0.go_high(t)
    
    # ni_usb_6343_0 analog outputs:
    transport_current_1.customramp(t, TimeMove04, PolyExp, 1, IB, WidthB, SkewB, ExpB, Cf=[Cf2, d1, Vel2, Vel3], samplerate=1/step_magnetic_transport, units='A')
    transport_current_2.customramp(t, TimeMove04, PolyExp, 0, IL, WidthL, SkewL, ExpL, Cf=[Cf2, d1, Vel2, Vel3], samplerate=1/step_magnetic_transport, units='A')                      
    transport_current_3.constant(t, 0, units='A')
    transport_current_4.customramp(t, TimeMove04, PolyExp, 2, IL, WidthL, SkewL, ExpL, Cf=[Cf2, d1, Vel2, Vel3], samplerate=1/step_magnetic_transport, units='A')

    return TimeMove04 
    

@stage
def move_5(t):
    # ni_usb_6343_0 digital outputs:
    curent_supply_4_select_line0.go_high(t)
    
    # ni_usb_6343_0 analog outputs:
    transport_current_1.customramp(t, TimeMove05, PolyExp, 2, IB, WidthB, SkewB, ExpB, Cf=[Cf2, d1, Vel3, Vel4], samplerate=1/step_magnetic_transport, units='A')
    transport_current_2.customramp(t, TimeMove05, PolyExp, 1, IL, WidthL, SkewL, ExpL, Cf=[Cf2, d1, Vel3, Vel4], samplerate=1/step_magnetic_transport, units='A')
    transport_current_3.customramp(t, TimeMove05, PolyExp, 0, IB, WidthB, SkewB, ExpB, Cf=[Cf2, d1, Vel3, Vel4], samplerate=1/step_magnetic_transport, units='A')
    transport_current_4.constant(t, 0, units='A')
    
    return TimeMove05

    
@stage
def move_6(t):
    # ni_usb_6343_0 digital outputs:
    curent_supply_1_select_line0.go_low(t)
    curent_supply_1_select_line1.go_high(t)
    
    # ni_usb_6343_0 analog outputs:
    transport_current_1.constant(t, 0, units='A')
    transport_current_2.customramp(t, TimeMove06, PolyExp, 2, IL, WidthL, SkewL, ExpL, Cf=[Cf2, d1, Vel4, Vel5], samplerate=1/step_magnetic_transport, units='A')
    transport_current_3.customramp(t, TimeMove06, PolyExp, 1, IB, WidthB, SkewB, ExpB, Cf=[Cf2, d1, Vel4, Vel5], samplerate=1/step_magnetic_transport, units='A')
    transport_current_4.customramp(t, TimeMove06, PolyExp, 0, IL, WidthL, SkewL, ExpL, Cf=[Cf2, d1, Vel4, Vel5], samplerate=1/step_magnetic_transport, units='A')
    
    return TimeMove06
    
@stage
def move_7(t):
    # ni_usb_6343_0 digital outputs:
    curent_supply_2_select_line0.go_low(t)
    curent_supply_2_select_line1.go_high(t)
    
    # ni_usb_6343_0 analog outputs:
    transport_current_1.customramp(t, TimeMove07, PolyExp, 0, IB, WidthB, SkewB, ExpB, Cf=[Cf2, d1, Vel5, Vel6], samplerate=1/step_magnetic_transport, units='A')
    transport_current_2.constant(t, 0, units='A')
    transport_current_3.customramp(t, TimeMove07, PolyExp, 2, IB, WidthB, SkewB, ExpB, Cf=[Cf2, d1, Vel5, Vel6], samplerate=1/step_magnetic_transport, units='A')
    transport_current_4.customramp(t, TimeMove07, PolyExp, 1, IL, WidthL, SkewL, ExpL, Cf=[Cf2, d1, Vel5, Vel6], samplerate=1/step_magnetic_transport, units='A')

    
    return TimeMove07
 

@stage
def move_8(t):
    # ni_usb_6343_0 digital outputs:
    curent_supply_3_select_line0.go_low(t)
    curent_supply_3_select_line1.go_high(t)
    
    # ni_usb_6343_0 analog outputs:
    transport_current_1.customramp(t, TimeMove08, PolyExp, 1, IB, WidthB, SkewB, ExpB, Cf=[Cf2, d1, Vel6, Vel7], samplerate=1/step_magnetic_transport, units='A')
    transport_current_2.customramp(t, TimeMove08, PolyExp, 0, IL, WidthL, SkewL, ExpL, Cf=[Cf2, d1, Vel6, Vel7], samplerate=1/step_magnetic_transport, units='A')
    transport_current_3.constant(t, 0, units='A')
    transport_current_4.customramp(t, TimeMove08, PolyExp, 2, IL, WidthL, SkewL, ExpL, Cf=[Cf2, d1, Vel6, Vel7], samplerate=1/step_magnetic_transport, units='A')

    return TimeMove08
     

@stage
def move_9(t):     
    # ni_usb_6343_0 digital outputs:
    curent_supply_4_select_line0.go_low(t)
    curent_supply_4_enable.go_low(t)
    
    # ni_usb_6343_1 digital outputs:
    kepco_enable_0.go_low(t)
    
    # ni_usb_6343_0 analog outputs:
    transport_current_1.customramp(t, TimeMove09, PolyExp, 2, IB, WidthB, SkewB, ExpB, Cf=[Cf2, d1, Vel7, Vel8], samplerate=1/step_magnetic_transport, units='A')
    transport_current_2.customramp(t, TimeMove09, PolyExp, 1, IL, WidthL, SkewL, ExpL, Cf=[Cf2, d1, Vel7, Vel8], samplerate=1/step_magnetic_transport, units='A')
    transport_current_3.customramp(t, TimeMove09, Poly4,   0, IBT, WidthBT, SkewBT,    Cf=[Cf2, d1, Vel7, Vel8], samplerate=1/step_magnetic_transport, units='A')
    transport_current_4.constant(t, -1, units='A')
    
    # ni_usb_6343_1 analog outputs:
    #x_bias.customramp(t, TimeMove09, LineRamp,  2.11*0.44, TpxShim,     samplerate=1/step_magnetic_transport, units='A')
    y_bias.customramp(t, TimeMove09, LineRamp,  MolYBias, TpyShimInitial,   samplerate=1/step_magnetic_transport, units='A')
    z_bias.customramp(t, TimeMove09, LineRamp, -0.8*MolZBias, a0*TpzShim,  samplerate=1/step_magnetic_transport, units='A')
    
    return TimeMove09
    
    
@stage
def move_10(t):
    # ni_usb_6343_0 digital outputs:
    curent_supply_1_select_line1.go_low(t)
    curent_supply_1_enable.go_low(t)
    curent_supply_4_select_line0.go_high(t)
    curent_supply_4_select_line1.go_high(t)
    curent_supply_4_enable.go_high(t)
    
    # ni_usb_6343_0 analog outputs:
    transport_current_1.constant(t, -1, units='A')
    transport_current_2.customramp(t, TimeMove10, PolyExp,   2, IL, WidthL, SkewL, ExpL, Cf=[Cf2, d1, Vel8, Vel9], samplerate=1/step_magnetic_transport, units='A')
    transport_current_3.customramp(t, TimeMove10, Poly4,     1, IBT, WidthBT, SkewBT,    Cf=[Cf2, d1, Vel8, Vel9], samplerate=1/step_magnetic_transport, units='A')
    transport_current_4.customramp(t, TimeMove10, PolyHalf1, 0, IFT, WidthFT, SkewFT,    Cf=[Cf2, d1, Vel8, Vel9], samplerate=1/step_magnetic_transport, units='A')
    
    # ni_usb_6343_1 analog outputs:
    # These lines redundant: already set in previous stage (are final values of ramps). Leaving in anyway:
    x_bias.constant(t, TpxShim, units='A')
    y_bias.constant(t, TpyShimInitial, units='A')
    z_bias.constant(t, a0*TpzShim, units='A')
   
    return TimeMove10
    
    
@stage
def move_11(t):
    # ni_usb_6343_0 digital outputs:
    curent_supply_2_select_line1.go_low(t)
    curent_supply_2_enable.go_low(t)
    
    # ni_usb_6343_0 analog outputs:
    transport_current_1.constant(t,  0, units='A')
    transport_current_2.constant(t, -1, units='A')
    
    transport_current_3.customramp(t, TimeMove11, Poly4,     2, IBT, WidthBT, SkewBT,Cf=[Cf2, d2, Vel9, 0,f_max], samplerate=1/step_magnetic_transport, units='A')
    transport_current_4.customramp(t, TimeMove11, PolyHalf1, 1, IFT, WidthFT, SkewFT, Cf=[Cf2, d2, Vel9, 0,f_max], samplerate=1/step_magnetic_transport, units='A')
    
    # novatechdds9m_1 channel outputs:
    RF_evap.setfreq(t,  StartRF, units='MHz')
    RF_evap.setamp(t, RFevapAmp) #1.000

    y_bias.customramp(t, TimeMove11, LineRamp, TpyShimInitial, TpyShimTrap, samplerate=1/step_magnetic_transport, units='A')
    # novatechdds9m_0 channel outputs:
    # if PartialTransferImaging:
    #     MOT_lock.frequency.constant(t, ResFreq+ImageFreqHighField, units='MHz') 
    # else:    
    #     MOT_lock.frequency.constant(t, ResFreq+ImageFreq, units='MHz')
    return TimeMove11    
    

@stage
def evaporate(t, EvapTime=1.0):
    if dipole_evap:
        dipole_switch.go_high(t)  
        dipole_intensity.constant(t, InitialDipoleInt)
        dipole_split.constant(t, InitialDipoleSplit)
    
    # ni_pci_6733_1 digital outputs:
    if UVSoakAtTop:
        UV_LED.go_high(t)
        
    # ni_usb_6343_0 analog outputs:
    transport_current_2.constant(t, 0, units='A')
    # ni_usb_6343_0 analog outputs:
    start_current3 = Poly4Asymmetric((f_max + 2)/3,None,IBT, WidthBT, SkewBT,1,Cf=None, time_argument_is_f=True)
    start_current4 = Poly4Asymmetric((f_max + 1)/4,None,IFT, WidthFT, SkewFT,1,Cf=None, time_argument_is_f=True)
    end_current3 = Poly4Asymmetric((f_super + 2)/3,None,IBT, WidthBT, SkewBT,1,Cf=None, time_argument_is_f=True)
    end_current4 = Poly4Asymmetric((f_super + 1)/4,None,IFT, WidthFT, SkewFT,1,Cf=None, time_argument_is_f=True)
    transport_current_3.customramp(t, EvapTime, LineRamp, start_current3, end_current3, samplerate=1/step_RF_evap, units='A')
    transport_current_4.customramp(t, EvapTime, LineRamp, start_current4, end_current4, samplerate=1/step_RF_evap, units='A')
    print (start_current4) 
    print (end_current4)  
    
    # ni_pci_6733_1 analog outputs:
    RF_mixer1.constant(t, RF_mixer)#0.6000
    RF_switch_0.go_high(t)
    #RF_mixer2.constant(t, 0.6000)
    #RF_mixer3.constant(t, 0.6000)
    
    # novatechdds9m_1 channel outputs:
    RF_evap.frequency.customramp(t, EvapTime, LineRamp, StartRF, EndRF, samplerate=1/step_RF_evap, units='MHz')
    
    # ni_usb_6343_1 analog outputs:
    y_bias.customramp(t, EvapTime, LineRamp, TpyShimTrap, TpyShimTrapRF, samplerate=1/step_RF_evap, units='A')
    
    return EvapTime  
 

    

  
@stage
def decompress_1(t):
    if not dipole_evap:
        UV_LED.go_low(t)
   
    # ni_usb_6343_0 analog outputs:
    end_current4 = Poly4Asymmetric((f_super + 1)/4,None,IFT, WidthFT, SkewFT,1,Cf=None, time_argument_is_f=True)
    
    transport_current_4.customramp(t, DecompTime1, LineRamp, end_current4, MiddleCurrent, samplerate=1/step_decompress, units='A')
    
    # ni_usb_6343_0 digital outputs:
    curent_supply_3_select_line0.go_low(t)
    curent_supply_3_select_line1.go_low(t)
    curent_supply_3_enable.go_low(t)
    
    # ni_usb_6343_1 analog outputs:
    y_bias.customramp(t, DecompTime1, LineRamp, TpyShimTrapRF, TpyShimTrap1, samplerate=1/step_decompress, units='A')
    
    # novatechdds9m_0 channel outputs:
    #RF_evap.frequency.customramp(t, DecompTime1, LineRamp, EndRF, EndFreq, samplerate=1/step_decompress, units='MHz')

    # RF OFF
    RF_evap.setfreq(t,  StartRF)
    RF_evap.setamp(t, 0.000) 
    RF_switch_0.go_low(t)
    RF_mixer1.constant(t, 0)
    return DecompTime1

    
@stage
def decompress_2(t):
    # ni_usb_6343_0 analog outputs:
    transport_current_4.customramp(t, DecompTime2, LineRamp, MiddleCurrent, FinalCurrent, samplerate=1/step_decompress, units='A')
    
    # ni_usb_6343_1 analog outputs:
    y_bias.customramp(t, DecompTime2, LineRamp, TpyShimTrap1, TpyShimTrap2, samplerate=1/step_decompress, units='A')
    
    return DecompTime2

    
@stage
def decompress_3(t):
        
    # ni_pci_6733_0 analog outputs:
    dipole_intensity.customramp(t, DecompTime3, ExpRamp, InitialDipoleInt, DipoleInt2, dipoleEvapTau, samplerate=1/step_decompress_3)
    dipole_split.customramp(t, DecompTime3, ExpRamp, InitialDipoleSplit, DipoleSplit2, dipoleEvapTau, samplerate=1/step_decompress_3)
        
    # ni_usb_6343_0 analog outputs:
    transport_current_4.customramp(t, DecompTime3, ExpRamp, FinalCurrent, 0, dipoleEvapTau, samplerate=1/step_decompress_3, units='A')
    
    # ni_usb_6343_1 analog outputs:
    y_bias.customramp(t, DecompTime3, LineRamp, TpyShimTrap2, TpyShimTrap3, samplerate=1/step_decompress_3, units='A')
    
    # ni_usb_6343_0 digital outputs:
    curent_supply_4_select_line0.go_low(t+DecompTime3)
    curent_supply_4_select_line1.go_low(t+DecompTime3)
    curent_supply_4_enable.go_low(t+DecompTime3)
    
    return DecompTime3

    
@stage
def ramp_to_highBfield(t):
    # ni_usb_6343_1 analog outputs:
    # y_bias.customramp(t, 250*ms, LineRamp, TpyShimTrap3, TpyShimStartARP, samplerate=1/step_ramp_Bfield, units='A')
    # z_bias.customramp(t, 250*ms, LineRamp, a0*TpzShim, a0*TpzShimStart, samplerate=1/step_ramp_Bfield, units='A')
    
    y_bias.customramp(t, 250*ms, LineRamp, TpyShimTrap3, Zimg_TpyShim, samplerate=1/step_ramp_Bfield, units='A')
    z_bias.customramp(t, 250*ms, LineRamp, a0*TpzShim, PTAI_TpzShim_start, samplerate=1/step_ramp_Bfield, units='A')
    return 250*ms

@stage
def ARP_uwave(t):
    # ni_usb_6343_1 analog outputs:
    #y_bias.customramp(t, 10*ms, LineRamp, TpyShimStartARP, TpyShimEndARP, samplerate=1/step_ramp_uwave, units='A')
    z_bias.customramp(t, 10*ms, LineRamp, PTAI_TpzShim_start, PTAI_TpzShim_end, samplerate=1/step_ramp_uwave, units='A')
  
    return 10*ms 

@stage
def dipole_evaporation(t):

    # ni_pci_6733_0 analog outputs:
    dipole_intensity.customramp(t, DipoleEvapTime, LineRamp, DipoleInt2, FinalDipoleInt, samplerate=1/step_dipole_evap)
    dipole_split.customramp(t, DipoleEvapTime, LineRamp, DipoleSplit2, FinalDipoleSplit, samplerate=1/step_dipole_evap)
    
    #Change field orientation to be 2G along z and 0 along y bias
    # ni_usb_6343_1 analog outputs:
    #y_bias.customramp(t, DipoleEvapTime, LineRamp, TpyShimEndARP, Zimg_TpyShim, samplerate=1/step_ramp_uwave, units='A')
    #z_bias.customramp(t, DipoleEvapTime, LineRamp, a0*TpzShimStart, PTAI_TpzShim_start, samplerate=1/step_ramp_Bfield, units='A')
    return DipoleEvapTime

    
@stage
def dipole_evaporation_2_OffsetRamp(t):
    # ni_pci_6733_0 analog outputs:
    dipole_intensity.customramp(t, DipoleEvapRampTime, EvapRampOffsetLocal, DipoleInt2, FinalDipoleRamp, DipoleIntMinimum, dipoleEvapTauRamp, samplerate=1/step_dipole_evap_ramp)
    #dipole_split.customramp(t, DipoleEvapRampTime, EvapRampOffsetLocal, DipoleSplit, FinalDipoleSplit, DipoleSplitMinimum,dipoleEvapTauRamp, samplerate=1/step_dipole_evap_ramp)
    return DipoleEvapRampTime    

@stage
def dipoleRampUp(t):
    # ni_pci_6733_0 analog outputs:
    dipole_intensity.customramp(t, dipoleRampUpTime, LineRamp, FinalDipoleInt, DipoleIntImFocusing, samplerate=1/step_dipole_RampUp)
    #dipole_split.customramp(t, dipoleRampUpTime, LineRamp, FinalDipoleSplit, DipoleSplitImFocusing, samplerate=1/step_dipole_RampUp)
    return dipoleRampUpTime



@stage
def ramp_uwave(t): 
    # novatechdds9m_1 channel outputs:
    uwave1.setfreq(t-200*us, (59 + uwaveoffset), units='MHz')#TimeSetNovatech=100*us
    uwave1.setamp(t-200*us, uamp_ARP)
    
    # ni_pci_6733_1 digital outputs:
    uWave_switch_0.go_high(t)
    
    scope_trigger_0.go_high(t)
    scope_trigger_0.go_low(t+1*ms)
    
    # ni_pci_6733_1 analog outputs:
    microwave_attenuator.customramp(t, 1*ms, LineRamp, 6.0, 0.0, samplerate=1/step_ramp_uwave)
    uwave_mixer1.customramp(t+1*ms, 1*ms, LineRamp, 0.0, u_w_mixer, samplerate=1/step_ramp_uwave)
   
    return 2*ms 
    
@stage
def uwave_off(t):
    # ni_pci_6733_1 analog outputs:
    microwave_attenuator.customramp(t+1*ms, 1*ms, LineRamp, 0.0, 6.0, samplerate=1/step_ramp_uwave)
    uwave_mixer1.customramp(t, 1*ms, LineRamp, u_w_mixer, 0.0, samplerate = 1/step_ramp_uwave)
    
    # ni_pci_6733_1 digital outputs:
    uWave_switch_0.go_low(t+2*ms)
   
    uwave1.setamp(t+2*ms, 0) # Changed 2018_10_10
   
    return 2*ms    


@stage
def uwave_snapOff(t):
#If ARP is working, but have not been able to measure Rabi frequency via pulsing, 
#can do the "ramp-hold-snap off" method to measure the Rabi frequency.
#In this case one would scan the final RF frequency value in the ramp portion.
#Fitting to ArcTan and extracting the width provides the Rabi frequency.     
    # ni_pci_6733_1 analog outputs:
    microwave_attenuator.constant(t, 6.0)
    uwave_mixer1.constant(t, 0.0)
    
    # ni_pci_6733_1 digital outputs:
    uWave_switch_0.go_low(t)   
    uwave1.setamp(t, 0)    
    return 1*ms

@stage
def blast_2_2(t):
    time_blast = pulse_beam(t, probe_1, AOM_probe_1, shutter_x, blast22_Int, 3*ms) #z TOF probe on 06/24/2019
    return time_blast


@stage
def set_uwave_resonance(t):
    # novatechdds9m_1 channel outputs:
    uwave1.setfreq(t, (59 + uwaveoffset_pulse), units='MHz')
    uwave1.setamp(t, uamp_pulse)
    return TimeSetNovatech


@stage
def uwave_pulse(t):
      
    #Turn on 
    uWave_switch_0.go_high(t)
    microwave_attenuator.constant(t, 0.0)
    uwave_mixer1.constant(t, 0.6)
    #Turn off
    uWave_switch_0.go_low(t+time_microwave_pulse)
    microwave_attenuator.constant(t + time_microwave_pulse, 6.0)
    uwave_mixer1.constant(t+time_microwave_pulse, 0.0)
      
    return time_microwave_pulse 


@stage
def uwave_pulse_reduceOD(t):      
    #Turn on 
    uWave_switch_0.go_high(t)
    microwave_attenuator.constant(t, 0.0)
    uwave_mixer1.constant(t, 0.6)
    #Turn off
    uWave_switch_0.go_low(t+time_uwavePulse_ReduceOD)
    microwave_attenuator.constant(t + time_uwavePulse_ReduceOD, 6.0)
    uwave_mixer1.constant(t+time_uwavePulse_ReduceOD, 0.0)
      
    return time_uwavePulse_ReduceOD    

@stage
def uwave_pulse_off(t):
    uwave1.setamp(t, 0.0)
    return time_microwave_pulse_off    


@stage
def ramp_uwaveImage(t): 
    # novatechdds9m_1 channel outputs:
    uwave1.setfreq(t-100*us, (59 + uwaveoffset_pulse + DetuneUwave), units='MHz')#TimeSetNovatech=100*us
    uwave1.setamp(t-100*us, uamp_ARP)
    
    # ni_pci_6733_1 digital outputs:
    uWave_switch_0.go_high(t)
    
    # ni_pci_6733_1 analog outputs:
    microwave_attenuator.customramp(t, uwaveImageRampTime, LineRamp, 6.0, 0.0, samplerate=1/step_ramp_uwave)
    uwave_mixer1.customramp(t, uwaveImageRampTime, LineRamp, 0.0, u_w_mixer, samplerate=1/step_ramp_uwave)
    return uwaveImageRampTime             

    
@stage 
def RFandCoils_off(t):
    RF_mixer1.constant(t, 0)
    RF_switch_0.go_low(t)
    
    #---- Turn off magnetic trap so we only have dipole trap, 
    #so that we can optimize the number of atoms in the dople trap.
    # ni_pci_6733_0 analog outputs:
    transport_current_2.constant(t, -1, units='A')
    transport_current_3.constant(t, 0, units='A')
    transport_current_4.constant(t, 0, units='A')
    
    # ni_usb_6343_0 digital outputs:
    curent_supply_4_select_line0.go_low(t)
    curent_supply_4_select_line1.go_low(t)
    curent_supply_4_enable.go_low(t)
    
    return TimeRFandCoilsOff  #2*ms
  
@stage 
def Dipole_off(t):
    # ni_pci_6733_0 analog outputs:
    dipole_intensity.constant(t, 0.0)
    # pulseblaster_0 outputs:
    dipole_switch.go_low(t)
   
    return Dipole_off_time    
   
def pulse_beam(t, beam, rf_switch, shutter, command, pulse_duration):
    beam.constant(t-TimeInSituOpenShutter-1*ms, 0)
    rf_switch.go_low(t-TimeInSituOpenShutter-1*ms)
    shutter.go_high(t-TimeInSituOpenShutter)
    rf_switch.go_high(t)
    beam.constant(t, command)
    beam.constant(t+pulse_duration, 0)
    shutter.go_low(t+pulse_duration)
    rf_switch.go_low(t+pulse_duration)   
    return pulse_duration


@stage 
def KineticSeries_Image(t, type='atoms', PresetFreq=False):

    probe_freq = ImageFreqHighField # ImageFreq
    total_time = 0.0
    if uwaveImaging or AndorF2_InsituImage:
            probe_freq = ImageFreqHighField + DetuneImageFreq    

    if PresetFreq:
        MOT_lock.frequency.constant(t-1000.*ms, ResFreq+probe_freq, units='MHz')      

    # Main acquisition
    if type == 'atoms':     
        shot_id = 'shot1'
        total_time += pulse_beam(t, probe_1, AOM_probe_1, shutter_x, ProbeInt_InSitu, AndorTimeImage)
    elif type == 'probe':
        shot_id = 'shot2'
        total_time += pulse_beam(t, probe_1, AOM_probe_1, shutter_x, ProbeInt_InSitu, AndorTimeImage)  
    elif type == 'dark':
        shot_id = 'shot3'
        total_time += AndorTimeImage

    Andor_iXon_ultra.expose(t-10*us,shot_id, type) 

    total_time += AndorAbsTimeDownload
    
    return total_time   


@stage 
def Fast_Kinetics_Image(t, type='atoms', PresetFreq=False):

    probe_freq = ImageFreqHighField # ImageFreq
    total_time = 0.0

    if PresetFreq:
        MOT_lock.frequency.constant(t-100.*ms, ResFreq+probe_freq, units='MHz')      

    # Main acquisition
    if type == 'atoms':     
        shot_id = 'shot1'
        AOM_probe_1.go_high(t) #rf switch 
        probe_1.constant(t, ProbeInt_InSitu)
        probe_1.constant(t+AndorTimeImage, 0)
        AOM_probe_1.go_low(t+AndorTimeImage) 
        total_time += AndorTimeImage

    elif type == 'probe':
        shot_id = 'shot2'
        AOM_probe_1.go_high(t)
        probe_1.constant(t, ProbeInt_InSitu)
        probe_1.constant(t+AndorTimeImage, 0)
        AOM_probe_1.go_low(t+AndorTimeImage) 
        total_time += AndorTimeImage
 
    elif type == 'dark':
        shot_id = 'shot3'
        total_time += AndorTimeImage

    elif type == 'probe_2':
        shot_id = 'shot4'
        AOM_probe_1.go_high(t)
        probe_1.constant(t, ProbeInt_InSitu)
        probe_1.constant(t+AndorTimeImage, 0)
        AOM_probe_1.go_low(t+AndorTimeImage) 
        total_time += AndorTimeImage

    Andor_iXon_ultra.expose(t-10*us,shot_id, type) 
    
    return total_time   



@stage 
def setField_PTAI_probe_dark_shots(t):

    x_bias.constant(t, TpxShim, units='A') # TpxShim = 1.511 A Zimg_TpxShim=1.574 A = 0 Gauss
    #y_bias.constant(t, Zimg_TpyShim, units='A') #0.003 A = 0 Gauss   #no changes here
    z_bias.constant(t, PTAI_TpzShim_end , units='A') #2 Gauss
    #z_bias.customramp(t, 10*ms, LineRamp, Zimg_TpzShim, PTAI_TpzShim_end, samplerate=1/step_ramp_uwave, units='A')
    return 1*ms

@stage
def snap_image(t, imaging_plane='z_TOF', type='atoms'):
    #As of 10/2019 this method is exclusively to be used with z TOF and x in-situ imaging.
    # Based on imaging plane, use a specific AOM/CCD/probe set.

    if imaging_plane == 'z_TOF':
        
        ###############  x in-situ beam as the TOF beam specifications - 2019/05/10
        AOM = AOM_probe_2
        probe, probeint, probe_freq = probe_2, ProbeInt2, ImageFreq #ImageFreqHighField#
        shutter = shutter_x_insitu
        CCD = XY_1_Flea3 
        
        ###############  Specifications with the real TOF beam, which is currently connected to MOT abs system, specifications - 2019/05/10
        #AOM = AOM_probe_1
        #CCD = XY_1_Flea3
        #probe, probeint, probe_freq = probe_1, ProbeInt, ImageFreq
        #shutter = shutter_z              
        
    elif imaging_plane == 'MOT_abs':
        AOM = AOM_probe_1
        CCD = YZ_2_Flea3
        probe, probeint, probe_freq = probe_1, ProbeInt, ImageFreq
        shutter = shutter_z

    elif imaging_plane == 'x_insitu':    
        CCD = YZ_1_Flea3
        if xRepump:
            AOM = AOM_MOT_repump
            probe, probeint, probe_freq = MOT_repump, ProbeIntRepump, ImageFreqXrepump
            shutter = shutter_top_repump
        else:
            AOM = AOM_probe_2
            probe, probeint, probe_freq = probe_2, ProbeInt2, ImageFreq
            shutter = shutter_x_insitu
    total_time = 0.0    
    # Repump
    if Repump :
        #2019/11/01 changing  for polarization investigation HAVE TO CHANGE BACK AFTER COMLETION!!
        pulse_beam(t-5*us, MOT_repump, AOM_MOT_repump, shutter_top_repump, 0.8, 5*us)
        #pulse_beam(t-5*us, MOT_repump, AOM_MOT_repump, shutter_top_repump, 0.8, TimeImage)
    if xRepump: 
        #pulse_beam(t-5*us, probe_1, AOM_probe_1, shutter_x, 0.8, TimeImage)
        pulse_beam(t-5*us, probe_2, AOM_probe_2, shutter_x_insitu, 0.8, TimeImage)   
    # Main acquisition
    if type == 'atoms':
        # Note: Same AOM is used for the probe beam and the MOT cooling beam        
        MOT_lock.frequency.constant(t-100.*ms, ResFreq+probe_freq, units='MHz')
        #set image freq in HoldAfterMove necause laser locking takes time        
        shot_id = 'shot1'
        total_time += pulse_beam(t, probe, AOM, shutter, probeint, TimeImage)
    elif type == 'probe':
        shot_id = 'shot2'
        total_time += pulse_beam(t, probe, AOM, shutter, probeint, TimeImage)  
    elif type == 'dark':
        shot_id = 'shot3'
        #total_time += pulse_beam(t, probe, AOM, shutter, 0.0, TimeImage)
        total_time += TimeImage
    elif type == 'red':
        shot_id = 'shot4'
        total_time += pulse_beam(t, probe, AOM, shutter, probeint, TimeImage)    
    elif type == 'blue':
        shot_id = 'shot5'
        total_time += pulse_beam(t, probe, AOM, shutter, probeint, TimeImage)
    
    #fluxgate_trig.go_high(t)
    #fluxgate_trig.go_low(t+1.*ms)

    CCD.expose(t-30*us, shot_id, type)
    total_time += TimeDownloadImage
    
    return total_time


@stage
def apply_gradient(t):
    #Goal: Provide a kick to later slosh BEC in trap by nonadiabatically removing the  
    #kick in order to measure the ODT trap frequencies
    # -i.e. excite n=0, l=1 resonance of the trap.

    # ni_usb_6343_1 analog outputs:
    x_bias.customramp(t, 1e-3, LineRamp, TpxShim, TpxShimOffset, samplerate=1/step_TOF, units='A')
    y_bias.customramp(t, 1e-3, LineRamp, Zimg_TpyShim, TpyShimOffset,  samplerate=1/step_TOF, units='A')
    z_bias.customramp(t, 1e-3, LineRamp, PTAI_TpzShim_end, TpzShimOffset,  samplerate=1/step_TOF, units='A')
    # ni_usb_6343_0 digital outputs:
    curent_supply_4_select_line0.go_high(t)
    curent_supply_4_select_line1.go_high(t)
    curent_supply_4_enable.go_high(t)
    # ni_usb_6343_0 analog outputs:
    transport_current_4.customramp(t, TimeApplyGradient, LineRamp, 0, gradient_current_slosh, samplerate=1/step_TOF, units='A')    
    return TimeApplyGradient

@stage
def snap_gradient(t):
    # ni_usb_6343_0 analog outputs:
    transport_current_4.constant(t, 0, units='A')
    
    # ni_usb_6343_0 digital outputs:
    curent_supply_4_select_line0.go_low(t)
    curent_supply_4_select_line1.go_low(t)
    curent_supply_4_enable.go_low(t)
    
    return 100e-6


    
@stage
def Short_TOF(t,duration, imaging_plane = 'x_insitu', SGstart=7*ms):

    if dipole_evap:
        dipole_intensity.constant(t, 0.0)
        dipole_switch.go_low(t)

    ''' AddedTime parameter accounts for the novatech programming conflict when xrepump
    imaging is used to image the magnetic trapped atoms after RF evaporation stage, 
    WITHOUT decompression stages. Without the AddedTime RF evaporation and MOT_lock freq.
    lead to a novatech timing error.  - 02/28/2020'''     
    if duration<5 and xRepumpImaging:
    # when in-situ x-repump imaging of RF cloud
        AddedTime = 4*ms
        t += AddedTime
    else: 
        AddedTime = 0*ms

    #Set bias fields for imaging
    if imaging_plane == 'x_insitu':    
        # ni_usb_6343_1 analog outputs:
        x_bias.constant(t, Ximg_TpxShim, units='A') #1 Gauss
        y_bias.constant(t, Ximg_TpyShim, units='A') #0 Gauss
        z_bias.constant(t, Ximg_TpzShim, units='A') #0 Gauss
    else:  
        x_bias.constant(t, Zimg_TpxShim, units='A') #1.574 A = 0 Gauss
        y_bias.constant(t, Zimg_TpyShim, units='A') #0.003 A = 0 Gauss   #TpyShimEndARP
        z_bias.constant(t, Zimg_TpzShim, units='A') 
        #2.25 Gauss  PTAI_TpzShim_end    #-1 1 Gauss Zimg_TpzShim
    #offset.constant(t, Offset + dTpzShim)
    
    # ni_usb_6343_0 digital outputs:
    transport_current_1.constant(t, -1., units='A')
    transport_current_2.constant(t, -1., units='A')
    transport_current_3.constant(t, 0., units='A')
    transport_current_4.constant(t, 0., units='A')
    
    # ni_usb_6343_0 digital outputs:
    curent_supply_3_select_line0.go_low(t)
    curent_supply_3_select_line1.go_low(t)
    curent_supply_3_enable.go_low(t)

    # ni_usb_6343_0 digital outputs:
    curent_supply_4_select_line0.go_low(t)
    curent_supply_4_select_line1.go_low(t)
    curent_supply_4_enable.go_low(t)

    # if not dipole_evap:
    #     end_current4 = Poly4Asymmetric((f_super + 1)/4,None,IFT, WidthFT, SkewFT,1,Cf=None, time_argument_is_f=True)
    #     transport_current_4.customramp(t, TimeLongTOF, LineRamp,end_current4,-1, samplerate=1 / step_magnetic_transport,units='A')
    #     curent_supply_4_select_line0.go_low(t)
    #     curent_supply_4_select_line1.go_low(t)
    #     curent_supply_4_enable.go_low(t)
    
    if SG:
        # ni_usb_6343_0 analog outputs:
        transport_current_4.constant(t+SGstart, SGCurrent, units='A')
    
        # ni_usb_6343_0 digital outputs:
        curent_supply_4_select_line0.go_high(t+SGstart)
        curent_supply_4_select_line1.go_high(t+SGstart)
        curent_supply_4_enable.go_high(t+SGstart)              
        # ni_usb_6343_0 analog outputs:  
        transport_current_4.constant(t+SGstart+5*ms, -1.0, units='A')
        
        # ni_usb_6343_0 digital outputs:
        curent_supply_4_select_line0.go_low(t+SGstart+5*ms)
        curent_supply_4_select_line1.go_low(t+SGstart+5*ms)
        curent_supply_4_enable.go_low(t+SGstart+5*ms)
    
    # if duration>0:
    #     return duration
    # else:
    #     return TimeLongTOF
    return duration+AddedTime
 
@stage
def AOM_MOT_cooling_reset_afterSnapImage(t):
    MOT_lock.setfreq(t, (ResFreq + EndFreqMol)*MHz)
    return 1*ms 

@stage
def pulse_speckle(t,speckle_pulse_dur):

    AOM_green_beam.constant(t-20*ms, speckle_amp)
    green_beam.go_low(t-20*ms)
    shutter_greenbeam.go_high(t-20*ms)
    

    green_beam.go_high(t)
    green_beam.go_low(t+speckle_pulse_dur)

    AOM_green_beam.constant(t+speckle_pulse_dur, green_beam_off_V
                            )
    shutter_greenbeam.go_low(t+speckle_pulse_dur)

    return speckle_pulse_dur 
        
@stage
def off(t):  
    # UV Soak -- keep the UV on the whole time
    if UVSoak or UVSoakBetweenShots:
        UV_LED.go_high(t)
    else:
        UV_LED.go_low(t)

    # ni_pci_6733_0 analog outputs:
    MOT_repump.constant(t,  UVMOTRepump)
    MOT_cooling.constant(t, UVMOTAmplitude)
    probe_1.constant(t,     ProbeInt)
   
    # ni_usb_6343_0 analog outputs:
    
    transport_current_1.constant(t, 0, units='A')
    transport_current_2.constant(t, 0, units='A')
    transport_current_3.constant(t, 0, units='A')
    transport_current_4.constant(t, 0, units='A')
   
    # ni_usb_6343_1 analog outputs:
    x_bias.constant(t, 2.11*UVxShim, units='A')
    y_bias.constant(t,      UVyShim, units='A')
    z_bias.constant(t, -0.8*UVzShim, units='A')
    
    AOM_probe_1.go_low(t)
    shutter_z.go_low(t)
    #probe_1.constant(t, 0.0)
    
    # novatechdds9m_0 channel outputs:
    MOT_lock.setfreq(t,  (ResFreq + UVMOTFreq)*MHz)
    RF_evap.setfreq(t,  StartRF)
    RF_evap.setamp(t, 0.0)
    FPGA_ao.constant(t, 0.0)
    # ni_usb_6343 outputs:
    green_beam.go_low(t)
    green_servo_trigger.go_low(t+5*ms)
    shutter_greenbeam.go_low(t)
    AOM_green_beam.constant(t, green_beam_off_V)
    fluxgate_trig.go_low(t)        
    dipole_switch.go_low(t)
    dipole_intensity.constant(t, 0.0)
    dipole_split.constant(t, InitialDipoleSplit)
    
    return 0.031



start()
t = 0
t += prep(t)
if image_MOT:
    t += small_MOT(t)
    t += MOT_image_1(t)
    t += download_MOT_image_1(t)
    t += MOT_image_2(t)
    t += download_MOT_image_2(t)
    t += MOT_image_3(t)
    t += download_MOT_image_3(t) 
    
t += UVMOT(t)    
t += cMOT(t)
t += molasses(t)
t += optical_pump_1(t)
t += optical_pump_2(t)
t += magnetic_trap(t)  

t += move_1(t)
t += move_2(t)
t += move_3(t)
t += move_4(t)
t += move_5(t)
t += move_6(t)
t += move_7(t)
t += move_8(t)

t += move_9(t)
t += move_10(t) 
t += move_11(t)

if dipole_evap:
    t += evaporate(t, EvapTime=RFevapTime)
    t += decompress_1(t)
    t += decompress_2(t)
    t += decompress_3(t)
    t += ramp_to_highBfield(t)  

    if uwave_transfer:
        t += ramp_uwave(t)
    
    if not snap_off_uwave:   
        t += ARP_uwave(t) # just ramp field, no u-wave changes here    
    
    if uwave_transfer: 
        t += uwave_off(t)
        t += 1*ms # to be sure the shutter is closed before blasting.
        t += blast_2_2(t)  
        
    t += dipole_evaporation(t)

    if snap_off_uwave:
        t += ramp_uwave(t) 
        t += ARP_uwave(t) # ramp bias field
        t += 60*ms
        t += uwave_snapOff(t)
 
    if uwave_pulsing:
        t += set_uwave_resonance(t)
        t += uwave_pulse(t)  
        t += uwave_pulse_off(t)

    if Reduce_InsituOD:
        t += set_uwave_resonance(t)
        t += uwave_pulse_reduceOD(t)  
        t += uwave_pulse_off(t)
        t += 1*ms
        t += blast_2_2(t) 
        ''' 20 ms is added in order to make sure all transferred atoms are 
        killed before the PTAI stage. Alternatively I could increase the probe pulse 
        duration in blast_2_2(t) stage.  
        ''' 
        t += 20*ms # 


    if PartialTransferImaging:
        t += set_uwave_resonance(t)
        #Take atoms shot PTAI images, (number_kinetics) times
        number_fk_images = Andor_iXon_ultra.camera_attributes['number_kinetics']        
        for i in range(number_fk_images):
            t += uwave_pulse(t)
            t += 3*us 
            if i==0:
                #Open shutter before taking the first image in the series
                probe_1.constant(t-TimeInSituOpenShutter-1*ms, 0) # t- 3.7 ms - 1ms
                AOM_probe_1.go_low(t-TimeInSituOpenShutter-1*ms)
                shutter_x.go_high(t-TimeInSituOpenShutter)
                t += Fast_Kinetics_Image(t, type='atoms', PresetFreq=True)
                t += AndorFK_Interval
            else:
                t += Fast_Kinetics_Image(t, type='atoms')
                t += AndorFK_Interval
        #Close shutter after taking the last image in the series
        AndorExposureTime = Andor_iXon_ultra.camera_attributes['exposure_time']         
        shutter_x.go_low(t)
        #shutter_x.go_low(t+ number_fk_images*(AndorFK_Interval+AndorExposureTime))
        #t+= AndorFK_TimeDownload    
        t += uwave_pulse_off(t) #duration 1*ms     

    if PTAI_LinewidthMeasure:
        # If enabled, configure Andor to operate in KS mode with 3 images
        t += set_uwave_resonance(t)
        for i in range(1):
            t += uwave_pulse(t)
            t += 3*us 
            t += KineticSeries_Image(t, type='atoms', PresetFreq=True)
        t += KineticSeries_Image(t, type='probe')
        t += KineticSeries_Image(t, type='dark')
        t += uwave_pulse_off(t) #duration 1*ms

    if AndorF2_InsituImage:
        '''
        If set to True, Andor has to be configured to KS mode with 3 images.
        For ROI 256x1024, download time is 11.15 ms.
        '''
        t += KineticSeries_Image(t, type='atoms', PresetFreq=True)
        t += KineticSeries_Image(t, type='probe')
        t += KineticSeries_Image(t, type='dark')

    if uwaveImaging:   
        t += ramp_uwaveImage(t) 

    ######## To measure the ODT frequencies ############
    # t += apply_gradient(t)
    # t += snap_gradient(t)
    # t += time_hold_slosh
    ########################
    
    ''' 100 ms is added to account for setting the z probe frequency when using the both 
    TOF and in-situ PTAI. 
    DO NOT REMOVE THIS EXTRA TIME before making sure mot_lock-freq 
    timings wrt imaging are as intended. 
    ''' 
    t += 100*ms
    t += Dipole_off(t) #duration = 0.1*ms
    if pulse_speckle_opt and speckle_pulse_dur>0.0:
        t += pulse_speckle(t,speckle_pulse_dur)
        
else:
    # Since we are not trying to make a BEC we can afford to be
    # less effective in the RF evaporation and just look at what we get
    t += evaporate(t, EvapTime=RFevapTimeNoDipole)
    # t += RFandCoils_off(t)
   
if AndorImaging:
    t += Short_TOF(t, duration=AndorTimeShTOF, imaging_plane='z_insitu',SGstart=12*ms)    
    t += KineticSeries_Image(t, type='atoms', PresetFreq=True)
    t += KineticSeries_Image(t, type='probe')
    t += KineticSeries_Image(t, type='dark')


if onlyZTOF_imaging or BothCameras:
    if pulse_speckle_opt:
        t += Short_TOF(t, duration=TimeLongTOF-speckle_pulse_dur, imaging_plane='z_TOF',SGstart=12*ms) # z_TOF      
    else:
        t += Short_TOF(t, duration=TimeLongTOF, imaging_plane='z_TOF',SGstart=12*ms) # z_TOF      
    t += snap_image(t, imaging_plane='z_TOF', type='atoms')# x_insitu 
    if uwaveImaging:
        uwave_off(t)
    t += snap_image(t, imaging_plane='z_TOF', type='probe')
    t += snap_image(t, imaging_plane='z_TOF', type='dark')

if xRepumpImaging:
    t += Short_TOF(t, duration=TOF_xRepump, imaging_plane='x_insitu',SGstart=12*ms)       
    t += snap_image(t, imaging_plane='x_insitu', type='atoms')# x_insitu 
    t += snap_image(t, imaging_plane='x_insitu', type='probe')
    t += snap_image(t, imaging_plane='x_insitu', type='dark')

#Add time needed to download the PTAI atoms FK series image
if PartialTransferImaging:    
    t += AndorFK_TimeDownload - (3*TimeDownloadImage + TimeLongTOF + 
                                 Dipole_off_time + time_microwave_pulse_off - 100*ms)

#Take probe and dark shot PTAI images, with the uwaves on
if PartialTransferImaging:    
    t += set_uwave_resonance(t) # duration 1 ms
    setField_PTAI_probe_dark_shots(t) # 1ms
    for i in range(number_fk_images):
        t += uwave_pulse(t)
        t += 3*us                     
        if i==0:
            #Open shutter before taking the first image in the series
            probe_1.constant(t-TimeInSituOpenShutter-1*ms, 0) # t- 3.7 ms - 1ms
            AOM_probe_1.go_low(t-TimeInSituOpenShutter-1*ms)
            shutter_x.go_high(t-TimeInSituOpenShutter)
            t += Fast_Kinetics_Image(t, type='probe')
            t += AndorFK_Interval
        else:
            t += Fast_Kinetics_Image(t, type='probe')
            t += AndorFK_Interval
    #Close shutter after taking the last image in the series        
    shutter_x.go_low(t)     
    t+= AndorFK_TimeDownload

    #DARK SHOT
    for i in range(number_fk_images):
        t += uwave_pulse(t)
        t += 3*us                   
        t += Fast_Kinetics_Image(t, type='dark')
        t += AndorFK_Interval
    t+= AndorFK_TimeDownload

    #######PROBE SHOT 2
    t += set_uwave_resonance(t) # duration 1 ms
    setField_PTAI_probe_dark_shots(t) # 1ms
    for i in range(number_fk_images):
        t += uwave_pulse(t)
        t += 3*us                     
        if i==0:
            #Open shutter before taking the first image in the series
            probe_1.constant(t-TimeInSituOpenShutter-1*ms, 0) # t- 3.7 ms - 1ms
            AOM_probe_1.go_low(t-TimeInSituOpenShutter-1*ms)
            shutter_x.go_high(t-TimeInSituOpenShutter)
            t += Fast_Kinetics_Image(t, type='probe_2')
            t += AndorFK_Interval
        else:
            t += Fast_Kinetics_Image(t, type='probe_2')
            t += AndorFK_Interval
    #Close shutter after taking the last image in the series        
    shutter_x.go_low(t)     
    t+= AndorFK_TimeDownload
    uwave_pulse_off(t) #duration 1*ms

t += off(t)

if dipole_evap:
    t += cooldown_time_short
else: 
    t += cooldown_time_long 

stop(t)