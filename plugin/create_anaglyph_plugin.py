#! /usr/bin/env python
from gimpfu import *
import os
from gimpfu_numpy_converter import *
from anaglyph_algorithm import Anaglyph
from depth_algorithm import DepthAlgo

def run(timg, tdrawable, mindisp, maxdisp,f1,f2,swap_lr):
    """! Plugin main function. Combines layers to form an anaglyph."""
    # init algo        
    anaglyph = Anaglyph(f1,f2)
    depthalgo = DepthAlgo(timg, mindisp, maxdisp)

    n=1
    nmax=len(timg.layers)
    for layer in reversed(timg.layers):
        print layer.name
        if not depthalgo.is_depth_map(layer):
            # convert layer data to numpy array
            mf = layer2array(layer, dtype=numpy.float)

            # determine depth
            d = depthalgo.get_disparity(layer)

            # update algo and progress bar        
            if (depthalgo.has_map(layer)):
                anaglyph.update_ext(mf,d)
            else:
                anaglyph.update(mf,d)

            pdb.gimp_progress_update(float(n)/float(nmax))
            n=n+1
    
    # create new output image
    new_image = pdb.gimp_image_new(timg.width, timg.height, RGB); 
    new_layer = pdb.gimp_layer_new(new_image, timg.width, timg.height, RGB, "main", 100.0, NORMAL_MODE)
    pdb.gimp_layer_add_alpha(new_layer)
    new_image.add_layer(new_layer)

    # convert algorithm output array (numpy) to gimp data
    copy_array_into_layer(anaglyph.get_result(swap_lr), new_layer)

    # display new image
    display = pdb.gimp_display_new(new_image)

print("registering create_anaglyph plugin.")
register(
    "create_anaglyph", 
    """Create an anaglyph from layers (generates a new image)
Layers named depth=<float> specify a fixed depth from 0 (near) to 1(far). Values outside 0..1 are also possible.""", "", "", "", "",
    "<Toolbox>/Xtns/Goto40/Create Anaglyph From Layers", 
    "GRAY*",
    [
    (PF_IMAGE,      "image",    "Input image",      None),
    (PF_DRAWABLE,   "drawable", "Input drawable",   None),
    (PF_FLOAT,        "mindisp",   "min disparity, percent width (near)",        0.0),
    (PF_FLOAT,        "maxdisp",   "max disparity, percent width (far)",        2.0),
    (PF_FLOAT,      "left_factor",   "luminance correction left (0.0..1.0)",        1.0),
    (PF_FLOAT,      "right_factor",   "luminance correction right (0.0..1.0)",        0.8),
    (PF_BOOL,      "swap_lr",   "swap left/right",        False),
#optional:    (PF_OPTION,     "mode",     "conversion mode",  0, ["layers","encoded"]),
    ],
    [],
    run
    )

main()

