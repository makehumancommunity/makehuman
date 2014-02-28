#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier, Glynn Clements,
                       Thanasis Papoutsidakis

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Various image processing operations.
"""

import numpy
from image import Image
from progress import Progress


'''
Unary graphical image operations
'''

def blurred(img, level=10.0, kernelSize = 15):
    """
    Apply a gaussian blur on the specified image. Returns a new blurred image.
    level is the level of blurring and can be any float.
    kernelSize is the size of the kernel used for convolution, and dictates the
    number of samples used, requiring longer processing for higher values.
    KernelSize should be a value between 5 and 30

    Based on a Scipy lecture example from https://github.com/scipy-lectures/scipy-lecture-notes
    Licensed under Creative Commons Attribution 3.0 United States License
    (CC-by) http://creativecommons.org/licenses/by/3.0/us
    """

    progress = Progress(0, None) (0)

    kernelSize = int(kernelSize)
    if kernelSize < 5:
        kernelSize = 5
    elif kernelSize > 30:
        kernelSize = 30

    # prepare an 1-D Gaussian convolution kernel
    t = numpy.linspace(-20, 20, kernelSize)
    bump = numpy.exp(-0.1*(t/level)**2)
    bump /= numpy.trapz(bump) # normalize the integral to 1
    padSize = int(kernelSize/2)
    paddedShape = (img.data.shape[0] + padSize, img.data.shape[1] + padSize)
    progress(0.15)

    # make a 2-D kernel out of it
    kernel = bump[:,numpy.newaxis] * bump[numpy.newaxis,:]

    # padded fourier transform, with the same shape as the image
    kernel_ft = numpy.fft.fft2(kernel, s=paddedShape, axes=(0, 1))
    progress(0.4)

    # convolve
    img_ft = numpy.fft.fft2(img.data, s=paddedShape, axes=(0, 1))
    progress(0.65)
    img2_ft = kernel_ft[:,:,numpy.newaxis] * img_ft
    data = numpy.fft.ifft2(img2_ft, axes=(0, 1)).real
    progress(0.9)

    # clip values to range
    data = numpy.clip(data, 0, 255)
    progress(1.0)

    return Image(data = data[padSize:data.shape[0], padSize:data.shape[1], :])

'''
Unary arithmetic image operations
'''

def clip(img):
    data = Image(data = img).data
    return Image(data = clipData(data).astype(numpy.uint8))

def clipData(data):
    return numpy.clip(data,0,255)

def normalize(img):
    data = Image(data = img).data
    return Image(data = normalizeData(data).astype(numpy.uint8))

def normalizeData(data):
    return (data.astype(float) * (255.0/float(data.max())) + 0.5).astype(int)

def invert(img):
    data = Image(data = img).data
    return Image(data = invertData(data).astype(numpy.uint8))

def invertData(data):
    if data.shape[2] in (2, 4):
        # Avoid inverting alpha channel.
        return numpy.dstack((255 - data[...,:-1], data[:,:,-1:]))
    else:
        return (255 - data)

'''
Binary arithmetic image operations
'''

def mix(img1, img2, weight1, weight2 = None):
    if img1 is None and img2 is None:
        return None
    img1 = Image(data = img1 if not (img1 is None) else getBlack(img2))
    img2 = Image(data = img2 if not (img2 is None) else getBlack(img1))
    img1, img2 = synchronizeChannels(img1, img2)
    return Image(data = mixData(img1.data, img2.data, weight1, weight2).astype(numpy.uint8))

def mixData(data1, data2, weight1, weight2 = None):
    if weight2 is None:
        weight2 =  1 - weight1
    return (weight1*data1.astype(float) +
            weight2*data2.astype(float) + 0.5).astype(int)

def multiply(img1, img2):
    if img1 is None and img2 is None:
        return None
    img1 = Image(data = img1 if not (img1 is None) else getWhite(img2))
    img2 = Image(data = img2 if not (img2 is None) else getWhite(img1))
    img1, img2 = synchronizeChannels(img1, img2)
    return Image(data = multiplyData(img1.data, img2.data).astype(numpy.uint8))

def multiplyData(data1, data2):
    return ((data1.astype(float) * data2.astype(float)) / 255.0 + 0.5).astype(int)

'''
Binary bitwise image operations
'''

def bitwiseAnd(img1, img2):
    if img1 is None and img2 is None:
        return None
    img1 = Image(data = img1 if not (img1 is None) else getWhite(img2))
    img2 = Image(data = img2 if not (img2 is None) else getWhite(img1))
    img1, img2 = synchronizeChannels(img1, img2)
    return Image(data = bitwiseAndData(img1.data, img2.data).astype(numpy.uint8))

def bitwiseAndData(data1, data2):
    return numpy.bitwise_and(data1, data2)

def bitwiseOr(img1, img2):
    if img1 is None and img2 is None:
        return None
    img1 = Image(data = img1 if not (img1 is None) else getBlack(img2))
    img2 = Image(data = img2 if not (img2 is None) else getBlack(img1))
    img1, img2 = synchronizeChannels(img1, img2)
    return Image(data = bitwiseOrData(img1.data, img2.data).astype(numpy.uint8))

def bitwiseOrData(data1, data2):
    return numpy.bitwise_or(data1, data2)

'''
Image synthesis
'''

def compose(channels):
    # 'channels' is a sequence of Images.
    outch = []
    i = 0
    for c in channels:
        if c.components == 1:
            outch.append(c.data[:,:,0:1])
        else:
            if c.components < i:
                raise TypeError("Image No. %i has not enough channels" % i)
            outch.append(c.data[:,:,i:i+1])
        i += 1
    return Image(data = numpy.dstack(outch).astype(numpy.uint8))

def colorAsImage(color, image = None, width = None, height = None):
    """
    Create or modify an image filled with a single color.
    """
    components = min(4, len(color))
    color = color[:components]
    if isinstance(color[0], float):
        color = (numpy.asarray(color, dtype=float) * 255 + 0.5).astype(numpy.uint8)
    else:
        color = numpy.asarray(color, dtype=numpy.uint8)
        
    if image:
        if image.components != components:
            raise TypeError("Color (%s) does not have same amount of channels as image (%s)" % (color, image.components))
        image.data[:,:] = color
        image.markModified()
        return image
    else:
        if width and height:
            return Image(data = numpy.tile(color, (height, width)).reshape((height, width, components)))
        else:
            raise TypeError("Specify either image or width and height.")

def getBlack(img):
    """
    Get a single black channel with the dimensions of the specified image.
    """
    return colorAsImage([0], image=None, width=img.height, height=img.width)

def getWhite(img):
    """
    Get a single white channel with the dimensions of the specified image.
    """
    return colorAsImage([255], image=None, width=img.height, height=img.width)

'''
Image analysis
'''

def getAlpha(img):
    """
    Returns the alpha channel of the specified image.
    """
    if img.components in (2, 4):
        return Image(data = img.data[..., -1][..., None])
    else:
        return getWhite(img)

def getChannel(img, channel):
    """
    Create a new monochrome image from a single channel of another image.
    """
    return Image(data = img.data[..., channel][..., None])

'''
Image conversions
'''

def resized(img, width, height):
    sw, sh = img.size
    if width is sw and height is sh:
        return Image(img)
    xmap = numpy.floor((numpy.arange(width) + 0.5) * sw / float(width)).astype(int)
    ymap = numpy.floor((numpy.arange(height) + 0.5) * sh / float(height)).astype(int)
    return Image(data = img.data[ymap,:][:,xmap])

def removeAlpha(img):
    return img.convert(img.components - 1 + img.components % 2)

def addAlpha(img, alpha = None):
    if alpha:
        return compose(
            [img] * (img.components - 1 + img.components % 2) + [alpha])
    else:
        return img.convert(img.components + img.components % 2)
    
def synchronizeChannels(img1, img2):
    if img1.components > img2.components:
        img2 = img2.convert(img1.components)
    else:
        img1 = img1.convert(img2.components)
    return img1, img2

'''
Mask manipulation
'''

def growMask(img, radius = 1, step = 1):
    """Grow a mask by a number of pixels."""
    out = Image(img)
    for i in xrange(int(float(radius)/float(step)+0.5)):
        out = expandMask(out, False, step)
    return out

def shrinkMask(img, radius = 1, step = 1):
    """Shrink a mask by a number of pixels."""
    out = Image(img)
    for i in xrange(int(float(radius)/float(step)+0.5)):
        out = expandMask(out, True, step)
    return out

def expandMask(img, shrink = False, step = 1):
    """Grow or shrink a mask by a pixel."""
    if shrink:
        img = invert(img)
    img = jitterSum(img.data, step) > 0
    img = Image(data = img.astype(numpy.uint8)*255)
    if shrink:
        img = invert(img)
    return img

def expand(img, mask, pixels):
    """
    Expand an image away from its borders defined by mask by
    an amount of pixels. The function returns the expanded
    image and mask.
    """

    for i in xrange(int(pixels+0.5)):
        expansion = jitterSum(img.data).astype(float)/255.0
        expmask = jitterSum(mask.data > 0)
        newmask = (expmask == 0).astype(numpy.uint8)
        expmask += newmask
        expansion /= expmask
        expansion = bitwiseAnd(invert(mask), (255.0*expansion+0.5).astype(numpy.uint8))
        img = bitwiseOr(bitwiseAnd(img, mask), expansion)
        mask = invert(newmask * 255)
        
    return img, mask

def jitterSum(data, step = 1):
    """
    Sum all pixels  of an image with their neighbours.
    """

    neighbours = numpy.empty((3, 3) + data.shape, dtype=numpy.uint16)
    neighbours[1,1] = data

    neighbours[1,0] = numpy.roll(neighbours[1,1], -step, axis=-2)
    neighbours[1,2] = numpy.roll(neighbours[1,1],  step, axis=-2)
    neighbours[0] = numpy.roll(neighbours[1], -step, axis=-3)
    neighbours[2] = numpy.roll(neighbours[1],  step, axis=-3)

    neighbours[1] += neighbours[0] + neighbours[2]
    neighbours[1,1] += neighbours[1,0] + neighbours[1,2]

    return neighbours[1,1]

