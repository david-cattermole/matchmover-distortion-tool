"""Writes a Nuke file with a Weta (3DE) Distortion node in it."""

import os
import os.path as p

import commonDataObjects as cdo

lensModelName = '3DE Classic LD Model'
lensModel = 'tde4_ldp_classic_3de_mixed'
distPara = 'Distortion'
defParas = ['Anamorphic Squeeze',
            'Curvature X',
            'Curvature Y',
            'Quartic Distortion']


def getNukeParameterName(para):
    para = para.replace(' ', '_')
    para = para.replace('-', '_') 
    return para


def main(cam, filePath, offset=None):
    if offset == None or not isinstance(offset, int):
        offset = 0

    lens = cam.name
    frameRange = (0, 0, 24)
    if (cam.sequences != None) and (len(cam.sequences) > 0):
        frameRange = cam.sequences[0].frameRange
    nfr = int(frameRange[1]-frameRange[0])
    fbw = cam.filmbackWidth
    fbh = cam.filmbackHeight
    lcx = 0.0
    lcy = 0.0
    pxa = cam.pixelAspectRatio

    fileName = p.split(filePath)[1]
    msg = "Writing 3DE Weta Nuke Distortion Node file to '%s'"
    print(msg % fileName)
    f = open(filePath,"w")
    if not f.closed:
        f.write('# Exported by %s %s\n'%(cdo.projectName, cdo.projectVersion))
        f.write('%s {\n' % lensModel)
        f.write(' direction undistort\n')

        # write Focal length
        focalData = cam.focalLength
        focalData.simplifyData()
        if focalData.static == False:
            f.write(' tde4_focal_length_cm {{curve ')	
            for frame in range(1,nfr+1):
                f.write ('x %i'%(frame+offset))
                f.write(' %.7f '%focalData.getValue(frame))
            f.write('}}\n')
        elif focalData.static == True:
            f.write(' tde4_focal_length_cm %.7f \n'%focalData.getValue(0))

        # write camera
        f.write(' tde4_filmback_width_cm %.7f \n'%fbw)
        f.write(' tde4_filmback_height_cm %.7f \n'%fbh)
        f.write(' tde4_lens_center_offset_x_cm %.7f \n'%lcx)
        f.write(' tde4_lens_center_offset_y_cm %.7f \n'%lcy)
        f.write(' tde4_pixel_aspect %.7f \n'%pxa)

        # write distortion parameters
        if cam.distortion.static == False:

            # write distortion parameter
            f.write(' Distortion {{curve ')
            for frame in range(1,nfr+1):
                f.write ('x %i'%(frame+offset))
                distValue = cam.distortion.getValue(frame)
                assert distValue != None
                f.write(' %.7f '% distValue)
            f.write('}}\n')

            # write default parameters.
            for para in defParas:
                f.write(' '+getNukeParameterName(para)+' {{curve ')
                for frame in range(1,nfr+1):
                    f.write ('x %i'%(frame+offset))
                    d = 0.0
                    if para == 'Anamorphic Squeeze':
                        d = 1.0
                    f.write(' %.7f '%d)	
                f.write('}}\n')

        elif cam.distortion.static == True: # case C

            # write distortion parameter
            f.write(' '+getNukeParameterName(distPara)+' %.7f \n')
            distValue = cam.distortion.getValue(0)
            assert distValue != None
            f.write(' %.7f \n'%distValue)

            # Write static default parameters
            for para in defParas:
                f.write(' '+getNukeParameterName(para)+' %.7f \n')
                d = 0.0
                if para == 'Anamorphic Squeeze':
                    d = 1.0
                f.write(' %.7f \n'%d)

        nodeName = 'tde4_ldp_%s_%s'%(str(cam.name), str(cam.index))
        replaceChar = '_'
        illegalChars = [' ', '-', '.', ',']
        for char in illegalChars:
            nodeName = nodeName.replace(char, replaceChar)
        f.write(' name %s\n'%nodeName)
        f.write('}\n')

    f.close()
    return True
