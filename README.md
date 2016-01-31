# GIMP Plugin "create_anaglyph"
GIMP Plugin to create Anaglyphs.
## Caution
The anaglyphs (stereo images) generated with this plugin may cause eyestrain or headache. Do not look too long at these images, especially if you compose images with conflicting or imperfect depth cues: e.g. stereoscopic depths information conflicting with (unlogical) occlusion information. 
## Examples
Left: input image (all layers merged), right: output anaglyph (you need red/cyan glasses):
![Example Anaglyph](/doc/images/demo500.png?raw=true "Left: input image (all layers merged), right: output anaglyph (you need red/cyan glasses)")

Examples with depth maps (you need red/cyan glasses):
![Example Anaglyphs with depth maps](/doc/images/depthmaps500.png?raw=true "Examples with depth maps (you need red/cyan glasses)")

Example of a simple comic strip (you need red/cyan glasses):
![Example of a simple comic strip](/doc/images/comicdemo.png?raw=true "Example of a simple comic strip (you need red/cyan glasses)")
## Documentation
The plugin and the plugin code, both, are described as [doxygen documentation](http://goto40.github.io/create_anaglyph/) included in the source files.
 * Usage
 * Installation
 * Architecture

Note: This small example demonstrates 
 * how to combine the python libraries numpy with GIMP (see [API doc](http://goto40.github.io/create_anaglyph/)). 
 * how to use doxygen with python (see [API doc](http://goto40.github.io/create_anaglyph/)).
 * how to use UMLPlant with doxygen and python (see [API doc](http://goto40.github.io/create_anaglyph/); manual adaptation of the doc/Doxyfile to your system is necessary).
