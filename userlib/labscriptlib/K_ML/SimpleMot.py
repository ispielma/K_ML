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
# cMOT
#
t += st.cMOT(t)

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

# t += st.MagneticTrapCapture(t)

#
# TOF
#
t += st.MOT_Cell_TOF(t)

#
# With atoms imaging
#
t += st.FloImage(t,
        MOT_x,
        MOT_Fl_Exposure,
        Mako_Download_Time,
        ShutterDevices=[D2_Repump_Sh, D2_Cooling_Sh, D2_Probe_1_Sh],
        DigitalDevices=[D2_Repump_DO, D2_Cooling_DO, D2_Probe_OP_DO],
        AnalogDevices=[D2_Repump_AO, D2_Cooling_AO, D2_Probe_OP_AO],
        AnalogValues=[D2_Repump_Volts_Imaging, D2_Cooling_Volts_Imaging, D2_Cooling_Volts_Imaging],
        CloseShutters=False,
        frametype='bright')

#
# No atoms imaging
#
t += st.FloImage(t,
        MOT_x,
        MOT_Fl_Exposure,
        Mako_Download_Time,
        ShutterDevices=[D2_Repump_Sh, D2_Cooling_Sh, D2_Probe_1_Sh],
        DigitalDevices=[D2_Repump_DO, D2_Cooling_DO, D2_Probe_OP_DO],
        AnalogDevices=[D2_Repump_AO, D2_Cooling_AO, D2_Probe_OP_AO],
        AnalogValues=[D2_Repump_Volts_Imaging, D2_Cooling_Volts_Imaging, D2_Cooling_Volts_Imaging],
        CloseShutters=True,
        frametype='dark')

#
# Set Dafault state
#
t += st.SetDefaults(t, mode='Shutdown')

# Stop the experiment
ls.stop(t)
