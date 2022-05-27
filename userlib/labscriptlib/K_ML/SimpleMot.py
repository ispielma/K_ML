# -*- coding: utf-8 -*-
"""
This file loads a MOT in the KML lab and takes a picture of it.
"""

import numpy as np

import labscript as ls
import labscript_utils as lu

from labscript import ns, us, ms, s, Hz, kHz, MHz, GHz

import labscriptlib.K_ML.Stages as st

lu.import_or_reload('labscriptlib.K_ML.connection_table')

MOT_Fl_Cameras = [MOT_x, MOT_z]
MOT_Fl_Download_Time = len(MOT_Fl_Cameras)*Mako_Download_Time

t = ls.start()

#
# Set Dafault state
#
t += st.SetDefaults(t)

#
# UV MOT
#
t += st.MOT(t, Time_UV_MOT,
        MOT_y_Bias_MOT,
        MOT_x_z_Bias_MOT,
        MOT_x_mz_Bias_MOT,
        MOT_Quad_MOT,
        D2_Lock_Freq_MOT,
        D2_Repump_Freq_MOT,
        UV=MOT_UV,
        DelayLight=10e-3,
        stage_label='UV')

#
# MOT
#
t += st.MOT(t, Time_MOT,
        MOT_y_Bias_MOT,
        MOT_x_z_Bias_MOT,
        MOT_x_mz_Bias_MOT,
        MOT_Quad_MOT,
        D2_Lock_Freq_MOT,
        D2_Repump_Freq_MOT,
        UV=False,
        DelayLight=0)

#
# FL  image the MOT
#
t += st.SimpleImage(t - MOT_Fl_Download_Time,
        MOT_Fl_Cameras,
        MOT_Fl_Exposure,
        MOT_Fl_Download_Time,
        ShutterDevices=[],
        DigitalDevices=[],
        AnalogDevices=[],
        AnalogValues=[],
        CloseShutters=[False, False],
        mode='fluorescence',
        frametype='MOT')

#
# cMOT
#
t += st.cMOT(t) + 1e-3

#
# FL  image the cMOT (do not increment time)
#
t += st.SimpleImage(t,
        MOT_Fl_Cameras,
        cMOT_Fl_Exposure,
        0,
        ShutterDevices=[],
        DigitalDevices=[],
        AnalogDevices=[],
        AnalogValues=[],
        CloseShutters=[False, False],
        mode='fluorescence',
        frametype='cMOT')

#
# Optical Molassas (sub Doppler cooling!)
#
ScopeTrigger.trigger(t, 1e-3)
t += st.Molasses(t)

#
# Optical pump
#

# t += st.OpticalPump(t)

#
# Capture in quadrupole trap!
#

# t += st.MagneticTrapCapture(t)

#
# TOF
#

t += st.MOT_Cell_TOF(t)

#
# Abs image the cloud
#
t += st.SimpleImage(t,
        [MOT_y],
        MOT_Abs_Exposure,
        Basler_Download_Time,
        ShutterDevices=[D2_Probe_1_Sh, D2_Repump_Img_Sh],
        DigitalDevices=[D2_Probe_OP_DO, D2_Repump_DO],
        AnalogDevices=[D2_Probe_OP_AO, D2_Repump_AO],
        AnalogValues=[D2_Probe_Volts_AI, D2_Repump_Volts_Imaging],
        PretriggerTime=20e-6,
        CloseShutters=[False, False],
        mode='absorption',
        frametype='MOT_TOF')

#
# Probe and dark frames for absorption imaging
#

t += st.SimpleImage(t,
        [MOT_y],
        MOT_Abs_Exposure,
        Basler_Download_Time,
        ShutterDevices=[D2_Probe_1_Sh, D2_Repump_Img_Sh],
        DigitalDevices=[D2_Probe_OP_DO, D2_Repump_DO],
        AnalogDevices=[D2_Probe_OP_AO, D2_Repump_AO],
        AnalogValues=[D2_Probe_Volts_AI, D2_Repump_Volts_Imaging],
        PretriggerTime=20e-6,
        CloseShutters=[True, False],
        mode='absorption',
        frametype='MOT_TOF_probe')

t += st.SimpleImage(t,
        [MOT_y],
        MOT_Abs_Exposure,
        Basler_Download_Time,
        ShutterDevices=[D2_Repump_Img_Sh],
        DigitalDevices=[D2_Repump_DO],
        AnalogDevices=[D2_Repump_AO],
        AnalogValues=[D2_Repump_Volts_Imaging],
        PretriggerTime=20e-6,
        CloseShutters=[True,True],
        mode='absorption',
        frametype='MOT_TOF_dark')

#
# No light fluorescence images (note that the analog values are set to
# the values during the associated stages.)
#
t += st.SimpleImage(t,
        MOT_Fl_Cameras,
        MOT_Fl_Exposure,
        MOT_Fl_Download_Time,
        ShutterDevices=[D2_Repump_Sh, D2_Cooling_Sh],
        DigitalDevices=[D2_Repump_DO, D2_Cooling_DO],
        AnalogDevices=[D2_Repump_AO, D2_Cooling_AO],
        AnalogValues=[D2_Repump_Volts, D2_Cooling_Volts],
        CloseShutters=[False, False],
        mode='fluorescence',
        frametype='MOT_dark')

t += st.SimpleImage(t,
        MOT_Fl_Cameras,
        cMOT_Fl_Exposure,
        MOT_Fl_Download_Time,
        ShutterDevices=[D2_Repump_Sh, D2_Cooling_Sh],
        DigitalDevices=[D2_Repump_DO, D2_Cooling_DO],
        AnalogDevices=[D2_Repump_AO, D2_Cooling_AO],
        AnalogValues=[D2_Repump_Volts_cMOT_Stop, D2_Cooling_Volts],
        CloseShutters=[True, True],
        mode='fluorescence',
        frametype='cMOT_dark')

# Plan: rewrite so as to do absorption imaging after TOF and to grab two FL images
# at the end of the MOT loading for number diagnostic.


#
# Set Dafault state
#
t += st.SetDefaults(t, mode='Shutdown')

# Stop the experiment
t += 100e-6
print("Stopping!")
ls.stop(t)
