from gimpfu import *
import numpy

# interp2-like function from matlab
def interp2(X,Y,Z):
    """! interpolates Z at locations X,Y
    output of function is of shape(X)==shape(Y)
    """
    from numpy import *
    X1 = array(floor(X),dtype=int);
    X2 = array(ceil(X),dtype=int);
    Y1 = array(floor(Y),dtype=int);
    Y2 = array(ceil(Y),dtype=int);

    M1 = logical_or(logical_or(Y1<0,Y1>=Z.shape[0]),logical_or(Y2<0,Y2>=Z.shape[0]))
    M2 = logical_or(logical_or(X1<0,X1>=Z.shape[1]),logical_or(X2<0,X2>=Z.shape[1]))
    M = logical_not(logical_or(M1,M2));

    X1[X1<0]=0;
    X1[X1>=Z.shape[1]]=Z.shape[1]-1;
    X2[X2<0]=0;
    X2[X2>=Z.shape[1]]=Z.shape[1]-1;
    XR = X-X1;
    Y1[Y1<0]=0;
    Y1[Y1>=Z.shape[0]]=Z.shape[0]-1;
    Y2[Y2<0]=0;
    Y2[Y2>=Z.shape[0]]=Z.shape[0]-1;
    YR = Y-Y1;
    ERG1 = Z[Y1,X1]+(Z[Y1,X2]-Z[Y1,X1])*XR;
    ERG2 = Z[Y2,X1]+(Z[Y2,X2]-Z[Y2,X1])*XR;
    ERG  = ERG1+(ERG2-ERG1)*YR;
    return ERG,M;

class Anaglyph:
    """! This class represents an algorithm to compute two stereo images from gimp layers and to combine them to an anaglyph. """
    def __init__(self, f1=1.0, f2=1.0):
        """! Creates an anaglyph algorithm.
        @param f1 the darkening factor for the left image (1.0 = no modification)
        @param f2 the darkening factor for the left image (1.0 = no modification)
        """
        self.f1=f1
        self.f2=f2
        self.imsum = None
        self.left  = None
        self.right = None
        self.aleft  = None
        self.aright = None

    def shiftx(self,img,d):
        """! Helper function to shift an image with a given disparity value. """
        res = numpy.roll(img,d,axis=1)
        if (d>0):
            res[:,:d]=0
        elif (d<0):
            res[:,d:]=0
        return res

    def shiftx_ext(self,img,d):
        """! Helper function to shift an image with a given disparity map. """
        w = d.shape[1]
        h = d.shape[0]
        x,y = numpy.meshgrid(numpy.arange(w),numpy.arange(h))
        x = x-d
        res,m = interp2(x,y,img);
        return res*m
        

    def update(self, layer_data, d):
        """! Update the image using a single depth value
        @param layer_data the layer to be added (as numpy array)
        @param d the disparity of the layer
        """
        h = layer_data.shape[0]
        w = layer_data.shape[1]
        if layer_data.shape[2]==1:
            tmp = numpy.ones((h,w,2))
            tmp[:,:,1]=numpy.reshape(layer_data,(h,w))
            layer_data=tmp
        if self.left==None:
            self.left  = numpy.zeros((h,w))
            self.right = numpy.zeros((h,w))
            self.aleft  = numpy.zeros((h,w))
            self.aright = numpy.zeros((h,w))
        else:
            assert(self.left.shape == (h,w), "shape must not change")
            
        imleft  = self.shiftx(layer_data[:,:,0],-d)
        imright = self.shiftx(layer_data[:,:,0],+d)
        alphaleft  = self.shiftx(layer_data[:,:,1],-d)
        alpharight = self.shiftx(layer_data[:,:,1],+d)
   
        self.left  = (self.left *(255-alphaleft )+imleft *alphaleft )/255
        self.right = (self.right*(255-alpharight)+imright*alpharight)/255
        self.aleft  = numpy.maximum(alphaleft,  self.aleft)
        self.aright = numpy.maximum(alpharight, self.aright)

    def update_ext(self, layer_data, d):
        """! Update the image using a depth map
        @param layer_data the layer to be added (as numpy array)
        @param d the disparity map of the layer
        """
        h = layer_data.shape[0]
        w = layer_data.shape[1]
        if self.left==None:
            self.left  = numpy.zeros((h,w))
            self.right = numpy.zeros((h,w))
            self.aleft  = numpy.zeros((h,w))
            self.aright = numpy.zeros((h,w))
        else:
            assert(self.left.shape == (h,w), "shape must not change")
            
        imleft  = self.shiftx_ext(layer_data[:,:,0],-d)
        imright = self.shiftx_ext(layer_data[:,:,0],+d)
        alphaleft  = self.shiftx_ext(layer_data[:,:,1],-d)
        alpharight = self.shiftx_ext(layer_data[:,:,1],+d)
   
        self.left  = (self.left *(255-alphaleft )+imleft *alphaleft )/255
        self.right = (self.right*(255-alpharight)+imright*alpharight)/255
        self.aleft  = numpy.maximum(alphaleft,  self.aleft)
        self.aright = numpy.maximum(alpharight, self.aright)

    def get_result(self,swap_lr):
        """! Combines the result collected so far (left and right image) as anaglyph. 
        @param swap_lr if true the left and right image are swapped.
        @return a numpy array representing the result image with 4 (RGBA) channels.
        """
        a = numpy.zeros((self.left.shape[0],self.left.shape[1],4))
        if swap_lr:
            r = self.left
            l = self.right
        else:
            l = self.left
            r = self.right            
        a[:,:,0] = l*self.f1 + (1-self.f1)/2
        a[:,:,1] = r*self.f2 + (1-self.f2)/2
        a[:,:,2] = r*self.f2 + (1-self.f2)/2
        a[:,:,3] = numpy.maximum(self.aleft,self.aright)
        return a
