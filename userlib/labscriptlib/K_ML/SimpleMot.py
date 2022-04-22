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
        D2_Repump_Freq,
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
        D2_Repump_Freq,
        UV=False,
        DelayLight=0)

#
# FL  image the MOT
#
t += st.SimpleImage(t - Mako_Download_Time,
        [MOT_x, MOT_z],
        MOT_Fl_Exposure,
        Mako_Download_Time,
        ShutterDevices=[],
        DigitalDevices=[],
        AnalogDevices=[],
        AnalogValues=[],
        CloseShutters=False,
        mode='fluorescence',
        frametype='MOT')

#
# cMOT
#
t += st.cMOT(t)

#
# FL  image the cMOT
#
t += st.SimpleImage(t,
        [MOT_x, MOT_z],
        MOT_Fl_Exposure,
        0,
        ShutterDevices=[],
        DigitalDevices=[],
        AnalogDevices=[],
        AnalogValues=[],
        CloseShutters=False,
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
t += st.OpticalPump(t)

#
# Capture in quadrupole trap!
#

t += st.MagneticTrapCapture(t)

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
        Mako_Download_Time,
        ShutterDevices=[D2_Repump_Sh, D2_Probe_1_Sh],
        DigitalDevices=[D2_Repump_DO, D2_Probe_OP_DO],
        AnalogDevices=[D2_Repump_AO, D2_Probe_OP_AO],
        AnalogValues=[D2_Repump_Volts_Imaging, D2_Probe_Volts_Abs],
        CloseShutters=False,
        mode='absorption',
        frametype='MOT_TOF')

#
# Probe and dark frames for absorption imaging
#

t += st.SimpleImage(t,
        [MOT_y],
        MOT_Abs_Exposure,
        Mako_Download_Time,
        ShutterDevices=[D2_Repump_Sh, D2_Probe_1_Sh],
        DigitalDevices=[D2_Repump_DO, D2_Probe_OP_DO],
        AnalogDevices=[D2_Repump_AO, D2_Probe_OP_AO],
        AnalogValues=[D2_Repump_Volts_Imaging, D2_Probe_Volts_Abs],
        CloseShutters=False,
        mode='absorption',
        frametype='MOT_TOF_probe')

t += st.SimpleImage(t,
        [MOT_y],
        MOT_Abs_Exposure,
        Mako_Download_Time,
        ShutterDevices=[D2_Repump_Sh,],
        DigitalDevices=[D2_Repump_DO,],
        AnalogDevices=[D2_Repump_AO,],
        AnalogValues=[D2_Repump_Volts_Imaging,],
        CloseShutters=True,
        mode='absorption',
        frametype='MOT_TOF_dark')

#
# No light fluorescence images (note that the analog values are set to
# the values during the associated stages.)
#
t += st.SimpleImage(t,
        [MOT_x, MOT_z],
        MOT_Fl_Exposure,
        Mako_Download_Time,
        ShutterDevices=[D2_Repump_Sh, D2_Cooling_Sh, D2_Probe_1_Sh],
        DigitalDevices=[D2_Repump_DO, D2_Cooling_DO, D2_Probe_OP_DO],
        AnalogDevices=[D2_Repump_AO, D2_Cooling_AO, D2_Probe_OP_AO],
        AnalogValues=[D2_Repump_Volts, D2_Cooling_Volts, D2_Cooling_Volts],
        CloseShutters=False,
        mode='fluorescence',
        frametype='MOT_dark')

t += st.SimpleImage(t,
        [MOT_x, MOT_z],
        MOT_Fl_Exposure,
        Mako_Download_Time,
        ShutterDevices=[D2_Repump_Sh, D2_Cooling_Sh, D2_Probe_1_Sh],
        DigitalDevices=[D2_Repump_DO, D2_Cooling_DO, D2_Probe_OP_DO],
        AnalogDevices=[D2_Repump_AO, D2_Cooling_AO, D2_Probe_OP_AO],
        AnalogValues=[D2_Repump_Volts_cMOT_Stop, D2_Cooling_Volts, D2_Cooling_Volts],
        CloseShutters=True,
        mode='fluorescence',
        frametype='cMOT_dark')

# Plan: rewrite so as to do absorption imaging after TOF and to grab two FL images
# at the end of the MOT loading for number diagnostic.


#
# Set Dafault state
#
t += st.SetDefaults(t, mode='Shutdown')

# Stop the experiment
ls.stop(t)
