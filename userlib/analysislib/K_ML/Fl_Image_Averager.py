import lyse
import os
from pathlib import Path
import matplotlib.pyplot as plt

# Is this script being run from within an interactive lyse session?
if lyse.spinning_top:
    # If so, use the filepath of the current shot
    h5_path = lyse.path
else:
    # If not, get the filepath of the last shot of the lyse DataFrame
    df = lyse.data()
    h5_path_and_file = df.filepath.iloc[-1]
    ShotId, _ = os.path.split(h5_path_and_file)

# Instantiate a lyse.Run object for this shot
run = lyse.Run(h5_path_and_file)

# Get a dictionary of the global variables used in this shot
run_globals = run.get_globals()

# Extract the images 'before' and 'after' generated from camera.expose
dark, bright = run.get_images('MOT_x', 'fluorescence', 'dark', 'bright')

# Compute the difference of the two images, after casting them to signed integers
# (otherwise negative differences wrap to 2**16 - 1 - diff)
diff = bright.astype(float) - dark.astype(float)

# Accumulate Average

if hasattr(lyse.routine_storage, 'LastShotId'):
    LastShotId = lyse.routine_storage.LastShotId
else:
    LastShotId = None
    
if ShotId == LastShotId:
    # We are averaging!
    lyse.routine_storage.shots += 1
    lyse.routine_storage.sum += diff
else:
    # We are resetting
    lyse.routine_storage.shots = 1
    lyse.routine_storage.sum = diff.copy()

lyse.routine_storage.LastShotId = ShotId

#
# Now plot the current image as well as the running average
#

fig = plt.figure(0,figsize=(7, 3.5))

gs = fig.add_gridspec(1, 2)
gs.update(left=0.12, bottom=0.1, top=0.93, wspace=0.05, hspace=0.4, right=0.99) 
    

ax = fig.add_subplot(gs[0,0])
ax.set_title(r'Current Image', loc='center', fontsize=8, x=0.5, pad=4)
ax.imshow(diff)
ax.set_xlabel('X pixel coordinate')
ax.set_ylabel('Y pixel coordinate')

ax = fig.add_subplot(gs[0,0])
ax.set_title(r'Average Image', loc='center', fontsize=8, x=0.5, pad=4)
ax.imshow(lyse.routine_storage.sum / lyse.routine_storage.counts )
ax.set_xlabel('X pixel coordinate')
ax.set_ylabel('Y pixel coordinate')

# Show the plot
plt.show()

# Compute a result based on the image processing and save it to the 'results' group of
# the shot file
# result = diff.std()
# run.save_result('foobar', result)
