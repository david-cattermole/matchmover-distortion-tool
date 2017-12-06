"""Convert Matchmover distortion values into 3DE distortion values."""

# Copyright David Cattermole, 2013
# Licensed under the GNU General Public License, 
# see "COPYING.txt" for more details.

import math
import os
import os.path as p

import commonDataObjects as cdo
import mmFileReader

def mmToTdeConvertDistortion(dst, fl, alpha,
                             fbw, fbh,
                             width, height):
    """Converts Matchmover lens distortion into 3DE lens distortion.

    dst - distortion value.
    fl - The focal, (focalLength*width)/filmbackWidth.
    alpha - The pixel aspect ratio.
    fbw, fbh - Filmback Width/Height.
    width, height - Image Width/Height.
    """
    fbw = fbw * alpha
    hwidth = width/2.0
    hheight = height/2.0
    rr = (hwidth*hwidth)+(hheight*hheight)/(alpha*alpha)

    # calculate the distance between the undistorted and distorted coordinates
    # (in Shake coords), then, get the difference between them, that is the
    # matchmover distortion value!
    k = dst/(fl*fl)

    # calculate new distorted point
    newr = 1.0+k*rr
    newptx = hwidth*newr
    newpty = hheight*newr
    diffx = (hwidth-newptx)
    diffy = (hheight-newpty)

    # get the top-right most point, and the distorted point too,
    # and get the ratio.
    ld1 = (math.sqrt((hwidth*hwidth)+(hheight*hheight))/2)
    ld2 = (math.sqrt((newptx*newptx)+(newpty*newpty))/2)
    ld = (ld2/ld1)-1.0

    return ld


def convertValue(inValue, inUnit, outUnit):
    assert (isinstance(inValue, int) or 
            isinstance(inValue, float) or 
            isinstance(inValue, cdo.KeyframeData))
    assert isinstance(inUnit, str)
    assert isinstance(outUnit, str)
    outValue = None

    # if we are not needing to convert, simply return.
    if inUnit == outUnit:
        outValue = inValue
        return outValue

    # get the conversion factor.
    conversionFactor = 1.0
    if ((inUnit == cdo.units.mm) and 
        (outUnit == cdo.units.cm)):
        conversionFactor = 0.1
    elif ((inUnit == cdo.units.cm) and 
        (outUnit == cdo.units.mm)):
        conversionFactor = 10.0

    # convert the value, taking "KeyframeData" into account.
    if isinstance(inValue, cdo.KeyframeData):
        outValue = cdo.KeyframeData()
        if inValue.static:
            value = inValue.getValue(0)
            assert inValue.length == 1
            outValue.setValue(value*conversionFactor, 0)
        else:
            inKeyValues = inValue.getKeyValues()
            for kv in inKeyValues:
                key = kv[0]
                value = kv[1]
                outValue.setValue(value*conversionFactor, key)
    else:
        outValue = inValue * conversionFactor

    assert outValue != None
    return outValue


def convertDistortion(cam, outType):
    inValue = cam.distortion
    outValue = None
    inType = cam._software

    if inType == cdo.softwareType.mm and \
         outType == cdo.softwareType.tde:

        outValue = cdo.KeyframeData()
        frameRange = (0, 0, 24)
        if (cam.sequences != None) and (len(cam.sequences) > 0):
            frameRange = cam.sequences[0].frameRange
        if (frameRange[1]-frameRange[0]) > 0:
            for i in range(frameRange[0], frameRange[1]):
                dst = cam.distortion.getValue(i)
                fl = cam.focal.getValue(i)
                k = mmToTdeConvertDistortion(dst, fl,
                                             cam.pixelAspectRatio,
                                             cam.filmbackWidth,
                                             cam.filmbackHeight,
                                             cam.width, cam.height)
                outValue.setValue(k, i)
        else:
            outValue.setValue(0.0, 0)
        outValue.simplifyData()
            
    return outValue

def convertCamera(cam, toSoftware):
    outCam = None
    inType = cam._software
    outType = toSoftware
    if inType == outType:
        msg = ('Warning: Camera did not convert to %s '
               'because the camera given has the type %s, '
               'cannot convert to same format.')
        print(msg % (repr(inType), repr(outType)))
        return False

    # Convert from Matchmover to 3DE4.
    if inType == cdo.softwareType.mm and \
       outType == cdo.softwareType.tde:
        outCam = cdo.TDECameraData()

        outCam.name = cam.name
        outCam.index = cam.index

        # Image resolution
        outCam.width = cam.width
        outCam.height = cam.height
        outCam.imageAspectRatio = cam.imageAspectRatio
        outCam.pixelAspectRatio = cam.pixelAspectRatio

        # Filmback
        outCam.filmbackWidth = convertValue(cam.filmbackWidth, cam._units, outCam._units)
        outCam.filmbackHeight = convertValue(cam.filmbackHeight, cam._units, outCam._units)
        outCam.filmAspectRatio = cam.filmAspectRatio
        aspectRatio = float(outCam.filmbackWidth/outCam.filmbackHeight)
        assert cdo.floatIsEqual(aspectRatio, outCam.filmAspectRatio)

        # Lens Centre
        outCam.lensCentreX = (cam.lensCentreX-0.5)*outCam.filmbackWidth
        outCam.lensCentreY = (cam.lensCentreY-0.5)*outCam.filmbackHeight

        # Focal Length
        outCam.focalLength = convertValue(cam.focalLength, cam._units, outCam._units)

        # convert distortion
        assert isinstance(cam.distortion, cdo.KeyframeData)
        assert cam.distortion.getValue(0) != None
        outCam.distortion = convertDistortion(cam, outType)

        # copy across the sequences
        outCam.sequences = cam.sequences

    return outCam
