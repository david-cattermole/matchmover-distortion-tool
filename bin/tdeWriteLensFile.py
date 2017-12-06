"""Writes a lens file from a TDECameraData object."""

# Copyright David Cattermole, 2013
# Licensed under the GNU General Public License, 
# see "COPYING.txt" for more details.

import commonDataObjects as cdo

lensModel = '3DE Classic LD Model'
distPara = 'Distortion'
defParas = ['Anamorphic Squeeze',
            'Curvature X',
            'Curvature Y',
            'Quartic Distortion']


def writeCurve(f, keyframes):
    if isinstance(keyframes, cdo.KeyframeData):
        if not keyframes.static:
            keysNum = keyframes.length
            f.write("%d\n"%keysNum)
            timeValues = keyframes.getTimeValues()
            for i in range(keysNum):
                time = timeValues[i]
                value = keyframes.getValue(time)
                f.write("%.15f %.15f "%(time,value))
                f.write("0.0 0.0 0.0 0.0 SMOOTH\n")
        else:
            f.write("0\n")
    else:
        if keyframes == None:
            f.write("0\n")
    return True


def main(cam, filePath):
    msg = "Writing 3DE Lens file to '%s'"
    print(msg % filePath)
    f = open(filePath,"w")
    if not f.closed:
        # write lens name
        name = cam.name + '_lens'
        f.write(name); f.write("\n")

        # write lens data
        f.write("%.15f "%(cam.filmbackWidth))
        f.write("%.15f "%(cam.filmbackHeight))
        f.write("%.15f "%(cam.focalLength.getValue(0)))
        f.write("%.15f "%(cam.filmAspectRatio))
        f.write("%.15f "%(0.0))
        f.write("%.15f "%(0.0))
        f.write("%.15f\n"%(cam.pixelAspectRatio))

        # write dynamic distortion
        if cam.distortion.static:
            f.write("%d\n"%(1))
        else:
            f.write("%d\n"%(0))

        # write out model
        f.write("%s\n"%lensModel)

        # write the distortion value out
        distValue = cam.distortion.getValue(0)
        f.write("%s\n"%(distPara))        
        f.write("%.15f\n"%(distValue))
        writeCurve(f, cam.distortion)

        # write out all other distortion default values
        for para in defParas:
            f.write("%s\n"%(para))
            d = 0.0
            if para == 'Anamorphic Squeeze':
                d = 1.0
            f.write("%.15f\n"%(d))
            writeCurve(f, None)

        f.write("<end_of_file>\n")
        f.close()

        msg = 'Successfully written 3DE Lens File!'
        print(msg)
    return True
