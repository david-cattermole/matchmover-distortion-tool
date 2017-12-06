"""Writes a raw text file from a TDECameraData object."""

# Copyright David Cattermole, 2013
# Licensed under the GNU General Public License, 
# see "COPYING.txt" for more details.

import os
import os.path as p

import commonDataObjects as cdo

lensModelName = '3DE Classic LD Model'
distPara = 'Distortion'
defParas = ['Anamorphic Squeeze',
            'Curvature X',
            'Curvature Y',
            'Quartic Distortion']


def writeCurve(f, keyframes):
    assert keyframes != None
    if isinstance(keyframes, cdo.KeyframeData):
        if not keyframes.static:
            keysNum = keyframes.length
            assert keyframes.length >= 0
            f.write("Number of Keys: %d\n"%keysNum)
            f.write("Time/Values:\n")
            timeValues = keyframes.getTimeValues()
            for i in range(keysNum):
                time = timeValues[i]
                value = keyframes.getValue(time)
                f.write("%.15f %.15f\n"%(time,value))
    return True


def main(cam, filePath):
    fileName = p.split(filePath)[1]
    msg = "Writing 3DE Raw Text file to '%s'."
    print(msg % fileName)
    f = open(filePath,"w")
    if not f.closed:
        # write camera name
        f.write('Camera Name: '+str(cam.name)+"\n")

        fl = 3.0 # 30mm
        if isinstance(cam.focalLength, cdo.KeyframeData):
            fl = cam.focalLength.getValue(0)
            assert fl != None

        # write lens data
        f.write("Focal Length (%s): %.4f\n"%(cam._units, fl))
        f.write("Filmback Width (%s): %.4f\n"%(cam._units, cam.filmbackWidth))
        f.write("Filmback Height (%s): %.4f\n"%(cam._units, cam.filmbackHeight))
        f.write("Film Aspect Ratio: %.4f\n"%cam.filmAspectRatio)
        f.write("Lens Centre X (%s): %.4f\n"%(cam._units, 0.0))
        f.write("Lens Centre Y (%s): %.4f\n"%(cam._units, 0.0))
        f.write("Pixel Aspect Ratio: %.4f\n\n"%cam.pixelAspectRatio)

        # write dynamic distortion
        if cam.distortion.static:
            f.write("Static Distortion\n\n")
        else:
            f.write("Animated Distortion\n\n")

        # write the distortion value out
        distValue = 0.0
        if isinstance(cam.distortion, cdo.KeyframeData):
            distValue = cam.distortion.getValue(0)
            assert distValue != None
        f.write("%s\n"%(distPara))        
        f.write("%.15f\n"%(distValue))
        writeCurve(f, cam.distortion)
        f.write("\n")

        # write out all other distortion default values
        for para in defParas:
            f.write("%s\n"%(para))
            d = 0.0
            if para == 'Anamorphic Squeeze':
                d = 1.0
            f.write("%.15f\n"%(d))
            keys = cdo.KeyframeData(static=True, initialValue=d)
            writeCurve(f, keys)
            f.write("\n")

        f.close()
    return True
