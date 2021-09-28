# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 08:18:53 2020

@author: rubidium
"""

import labscript as ls
import labscript_utils as lsu

ls.config.suppress_mild_warnings = True
ls.compiler.save_hg_info = False

from labscript_devices.PulseBlasterUSB import PulseBlasterUSB
from labscript_devices.NI_DAQmx.labscript_devices import NI_PCI_6733, NI_USB_6229, NI_USB_6343
from labscript_devices.NovaTechDDS9M import NovaTechDDS9M
from labscript_devices.IMAQdxCamera.labscript_devices import IMAQdxCamera

from labscript_utils.unitconversions import IntraAction

###############################################################################
#
# Pulse Blaster
#
###############################################################################

PulseBlasterUSB('pb0', board_number=0, programming_scheme='pb_stop_programming/STOP')

ls.DigitalOut(name="D2_Lock_DO", parent_device=pb0.direct_outputs, connection='flag 0')
ls.DigitalOut(name="pb0_01", parent_device=pb0.direct_outputs, connection='flag 1')
ls.DigitalOut(name="pb0_02", parent_device=pb0.direct_outputs, connection='flag 2')
ls.DigitalOut(name="pb0_03", parent_device=pb0.direct_outputs, connection='flag 3')
ls.DigitalOut(name="pb0_04", parent_device=pb0.direct_outputs, connection='flag 4')
ls.DigitalOut(name="pb0_05", parent_device=pb0.direct_outputs, connection='flag 5')
ls.DigitalOut(name="pb0_06", parent_device=pb0.direct_outputs, connection='flag 6')
ls.DigitalOut(name="pb0_07", parent_device=pb0.direct_outputs, connection='flag 7')
ls.DigitalOut(name="pb0_08", parent_device=pb0.direct_outputs, connection='flag 8')
ls.DigitalOut(name="pb0_09", parent_device=pb0.direct_outputs, connection='flag 9')
ls.DigitalOut(name="pb0_10", parent_device=pb0.direct_outputs, connection='flag 10')
ls.DigitalOut(name="pb0_11", parent_device=pb0.direct_outputs, connection='flag 11')
ls.DigitalOut(name="pb0_12", parent_device=pb0.direct_outputs, connection='flag 12') 
ls.DigitalOut(name="pb0_13", parent_device=pb0.direct_outputs, connection='flag 13')
ls.DigitalOut(name="pb0_14", parent_device=pb0.direct_outputs, connection='flag 14')
ls.DigitalOut(name="pb0_15", parent_device=pb0.direct_outputs, connection='flag 15')
ls.DigitalOut(name="pb0_16", parent_device=pb0.direct_outputs, connection='flag 16')
ls.DigitalOut(name="pb0_17", parent_device=pb0.direct_outputs, connection='flag 17')
ls.DigitalOut(name="pb0_18", parent_device=pb0.direct_outputs, connection='flag 18')
ls.DigitalOut(name="pb0_19", parent_device=pb0.direct_outputs, connection='flag 19')
ls.ClockLine(name="pb0_NI_PCI", pseudoclock=pb0.pseudoclock, connection='flag 20')
ls.ClockLine(name="pb0_nt1", pseudoclock=pb0.pseudoclock, connection='flag 21')

# Didn't seem to work?
ls.DigitalOut(name="pb0_22", parent_device=pb0.direct_outputs, connection='flag 22')
ls.DigitalOut(name='pb0_23', parent_device=pb0.direct_outputs, connection='flag 23')

###############################################################################
#
# NI Devices
#
###############################################################################

NI_PCI_6733(
    name="NI_PCI_01", 
    parent_device=pb0_NI_PCI,
    MAX_name='PCI_01',
    clock_terminal='/PCI_01/PFI0',
)

ls.AnalogOut(name='ni_pci_01_ao0', parent_device=NI_PCI_01, connection='ao0')
ls.AnalogOut(name='ni_pci_01_ao1', parent_device=NI_PCI_01, connection='ao1')
ls.AnalogOut(name='ni_pci_01_ao2', parent_device=NI_PCI_01, connection='ao2')
ls.AnalogOut(name='ni_pci_01_ao3', parent_device=NI_PCI_01, connection='ao3')
ls.AnalogOut(name='ni_pci_01_ao4', parent_device=NI_PCI_01, connection='ao4')
ls.AnalogOut(name='ni_pci_01_ao5', parent_device=NI_PCI_01, connection='ao5')
ls.AnalogOut(name='ni_pci_01_ao6', parent_device=NI_PCI_01, connection='ao6')
ls.AnalogOut(name='ni_pci_01_ao7', parent_device=NI_PCI_01, connection='ao7')


ls.DigitalOut(name='ScopeTrigger', parent_device=NI_PCI_01, connection='port0/line0')
ls.DigitalOut(name='UV_DO', parent_device=NI_PCI_01, connection='port0/line1')
ls.DigitalOut(name='ni_pci_01_do2', parent_device=NI_PCI_01, connection='port0/line2')
ls.DigitalOut(name='ni_pci_01_do3', parent_device=NI_PCI_01, connection='port0/line3')
ls.DigitalOut(name='ni_pci_01_do4', parent_device=NI_PCI_01, connection='port0/line4')
ls.DigitalOut(name='ni_pci_01_do5', parent_device=NI_PCI_01, connection='port0/line5')
ls.DigitalOut(name='ni_pci_01_do6', parent_device=NI_PCI_01, connection='port0/line6')
ls.Trigger(name='MOT_Camera_Trigger', parent_device=NI_PCI_01, connection='port0/line7')

NI_PCI_6733(
    name="NI_PCI_02", 
    parent_device=pb0_NI_PCI,
    MAX_name='PCI_02',
    clock_terminal='/PCI_02/PFI0',
)

ls.AnalogOut(name='D2_Repump_AO', parent_device=NI_PCI_02, connection='ao0')
ls.AnalogOut(name='D2_Repump_FM', parent_device=NI_PCI_02, connection='ao1', 
             unit_conversion_class=IntraAction.IntraAction_FM, 
             unit_conversion_parameters={'f_0': 80.23, 'MHz_per_V': 30.49}
             )
ls.AnalogOut(name='D2_Cooling_AO', parent_device=NI_PCI_02, connection='ao2')
ls.AnalogOut(name='D2_Probe_OP_AO', parent_device=NI_PCI_02, connection='ao3')
ls.AnalogOut(name='ni_pci_02_ao4', parent_device=NI_PCI_02, connection='ao4')
ls.AnalogOut(name='ni_pci_02_ao5', parent_device=NI_PCI_02, connection='ao5')
ls.AnalogOut(name='ni_pci_02_ao6', parent_device=NI_PCI_02, connection='ao6')
ls.AnalogOut(name='ni_pci_02_ao7', parent_device=NI_PCI_02, connection='ao7')

ls.DigitalOut(name='D2_Repump_DO', parent_device=NI_PCI_02, connection='port0/line0')
ls.DigitalOut(name='D2_Repump_Sh', parent_device=NI_PCI_02, connection='port0/line1')
ls.DigitalOut(name='D2_Cooling_DO', parent_device=NI_PCI_02, connection='port0/line2')
ls.DigitalOut(name='D2_Cooling_Sh', parent_device=NI_PCI_02, connection='port0/line3')
ls.DigitalOut(name='D2_Probe_OP_DO', parent_device=NI_PCI_02, connection='port0/line4')
ls.DigitalOut(name='D2_Probe_1_Sh', parent_device=NI_PCI_02, connection='port0/line5')
ls.DigitalOut(name='D2_Probe_2_Sh', parent_device=NI_PCI_02, connection='port0/line6')
ls.DigitalOut(name='D2_OP_Sh', parent_device=NI_PCI_02, connection='port0/line7')

NI_USB_6229(
    name="NI_USB_01", 
    parent_device=pb0_NI_PCI,
    MAX_name='USB_01',
    clock_terminal='/USB_01/PFI0',
)

ls.AnalogOut(name='Power_AMP_CNTRL_Line_CH1', parent_device=NI_USB_01, connection='ao0')
ls.AnalogOut(name='Power_AMP_CNTRL_Line_CH2', parent_device=NI_USB_01, connection='ao1')
ls.AnalogOut(name='Power_AMP_CNTRL_Line_CH3', parent_device=NI_USB_01, connection='ao2')
ls.AnalogOut(name='Power_AMP_CNTRL_Line_CH4', parent_device=NI_USB_01, connection='ao3')

ls.DigitalOut(name='Power_AMP_DIS_Line_CH1', parent_device=NI_USB_01, connection='port0/line0')
ls.DigitalOut(name='Power_AMP_DIS_Line_CH2', parent_device=NI_USB_01, connection='port0/line1')
ls.DigitalOut(name='Power_AMP_DIS_Line_CH3', parent_device=NI_USB_01, connection='port0/line2')
ls.DigitalOut(name='Power_AMP_DIS_Line_CH4', parent_device=NI_USB_01, connection='port0/line3')

###############################################################################
#
# Novatechs
#
###############################################################################

NovaTechDDS9M(name='nt_1',
                parent_device=pb0_nt1,
                com_port='com6',
                baud_rate=115200,
                default_baud_rate=19200,
                phase_mode='aligned', # continuous
                update_mode='synchronous', # asynchronous
                synchronous_first_line_repeat=False # True
                )

ls.DDS(name='D2_Lock_DDS', parent_device=nt_1, connection='channel 0')
ls.DDS(name='nt1_1', parent_device=nt_1, connection='channel 1')
ls.StaticDDS(name='nt1_2', parent_device=nt_1, connection='channel 2')
ls.StaticDDS(name='nt1_3', parent_device=nt_1, connection='channel 3')

###############################################################################
#
# Cameras
#
###############################################################################

###############################################################################
#
# Cameras
#
###############################################################################

Basler_camera_imaqdx_attributes = {
    'AcquisitionAttributes::AdvancedEthernet::Controller::DestinationMode': 'Unicast',
    'AcquisitionAttributes::AdvancedEthernet::Controller::DestinationMulticastAddress': '239.192.0.1',
    'AcquisitionAttributes::AdvancedEthernet::EventParameters::MaxOutstandingEvents': 50,
    'AcquisitionAttributes::AdvancedGenicam::EventsEnabled': 1,
    'AcquisitionAttributes::Bayer::Algorithm': 'Bilinear',
    'AcquisitionAttributes::Bayer::GainB': 1.0,
    'AcquisitionAttributes::Bayer::GainG': 1.0,
    'AcquisitionAttributes::Bayer::GainR': 1.0,
    'AcquisitionAttributes::Bayer::Pattern': 'Use hardware value',
    'AcquisitionAttributes::IncompleteBufferMode': 'Ignore',
    'AcquisitionAttributes::OutputImageType': 'Auto',
    'AcquisitionAttributes::PacketSize': 1500,
    'AcquisitionAttributes::Timeout': 5000,
    'CameraAttributes::AOI::BinningHorizontal': 1,
    'CameraAttributes::AOI::BinningVertical': 1,
    'CameraAttributes::AOI::CenterX': 0,
    'CameraAttributes::AOI::CenterY': 0,
    'CameraAttributes::AOI::Height': 494,
    'CameraAttributes::AOI::OffsetX': 0,
    'CameraAttributes::AOI::OffsetY': 0,
    'CameraAttributes::AOI::Width': 659,
    'CameraAttributes::AcquisitionTrigger::AcquisitionFrameCount': 1,
    'CameraAttributes::AcquisitionTrigger::AcquisitionFrameRateAbs': 59.99880002399952,
    'CameraAttributes::AcquisitionTrigger::AcquisitionFrameRateEnable': 0,
    'CameraAttributes::AcquisitionTrigger::AcquisitionMode': 'Continuous',
    'CameraAttributes::AcquisitionTrigger::ExposureAuto': 'Off',
    'CameraAttributes::AcquisitionTrigger::ExposureMode': 'Trigger Width',
    'CameraAttributes::AcquisitionTrigger::TriggerActivation': 'Rising Edge',
    'CameraAttributes::AcquisitionTrigger::TriggerMode': 'On',
    'CameraAttributes::AcquisitionTrigger::TriggerSelector': 'Frame Start',
    'CameraAttributes::AcquisitionTrigger::TriggerSource': 'Line 1',
    'CameraAttributes::AnalogControls::BlackLevelRaw': 400,
    'CameraAttributes::AnalogControls::BlackLevelSelector': 'All',
    'CameraAttributes::AnalogControls::DigitalShift': 0,
    'CameraAttributes::AnalogControls::GainAuto': 'Off',
    'CameraAttributes::AnalogControls::GainRaw': 300,
    'CameraAttributes::AnalogControls::GainSelector': 'All',
    'CameraAttributes::AnalogControls::Gamma': 1.0,
    'CameraAttributes::AnalogControls::GammaEnable': 0,
    'CameraAttributes::AnalogControls::GammaSelector': 'User',
    'CameraAttributes::AutoFunctions::AutoExposureTimeAbsLowerLimit': 100.0,
    'CameraAttributes::AutoFunctions::AutoExposureTimeAbsUpperLimit': 1000000.0,
    'CameraAttributes::AutoFunctions::AutoFunctionAOIs::AutoFunctionAOIHeight': 494,
    'CameraAttributes::AutoFunctions::AutoFunctionAOIs::AutoFunctionAOIOffsetX': 0,
    'CameraAttributes::AutoFunctions::AutoFunctionAOIs::AutoFunctionAOIOffsetY': 0,
    'CameraAttributes::AutoFunctions::AutoFunctionAOIs::AutoFunctionAOISelector': 'AOI 1',
    'CameraAttributes::AutoFunctions::AutoFunctionAOIs::AutoFunctionAOIUsageIntensity': 1,
    'CameraAttributes::AutoFunctions::AutoFunctionAOIs::AutoFunctionAOIUsageWhiteBalance': 0,
    'CameraAttributes::AutoFunctions::AutoFunctionAOIs::AutoFunctionAOIWidth': 659,
    'CameraAttributes::AutoFunctions::AutoFunctionProfile': 'Gain at minimum',
    'CameraAttributes::AutoFunctions::AutoGainRawLowerLimit': 300,
    'CameraAttributes::AutoFunctions::AutoGainRawUpperLimit': 600,
    'CameraAttributes::AutoFunctions::AutoTargetValue': 2048,
    'CameraAttributes::ChunkDataStreams::ChunkModeActive': 0,
    'CameraAttributes::DeviceInformation::DeviceUserID': 'Basler',
    'CameraAttributes::DigitalIO::LineFormat': 'Opto-coupled',
    'CameraAttributes::DigitalIO::LineInverter': 0,
    'CameraAttributes::DigitalIO::LineMode': 'Output',
    'CameraAttributes::DigitalIO::LineSelector': 'Output Line 1',
    'CameraAttributes::DigitalIO::LineSource': 'User Output',
    'CameraAttributes::DigitalIO::UserOutputSelector': 'User Settable Output 1',
    'CameraAttributes::DigitalIO::UserOutputValue': 0,
    'CameraAttributes::DigitalIO::UserOutputValueAll': 0,
    'CameraAttributes::EventsGeneration::EventNotification': 'Notification Off',
    'CameraAttributes::EventsGeneration::EventSelector': 'Exposure End',
    'CameraAttributes::ImageFormat::PixelFormat': 'Mono 12 Packed',
    'CameraAttributes::ImageFormat::ReverseX': 0,
    'CameraAttributes::ImageFormat::TestImageSelector': 'Test Image Off',
    'CameraAttributes::LUTControls::LUTEnable': 0,
    'CameraAttributes::LUTControls::LUTIndex': 0,
    'CameraAttributes::LUTControls::LUTSelector': 'Luminance LUT',
    'CameraAttributes::LUTControls::LUTValue': 0,
    'CameraAttributes::TimerControls::TimerDelayAbs': 0.0,
    'CameraAttributes::TimerControls::TimerDelayRaw': 0,
    'CameraAttributes::TimerControls::TimerDelayTimebaseAbs': 1.0,
    'CameraAttributes::TimerControls::TimerDurationAbs': 4095.0,
    'CameraAttributes::TimerControls::TimerDurationRaw': 4095,
    'CameraAttributes::TimerControls::TimerDurationTimebaseAbs': 1.0,
    'CameraAttributes::TimerControls::TimerSelector': 'Timer 1',
    'CameraAttributes::TimerControls::TimerTriggerActivation': 'Rising Edge',
    'CameraAttributes::TimerControls::TimerTriggerSource': 'Exposure Active',
    'CameraAttributes::UserSets::DefaultSetSelector': 'Standard',
    'CameraAttributes::UserSets::UserSetSelector': 'Default Configuration Set',
}

Basler_manual_mode_imaqdx_attributes = {
    'CameraAttributes::AcquisitionTrigger::AcquisitionMode': 'Continuous',
    'CameraAttributes::AcquisitionTrigger::TriggerMode': 'Off',
    'CameraAttributes::AcquisitionTrigger::ExposureMode': 'Timed',
#    'CameraAttributes::AcquisitionTrigger::ExposeTimeRaw': 8000,
    }

#'MOT_x' camera
IMAQdxCamera(name='MOT_x', 
    parent_device=MOT_Camera_Trigger,
    connection='trigger', 
    trigger_edge_type='rising',
    orientation = 'MOT_x', 
    serial_number=0x3053162459, 
    camera_attributes=Basler_camera_imaqdx_attributes,
    manual_mode_camera_attributes=Basler_manual_mode_imaqdx_attributes,
    stop_acquisition_timeout=10,
    exception_on_failed_shot=False)

if __name__ == '__main__':
    # Begin issuing labscript primitives
    # start() elicits the commencement of the shot
    ls.start()

    # Stop the experiment shot with stop()
    ls.stop(1.0)