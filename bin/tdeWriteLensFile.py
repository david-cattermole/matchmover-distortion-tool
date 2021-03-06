"""Writes a lens file from a TDECameraData object."""

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


class Options(object):
    def __init__(self):
        self.filePath = None
        self.time = None
        self.outDir = None


def writeCurve(f, keyframes, timeList):
    if isinstance(keyframes, cdo.KeyframeData):
        if keyframes.static == False:
            keysNum = keyframes.length
            f.write("%d\n"%keysNum)
            timeValues = keyframes.getTimeValues()
            for i in range(keysNum):
                time = timeValues[i]
                if cdo.isFrameInTimeList(time, timeList):
                    value = keyframes.getValue(time)
                    f.write("%.15f %.15f "%(time,value))
                    f.write("0.0 0.0 0.0 0.0 SMOOTH\n")
        else:
            f.write("0\n")
    else:
        if keyframes == None:
            f.write("0\n")
    return True


def main(cam, options):
    filePath = options.filePath
    assert filePath != None
    outDir = options.outDir
    timeList = cdo.parseTimeString(options.time)

    outFilePath = cdo.createOutFileName(filePath, cam.name, cdo.exportDesc.tdeLens, 'txt', outDir)
    outFileName = p.split(outFilePath)[1]
    msg = "Writing 3DE Lens file to '%s'."
    print(msg % outFileName)
    f = open(outFilePath,"w")
    if not f.closed:
        # write lens name
        f.write(cam.name+'_lens\n')

        fl = float(3) # 30mm
        if isinstance(cam.focalLength, cdo.KeyframeData):
            fl = cam.focalLength.getValue(0)
            assert fl != None

        # write lens data
        f.write("%.15f "%(cam.filmbackWidth))
        f.write("%.15f "%(cam.filmbackHeight))
        f.write("%.15f "%(fl))
        f.write("%.15f "%(cam.filmAspectRatio))
        f.write("%.15f "%(float(0)))
        f.write("%.15f "%(float(0)))
        f.write("%.15f\n"%(cam.pixelAspectRatio))

        # write dynamic distortion
        # If the distortion is animated, we must write a curve out for the focus distance.
        if cam.distortion.static:
            f.write("DISTORTION_STATIC\n")
        else:
            f.write("DISTORTION_DYNAMIC_FOCUS_DISTANCE\n")

        # write out model
        f.write("%s\n"%lensModelName)

        # write the distortion value out
        distValue = float(0)
        if isinstance(cam.distortion, cdo.KeyframeData):
            distValue = cam.distortion.getValue(0)
            assert distValue != None
        f.write("%s\n"%(distPara))
        f.write("%.15f\n"%(distValue))
        writeCurve(f, cam.distortion, timeList)

        # write out all other distortion default values
        for para in defParas:
            f.write("%s\n"%(para))
            d = 0.0
            if para == 'Anamorphic Squeeze':
                d = 1.0
            f.write("%.15f\n"%(d))
            writeCurve(f, None, timeList)

        f.write("<end_of_file>\n")
        f.close()
        assert p.isfile(outFilePath) == True
    return True
