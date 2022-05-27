import lyse
import numpy as np
import scipy

import lmfit
import os
import matplotlib.pyplot as plt
import traceback

def AbsImg(atoms, bright, dark):
    a = atoms - dark
    b = bright - dark
    
    a[a<1] = 1
    b[b<1] = 1
    
    return -np.log(a/b)

FIT = True
ReduceImage = 4 # factor to reduce image

Error = False # Test for error states

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

try:
    fl_keys = ['MOT', 'cMOT', 'MOT_dark', 'cMOT_dark']
    MOT_x_images = run.get_images_dict('MOT_x', 'fluorescence', *fl_keys)
    MOT_z_images = run.get_images_dict('MOT_z', 'fluorescence', *fl_keys)
    
    abs_keys = ['MOT_TOF', 'MOT_TOF_probe', 'MOT_TOF_dark']
    MOT_y_images = run.get_images_dict('MOT_y', 'absorption', *abs_keys)
except:
    # OK so an image was missing!
    Error = True

# Try to get scope traces
try:
    ScopeTraces = run.get_trace('ComputerScope1', raw_data=True)
    print('GotScope')
except:
    ScopeTraces = None

# Compute the difference of the two images, after casting them to signed integers
# (otherwise negative differences wrap to 2**16 - 1 - diff)
try:
    MOT_x_images['MOT_diff'] = MOT_x_images['MOT'].astype(float) - MOT_x_images['MOT_dark'].astype(float)
    MOT_x_images['cMOT_diff'] = MOT_x_images['cMOT'].astype(float) - MOT_x_images['cMOT_dark'].astype(float)
    
    MOT_z_images['MOT_diff'] = MOT_z_images['MOT'].astype(float) - MOT_z_images['MOT_dark'].astype(float)
    MOT_z_images['cMOT_diff'] = MOT_z_images['cMOT'].astype(float) - MOT_z_images['cMOT_dark'].astype(float)
    
    MOT_y_images['MOT_TOF_OD'] = AbsImg(MOT_y_images['MOT_TOF'].astype(float), MOT_y_images['MOT_TOF_probe'].astype(float),
                                        MOT_y_images['MOT_TOF_dark'].astype(float) )
except:
    # An image contained bad data (often the case when a data transfer error
    # occured)
    Error = True

if Error:
    Counts = np.nan
    MaxCounts = np.nan
    xWidth = np.nan
    yWidth = np.nan
    x0 = np.nan
    y0 = np.nan
else:
    
    
    OD = MOT_y_images['MOT_TOF_OD']
    
    Counts = OD.sum()
    MaxCounts = OD.max()
    xWidth = 0
    yWidth = 0
    x0 = 0
    y0 = 0  
    
    xpts = OD.shape[1]
    ypts = OD.shape[0]
    OD_extent = np.array([-run_globals['Camera_MOT_y_pixel_size']*xpts/2,
                          run_globals['Camera_MOT_y_pixel_size']*xpts/2,
                          -run_globals['Camera_MOT_y_pixel_size']*ypts/2,
                          run_globals['Camera_MOT_y_pixel_size']*ypts/2]) 

    if FIT:

        #
        # Perform a simple gaussian fit to the AI image and save it to the 'results' group
        #
        
        def gauss2d(x, y, offset=0, amplitude=1., centerx=0., centery=0., sigmax=1., sigmay=1.):
            """Return a two dimensional lorentzian.
            """
        
            return amplitude*np.exp(-0.5*((x-centerx)/sigmax)**2-0.5*((y-centery)/sigmay)**2) + offset
        
        # Now reduce the image size for faster fitting
        
        OD = scipy.ndimage.zoom(OD, 1/ReduceImage)
        
        xpts = OD.shape[1]
        ypts = OD.shape[0]

        xvals = np.linspace(-xpts/2, xpts/2, xpts)*run_globals['Camera_MOT_y_pixel_size']*ReduceImage
        yvals = np.linspace(-ypts/2, ypts/2, ypts)*run_globals['Camera_MOT_y_pixel_size']*ReduceImage

        xy_grids = np.meshgrid(xvals, yvals)

        # Now fit to an 2D gauss
        try:
            model = lmfit.Model(gauss2d, independent_vars=['x', 'y'])
            params = model.make_params()
            params['offset'].set(value=OD.max(), min=-5, max=5)
            params['centerx'].set(0, min=0.5*xvals.min(), max=0.5*xvals.max())
            params['centery'].set(0, min=0.5*yvals.min(), max=0.5*yvals.max())
            
            params['amplitude'].set(value=OD.max(), min=0, max=4096)
                    
            params['sigmax'].set(value=3000, min=500, max=4*xvals.max())
            params['sigmay'].set(value=3000, min=500, max=4*yvals.max())
    
            result = model.fit(OD.ravel(), x=xy_grids[1].ravel(), y=xy_grids[0].ravel(), 
                               params=params)   
            
            MaxCounts = result.params['amplitude'].value
            
            xWidth = result.params['sigmax'].value
            yWidth = result.params['sigmay'].value
            
            # this was messing with the computed PSD in some cases because of bad
            # fits with large widths.
            # Counts = 2*np.pi*MaxCounts * xWidth* yWidth
            
            x0 = result.params['centerx'].value
            y0 = result.params['centery'].value
        except ValueError as err:
            traceback.print_exc()
            FIT=False    

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
    ax.set_ylabel('Y position (um)')

    ax = fig.add_subplot(gs[1,0])
    ax.set_title(r'x cMOT', loc='center', fontsize=8, x=0.5, pad=4)
    im = ax.imshow(MOT_x_images['cMOT_diff'], 
                   origin='lower',
                   # extent=[xvals.min(),xvals.max(),yvals.min(),yvals.max()]
                   )
    ax.set_xlabel('X position (um)'); ax.set_ylabel('Y position (um)')

    ax = fig.add_subplot(gs[0,1])
    ax.set_title(r'z MOT', loc='center', fontsize=8, x=0.5, pad=4)
    im = ax.imshow(MOT_z_images['MOT_diff'], 
                   origin='lower',
                   # extent=[xvals.min(),xvals.max(),yvals.min(),yvals.max()]
                   )

    ax = fig.add_subplot(gs[1,1])
    ax.set_title(r'z cMOT', loc='center', fontsize=8, x=0.5, pad=4)
    im = ax.imshow(MOT_z_images['cMOT_diff'], 
                   origin='lower',
                   # extent=[xvals.min(),xvals.max(),yvals.min(),yvals.max()]
                   )
    ax.set_xlabel('X position (um)'); 

    ax = fig.add_subplot(gs[0,2])
    ax.set_title(r'y MOT TOF', loc='center', fontsize=8, x=0.5, pad=4)
    im = ax.imshow(MOT_y_images['MOT_TOF_OD'], 
                   origin='lower',
                   extent=OD_extent
                   )

    if FIT:
        ax.contour(xvals, yvals, 
                   model.eval(x=xy_grids[1], y=xy_grids[0],  params=result.params),
                   levels=3, colors='r')
        
    ax.set_xlabel('X position (um)');

    ax = fig.add_subplot(gs[1,2])
    ax.set_title(r'y MOT TOF raw', loc='center', fontsize=8, x=0.5, pad=4)
    im = ax.imshow(MOT_y_images['MOT_TOF_probe'].astype(float) - MOT_y_images['MOT_TOF_dark'].astype(float), 
                   origin='lower',
                   extent=OD_extent
                   )
    ax.set_xlabel('X position (um)');


    # Show the plot
    plt.show()



#
# Save desired data
#

run.save_result('Counts', Counts)
run.save_result('MaxCounts', MaxCounts)
run.save_result('xWidth', xWidth) 
run.save_result('yWidth', yWidth) 
run.save_result('PSD', Counts / (xWidth*yWidth) ) # Fake PSD

run.save_result('x0', x0) 
run.save_result('y0', y0) 



