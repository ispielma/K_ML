# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 15:23:09 2022

@author: rubidium
"""

import lyse
import numpy as np
import matplotlib.pyplot as plt

import lmfit
df = lyse.data(n_sequences=3)


FIT = 'gauss' # 'gauss' # 'exp' # 'loading' # None
X_LABEL = 'MOT_x_z_Bias_Imaging'
ScriptName = 'MOT_Three_Camera_Image_Process'

# Let's obtain the dataframe for all of lyse's currently loaded shots:

# mot load rate was saved by a routine called calculate_load_rate:

Counts = df[ScriptName, 'Counts']
xWidth = df[ScriptName, 'xWidth']
yWidth = df[ScriptName, 'yWidth']
x0 = df[ScriptName, 'x0']
y0 = df[ScriptName, 'y0']

try:
    scan = df['scan']
except:
    scan = np.arange(len(Counts))

if FIT == 'Loading':
    # Now fit to an exponential
    
    if len(scan) < 4:
        FIT = False
    else:
        model = lmfit.models.ExpressionModel("amp * (1 - exp(-x / tau))")
        result = model.fit(Counts, 
                            x=scan, 
                            amp=Counts.max(), 
                            tau=1)
        
        scan_Smooth = np.linspace(
                                scan.min(), 
                                scan.max(), 
                                128)
        
        MOT_Counts_Smooth = model.eval(x=scan_Smooth)
elif FIT == 'exp':
    # Now fit to an exponential
    if len(scan) < 5:
        FIT = False
    else:
        model = lmfit.models.ExpressionModel("amp * exp(-x / tau) + offset")
        result = model.fit(Counts, 
                            x=scan, 
                            amp=Counts.max(), 
                            offset=0,
                            tau=1)
        
        scan_Smooth = np.linspace(
                                scan.min(), 
                                scan.max(), 
                                128)
        
        MOT_Counts_Smooth = model.eval(x=scan_Smooth)
elif FIT == 'gauss':
    # Now fit to an exponential
    if len(scan) < 6:
        FIT = False
    else:
        model = lmfit.models.ExpressionModel("amp * exp(-0.5*((x-x0) / tau)**2 ) + offset")
        result = model.fit(Counts, 
                            x=scan, 
                            amp=Counts.max(), 
                            offset=0,
                            tau=0.25,
                            x0=0)
        
        scan_Smooth = np.linspace(
                                scan.min(), 
                                scan.max(), 
                                128)
        
        MOT_Counts_Smooth = model.eval(x=scan_Smooth)
    
    
# Let's plot them against each other:

fig = plt.figure(0,figsize=(7, 3.5))
gs = fig.add_gridspec(2, 2)
gs.update(left=0.12, bottom=0.15, top=0.93, wspace=0.4, hspace=0.8, right=0.99) 

ax = fig.add_subplot(gs[0,0])
ax.plot(scan, Counts,'bo')

if FIT == 'exp':
    ax.set_title(r'$\tau = {:1.3f}$ s'.format(result.params['tau'].value))
    ax.plot(scan_Smooth, MOT_Counts_Smooth, "-")
if FIT == 'gauss':
    ax.set_title(r'$x_0 = {:1.3f}$ s'.format(result.params['x0'].value))
    ax.plot(scan_Smooth, MOT_Counts_Smooth, "-")


ax.set_xlabel(X_LABEL)
ax.set_ylabel('Counts (arb)')

ax = fig.add_subplot(gs[0,1])
ax.plot(scan, xWidth,'bo', label='xWidth')
ax.plot(scan, yWidth,'ro', label='yWidth')

ax.set_xlabel(X_LABEL)
ax.set_ylabel('RMS width (um)')
ax.set_ylim([None,None])

ax.legend()

ax = fig.add_subplot(gs[1,1])
ax.plot(scan, x0, 'bo', label='x0')
ax.plot(scan, y0, 'ro', label='y0')

ax.set_xlabel(X_LABEL)
ax.set_ylabel('position (um)')

ax.legend()


#To save this result to the output hdf5 file, we have to instantiate a
#Sequence object:
# seq = Sequence(path, df)
# seq.save_result('detuning_loadrate_slope',c)