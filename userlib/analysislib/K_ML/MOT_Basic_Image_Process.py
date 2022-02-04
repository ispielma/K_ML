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

# Extract the images 'before' and 'after' generated from camera.expose
dark, bright = run.get_images('MOT_x', 'fluorescence', 'dark', 'bright')

# Compute the difference of the two images, after casting them to signed integers
# (otherwise negative differences wrap to 2**16 - 1 - diff)
diff = bright.astype(float) - dark.astype(float)

# Compute a result based on the image processing and save it to the 'results' group


xpts = diff.shape[1]
ypts = diff.shape[0]

xvals = np.linspace(-xpts/2, xpts/2, xpts)
yvals = np.linspace(-ypts/2, ypts/2, ypts)
xy_grids = np.meshgrid(xvals, yvals)

xWidth = 0
yWidth = 0
x0 = 0
y0 = 0

if FIT:
    
    def gauss2d(x, y, offset=0, amplitude=1., centerx=0., centery=0., sigmax=1., sigmay=1.):
        """Return a two dimensional lorentzian.
        """
    
        return amplitude*np.exp(-((x-centerx)/sigmax)**2-((y-centery)/sigmay)**2) + offset
    
    # Now fit to an 2D gauss
    try:
        model = lmfit.Model(gauss2d, independent_vars=['x', 'y'])
        params = model.make_params()
        params['offset'].set(value=diff.max(), min=-5, max=5)
        params['centerx'].set(0, min=1.5*xvals.min(), max=1.5*xvals.max())
        params['centery'].set(0, min=1.5*yvals.min(), max=1.5*yvals.max())
        
        params['amplitude'].set(value=diff.max(), min=0, max=4096)
                
        params['sigmax'].set(value=200, min=10, max=2*xvals.max())
        params['sigmay'].set(value=200, min=10, max=2*yvals.max())

        result = model.fit(diff.ravel(), x=xy_grids[1].ravel(), y=xy_grids[0].ravel(), 
                           params=params)   
    
        xWidth = result.params['sigmax'].value
        yWidth = result.params['sigmay'].value
        
        x0 = result.params['centerx'].value
        y0 = result.params['centery'].value
    except ValueError as err:
        traceback.print_exc()
        FIT=False

run.save_result('Counts', diff.sum())
run.save_result('MaxCounts', diff.max())
run.save_result('xWidth', xWidth) 
run.save_result('yWidth', yWidth) 
run.save_result('x0', x0) 
run.save_result('y0', y0) 

#
# Now plot the current image as well as the running average
#

fig = plt.figure(0,figsize=(4, 3.5))

gs = fig.add_gridspec(1, 3, width_ratios=[2, 1, 1])
gs.update(left=0.12, bottom=0.1, top=0.93, wspace=0.2, hspace=0.4, right=0.99) 
    
ax = fig.add_subplot(gs[0,0])
ax.set_title(r'Current Image', loc='center', fontsize=8, x=0.5, pad=4)
im = ax.imshow(diff, 
               origin='lower',
               extent=[-xpts/2,xpts/2, -ypts/2,ypts/2]
               )

if FIT:
    ax.contour(xvals, yvals, 
               model.eval(x=xy_grids[1], y=xy_grids[0],  params=result.params),
               levels=3, colors='r')
           
ax.set_xlabel('X pixel coordinate')
ax.set_ylabel('Y pixel coordinate')

# Color bar
ax = fig.add_subplot(gs[0,1])
ax.axis('off')
fig.colorbar(im, ax=ax)

# Show the plot
plt.show()

