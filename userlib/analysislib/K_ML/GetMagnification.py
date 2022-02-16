# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 15:23:09 2022

This function aims to fit a falling cloud to get the magnification of an
imaging system, and it will also fit the widths to estimate the temperature 
"""

import lyse
import numpy as np
import matplotlib.pyplot as plt

import lmfit
df = lyse.data(n_sequences=1)


FIT = True
X_LABEL = 'TOF Time'
scan = df['scan']

# Let's obtain the dataframe for all of lyse's currently loaded shots:

Counts = df['MOT_Basic_Image_Process', 'Counts']
xWidth = df['MOT_Basic_Image_Process', 'xWidth']
yWidth = df['MOT_Basic_Image_Process', 'yWidth']
x0 = df['MOT_Basic_Image_Process', 'x0']
y0 = df['MOT_Basic_Image_Process', 'y0']

if FIT:
    # Now fit to an exponential
    model = lmfit.models.ExpressionModel("9.8e6 * M * x**2/2 + m*x + b")
    result = model.fit(x0, 
                        x=scan, 
                        M=1,
                        m=0,
                        b=-150,
                        )
    
    print(result.params)
    
    scan_Smooth = np.linspace(
                            scan.min(), 
                            scan.max(), 
                            128)
    
    Position_Smooth = model.eval(x=scan_Smooth)

# Let's plot them against each other:

fig = plt.figure(0,figsize=(7, 3.5))
gs = fig.add_gridspec(2, 2)
gs.update(left=0.12, bottom=0.15, top=0.93, wspace=0.2, hspace=0.8, right=0.99) 

ax = fig.add_subplot(gs[0,0])
ax.plot(scan, Counts,'bo')

ax.set_xlabel(X_LABEL)
ax.set_ylabel('Counts (arb)')

ax = fig.add_subplot(gs[0,1])
ax.plot(scan, xWidth,'bo', label='xWidth')
ax.plot(scan, yWidth,'ro', label='yWidth')

ax.set_xlabel(X_LABEL)
ax.set_ylabel('RMS width (meters)')
ax.set_ylim([None,None])

ax.legend()

ax = fig.add_subplot(gs[1,1])
ax.plot(scan, x0, 'bo', label='x0')
ax.plot(scan, y0, 'ro', label='y0')

if FIT:
    ax.set_title(r'$M = {:1.3f}$'.format(result.params['M'].value))
    ax.plot(scan_Smooth, Position_Smooth, "-")

ax.set_xlabel(X_LABEL)
ax.set_ylabel('position (um)')

ax.legend()