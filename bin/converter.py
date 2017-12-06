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
    fbw = fbw * alpha

    hwidth = width/2.0
    hheight = height/2.0
    
    focal = (fl/width)*(fbw)
    fb = (focal*width)/fl
    
    ppx=width/2; 
    ppy=height/2; 
    rr = (hwidth*hwidth)+(hheight*hheight)/(alpha*alpha)
    rr = rr/10.0

    # calculate the distance between the undistorted and distorted coordinates
    # (in Shake coords), then, get the difference between them, that is the
    # matchmover distortion value!
    k = dst/(fl*fl)
    
    newr = 1.0+k*rr
    newptx = hwidth*newr
    newpty = hheight*newr
    diffx = (hwidth-newptx)
    diffy = (hheight-newpty)

    # WARNING: Below is a value of "30.5", this is a guessed value, I do not know why it needs to be that value, I'm sure there is a reason, but it is approximate.
    ld1 = (math.sqrt((hwidth*hwidth)+(hheight*hheight))/2)
    ld2 = (math.sqrt((newptx*newptx)+(newpty*newpty))/2)
    ld = ((ld2-ld1)/width)*30.5
        
    # print 'distortion value: %s' % repr(ld)
    return ld


def convertValue(inValue, inUnit, outUnit):
    outValue = None

    # get the conversion factor.
    conversionFactor = 1.0
    if (inUnit == cdo.units.mm) and \
       (outUnit == cdo.units.cm):
        conversionFactor = 0.1

    # convert the value, taking "KeyframeData" into account.
    if isinstance(inValue, cdo.KeyframeData):
        outValue = cdo.KeyframeData()
        if inValue.static:
            value = inValue.getValue(0)
            outValue.setValue(value*conversionFactor, 0)
        else:
            inKeyValues = inValue.getKeyValues()
            for kv in inKeyValues:
                key = kv[0]
                value = kv[1]
                outValue.setValue(value*conversionFactor, key)
    else:
        outValue = inValue * conversionFactor
    return outValue


def convertDistortion(cam, outType):
    inValue = cam.distortion
    outValue = None
    inType = cam._software

    if not isinstance(inValue, cdo.KeyframeData):
        msg = ('Warning: Distortion is not a KeyframeData object, '
               'it therefore will not be converted, %s.')
        print(msg % repr(inValue))
    else:
        if inType == outType:
            outValue = inValue
        elif inType == cdo.softwareType.mm and \
             outType == cdo.softwareType.tde:

            msg = ('Warning: Cannot convert distortion, '
                   '%s is not KeyframeData, %s.')
            if not isinstance(cam.focal, cdo.KeyframeData):
                print(msg % ('focal', repr(cam.focal)))
                return outValue
            if not isinstance(cam.distortion, cdo.KeyframeData):
                print(msg % ('distortion', repr(cam.distortion)))
                return outValue

            outValue = cdo.KeyframeData()
            frameRange = cam.sequences[0].frameRange
            for i in range(frameRange[0], frameRange[1]):
                dst = cam.distortion.getValue(i)
                fl = cam.focal.getValue(i)
                k = mmToTdeConvertDistortion(dst, fl,
                                             cam.pixelAspectRatio,
                                             cam.filmbackWidth,
                                             cam.filmbackHeight,
                                             cam.width, cam.height)
                outValue.setValue(k, i)
            
    return outValue

def convertCamera(cam, toSoftware):
    outCam = None
    inType = cam._software
    outType = toSoftware
    if inType == outType:
        msg = ('Warning: Camera did not convert to %s '
               'because the camera given has the type %s, '
               'cannot convert to same format.')
        print(msg % (inType, outType))
        return False

    # Convert from Matchmover to 3DE4.
    if inType == cdo.softwareType.mm and \
       outType == cdo.softwareType.tde:
        outCam = cdo.TDECameraData()

        outCam.name = cam.name
        outCam.index = cam.index
        outCam.focalLength = convertValue(cam.focalLength, cam._units, outCam._units)
        outCam.filmbackWidth = convertValue(cam.filmbackWidth, cam._units, outCam._units)
        outCam.filmbackHeight = convertValue(cam.filmbackHeight, cam._units, outCam._units)
        outCam.filmAspectRatio = cam.filmAspectRatio
        outCam.width = cam.width
        outCam.height = cam.height
        outCam.imageAspectRatio = cam.imageAspectRatio
        outCam.pixelAspectRatio = cam.pixelAspectRatio
        outCam.distortion = convertDistortion(cam, outType)

    return outCam

    
# Test
if __name__ == '__main__':
    filePaths = ['/home/davidc/Dev/mmDistortionTool/exampleFiles/camera_xml.rzml',
                 '/home/davidc/Dev/mmDistortionTool/exampleFiles/uhaul_m14b.rzml',
                 '/home/davidc/Dev/mmDistortionTool/exampleFiles/uhaul_m14.rzml']
    for filePath in filePaths:
        print 'filePath:', repr(filePath)
        proj = mmFileReader.readRZML(filePath)
        for cam in proj.cameras:
            print 'cam.name:', cam.name
            print 'cam.filmbackWidth:', cam.filmbackWidth
            print 'cam.filmbackHeight:', cam.filmbackHeight
            print 'cam.filmAspectRatio:', cam.filmAspectRatio
            print 'cam.width:', cam.width
            print 'cam.height:', cam.height
            print 'cam.imageAspectRatio:', cam.imageAspectRatio
            print 'cam.pixelAspectRatio:', cam.pixelAspectRatio
            print 'cam.focal:', cam.focal.getKeyValues()
            print 'cam.distortion:', cam.distortion.getKeyValues()
            print 'cam.focalLength:', cam.focalLength.getKeyValues()
            print 'cam.sequences:', cam.sequences

            tdeCam = convertCamera(cam, cdo.softwareType.tde)
            print 'tdeCam.name:', tdeCam.name
            print 'tdeCam.filmbackWidth:', tdeCam.filmbackWidth
            print 'tdeCam.filmbackHeight:', tdeCam.filmbackHeight
            print 'tdeCam.filmAspectRatio:', tdeCam.filmAspectRatio
            print 'tdeCam.width:', tdeCam.width
            print 'tdeCam.height:', tdeCam.height
            print 'tdeCam.imageAspectRatio:', tdeCam.imageAspectRatio
            print 'tdeCam.pixelAspectRatio:', cam.pixelAspectRatio
            print 'tdeCam.distortion:', tdeCam.distortion.getKeyValues()
            print 'tdeCam.focalLength:', tdeCam.focalLength.getKeyValues()
            print 'tdeCam.sequences:', tdeCam.sequences
            print '------end cam------'
        print '------end file------'
