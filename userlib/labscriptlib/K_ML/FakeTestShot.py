# -*- coding: utf-8 -*-
#Shot to test the functionality of the arduino interlock device, 
# especially during the change of states of labscript (Maunual, Transition to Buffer, Buffered, Transition to Manual).
"""
Fake Test Shot
Created on Fri Apr  1 16:29:47 2022

@author: rubidium
"""

import numpy as np

import labscript as ls
import labscript_utils as lu

from labscript import ns, us, ms, s, Hz, kHz, MHz, GHz
import labscriptlib.K_ML.Stages as st
lu.import_or_reload('labscriptlib.K_ML.connection_table')

t = ls.start()
t += st.SetDefaults(t)


#Do nothing, because we want to test writing to h5, transitions between states, etc.


t += st.SetDefaults(t, mode='Shutdown')
ls.stop(t)