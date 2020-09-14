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
# A timing variable t is used for convenience
# start() elicits the commencement of the shot
t = 0
ls.start()

#
# Set Dafault state
#

SetDefault(t)

ls.add_time_marker(t, "Snap dark frame", verbose=True)

t += 0.002
ls.add_time_marker(t, "UV on", verbose=True)
UV_DO.go_high(t)

# Wait for 0.5 seconds
t += 0.5
UV_DO.go_low(t)
D2_Repump_DO.go_high(t)
D2_Repump_Sh.go_high(t)
# Ramp analog_out from 0.0 V to 1.0 V over 0.25 s with a 1 kS/s sample rate
t += D2_Repump_AO.ramp(t=t, initial=0.0, final=1.0, duration=2.0, samplerate=1e3)

#
# Set Dafault state
#
t += 2.0
SetDefault(t)

# Stop the experiment shot with stop()
t += 0.1
ls.stop(t)
