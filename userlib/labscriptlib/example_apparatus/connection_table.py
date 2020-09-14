from labscript import *

compiler.save_hg_info = False

from labscript_devices.PulseBlaster_SP2_24_100_32k import PulseBlaster_SP2_24_100_32k
from labscript_devices.NI_PCI_6733 import NI_PCI_6733
from labscript_devices.NI_USB_6343 import NI_USB_6343
from labscript_devices.NI_DAQmx.labscript_devices import NI_PCI_6733, NI_USB_6343
from labscript_devices.NovaTechDDS9M import NovaTechDDS9M
from labscript_utils.unitconversions import BidirectionalCoilDriver
from labscript_devices.IMAQdxCamera.labscript_devices import IMAQdxCamera
# from labscript_devices.NewFocusPicomotor8742.labscript_devices import NewFocusPicomotor8742, Picomotor
# from labscript_devices.ChipFPGA import ChipFPGA
from labscript_devices.TekScope.labscript_devices import TekScope
# from labscript_devices.AndorSolis.labscript_devices import AndorSolis

PulseBlaster_SP2_24_100_32k('pulseblaster_0', programming_scheme='pb_stop_programming/STOP', pulse_width='minimum')

DigitalOut(name='AOM_MOT_repump',          parent_device=pulseblaster_0.direct_outputs, connection='flag 0')
DigitalOut(name='shutter_MOT_repump',      parent_device=pulseblaster_0.direct_outputs, connection='flag 1')
Trigger(name='camera_trigger_1',           parent_device=pulseblaster_0.direct_outputs, connection='flag 3',
        trigger_edge_type='falling')
DigitalOut(name='AOM_MOT_cooling',         parent_device=pulseblaster_0.direct_outputs, connection='flag 4')
DigitalOut(name='shutter_MOT_cooling',     parent_device=pulseblaster_0.direct_outputs, connection='flag 5')
DigitalOut(name='AOM_optical_pumping',     parent_device=pulseblaster_0.direct_outputs, connection='flag 6')
DigitalOut(name='shutter_optical_pumping', parent_device=pulseblaster_0.direct_outputs, connection='flag 7')
DigitalOut(name='AOM_probe_1',             parent_device=pulseblaster_0.direct_outputs, connection='flag 8')
DigitalOut(name='shutter_z',               parent_device=pulseblaster_0.direct_outputs, connection='flag 9')
DigitalOut(name='AOM_probe_2',             parent_device=pulseblaster_0.direct_outputs, connection='flag 10')
DigitalOut(name='shutter_x',               parent_device=pulseblaster_0.direct_outputs, connection='flag 11')
DigitalOut(name='DDS_C_update',            parent_device=pulseblaster_0.direct_outputs, connection='flag 12')
Trigger(name='camera_trigger_0',           parent_device=pulseblaster_0.direct_outputs, connection='flag 13',
        trigger_edge_type='falling')
Trigger(name='camera_trigger_2',           parent_device=pulseblaster_0.direct_outputs, connection='flag 14',
        trigger_edge_type='falling')
Trigger(name='camera_trigger_3',           parent_device=pulseblaster_0.direct_outputs, connection='flag 15',
        trigger_edge_type='falling')
#DigitalOut(name='DDS_A_update',            parent_device=pulseblaster_0.direct_outputs, connection='flag 14') #disconnected on 03.20.18       
#DigitalOut(name='DDS_B_update',            parent_device=pulseblaster_0.direct_outputs, connection='flag 15') #disconnected on 03.20.18
DigitalOut(name='shutter_top_repump',      parent_device=pulseblaster_0.direct_outputs, connection='flag 16')
DigitalOut(name='dipole_switch',      parent_device=pulseblaster_0.direct_outputs, connection='flag 17')
DigitalOut(name='fluxgate_trig',            parent_device=pulseblaster_0.direct_outputs, connection='flag 19')
ClockLine(name='pulseblaster_0_ni_pci_clock',     pseudoclock=pulseblaster_0.pseudoclock, connection='flag 23')
ClockLine(name='pulseblaster_0_ni_usb_0_clock',   pseudoclock=pulseblaster_0.pseudoclock, connection='flag 21')
ClockLine(name='pulseblaster_0_ni_usb_1_clock',   pseudoclock=pulseblaster_0.pseudoclock, connection='flag 20')
ClockLine(name='pulseblaster_0_ni_usb_2_clock',   pseudoclock=pulseblaster_0.pseudoclock, connection='flag 18')
#ClockLine(name='pulseblaster_0_ni_usb_3_clock',   pseudoclock=pulseblaster_0.pseudoclock, connection='flag 19')
ClockLine(name='pulseblaster_0_novatech_0_clock', pseudoclock=pulseblaster_0.pseudoclock, connection='flag 22')
ClockLine(name='pulseblaster_0_novatech_1_clock', pseudoclock=pulseblaster_0.pseudoclock, connection='flag 2')

NI_PCI_6733(
    name='ni_pci_6733_0',
    parent_device=pulseblaster_0_ni_pci_clock,
    MAX_name='Dev1',
    clock_terminal='/Dev1/RTSI0',
)

AnalogOut(name='MOT_repump',           parent_device=ni_pci_6733_0, connection='ao0', limits=(0.0,0.9))
AnalogOut(name='Bragg_repump',                 parent_device=ni_pci_6733_0, connection='ao1', limits=(0.0,0.9))
AnalogOut(name='MOT_cooling',          parent_device=ni_pci_6733_0, connection='ao2', limits=(0.0,0.9))
AnalogOut(name='optical_pumping',     parent_device=ni_pci_6733_0, connection='ao3', limits=(0.0,0.9))
AnalogOut(name='probe_1',              parent_device=ni_pci_6733_0, connection='ao4', limits=(0.0,0.9))
AnalogOut(name='probe_2',              parent_device=ni_pci_6733_0, connection='ao5', limits=(0.0,0.9))
AnalogOut(name='dipole_intensity',    parent_device=ni_pci_6733_0, connection='ao6')
AnalogOut(name='dipole_split',         parent_device=ni_pci_6733_0, connection='ao7', limits=(0.0,1.0))

DigitalOut(name='UV_LED',               parent_device=ni_pci_6733_0, connection='port0/line0')
DigitalOut(name='Bragg_repumpTTL',                parent_device=ni_pci_6733_0, connection='port0/line1')
DigitalOut(name='grad_cancel_switch', parent_device=ni_pci_6733_0, connection='port0/line2')
DigitalOut(name='dipole_shutter',      parent_device=ni_pci_6733_0, connection='port0/line3')
DigitalOut(name='shutter_x_insitu',                parent_device=ni_pci_6733_0, connection='port0/line4')
DigitalOut(name='Bragg_shutter',                parent_device=ni_pci_6733_0, connection='port0/line5')

DigitalOut(name='FPGA_trigger',                parent_device=ni_pci_6733_0, connection='port0/line7') #disconnected on 03.20.18

NI_PCI_6733(
    name='ni_pci_6733_1',
    parent_device=pulseblaster_0_ni_pci_clock,
    MAX_name='Dev2',
    clock_terminal='/Dev2/RTSI0',
)

AnalogOut(name='RF_mixer1',               parent_device=ni_pci_6733_1, connection='ao0')
AnalogOut(name='uwave_mixer1',            parent_device=ni_pci_6733_1, connection='ao1')
AnalogOut(name='FPGA_ao',               parent_device=ni_pci_6733_1, connection='ao2') #disconnected on 03.20.18             
AnalogOut(name='RF_mixer3',               parent_device=ni_pci_6733_1, connection='ao3')
AnalogOut(name='microwave_attenuator',    parent_device=ni_pci_6733_1, connection='ao4')
AnalogOut(name='uwave_power_1',           parent_device=ni_pci_6733_1, connection='ao5')
AnalogOut(name='long_trap',           parent_device=ni_pci_6733_1, connection='ao6') #disconnected on 03.20.18
AnalogOut(name='fine_zbias',              parent_device=ni_pci_6733_1, connection='ao7',
          unit_conversion_class=BidirectionalCoilDriver, unit_conversion_parameters={'slope': kepco_servo_scaling})

Trigger(name='scope_trigger_0',           parent_device=ni_pci_6733_1, connection='port0/line0',
        trigger_edge_type='rising') 
DigitalOut(name='scope_trigger_1',        parent_device=ni_pci_6733_1, connection='port0/line1')
DigitalOut(name='RF_DDS_switch_0',        parent_device=ni_pci_6733_1, connection='port0/line2') #disconnected on 03.20.18
DigitalOut(name='RF_switch_0',            parent_device=ni_pci_6733_1, connection='port0/line3')
DigitalOut(name='uWave_DDS_sel_0',        parent_device=ni_pci_6733_1, connection='port0/line4')
DigitalOut(name='uWave_DDS_sel_1',        parent_device=ni_pci_6733_1, connection='port0/line5') #disconnected on 03.20.18
DigitalOut(name='uWave_DDS_switch_0',     parent_device=ni_pci_6733_1, connection='port0/line6') #disconnected on 03.20.18
DigitalOut(name='uWave_switch_0',         parent_device=ni_pci_6733_1, connection='port0/line7') 

# NI_USB_6343(name='ni_usb_6343_0', parent_device=pulseblaster_0_ni_usb_0_clock, clock_terminal='/Dev3/PFI0', MAX_name='Dev3')

NI_USB_6343(
    name='ni_usb_6343_0',
    parent_device=pulseblaster_0_ni_usb_0_clock,
    MAX_name='Dev3',
    clock_terminal='/Dev3/PFI0',
    acquisition_rate=1000,
    max_AO_sample_rate=1 / (5 * us),
)

AnalogOut(name='transport_current_1',     parent_device=ni_usb_6343_0, connection='ao0',
          unit_conversion_class=BidirectionalCoilDriver, unit_conversion_parameters={'slope': transport_scaling_1})
AnalogOut(name='transport_current_2',     parent_device=ni_usb_6343_0, connection='ao1',
          unit_conversion_class=BidirectionalCoilDriver, unit_conversion_parameters={'slope': transport_scaling_2})
AnalogOut(name='transport_current_3',     parent_device=ni_usb_6343_0, connection='ao2',
          unit_conversion_class=BidirectionalCoilDriver, unit_conversion_parameters={'slope': transport_scaling_3})
AnalogOut(name='transport_current_4',     parent_device=ni_usb_6343_0, connection='ao3',
          unit_conversion_class=BidirectionalCoilDriver, unit_conversion_parameters={'slope': transport_scaling_4})

#AnalogIn(name='transport_current_1_AI', parent_device=ni_usb_6343_0, connection='ai0')
# AnalogIn(name='transport_current_2_AI', parent_device=ni_usb_6343_0, connection='ai1')
# AnalogIn(name='transport_current_3_AI', parent_device=ni_usb_6343_0, connection='ai2')
# AnalogIn(name='transport_current_4_AI', parent_device=ni_usb_6343_0, connection='ai3')
          
DigitalOut(name='curent_supply_1_select_line0', parent_device=ni_usb_6343_0, connection='port0/line0')
DigitalOut(name='curent_supply_1_select_line1', parent_device=ni_usb_6343_0, connection='port0/line1')
DigitalOut(name='curent_supply_1_enable',       parent_device=ni_usb_6343_0, connection='port0/line2')

DigitalOut(name='curent_supply_2_select_line0', parent_device=ni_usb_6343_0, connection='port0/line3')
DigitalOut(name='curent_supply_2_select_line1', parent_device=ni_usb_6343_0, connection='port0/line4')
DigitalOut(name='curent_supply_2_enable',       parent_device=ni_usb_6343_0, connection='port0/line5')

DigitalOut(name='curent_supply_3_select_line0', parent_device=ni_usb_6343_0, connection='port0/line6')
DigitalOut(name='curent_supply_3_select_line1', parent_device=ni_usb_6343_0, connection='port0/line7')
DigitalOut(name='curent_supply_3_enable',       parent_device=ni_usb_6343_0, connection='port0/line8')

DigitalOut(name='curent_supply_4_select_line0', parent_device=ni_usb_6343_0, connection='port0/line9')
DigitalOut(name='curent_supply_4_select_line1', parent_device=ni_usb_6343_0, connection='port0/line10')
DigitalOut(name='curent_supply_4_enable',       parent_device=ni_usb_6343_0, connection='port0/line11')
DigitalOut(name='DO12',                         parent_device=ni_usb_6343_0, connection='port0/line12')

Trigger(name='transport_oscilloscope_trigger', parent_device=ni_usb_6343_0, connection='port0/line15')



# NI_USB_6343(name='ni_usb_6343_1', parent_device=pulseblaster_0_ni_usb_1_clock, clock_terminal='/Dev4/PFI0', MAX_name='Dev4')

NI_USB_6343(
    name='ni_usb_6343_1',
    parent_device=pulseblaster_0_ni_usb_1_clock,
    MAX_name='Dev4',
    clock_terminal='/Dev4/PFI0',
    acquisition_rate=1000,
)

AnalogOut(name='x_bias',  parent_device=ni_usb_6343_1, connection='ao0',
          unit_conversion_class=BidirectionalCoilDriver, unit_conversion_parameters={'slope': kepco_servo_scaling})
AnalogOut(name='y_bias',  parent_device=ni_usb_6343_1, connection='ao1',
          unit_conversion_class=BidirectionalCoilDriver, unit_conversion_parameters={'slope': kepco_y_scaling})
AnalogOut(name='z_bias',  parent_device=ni_usb_6343_1, connection='ao2',
          unit_conversion_class=BidirectionalCoilDriver, unit_conversion_parameters={'slope': kepco_z_scaling})
AnalogOut(name='offset',  parent_device=ni_usb_6343_1, connection='ao3')

DigitalOut(name='kepco_enable_0', parent_device=ni_usb_6343_1, connection='port0/line0')
DigitalOut(name='kepco_enable_1', parent_device=ni_usb_6343_1, connection='port0/line1')

# AnalogIn(name='top_x_kepco', parent_device=ni_usb_6343_1, connection='ai0')
# AnalogIn(name='top_y_kepco', parent_device=ni_usb_6343_1, connection='ai1')
# AnalogIn(name='top_z_kepco', parent_device=ni_usb_6343_1, connection='ai2')
# AnalogIn(name='Dev4_AI3',    parent_device=ni_usb_6343_1, connection='ai3')

# NI_USB_6343(
#     name='ni_usb_6343_2',
#     parent_device=pulseblaster_0_ni_usb_2_clock,
#     MAX_name='DevTiSapp',
#     clock_terminal='/DevTiSapp/PFI0',
#     acquisition_rate=1000,
# )

# AnalogOut(name='mixer_raman_1',     parent_device=ni_usb_6343_2, connection='ao0')
# AnalogOut(name='mixer_raman_2',     parent_device=ni_usb_6343_2, connection='ao1')
# AnalogOut(name='Bragg_probe',      parent_device=ni_usb_6343_2, connection='ao2')
# AnalogOut(name='AOM_green_beam',  parent_device=ni_usb_6343_2, connection='ao3')

# DigitalOut(name='raman_1', parent_device=ni_usb_6343_2, connection='port0/line0')
# DigitalOut(name='raman_2', parent_device=ni_usb_6343_2, connection='port0/line1')
# DigitalOut(name='green_beam', parent_device=ni_usb_6343_2, connection='port0/line2')
# DigitalOut(name='shutter_raman1', parent_device=ni_usb_6343_2, connection='port0/line3')
# DigitalOut(name='shutter_raman2', parent_device=ni_usb_6343_2, connection='port0/line4')
# DigitalOut(name='shutter_greenbeam', parent_device=ni_usb_6343_2, connection='port0/line5')
# DigitalOut(name='green_servo_trigger', parent_device=ni_usb_6343_2, connection = 'port0/line6')
# DigitalOut(name='andor_ccd_trigger',   parent_device=ni_usb_6343_2, connection = 'port0/line7')
# DigitalOut(name='long_trap_switch',     parent_device=ni_usb_6343_2, connection = 'port0/line8')
# DigitalOut(name='DO_9',     parent_device=ni_usb_6343_2, connection = 'port0/line9')

#NI_USB_6002(name='ni_usb_6002_0', parent_device=pulseblaster_0_ni_usb_3_clock, clock_terminal='/Dev6/PFI0', MAX_name='Dev6')

# NI_DAQmx(name='ni_usb_6002_0', parent_device=pulseblaster_0_ni_usb_3_clock,
        # MAX_name='Dev6',
        # clock_terminal='/Dev6/PFI0', 
        # num_AO=2,
        # sample_rate_AO=5000,
        # static_AO=True,
        # num_DO=8,
        # sample_rate_DO=1000,
        # static_DO=False,
        # num_AI=4,
        # clock_terminal_AI='/Dev6/PFI0',
        # mode_AI='labscript', # 'labscript', 'gated', 'triggered'
        # sample_rate_AI=50000, 
        # num_PFI=0
# )

# StaticAnalogOut(name='AO0',     parent_device=ni_usb_6002_0, connection='ao0')
# StaticAnalogOut(name='AO1',     parent_device=ni_usb_6002_0, connection='ao1')

# StaticDigitalOut(name='DO6_0',  parent_device=ni_usb_6002_0, connection='port0/line0')
# StaticDigitalOut(name='DO6_1',  parent_device=ni_usb_6002_0, connection='port0/line1')
# StaticDigitalOut(name='DO6_2',  parent_device=ni_usb_6002_0, connection='port0/line2')
# StaticDigitalOut(name='DO6_3',  parent_device=ni_usb_6002_0, connection='port0/line3')
# StaticDigitalOut(name='DO6_4',  parent_device=ni_usb_6002_0, connection='port0/line4')
# StaticDigitalOut(name='DO6_5',  parent_device=ni_usb_6002_0, connection='port0/line5')
# StaticDigitalOut(name='DO6_6',  parent_device=ni_usb_6002_0, connection='port0/line6')
# StaticDigitalOut(name='DO6_7',  parent_device=ni_usb_6002_0, connection='port0/line7')

# AnalogIn(name='Dev6_AI0', parent_device=ni_usb_6002_0, connection='ai0')
# AnalogIn(name='Dev6_AI1', parent_device=ni_usb_6002_0, connection='ai1')

# Novatechs DDS

NovaTechDDS9M(name='novatechdds9m_0', 
                parent_device=pulseblaster_0_novatech_0_clock, 
                com_port='com9',
                baud_rate=57600, # 19200 or 57600
                default_baud_rate=19200, 
                update_mode='asynchronous', 
                phase_mode='continuous')

DDS(name='MOT_lock',            parent_device=novatechdds9m_0, connection='channel 0')
DDS(name='AOM_Raman_1',         parent_device=novatechdds9m_0, connection='channel 1')
StaticDDS(name='AOM_Raman_2',   parent_device=novatechdds9m_0, connection='channel 2')
StaticDDS(name='Nov_0_3',       parent_device=novatechdds9m_0, connection='channel 3')

NovaTechDDS9M(name='novatechdds9m_1',
                parent_device=pulseblaster_0_novatech_1_clock, 
                com_port='com7',
                baud_rate=57600, # 19200 or 57600
                default_baud_rate=19200, 
                update_mode='asynchronous')

DDS(name='RF_evap',         parent_device=novatechdds9m_1, connection='channel 0')
DDS(name='uwave1',          parent_device=novatechdds9m_1, connection='channel 1')
StaticDDS(name='Bragg_repumpFreq',       parent_device=novatechdds9m_1, connection='channel 2')
StaticDDS(name='Bragg_probeFreq',    parent_device=novatechdds9m_1, connection='channel 3')

# Wait Monitors
DigitalOut(name='dummy_wait_monitor', parent_device=ni_pci_6733_0, connection='port0/line6')
# WaitMonitor(
#     name='wait_monitor',
#     parent_device=ni_pci_6733_0,
#     connection='port0/line6',
#     acquisition_device=ni_pci_6733_0,
#     acquisition_connection='Ctr0',
#     # timeout_device=ni_usb_6343_0,
#     # timeout_connection='port1/line2',
# )

# Cameras

#Camera(name='XY_1_Flea3', parent_device=camera_trigger_1, connection='trigger', BIAS_port=1024, 
#         serial_number=0x00B09D0100AC001B, SDK='IMAQdx_Flea3_Firewire', effective_pixel_size=5.9e-6, exposuretime=10e-3, 
#         orientation = 'xy', trigger_edge_type='falling')
        
# Camera(name='XY_2_Flea3', parent_device=camera_trigger_1, connection='trigger', BIAS_port=1025, 
        # serial_number=0x00B09D0100AC001C, SDK='IMAQdx_Flea3_Firewire', effective_pixel_size=5.9e-6, exposuretime=10e-3, 
        # orientation = 'xy')
        
# Camera(name='XY_3_Flea3', parent_device=camera_trigger_1, connection='trigger', BIAS_port=1026, 
        # serial_number=0x00B09D0100AC001D, SDK='IMAQdx_Flea3_Firewire', effective_pixel_size=5.9e-6, exposuretime=10e-3, 
        # orientation = 'xy')
        
# Setup for 12 bit images acquired as U16
IMAQdx_properties = [
["CameraAttributes::Sharpness::Mode", "Off"],
["CameraAttributes::Gamma::Mode", "Off"],
["CameraAttributes::FrameRate::Mode", "Auto"],
["CameraAttributes::Brightness::Mode", "Absolute"],
["CameraAttributes::Brightness::Value", "2.0"],
["CameraAttributes::AutoExposure::Mode", "Off"],
["CameraAttributes::TriggerDelay::Mode", "Off"],
["CameraAttributes::Trigger::TriggerActivation", "Level Low"], # 0 for enum
["CameraAttributes::Trigger::TriggerMode", "Mode 1"], # 1 for enum, Bulb Mode
["CameraAttributes::Trigger::TriggerSource", "Source 0"],
["CameraAttributes::Trigger::TriggerParameter", "0"],
["CameraAttributes::Shutter::Mode", "Absolute"], 
["CameraAttributes::Shutter::Value", "10e-3"], 
["CameraAttributes::Gain::Mode", "Absolute"], # Must be before Gain::Value
["CameraAttributes::Gain::Value", "0"],
["AcquisitionAttributes::Timeout", "120000"],
["AcquisitionAttributes::Speed", "400 Mbps"], # 2 for enum, options 100,200,400,800
["AcquisitionAttributes::VideoMode", "Format 7, Mode 0, 648 x 488"], # 13
["AcquisitionAttributes::Width", "648"],
["AcquisitionAttributes::Height", "488"],
#["AcquisitionAttributes::VideoMode", "Format 7, Mode 1, 324 x 244"], # 14
#["AcquisitionAttributes::Width", "324"],
#["AcquisitionAttributes::Height", "244"],
["AcquisitionAttributes::ShiftPixelBits", "true"],
["AcquisitionAttributes::SwapPixelBytes", "false"],
["AcquisitionAttributes::BitsPerPixel", "12-bit"],
["AcquisitionAttributes::PixelFormat", "Mono 16"] # Needs to be near the end for some reason
]

# IMAQdx_properties2 = IMAQdx_properties2.copy()

# Could not find "PixelSignedness" which wants to be "Unsigned", 0 for enum

# Video Modes:
# 0-6: Mono 8, 640x480, 1.88 to 120 fps
# 7-12: Mono 16, 640x480, 1.88 to 60 fps
# *9: 7.5 fps (max at 100 Mbps) (don't set PixelFormat for this)
# *13: Format 7, Mode 0, 648 x 488
# 14: Format 7, Mode 1, 324 x 244
# 15: Format 7, Mode 7, 648 x 488

# These modes can be "discovered" with Enumate Video Modes.vi.
# The stared "*" ones above work best for our purposes.


RemoteBLACS('imaging_computer', '129.6.128.90')

MOT_camera_imaqdx_attributes = {
    "CameraAttributes::Sharpness::Mode": "Off",
    "CameraAttributes::Gamma::Mode": "Off",
    "CameraAttributes::FrameRate::Mode": "Auto",
    "CameraAttributes::Brightness::Mode": "Absolute",
    "CameraAttributes::Brightness::Value": 2.0,
    "CameraAttributes::AutoExposure::Mode": "Off",
    "CameraAttributes::TriggerDelay::Mode": "Off",
    "CameraAttributes::Trigger::TriggerActivation": "Level Low",  # 0 for enum
    "CameraAttributes::Trigger::TriggerMode": "Mode 1",  # 1 for enum, Bulb Mode
    "CameraAttributes::Trigger::TriggerSource": "Source 0",
    "CameraAttributes::Trigger::TriggerParameter": 0,
    # "CameraAttributes::Shutter::Mode": "Absolute",
    # "CameraAttributes::Shutter::Value": 10e-3,
    "CameraAttributes::Gain::Mode": "Absolute",  # Must be before Gain::Value
    "CameraAttributes::Gain::Value": 0,
    "AcquisitionAttributes::Timeout": 120000,
    "AcquisitionAttributes::Speed": "400 Mbps",  # 2 for enum, options 100,200,400,800
    "AcquisitionAttributes::VideoMode": "Format 7, Mode 0, 648 x 488",  # 13
    "AcquisitionAttributes::Width": 648,
    "AcquisitionAttributes::Height": 488,
    "AcquisitionAttributes::ShiftPixelBits": True,
    "AcquisitionAttributes::SwapPixelBytes": False,
    "AcquisitionAttributes::BitsPerPixel": "12-bit",
    "AcquisitionAttributes::PixelFormat": "Mono 16",  # Needs to be near the end for some reason
}

manual_mode_imaqdx_attributes = {"CameraAttributes::Trigger::TriggerMode": "Off"}

#'z_TOF' camera
IMAQdxCamera(name='XY_1_Flea3', 
    parent_device=camera_trigger_0, #For focusing in IP1 using the in-situ trigger line 2019/05/09
    #parent_device=camera_trigger_1, #on 2019/06/06 
    connection='trigger', 
    trigger_edge_type='falling',
    orientation = 'xy', 
    trigger_duration=100e-6,
    serial_number=0x00B09D0100AC001B, 
    camera_attributes=MOT_camera_imaqdx_attributes,
    manual_mode_camera_attributes=manual_mode_imaqdx_attributes,
    stop_acquisition_timeout=10,
    exception_on_failed_shot=False,
    worker=imaging_computer)
 
#'z_insitu' camera 
# IMAQdxCamera(name='XY_2_Flea3', 
#     parent_device=camera_trigger_0, 
#     connection='trigger', 
#     trigger_edge_type='falling',
#     orientation = 'xy', 
#     trigger_duration=100e-6,
#     serial_number=0x00B09D0100AB1223, 
#     imaqdx_attributes=MOT_camera_imaqdx_attributes,
#     manual_mode_imaqdx_attributes=manual_mode_imaqdx_attributes,
#     worker=imaging_computer)  

#'x_insitu' camera
IMAQdxCamera(name='YZ_1_Flea3', 
    parent_device=camera_trigger_3, 
    connection='trigger', 
    trigger_edge_type='falling',
    orientation = 'yz', 
    trigger_duration=100e-6,
    serial_number=0x00B09D01009014EF, 
    camera_attributes=MOT_camera_imaqdx_attributes,
    manual_mode_camera_attributes=manual_mode_imaqdx_attributes,
    stop_acquisition_timeout=10,
        exception_on_failed_shot=False,
    worker=imaging_computer)  

IMAQdxCamera(name='MOT_camera', 
    parent_device=camera_trigger_2, 
    connection='trigger', 
    trigger_edge_type='falling',
    orientation = 'yz', 
    trigger_duration=100e-6,
    serial_number=0x00B09D01009E7111, 
    camera_attributes=MOT_camera_imaqdx_attributes,
    manual_mode_camera_attributes=manual_mode_imaqdx_attributes,
    stop_acquisition_timeout=10,
    exception_on_failed_shot=False,
    worker=imaging_computer)    

# andor_attributes = {}

# AndorSolis(name='pricey_but_dicey', 
#     parent_device=camera_trigger_0, 
#     connection='trigger', 
#     trigger_edge_type='falling',
#     orientation = 'yz', 
#     trigger_duration=100e-6,
#     serial_number=0xBADBEEDAD, 
#     camera_attributes=andor_attributes,
#     manual_mode_camera_attributes=andor_attributes,
#     exception_on_failed_shot=False,
#     worker=imaging_computer)

#TekScope(name='MOT_scope', addr='USB0::0x0699::0x03A4::C043076::INSTR', preamble_string='WFMP')
#TekScope(name='RF_and_locks_scope', addr='USB0::0x0699::0x0368::C102732::INSTR', preamble_string='WFMP')

# NewFocusPicomotor8742(name='tester', host='169.254.34.178', port=23)

# Picomotor(name='test_motor_X', parent_device=tester, connection=1)
# Picomotor(name='test_motor_Y', parent_device=tester, connection=2)
# Picomotor(name='axis_3', parent_device=tester, connection=3)
# Picomotor(name='axis_4', parent_device=tester, connection=4)

#ChipFPGA
#ChipFPGA(name='chipfpga', parent_device=pulseblaster_0_ni_pci_clock, visa_resource="ASRL14::INSTR") 
          
class ServoOutputSelect(object):
    """Object to abstract the output selection on one of the current servos"""
    def __init__(self, line0, line1):
        # Line 0 is most significant bit, line 1 is least significant bit.
        self.line0 = line0
        self.line1 = line1
        
    def __call__(self, t, number):
        """Given an output number from 0 - 3,
        sets the two output lines with the corresponding binary number"""
        bits = bin(number)[2:]
        if int(bits[0]):
            line0.go_high(t)
        else:
            line0.go_low(t)
        if int(bits[1]):
            line1.go_high(t)
        else:
            line1.go_low(t)
            
# convenience functions for selecting servo outputs:
# servo_1_select_output = ServoOutputSelect(curent_supply_1_select_line0, curent_supply_1_select_line1)
# servo_2_select_output = ServoOutputSelect(curent_supply_2_select_line0, curent_supply_2_select_line1)
# servo_3_select_output = ServoOutputSelect(curent_supply_3_select_line0, curent_supply_3_select_line1)
# servo_4_select_output = ServoOutputSelect(curent_supply_4_select_line0, curent_supply_4_select_line1)


if __name__ == '__main__':
    # Only compile if we are in a connection table compilation. Otherwise,
    # do not compile. That way, this script can be imported by other experiment scripts.
    start()
    stop(1)