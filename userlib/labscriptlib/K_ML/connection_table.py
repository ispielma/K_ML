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
from labscript_devices.TekScope.labscript_devices import TekScope
from user_devices.Arduino_Interlock.labscript_user_devices import Arduino_Interlock

import pythonlib.IntraAction as IntraAction
import pythonlib.CurrentSupply as CurrentSupply

###############################################################################
#
# Pulse Blaster
#
###############################################################################

PulseBlasterUSB('PB0', board_number=0, programming_scheme='pb_stop_programming/STOP')

ls.DigitalOut(name="D2_Lock_DO", parent_device=PB0.direct_outputs, connection='flag 0')
ls.DigitalOut(name="pb0_01", parent_device=PB0.direct_outputs, connection='flag 1')
ls.DigitalOut(name="pb0_02", parent_device=PB0.direct_outputs, connection='flag 2')
ls.DigitalOut(name="pb0_03", parent_device=PB0.direct_outputs, connection='flag 3')
ls.DigitalOut(name="pb0_04", parent_device=PB0.direct_outputs, connection='flag 4')
ls.DigitalOut(name="pb0_05", parent_device=PB0.direct_outputs, connection='flag 5')
ls.DigitalOut(name="pb0_06", parent_device=PB0.direct_outputs, connection='flag 6')
ls.DigitalOut(name="pb0_07", parent_device=PB0.direct_outputs, connection='flag 7')
ls.DigitalOut(name="pb0_08", parent_device=PB0.direct_outputs, connection='flag 8')
ls.DigitalOut(name="pb0_09", parent_device=PB0.direct_outputs, connection='flag 9')
ls.DigitalOut(name="pb0_10", parent_device=PB0.direct_outputs, connection='flag 10')
ls.DigitalOut(name="pb0_11", parent_device=PB0.direct_outputs, connection='flag 11')
ls.DigitalOut(name="pb0_12", parent_device=PB0.direct_outputs, connection='flag 12')
ls.DigitalOut(name="pb0_13", parent_device=PB0.direct_outputs, connection='flag 13')
ls.DigitalOut(name="pb0_14", parent_device=PB0.direct_outputs, connection='flag 14')
ls.DigitalOut(name="pb0_15", parent_device=PB0.direct_outputs, connection='flag 15')
ls.DigitalOut(name="pb0_16", parent_device=PB0.direct_outputs, connection='flag 16')
ls.DigitalOut(name="pb0_17", parent_device=PB0.direct_outputs, connection='flag 17')
ls.DigitalOut(name="pb0_18", parent_device=PB0.direct_outputs, connection='flag 18')

ls.ClockLine(name="pb0_NI_USB", pseudoclock=PB0.pseudoclock, connection='flag 19')
ls.ClockLine(name="pb0_NI_PCI", pseudoclock=PB0.pseudoclock, connection='flag 20')
ls.ClockLine(name="pb0_nt1", pseudoclock=PB0.pseudoclock, connection='flag 21')

# Didn't seem to work?
ls.DigitalOut(name="pb0_22", parent_device=PB0.direct_outputs, connection='flag 22')
ls.DigitalOut(name='pb0_23', parent_device=PB0.direct_outputs, connection='flag 23')

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


ls.Trigger(name='ScopeTrigger', parent_device=NI_PCI_01, connection='port0/line0', 
           trigger_edge_type='rising')
ls.DigitalOut(name='UV_DO', parent_device=NI_PCI_01, connection='port0/line1')
ls.DigitalOut(name='ni_pci_01_do2', parent_device=NI_PCI_01, connection='port0/line2')
ls.DigitalOut(name='ni_pci_01_do3', parent_device=NI_PCI_01, connection='port0/line3')

ls.Trigger(name='MOT_Camera_Trigger', parent_device=NI_PCI_01, connection='port0/line4')
ls.Trigger(name='MOT_z_Camera_Trigger', parent_device=NI_PCI_01, connection='port0/line5')
ls.Trigger(name='MOT_x_Camera_Trigger', parent_device=NI_PCI_01, connection='port0/line6')
ls.Trigger(name='MOT_y_Camera_Trigger', parent_device=NI_PCI_01, connection='port0/line7')

NI_PCI_6733(
    name="NI_PCI_02",
    parent_device=pb0_NI_PCI,
    MAX_name='PCI_02',
    clock_terminal='/PCI_02/PFI0',
)

ls.AnalogOut(name='D2_Repump_AO', parent_device=NI_PCI_02, connection='ao0')
ls.AnalogOut(name='D2_Repump_FM', parent_device=NI_PCI_02, connection='ao1',
             unit_conversion_class=IntraAction.IntraAction_FM,
             unit_conversion_parameters={'f_0': D2_Repump_FM_UC_f0, 
                                         'MHz_per_V': D2_Repump_FM_UC_MHz_per_V}
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
    parent_device=pb0_NI_USB,
    MAX_name='USB_01',
    clock_terminal='/USB_01/PFI0',
)

ls.AnalogOut(name='MOT_y_Bias', parent_device=NI_USB_01, connection='ao0',
             unit_conversion_class=CurrentSupply.CurrentSupplyBias,
             unit_conversion_parameters={'V_0': MOT_y_Bias_UC_V_0, 
                                         'A_per_V': MOT_y_Bias_UC_A_per_V,
                                         'G_per_V': MOT_y_Bias_UC_G_per_V}
             )
ls.AnalogOut(name='MOT_x_z_Bias', parent_device=NI_USB_01, connection='ao1',
             unit_conversion_class=CurrentSupply.CurrentSupplyBias,
             unit_conversion_parameters={'V_0':MOT_x_z_Bias_UC_V_0, 
                                         'A_per_V': MOT_x_z_Bias_UC_A_per_V,
                                         'G_per_V': MOT_x_z_Bias_UC_G_per_V}
             )
ls.AnalogOut(name='MOT_x_mz_Bias', parent_device=NI_USB_01, connection='ao2',
             unit_conversion_class=CurrentSupply.CurrentSupplyBias,
             unit_conversion_parameters={'V_0': MOT_x_mz_Bias_UC_V_0, 
                                         'A_per_V': MOT_x_mz_Bias_UC_A_per_V,
                                         'G_per_V':MOT_x_mz_Bias_UC_G_per_V}
             )
ls.AnalogOut(name='MOT_Quad', parent_device=NI_USB_01, connection='ao3',
             unit_conversion_class=CurrentSupply.CurrentSupplyGradient,
             unit_conversion_parameters={'A_per_V': MOT_Quad_UC_A_per_V,
                                         'G_per_cm_per_V': MOT_Quad_UC_G_per_cm_per_V}
             )
ls.DigitalOut(name='MOT_y_Bias_Disable', parent_device=NI_USB_01, connection='port0/line0')
ls.DigitalOut(name='MOT_x_z_Bias_Disable', parent_device=NI_USB_01, connection='port0/line1')
ls.DigitalOut(name='MOT_x_mz_Bias_Disable', parent_device=NI_USB_01, connection='port0/line2')
ls.DigitalOut(name='MOT_Quad_Disable', parent_device=NI_USB_01, connection='port0/line3')

NI_USB_6229(
    name="NI_USB_02",
    parent_device=pb0_NI_USB,
    MAX_name='USB_02',
    clock_terminal='/USB_02/PFI0',
)
ls.AnalogOut(name='ni_usb_02_ao0', parent_device=NI_USB_02, connection='ao0')
ls.AnalogOut(name='ni_usb_02_ao1', parent_device=NI_USB_02, connection='ao1')
ls.DigitalOut(name='ni_usb_02_do0', parent_device=NI_USB_02, connection='port0/line0')
ls.DigitalOut(name='ni_usb_02_d01', parent_device=NI_USB_02, connection='port0/line1')
ls.DigitalOut(name='ni_usb_02_d02', parent_device=NI_USB_02, connection='port0/line2')
ls.DigitalOut(name='ni_usb_02_d03', parent_device=NI_USB_02, connection='port0/line3')

###############################################################################
#
# Novatechs
#
###############################################################################

NovaTechDDS9M(name='NT_1',
                parent_device=pb0_nt1,
                com_port='com5',
                baud_rate=115200,
                default_baud_rate=19200,
                phase_mode='aligned', # continuous aligned
                update_mode='asynchronous', # asynchronous synchronous
                synchronous_first_line_repeat=False # True
                )

ls.DDS(name='D2_Lock_DDS', parent_device=NT_1, connection='channel 0')
ls.DDS(name='nt1_1', parent_device=NT_1, connection='channel 1')
ls.StaticDDS(name='nt1_2', parent_device=NT_1, connection='channel 2')
ls.StaticDDS(name='nt1_3', parent_device=NT_1, connection='channel 3')

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

Old_Mako_camera_imaqdx_attributes = {
    'AcquisitionAttributes::AdvancedEthernet::BandwidthControl::DesiredPeakBandwidth': 1000,
    'AcquisitionAttributes::AdvancedEthernet::Controller::DestinationMode': 'Unicast',
    'AcquisitionAttributes::AdvancedEthernet::Controller::DestinationMulticastAddress': '239.192.0.1',
    'AcquisitionAttributes::AdvancedEthernet::EventParameters::MaxOutstandingEvents': 50,
    'AcquisitionAttributes::AdvancedEthernet::FirewallTraversal::Enabled': 1,
    'AcquisitionAttributes::AdvancedEthernet::FirewallTraversal::KeepAliveTime': 30,
    'AcquisitionAttributes::AdvancedEthernet::PacketReceptionParameters::KernelReceiveBufferSizeRequested': 2000000,
    'AcquisitionAttributes::AdvancedEthernet::PacketReceptionParameters::MaximumPacketsPerReception': 100,
    'AcquisitionAttributes::AdvancedEthernet::PacketReceptionParameters::PacketReceptionTimeout': 450,
    'AcquisitionAttributes::AdvancedEthernet::PacketReceptionParameters::ThreadPriority': 1,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::MaxResendsPerPacket': 25,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::MemoryWindowSize': 1024,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::MissingPacketTimeout': 2,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::NewPacketTimeout': 100,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::ResendBatchingPercentage': 10,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::ResendResponseTimeout': 2,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::ResendsEnabled': 1,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::ResendThresholdPercentage': 5,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::ResendTimerResolution': 1,
    'AcquisitionAttributes::AdvancedEthernet::TestPacketParameters::MaxTestPacketRetries': 1,
    'AcquisitionAttributes::AdvancedEthernet::TestPacketParameters::TestPacketEnabled': 1,
    'AcquisitionAttributes::AdvancedEthernet::TestPacketParameters::TestPacketTimeout': 250,
    'AcquisitionAttributes::AdvancedGenicam::CommandTimeout': 100,
    'AcquisitionAttributes::AdvancedGenicam::EventsEnabled': 1,
    'AcquisitionAttributes::AdvancedGenicam::IgnoreCameraValidationErrors': 0,
    'AcquisitionAttributes::AdvancedGenicam::PersistenceAlgorithm': 'Auto',
    'AcquisitionAttributes::Bayer::Algorithm': 'Bilinear',
    'AcquisitionAttributes::Bayer::GainB': 1,
    'AcquisitionAttributes::Bayer::GainG': 1,
    'AcquisitionAttributes::Bayer::GainR': 1,
    'AcquisitionAttributes::Bayer::Pattern': 'Use hardware value',
    'AcquisitionAttributes::BitsPerPixel': 'Use hardware value',
    'AcquisitionAttributes::ChunkDataDecoding::ChunkDataDecodingEnabled': 0,
    'AcquisitionAttributes::ChunkDataDecoding::MaximumChunkCopySize': 64,
    'AcquisitionAttributes::HardwareMaximumQueuedBufferCount': 1000,
    'AcquisitionAttributes::HardwareRequeueBufferListThreshold': 50,
    'AcquisitionAttributes::IgnoreFirstFrame': 0,
    'AcquisitionAttributes::ImageDecoderCopyMode': 'Auto',
    'AcquisitionAttributes::IncompleteBufferMode': 'Ignore',
    'AcquisitionAttributes::OutputImageType': 'Auto',
    'AcquisitionAttributes::OverwriteMode': 'Get Newest',
    'AcquisitionAttributes::PacketSize': 1500,
    'AcquisitionAttributes::PixelSignedness': 'Use hardware value',
    'AcquisitionAttributes::ReceiveTimestampMode': 'None',
    'AcquisitionAttributes::ShiftPixelBits': 0,
    'AcquisitionAttributes::SwapPixelBytes': 0,
    'AcquisitionAttributes::Timeout': 5000,
    'CameraAttributes::Controls::Exposure::ExposureTimeAbs': 50.0,
    'CameraAttributes::Acquisition::AcquisitionMode': 'Continuous',
    'CameraAttributes::Acquisition::AcquisitionFrameCount': 1,
    'CameraAttributes::Acquisition::AcquisitionFrameRateAbs': 229.41,
    'CameraAttributes::Acquisition::RecorderPreEventCount': 0,
    'CameraAttributes::Acquisition::Trigger::TriggerSelector': 'FrameStart',
    'CameraAttributes::Acquisition::Trigger::TriggerSelector': 'FrameStart',
    'CameraAttributes::Acquisition::Trigger::TriggerMode': 'On',
    'CameraAttributes::Acquisition::Trigger::TriggerSelector': 'AcquisitionStart',
    'CameraAttributes::Acquisition::Trigger::TriggerMode': 'Off',
    'CameraAttributes::Acquisition::Trigger::TriggerSelector': 'AcquisitionEnd',
    'CameraAttributes::Acquisition::Trigger::TriggerMode': 'Off',
    'CameraAttributes::Acquisition::Trigger::TriggerSelector': 'AcquisitionRecord',
    'CameraAttributes::Acquisition::Trigger::TriggerMode': 'On',
    'CameraAttributes::Acquisition::Trigger::TriggerSelector': 'FrameStart',
    'CameraAttributes::Acquisition::Trigger::TriggerSelector': 'FrameStart',
    'CameraAttributes::Acquisition::Trigger::TriggerSource': 'Freerun',
    'CameraAttributes::Acquisition::Trigger::TriggerSelector': 'AcquisitionStart',
    'CameraAttributes::Acquisition::Trigger::TriggerSource': 'Line1',
    'CameraAttributes::Acquisition::Trigger::TriggerSelector': 'AcquisitionEnd',
    'CameraAttributes::Acquisition::Trigger::TriggerSource': 'Line1',
    'CameraAttributes::Acquisition::Trigger::TriggerSelector': 'AcquisitionRecord',
    'CameraAttributes::Acquisition::Trigger::TriggerSource': 'Line1',
    'CameraAttributes::Acquisition::Trigger::TriggerSelector': 'FrameStart',
    'CameraAttributes::Acquisition::Trigger::TriggerSelector': 'FrameStart',
    'CameraAttributes::Acquisition::Trigger::TriggerActivation': 'RisingEdge',
    'CameraAttributes::Acquisition::Trigger::TriggerSelector': 'AcquisitionStart',
    'CameraAttributes::Acquisition::Trigger::TriggerActivation': 'RisingEdge',
    'CameraAttributes::Acquisition::Trigger::TriggerSelector': 'AcquisitionEnd',
    'CameraAttributes::Acquisition::Trigger::TriggerActivation': 'RisingEdge',
    'CameraAttributes::Acquisition::Trigger::TriggerSelector': 'AcquisitionRecord',
    'CameraAttributes::Acquisition::Trigger::TriggerActivation': 'RisingEdge',
    'CameraAttributes::Acquisition::Trigger::TriggerOverlap': 'Off',
    'CameraAttributes::Acquisition::Trigger::TriggerDelayAbs': 0,
    'CameraAttributes::Acquisition::Trigger::TriggerSelector': 'FrameStart',
    'CameraAttributes::DeviceStatus::DeviceTemperatureSelector': 'Main',
    'CameraAttributes::GigE::StreamBytesPerSecond': 115000000,
    'CameraAttributes::GigE::BandwidthControlMode': 'StreamBytesPerSecond',
    'CameraAttributes::GigE::GevSCPSPacketSize': 1500,
    'CameraAttributes::GigE::ChunkModeActive': 0,
    'CameraAttributes::GigE::StreamFrameRateConstrain': 1,
    'CameraAttributes::GigE::StreamHold::StreamHoldEnable': 'Off',
    'CameraAttributes::ImageMode::DecimationHorizontal': 1,
    'CameraAttributes::ImageMode::DecimationVertical': 1,
    'CameraAttributes::ImageMode::ReverseX': 0,
    'CameraAttributes::ImageMode::ReverseY': 0,
    'CameraAttributes::ImageFormat::PixelFormat': 'Mono12Packed',
    'CameraAttributes::ImageFormat::Width': 644,
    'CameraAttributes::ImageFormat::Height': 484,
    'CameraAttributes::ImageFormat::OffsetX': 0,
    'CameraAttributes::ImageFormat::OffsetY': 0,
    'CameraAttributes::Controls::Gamma': 1,
    'CameraAttributes::Controls::DefectMaskEnable': 1,
    'CameraAttributes::Controls::DSPSubregion::DSPSubregionLeft': 0,
    'CameraAttributes::Controls::DSPSubregion::DSPSubregionTop': 0,
    'CameraAttributes::Controls::DSPSubregion::DSPSubregionRight': 644,
    'CameraAttributes::Controls::DSPSubregion::DSPSubregionBottom': 484,
    'CameraAttributes::Controls::Exposure::ExposureAuto': 'Off',
    'CameraAttributes::Controls::Exposure::ExposureTimeAbs': 15000,
    'CameraAttributes::Controls::Exposure::ExposureTimePWL1': 15000,
    'CameraAttributes::Controls::Exposure::ExposureTimePWL2': 15000,
    'CameraAttributes::Controls::Exposure::ExposureAutoControl::ExposureAutoTarget': 50,
    'CameraAttributes::Controls::Exposure::ExposureAutoControl::ExposureAutoAlg': 'Mean',
    'CameraAttributes::Controls::Exposure::ExposureAutoControl::ExposureAutoMin': 83,
    'CameraAttributes::Controls::Exposure::ExposureAutoControl::ExposureAutoMax': 500000,
    'CameraAttributes::Controls::Exposure::ExposureAutoControl::ExposureAutoRate': 100,
    'CameraAttributes::Controls::Exposure::ExposureAutoControl::ExposureAutoOutliers': 0,
    'CameraAttributes::Controls::Exposure::ExposureAutoControl::ExposureAutoAdjustTol': 5,
    'CameraAttributes::Controls::GainControl::GainSelector': 'All',
    'CameraAttributes::Controls::GainControl::Gain': 0,
    'CameraAttributes::Controls::GainControl::GainSelector': 'All',
    'CameraAttributes::Controls::GainControl::GainSelector': 'All',
    'CameraAttributes::Controls::GainControl::GainRaw': 0,
    'CameraAttributes::Controls::GainControl::GainSelector': 'All',
    'CameraAttributes::Controls::GainControl::GainSelector': 'All',
    'CameraAttributes::Controls::GainControl::GainAuto': 'Off',
    'CameraAttributes::Controls::GainControl::GainSelector': 'All',
    'CameraAttributes::Controls::GainControl::GainAutoControl::GainAutoTarget': 50,
    'CameraAttributes::Controls::GainControl::GainAutoControl::GainAutoMin': 0,
    'CameraAttributes::Controls::GainControl::GainAutoControl::GainAutoMax': 26,
    'CameraAttributes::Controls::GainControl::GainAutoControl::GainAutoRate': 100,
    'CameraAttributes::Controls::GainControl::GainAutoControl::GainAutoOutliers': 0,
    'CameraAttributes::Controls::GainControl::GainAutoControl::GainAutoAdjustTol': 5,
    'CameraAttributes::Controls::BlackLevelControl::BlackLevel': 4,
    'CameraAttributes::IO::SyncIn::SyncInSelector': 'SyncIn1',
    'CameraAttributes::IO::SyncIn::SyncInSelector': 'SyncIn1',
    'CameraAttributes::IO::SyncIn::SyncInGlitchFilter': 0,
    'CameraAttributes::IO::SyncIn::SyncInSelector': 'SyncIn1',
    'CameraAttributes::IO::SyncOut::SyncOutSelector': 'SyncOut1',
    'CameraAttributes::IO::SyncOut::SyncOutSelector': 'SyncOut1',
    'CameraAttributes::IO::SyncOut::SyncOutSource': 'Exposing',
    'CameraAttributes::IO::SyncOut::SyncOutSelector': 'SyncOut2',
    'CameraAttributes::IO::SyncOut::SyncOutSource': 'Exposing',
    'CameraAttributes::IO::SyncOut::SyncOutSelector': 'SyncOut3',
    'CameraAttributes::IO::SyncOut::SyncOutSource': 'Exposing',
    'CameraAttributes::IO::SyncOut::SyncOutSelector': 'SyncOut1',
    'CameraAttributes::IO::SyncOut::SyncOutSelector': 'SyncOut1',
    'CameraAttributes::IO::SyncOut::SyncOutPolarity': 'Normal',
    'CameraAttributes::IO::SyncOut::SyncOutSelector': 'SyncOut2',
    'CameraAttributes::IO::SyncOut::SyncOutPolarity': 'Normal',
    'CameraAttributes::IO::SyncOut::SyncOutSelector': 'SyncOut3',
    'CameraAttributes::IO::SyncOut::SyncOutPolarity': 'Normal',
    'CameraAttributes::IO::SyncOut::SyncOutSelector': 'SyncOut1',
    'CameraAttributes::IO::Strobe::StrobeSource': 'FrameTrigger',
    'CameraAttributes::IO::Strobe::StrobeDurationMode': 'Source',
    'CameraAttributes::IO::Strobe::StrobeDelay': 0,
    'CameraAttributes::IO::Strobe::StrobeDuration': 0,
    'CameraAttributes::SavedUserSets::UserSetSelector': 'Default',
    'CameraAttributes::SavedUserSets::UserSetDefaultSelector': 'Default',
    'CameraAttributes::EventControl::EventSelector': 'AcquisitionStart',
    'CameraAttributes::EventControl::EventSelector': 'AcquisitionStart',
    'CameraAttributes::EventControl::EventNotification': 'Off',
    'CameraAttributes::EventControl::EventSelector': 'AcquisitionEnd',
    'CameraAttributes::EventControl::EventNotification': 'Off',
    'CameraAttributes::EventControl::EventSelector': 'FrameTrigger',
    'CameraAttributes::EventControl::EventNotification': 'Off',
    'CameraAttributes::EventControl::EventSelector': 'ExposureEnd',
    'CameraAttributes::EventControl::EventNotification': 'Off',
    'CameraAttributes::EventControl::EventSelector': 'AcquisitionRecordTrigger',
    'CameraAttributes::EventControl::EventNotification': 'Off',
    'CameraAttributes::EventControl::EventSelector': 'Line1RisingEdge',
    'CameraAttributes::EventControl::EventNotification': 'Off',
    'CameraAttributes::EventControl::EventSelector': 'Line1FallingEdge',
    'CameraAttributes::EventControl::EventNotification': 'Off',
    'CameraAttributes::EventControl::EventSelector': 'FrameTriggerReady',
    'CameraAttributes::EventControl::EventNotification': 'Off',
    'CameraAttributes::EventControl::EventSelector': 'ExposureStart',
    'CameraAttributes::EventControl::EventNotification': 'Off',
    'CameraAttributes::EventControl::EventSelector': 'AcquisitionStart',
    'CameraAttributes::EventControl::EventsEnable1': 0,
    'CameraAttributes::Controls::LUTControl::LUTSelector': 'LUT1',
    'CameraAttributes::Controls::LUTControl::LUTEnable': 0,
    'CameraAttributes::Controls::LUTControl::LUTSelector': 'LUT1',

}

Mako_camera_imaqdx_attributes = {
    'AcquisitionAttributes::AdvancedEthernet::BandwidthControl::DesiredPeakBandwidth': 1000.0,
    'AcquisitionAttributes::AdvancedEthernet::Controller::DestinationMode': 'Unicast',
    'AcquisitionAttributes::AdvancedEthernet::Controller::DestinationMulticastAddress': '239.192.0.1',
    'AcquisitionAttributes::AdvancedEthernet::EventParameters::MaxOutstandingEvents': 50,
    'AcquisitionAttributes::AdvancedEthernet::FirewallTraversal::Enabled': 1,
    'AcquisitionAttributes::AdvancedEthernet::FirewallTraversal::KeepAliveTime': 30,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::MaxResendsPerPacket': 25,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::MemoryWindowSize': 1024,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::MissingPacketTimeout': 2,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::NewPacketTimeout': 100,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::ResendBatchingPercentage': 10,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::ResendResponseTimeout': 2,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::ResendThresholdPercentage': 5,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::ResendTimerResolution': 1,
    'AcquisitionAttributes::AdvancedEthernet::ResendParameters::ResendsEnabled': 1,
    'AcquisitionAttributes::AdvancedEthernet::TestPacketParameters::MaxTestPacketRetries': 1,
    'AcquisitionAttributes::AdvancedEthernet::TestPacketParameters::TestPacketEnabled': 1,
    'AcquisitionAttributes::AdvancedEthernet::TestPacketParameters::TestPacketTimeout': 250,
    'AcquisitionAttributes::AdvancedGenicam::CommandTimeout': 100,
    'AcquisitionAttributes::AdvancedGenicam::EventsEnabled': 1,
    'AcquisitionAttributes::AdvancedGenicam::IgnoreCameraValidationErrors': 0,
    'AcquisitionAttributes::AdvancedGenicam::PersistenceAlgorithm': 'Auto',
    'AcquisitionAttributes::Bayer::Algorithm': 'Bilinear',
    'AcquisitionAttributes::Bayer::GainB': 1.0,
    'AcquisitionAttributes::Bayer::GainG': 1.0,
    'AcquisitionAttributes::Bayer::GainR': 1.0,
    'AcquisitionAttributes::Bayer::Pattern': 'Use hardware value',
    'AcquisitionAttributes::BitsPerPixel': 'Use hardware value',
    'AcquisitionAttributes::ChunkDataDecoding::ChunkDataDecodingEnabled': 0,
    'AcquisitionAttributes::ChunkDataDecoding::MaximumChunkCopySize': 64,
    'AcquisitionAttributes::HardwareMaximumQueuedBufferCount': 1000,
    'AcquisitionAttributes::HardwareRequeueBufferListThreshold': 50.0,
    'AcquisitionAttributes::ImageDecoderCopyMode': 'Auto',
    'AcquisitionAttributes::IncompleteBufferMode': 'Ignore',
    'AcquisitionAttributes::OutputImageType': 'Auto',
    'AcquisitionAttributes::OverwriteMode': 'Get Newest',
    'AcquisitionAttributes::PacketSize': 1500,
    'AcquisitionAttributes::ReceiveTimestampMode': 'None',
    'AcquisitionAttributes::ShiftPixelBits': 0,
    'AcquisitionAttributes::SwapPixelBytes': 0,
    'AcquisitionAttributes::Timeout': 5000,
    'CameraAttributes::Acquisition::AcquisitionFrameCount': 1,
    'CameraAttributes::Acquisition::AcquisitionFrameRateAbs': 229.41041523285156,
    'CameraAttributes::Acquisition::AcquisitionMode': 'Continuous',
    'CameraAttributes::Acquisition::RecorderPreEventCount': 0,
    'CameraAttributes::Acquisition::Trigger::TriggerActivation': 'RisingEdge',
    'CameraAttributes::Acquisition::Trigger::TriggerDelayAbs': 0.0,
    'CameraAttributes::Acquisition::Trigger::TriggerMode': 'On',
    'CameraAttributes::Acquisition::Trigger::TriggerOverlap': 'Off',
    'CameraAttributes::Acquisition::Trigger::TriggerSelector': 'FrameStart',
    'CameraAttributes::Acquisition::Trigger::TriggerSource': 'Line1',
    'CameraAttributes::Controls::BlackLevelControl::BlackLevel': 4.0,
    'CameraAttributes::Controls::BlackLevelControl::BlackLevelSelector': 'All',
    'CameraAttributes::Controls::DSPSubregion::DSPSubregionBottom': 484,
    'CameraAttributes::Controls::DSPSubregion::DSPSubregionLeft': 0,
    'CameraAttributes::Controls::DSPSubregion::DSPSubregionRight': 644,
    'CameraAttributes::Controls::DSPSubregion::DSPSubregionTop': 0,
    'CameraAttributes::Controls::DefectMaskEnable': 1,
    'CameraAttributes::Controls::Exposure::ExposureAuto': 'Off',
    'CameraAttributes::Controls::Exposure::ExposureMode': 'TriggerWidth',
#    'CameraAttributes::Controls::Exposure::ExposureTimeAbs': 15000.0,
    'CameraAttributes::Controls::Exposure::ThresholdPWL1': 63,
    'CameraAttributes::Controls::Exposure::ThresholdPWL2': 63,
    'CameraAttributes::Controls::GainControl::Gain': 0.0,
    'CameraAttributes::Controls::GainControl::GainAuto': 'Off',
    'CameraAttributes::Controls::GainControl::GainSelector': 'All',
    'CameraAttributes::Controls::Gamma': 1.0,
    'CameraAttributes::Controls::LUTControl::LUTEnable': 0,
    'CameraAttributes::Controls::LUTControl::LUTIndex': 0,
    'CameraAttributes::Controls::LUTControl::LUTMode': 'Luminance',
    'CameraAttributes::Controls::LUTControl::LUTSelector': 'LUT1',
    'CameraAttributes::Controls::LUTControl::LUTValue': 4095,
    'CameraAttributes::DeviceStatus::DeviceTemperatureSelector': 'Main',
    'CameraAttributes::EventControl::EventNotification': 'Off',
    'CameraAttributes::EventControl::EventSelector': 'AcquisitionStart',
    'CameraAttributes::EventControl::EventsEnable1': 0,
    'CameraAttributes::GigE::BandwidthControlMode': 'StreamBytesPerSecond',
    'CameraAttributes::GigE::ChunkModeActive': 0,
    'CameraAttributes::GigE::StreamBytesPerSecond': 115000000,
    'CameraAttributes::GigE::StreamFrameRateConstrain': 1,
    'CameraAttributes::GigE::StreamHold::StreamHoldEnable': 'Off',
    'CameraAttributes::IO::Strobe::StrobeDelay': 0,
    'CameraAttributes::IO::Strobe::StrobeDuration': 0,
    'CameraAttributes::IO::Strobe::StrobeDurationMode': 'Source',
    'CameraAttributes::IO::Strobe::StrobeSource': 'FrameTrigger',
    'CameraAttributes::IO::SyncIn::SyncInGlitchFilter': 0,
    'CameraAttributes::IO::SyncIn::SyncInSelector': 'SyncIn1',
    'CameraAttributes::IO::SyncOut::SyncOutLevels': 0,
    'CameraAttributes::IO::SyncOut::SyncOutPolarity': 'Normal',
    'CameraAttributes::IO::SyncOut::SyncOutSelector': 'SyncOut1',
    'CameraAttributes::IO::SyncOut::SyncOutSource': 'Exposing',
    'CameraAttributes::ImageFormat::Height': 484,
    'CameraAttributes::ImageFormat::OffsetX': 0,
    'CameraAttributes::ImageFormat::OffsetY': 0,
    'CameraAttributes::ImageFormat::PixelFormat': 'Mono12Packed',
    'CameraAttributes::ImageFormat::Width': 644,
    'CameraAttributes::ImageMode::DecimationHorizontal': 1,
    'CameraAttributes::ImageMode::DecimationVertical': 1,
    'CameraAttributes::ImageMode::ReverseX': 0,
    'CameraAttributes::ImageMode::ReverseY': 0,
    'CameraAttributes::Info::DeviceUserID': '',
    'CameraAttributes::SavedUserSets::UserSetDefaultSelector': 'Default',
    'CameraAttributes::SavedUserSets::UserSetSelector': 'Default',
}

Basler_manual_mode_imaqdx_attributes = {
    'CameraAttributes::AcquisitionTrigger::AcquisitionMode': 'Continuous',
    'CameraAttributes::AcquisitionTrigger::TriggerMode': 'Off',
    'CameraAttributes::AcquisitionTrigger::ExposureMode': 'Timed',
    'CameraAttributes::AnalogControls::GainRaw': 300,
    }

Mako_manual_mode_imaqdx_attributes = {
    'CameraAttributes::Acquisition::AcquisitionMode': 'Continuous',
    'CameraAttributes::Acquisition::Trigger::TriggerMode': 'Off',
    'CameraAttributes::Controls::GainControl::Gain': 0,
    #'CameraAttributes::Controls::Exposure::ExposureTimeAbs': 1500.0,
    }

#'MOT_y' camera
IMAQdxCamera(name='MOT_y',
    parent_device=MOT_y_Camera_Trigger,
    connection='trigger',
    trigger_edge_type='rising',
    orientation = 'MOT_y',
    serial_number=0x3053162459,
    camera_attributes=Basler_camera_imaqdx_attributes,
    manual_mode_camera_attributes=Basler_manual_mode_imaqdx_attributes,
    stop_acquisition_timeout=10,
    exception_on_failed_shot=False)

#'MOT_x' camera
IMAQdxCamera(name='MOT_x',
    parent_device=MOT_x_Camera_Trigger,
    connection='trigger',
    trigger_edge_type='rising',
    orientation = 'MOT_x',
    serial_number=0xF315C0B0B,
    camera_attributes=Mako_camera_imaqdx_attributes,
    manual_mode_camera_attributes=Mako_manual_mode_imaqdx_attributes,
    stop_acquisition_timeout=10,
    exception_on_failed_shot=False)

#'MOT_???' camera
IMAQdxCamera(name='MOT_z',
    parent_device=MOT_z_Camera_Trigger,
    connection='trigger',
    trigger_edge_type='rising',
    orientation = 'MOT_z',
    serial_number=0xF315D2ACE,
    camera_attributes=Mako_camera_imaqdx_attributes,
    manual_mode_camera_attributes=Mako_manual_mode_imaqdx_attributes,
    stop_acquisition_timeout=10,
    exception_on_failed_shot=False)

#'MOT_???' camera
IMAQdxCamera(name='Mako3',
    parent_device=MOT_Camera_Trigger,
    connection='trigger',
    trigger_edge_type='rising',
    orientation = 'Mako3',
    serial_number=0xF315D2ACF,
    camera_attributes=Mako_camera_imaqdx_attributes,
    manual_mode_camera_attributes=Mako_manual_mode_imaqdx_attributes,
    stop_acquisition_timeout=10,
    exception_on_failed_shot=False)


# TekScope(name='ComputerScope1', 
#          addr='USB0::0x0699::0x03A4::C010346::INSTR', 
#          preamble_string='WFMP')

Arduino_Interlock( name = 'Arduino_Interlock',
          addr='ASRL20::INSTR', 
          timeout = 10)


if __name__ == '__main__':
    # Begin issuing labscript primitives
    # start() elicits the commencement of the shot
    ls.start()

    # Stop the experiment shot with stop()
    ls.stop(1.0)
