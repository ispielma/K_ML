import numpy as np

import labscript as ls
from labscript import ns, us, ms, s, Hz, kHz, MHz, GHz
from  labscript_utils import import_or_reload
import_or_reload('labscriptlib.Rb_ML.connection_table')  

def SetDefault(t):
    D2_Repump_AO.constant(t, 0.0)
    
    D2_Lock_DO.go_high(t)
    D2_Repump_DO.go_low(t)
    D2_Repump_Sh.go_low(t)
    UV_DO.go_low(t)  
    
    D2_Lock_DDS.setfreq(t, D2_Lock_Freq)
    D2_Lock_DDS.setamp(t, 1.0) # -80dBm
    
    # Assure two triggers per NI card
    ni_pci_01_do0.go_high(t)
    ni_pci_01_do0.go_low(t+0.001)
    ni_pci_01_ao0.constant(t, 1.0)
    ni_pci_01_ao0.constant(t+0.001, 0.0)
    
    ni_pci_02_do7.go_high(t)
    ni_pci_02_do7.go_low(t+0.001)
    ni_pci_02_ao7.constant(t, 1.0)
    ni_pci_02_ao7.constant(t+0.001, 0.0)
    
# Begin issuing labscript primitives
t = 0
ls.start()

#
# Set Dafault state
#

SetDefault(t)

#
# Snap a dark frame
#
ls.add_time_marker(t, "Snap dark frame", verbose=True)
MOT_x.snap(t, 'fluorescence', frametype='dark', trigger_duration=1*ms)
t += 1*ms

#
# Apply UV
#
ls.add_time_marker(t, "UV on", verbose=True)
UV_DO.go_high(t)
t += 0.5

#
# Acquire bright frame post UV
#

UV_DO.go_low(t)
D2_Repump_DO.go_high(t)
D2_Repump_Sh.go_high(t)
D2_Repump_AO.constant(t, 1.0)
MOT_x.snap(t, 'fluorescence', frametype='bright', trigger_duration=1*ms)

t+= 1*ms

#
# Set Dafault state
#
SetDefault(t)

# Stop the experiment shot with stop()
t += 1*ms
ls.stop(t)
