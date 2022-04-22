import lyse
import numpy as np
import lmfit
import os
import matplotlib.pyplot as plt
import traceback

FIT = True

# Is this script being run from within an interactive lyse session?
if lyse.spinning_top:
    # If so, use the filepath of the current shot
    h5_path_and_file = lyse.path
else:
    # If not, get the filepath of the last shot of the lyse DataFrame
    df = lyse.data()
    h5_path_and_file = df.filepath.iloc[-1]

ShotId, _ = os.path.split(h5_path_and_file)

# Instantiate a lyse.Run object for this shot
run = lyse.Run(h5_path_and_file)

# Get a dictionary of the global variables used in this shot
run_globals = run.get_globals()

# Extract the images

fl_keys = ['MOT', 'cMOT', 'MOT_dark', 'cMOT_dark']
MOT_x_images = run.get_images_dict('MOT_x', 'fluorescence', *fl_keys)
MOT_z_images = run.get_images_dict('MOT_z', 'fluorescence', *fl_keys)

abs_keys = ['MOT_TOF', 'MOT_TOF_probe', 'MOT_TOF_dark']
MOT_y_images = run.get_images_dict('MOT_y', 'absorption', *abs_keys)

# Try to get scope traces
try:
    ScopeTraces = run.get_trace('ComputerScope1', raw_data=True)
    print('GotScope')
except:
    ScopeTraces = None

# Compute the difference of the two images, after casting them to signed integers
# (otherwise negative differences wrap to 2**16 - 1 - diff)

MOT_x_images['MOT_diff'] = MOT_x_images['MOT'].astype(float) - MOT_x_images['MOT_dark'].astype(float)
MOT_x_images['cMOT_diff'] = MOT_x_images['cMOT'].astype(float) - MOT_x_images['cMOT_dark'].astype(float)

MOT_z_images['MOT_diff'] = MOT_z_images['MOT'].astype(float) - MOT_z_images['MOT_dark'].astype(float)
MOT_z_images['cMOT_diff'] = MOT_z_images['cMOT'].astype(float) - MOT_z_images['cMOT_dark'].astype(float)

MOT_y_images['MOT_TOF_OD'] = -np.log((MOT_y_images['MOT_TOF'].astype(float) - MOT_y_images['MOT_TOF_dark'].astype(float)) / 
                                     (MOT_y_images['MOT_TOF_probe'].astype(float) - MOT_y_images['MOT_TOF_dark'].astype(float)) )


#
# Now plot all five images
#

fig = plt.figure(0,figsize=(4, 3.5))

gs = fig.add_gridspec(2, 3)
gs.update(left=0.12, bottom=0.1, top=0.93, wspace=0.2, hspace=0.4, right=0.99) 
    
ax = fig.add_subplot(gs[0,0])
ax.set_title(r'x MOT', loc='center', fontsize=8, x=0.5, pad=4)
im = ax.imshow(MOT_x_images['MOT_diff'], 
               origin='lower',
               # extent=[xvals.min(),xvals.max(),yvals.min(),yvals.max()]
               )
ax.set_xlabel('X position (um)'); ax.set_ylabel('Y position (um)')

ax = fig.add_subplot(gs[0,1])
ax.set_title(r'x cMOT', loc='center', fontsize=8, x=0.5, pad=4)
im = ax.imshow(MOT_x_images['cMOT_diff'], 
               origin='lower',
               # extent=[xvals.min(),xvals.max(),yvals.min(),yvals.max()]
               )
ax.set_xlabel('X position (um)'); ax.set_ylabel('Y position (um)')

ax = fig.add_subplot(gs[1,0])
ax.set_title(r'z MOT', loc='center', fontsize=8, x=0.5, pad=4)
im = ax.imshow(MOT_z_images['MOT_diff'], 
               origin='lower',
               # extent=[xvals.min(),xvals.max(),yvals.min(),yvals.max()]
               )
ax.set_xlabel('X position (um)'); ax.set_ylabel('Y position (um)')

ax = fig.add_subplot(gs[1,1])
ax.set_title(r'z cMOT', loc='center', fontsize=8, x=0.5, pad=4)
im = ax.imshow(MOT_z_images['cMOT_diff'], 
               origin='lower',
               # extent=[xvals.min(),xvals.max(),yvals.min(),yvals.max()]
               )
ax.set_xlabel('X position (um)'); ax.set_ylabel('Y position (um)')

ax = fig.add_subplot(gs[2,0])
ax.set_title(r'y MOT TOF', loc='center', fontsize=8, x=0.5, pad=4)
im = ax.imshow(MOT_y_images['MOT_TOF_OD'], 
               origin='lower',
               # extent=[xvals.min(),xvals.max(),yvals.min(),yvals.max()]
               )
ax.set_xlabel('X position (um)'); ax.set_ylabel('Y position (um)')


# Show the plot
plt.show()

