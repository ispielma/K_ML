# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 15:23:09 2022

@author: rubidium
"""

import lyse
import numpy as np
import matplotlib.pyplot as plt

import lmfit
df = lyse.data(n_sequences=1)


FIT = False
X_LABEL = 'y current (V)'
scan = df['scan']

# Let's obtain the dataframe for all of lyse's currently loaded shots:

# mot load rate was saved by a routine called calculate_load_rate:

MOT_Counts = df['MOT_Basic_Image_Process', 'MOT_Counts']

if FIT:
    # Now fit to an exponential
    model = lmfit.models.ExpressionModel("amp * (1 - exp(-x / tau))")
    result = model.fit(MOT_Counts, 
                        x=scan, 
                        amp=MOT_Counts.max(), 
                        tau=1)
    
    scan_Smooth = np.linspace(
                            scan.min(), 
                            scan.max(), 
                            128)
    
    MOT_Counts_Smooth = model.eval(x=scan_Smooth)

# Let's plot them against each other:

fig = plt.figure(0,figsize=(7, 3.5))
gs = fig.add_gridspec(1, 1)
gs.update(left=0.12, bottom=0.15, top=0.93, wspace=0.2, hspace=0.4, right=0.99) 

ax = fig.add_subplot(gs[0,0])
ax.plot(scan, MOT_Counts,'bo')

if FIT:
    ax.set_title(r'$\tau = {:1.3f}$ s'.format(result.params['tau'].value))
    ax.plot(scan_Smooth, MOT_Counts_Smooth, "-")

ax.set_xlabel(X_LABEL)
ax.set_ylabel('Counts (arb)')


#To save this result to the output hdf5 file, we have to instantiate a
#Sequence object:
# seq = Sequence(path, df)
# seq.save_result('detuning_loadrate_slope',c)