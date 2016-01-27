## 
# \mainpage Introduction
# The anaglyph Generator generates a stereoscopic anaglyph image from a given
# layered gray level image. Every layer is assigned a specific depth.
# This information is then utilized to generate the stereoscopic image.
# * \ref page_usage
# * \ref page_installation
# * Software \ref page_architecture (maintenance)
#
# ### Example input/output
# \image html demo500.png left: input image, all layers merged. right: generated anaglyph (you need red/cyan glasses)
#
# ### Used software:
# * http://www.gimp.org, the drawing application "The GIMP".
# * http://www.python.org to write the software (a GIMP plugin).
# * http://www.numpy.org (python lib) for simple signal/array processing.
# * http://de.plantuml.com/ to generate UML images.
# * http://www.arc42.org/ software architecture structure.
# * http://www.doxygen.org/ to generate the documentation.
#
#
# \page page_usage Usage
# The plugin is visible in the menu "Filters/Goto 40/Create Anaglyph From Layers".
#
# ### Parameters and simple layer usage
# The plugin has the following parameters:
#  * "min disparity, percent width (near)":
#    * minimum disparity (shift between left and right, generates depth perception)
#    * 0 = no depth (screen)
#    * <0 = between user and screen
#    * >0 = behind screen
#  * "max disparity, percent width (far)":
#    * like min. disparity (should be > min. disparity)
#  * "luminance correction left (0.0..1.0)":
#    * 1.0 = no correction; <1.0 darkens left image
#  * "luminance correction right (0.0..1.0)":
#    * 1.0 = no correction; <1.0 darkens right image
#  * "swap left/right":
#    * normally "no"
#    * "yes" swaps left and right image (you swap the left and right side of your glasses)
#
# Image and layer properties:
#  * Only gray level images with and alpha channel can be used.
#  * All layers must have the full image size.
#  * All layers must have no layer mask (apply before use).
#  * The order of layers is used as depth (most visible layer is nearest).
#
# ### Special layer properties
#  * Layers named "depthmap <name> <float> to <float>" are ignored. They define depth maps with a given value range, which can be used as depth info for other layers.
#  * The name of the layer can overwrite the depth deduced from the layer order:
#    * "background" : a layer without disparity (typically colored in one color).
#    * "depth=<float>" : fixed depth of this layer (0.0=nearest layer, 1.0=farthest layer).
#    * "reldepthmap <name>" : use depth map (is scaled such that the range 0.0 to 1.0 fits the space between two layers).
#    * "fixdepthmap <name>" : use depth map with fixed depths.
#
# Important note when using depthmaps:
#  * Depth is stimulated through an artifical disparity (a shift between left and right image).
#  * The depthmaps specify this shift for every pixel.
#  * However, the depthmaps are used to determine where a pixel comes from and not where it goes to. Thus, a depth map region must be wider than the object is is meant for. Also it may yield strange effects when it as abrupt changes (discontinuities). Best, is to use smooth depth maps, ideally representing a vertical gradient (constant from left to right).
#
# \image html depthmaps500.png images generated with depthmaps (you need red/cyan glasses)
# \image html depthmaps500_expl.png left: gimp screenshot demonstrating the usage of depth maps; right: example depthmap
#
# ### Observations / open points
#  * JPG compression seems to destroy the stereoscopic effect in some cases (artifacts or color corruption?).
#  * On my screen, with my glasses, with my eyes it is helpful to darken the cyan image.
#
# \page page_installation Installation
# You need numpy to execute the plugin (e.g., apt-get install numpy).
# You need to put the plugin code in the gimp plugin search path (e.g. see "Edit/Preferences/Folders/Plug-Ins").
#
# \page page_architecture Architecture
# This page describes the architecture of the software. It helps modifying and maintaining the software. It also demonstrates how to combine numpy (or scipy) with gimp (gimpfu_numpy_converter.py).
#
#   ### Goal
#   Create a tool to generate anaglyphs from (scanned) flat images arranged in depth.
#
#   ### Constraints
#   The selected solution has the following constraints: Plugins must be written in python or scheme. 
#
#   ### Context
#   The context of the plugin is gimp (who owns/calls the plugin)
#   and additional required libraries for signal/image processing.
#
#   ### Solution
#    * Real 3D renderer (blender, povray) were considered to be too complex to use for this task.
#    * A gimp plugin seemed to be a possible solution. 
#     * It allows easy composition of scanned images.
#     * It also allows to scan and pre process the images.
#
#   ### Building Block View
#   The context of the plugin is gimp (who owns/calls the plugin)
#   and additional required libraries.
#   The plugin itself is organized as follows:
#    * Module create_anaglyph_plugin.py (component "Plugin"): The main plugin code (control code)
#    * Module anaglyph_algorithm.py (component "anaglyph_algorithm", class anaglyph_algorithm.Anaglyph): the core algorithm
#    * Module depth_algorithm.py (component "depth_algorithm", class depth_algorithm.DepthAlgo): functions to determine a layers depth
#    * Module gimpfu_numpy_converter.py (component "gimpfu_numpy_converter"): functions to convert from/to gimpfu data structures to/from numpy arrays.
#   \startuml
#    node "Create Anaglyph Plugin" {
#    component [anaglyph_algorithm] #Cyan
#    component [depth_algorithm] #LightBlue
#    component [gimpfu_numpy_converter] #LightGreen
#      [Plugin] ..> [gimpfu_numpy_converter] : use
#      [Plugin] ..> [anaglyph_algorithm] : use
#      [Plugin] ..> [depth_algorithm] : use
#    }
#    [gimpfu_numpy_converter] ..> [numpy] :use
#    [gimpfu_numpy_converter] ..> [gimpfu] :use
#    [anaglyph_algorithm] ..> [numpy] :use
#    [anaglyph_algorithm] ..> [gimpfu] :use
#    [depth_algorithm] ..> [numpy] :use
#    [depth_algorithm] ..> [gimpfu] :use
#    [gimp] ..> [Plugin] :calls
#   \enduml
#
#   ###Runtime View
#   Here we sketch the activities executed by the plugin (create_anaglyph_plugin.run). The colors match the components 
#   corresponding to the described modules above.
#   \startuml
#    start
#    if (check input format and parameters) then (ok)
#     #Cyan:init algorithm output (numpy);
#     while(for each layer of the input image)
#       #LightBlue:determine depth of layer;
#       note left
#        The depth is influenced by the parameters 
#        (e.g. min/max disparity). The depth can be 
#        extracted from the layers' name (keyword 
#        based) or from the natural layer order.
#       end note
#       #LightGreen:convert layer data to numpy array;
#       #Cyan:update algorithm output (numpy);
#       note left
#        The algorithm needs the layers gray 
#        level image representation and the 
#        alpha channel.
#       end note
#       :update progress bar;
#     endwhile
#     :create new image with algorithm output;
#     #LightGreen:convert algorithm output array (numpy) to gimp data;
#     :display output (gimp);
#    else (not ok)
#     :error message;
#       note right
#        parameter checking 
#        is not implemented.
#       end note
#    endif
#    end
#   \enduml
#
#   ###Deployment View:
#   (see \ref page_installation)
#
#   ###Concepts
#    * Data is converted from the gimp format to numpy and back.
#    * Algorithms process on numpy arrays.
# 

