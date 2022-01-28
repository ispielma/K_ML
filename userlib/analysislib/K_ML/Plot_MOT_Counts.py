# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 15:23:09 2022

@author: rubidium
"""

import lyse
import numpy as np
import matplotlib.pyplot as plt

# Let's obtain the dataframe for all of lyse's currently loaded shots:
df = lyse.data()

# Now let's see how the MOT load rate varies with, say a global called
# 'detuning', which might be the detuning of the MOT beams:

MOT_Load_Time = df['MOT_Load_Time']

# mot load rate was saved by a routine called calculate_load_rate:

MOT_Counts = df['Fl_Image_Averager', 'MOT_Counts']

# Let's plot them against each other:

fig = plt.figure(0,figsize=(7, 3.5))
gs = fig.add_gridspec(1, 1)
gs.update(left=0.12, bottom=0.1, top=0.93, wspace=0.2, hspace=0.4, right=0.99) 

ax = fig.add_subplot(gs[0,0])
ax.plot(MOT_Load_Time, MOT_Counts,'bo')


#To save this result to the output hdf5 file, we have to instantiate a
#Sequence object:
# seq = Sequence(path, df)
# seq.save_result('detuning_loadrate_slope',c)