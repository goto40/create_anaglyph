from gimpfu import *
import numpy

def layer2array(layer,dtype=None):
    """!
    converts a layer to an array.
    @param layer a gimp layer
    @param dtype the requested output type (optional)
    @return a numpy array representing the layer (height x width x channels)
    """
    r = layer.get_pixel_rgn(0, 0, layer.width, layer.height, False, False)
    m = numpy.reshape(numpy.fromstring(r[:,:],dtype=numpy.uint8),(r.h,r.w,r.bpp))
    if dtype!=None:
        return numpy.array(m, dtype=dtype)
    else:
        return m

def copy_array_into_layer(data, layer):
    """!
    copies an array into a layer. (image/layer size must match)
    @param layer a gimp layer
    @param data a numpy array representing the layer (height x width x channels; must match the layers' size/channels). The data is converted into uint8.
   """
    r = layer.get_pixel_rgn(0, 0, layer.width, layer.height, False, False)
    data8 = numpy.array(data[:],dtype=numpy.uint8);
    r[:,:] = data8.tostring()


