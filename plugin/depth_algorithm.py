import re
from gimpfu_numpy_converter import *

class DepthAlgo:
    """!
    This class is responsible to compute the depth of a layer. This can be a single depth value or a depth map.
    """
    def __init__(self, gimp_image, mindisp, maxdisp):
        """!
        Creates a DepthAlgo.
        @param gimp_image the gimp image to be processed        
        @param min_disp the minimum disparity to be processed (relative to image width)        
        @param max_disp the maximum disparity to be processed (relative to image width)        
        """
        self.gimp_image = gimp_image
        self.mindisp = mindisp
        self.maxdisp = maxdisp
        self.n=0
        self.depthmaps={}
        self.normallayers=[]
        for layer in reversed(gimp_image.layers):
            m = self.is_depth_map(layer) 
            isnormal = not( m or self.has_fixdepthmap(layer) or self.has_depth(layer))
            if isnormal:
                #print("normal layer: %s --> %d"%(layer.name,self.n))
                self.n+=1
                self.normallayers.insert(0,layer)
            elif m:
                data = layer2array(layer, dtype=numpy.float)
                data = data[:,:,0]
                assert(data.max()>data.min())
                data = (data-data.min())/(data.max()-data.min())*1.0
                mi = float(m.group(2))
                ma = float(m.group(3))
                assert(ma>mi)
                self.depthmaps[m.group(1)] = mi+data*(ma-mi)
        #print("layer count n==%d"%(self.n))


    def is_depth_map(self, gimp_layer):
        """!
        Determines if a layer is a depth map.
        @param gimp_layer the layer to be investigated.
        @return the matcher containing (name, mindepth, maxdepth) or None (logically maps to a boolean)
        """
        pat = re.compile(r'depthmap\s+(\w+)\s+(-?[\d\.]+)\s+to\s+(-?[\d\.]+)')
        m=pat.match(gimp_layer.name)
        return m

    def has_map(self, gimp_layer):
        """! 
        @param gimp_layer the layer to be investigated.
        @return if this layer has a depth map (or a single depth for the whole layer)
        """
        return bool(self.has_reldepthmap(gimp_layer)) or bool(self.has_fixdepthmap(gimp_layer))

    def has_reldepthmap(self, gimp_layer):
        """! Determines if a layer has (uses) a depth map as relative map (relative depth values between the neighboring layers)
        @param gimp_layer the layer to be investigated.
        @return the matcher containing the map name or None (logically maps to a boolean)
        """
        pat = re.compile(r'reldepthmap\s*=\s*(\w+)')
        m=pat.match(gimp_layer.name)
        return m

    def has_fixdepthmap(self, gimp_layer):
        """! Determines if a layer has (uses) a depth map as fixed map fixed depth values)
        @param gimp_layer the layer to be investigated.
        @return the matcher containing the map name or None (logically maps to a boolean)
        """
        pat = re.compile(r'fixdepthmap\s*=\s*(\w+)')
        m=pat.match(gimp_layer.name)
        return m

    def has_depth(self, gimp_layer):
        """! Determines if a used depth is specified for the layer
        @param gimp_layer the layer to be investigated.
        @return the matcher containing the map depth (logically maps to a boolean)
        """
        n=gimp_layer.name
        if (n.startswith("background")):
            n="depth=0" 
        pat = re.compile(r'depth=(-?[\d\.]+)')
        m=pat.match(n)
        return m

    def get_disparity(self, gimp_layer):
        """! Determines the depth value or the map of depth values of a layer
        @param gimp_layer the layer to be investigated.
        @retrun the depth value (as absolute disparity in pixels) either as single value or as array of values.
        """
        idx = self.gimp_image.layers.index(gimp_layer) # raises exception on error
        mrel=self.has_reldepthmap(gimp_layer)
        mfix=self.has_fixdepthmap(gimp_layer)
        if self.n>1:
            d = float(idx)/float(self.n-1)
        else:
            d = 0
        if self.has_map(gimp_layer):
            if mrel:
                print("relative map detected: "+gimp_layer.name)
                d0 = d-float(1.0/(self.n-1))
                d1 = d+float(1.0/(self.n-1))
                assert(mrel.group(1) in self.depthmaps.keys())
                d = self.depthmaps[mrel.group(1)]
                d =  d0+d*(d1-d0)
            else:
                print("fixed map detected: "+gimp_layer.name)
                assert(mfix.group(1) in self.depthmaps.keys())
                d = self.depthmaps[mfix.group(1)]
            d = self.mindisp+float(self.maxdisp-self.mindisp)*d
            return numpy.floor(0.5+d*self.gimp_image.width/100.0)
        else:
            m=self.has_depth(gimp_layer)
            if (m):
                d = float(m.group(1))
                #print("detected fixed depth: %s=rel. %f"%(gimp_layer.name,d))
            else:
                idx = self.normallayers.index(gimp_layer) # raises exception on error
                if self.n>1:
                    d = float(idx)/float(self.n-1)
                else:
                    d = 0

            d = self.mindisp+float(self.maxdisp-self.mindisp)*d
            #print("***** depth, idx=%d, d=%f"%(idx,d))
            return int(0.5+d*self.gimp_image.width/100.0)
            

