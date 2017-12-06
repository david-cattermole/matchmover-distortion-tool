"""Test the package, run unit tests."""

# Copyright David Cattermole, 2013
# Licensed under the GNU General Public License, 
# see "COPYING.txt" for more details.

import os
import os.path as p
import math

import commonDataObjects as cdo
import mmFileReader as mfr
import converter
import tdeWriteLensFile
import tdeWriteWetaNukeDistortionNode
import mmDistortionConverter as mdc


def main(filePath):
    project = mfr.readRZML(filePath)

    assert project._software != None
    assert project._units != None
    assert project.name != None
    assert project.index != None
    assert project.path != None
    assert project.frameRange != None
    assert project.cameras != None
    assert project.sequences != None
    assert p.isfile(project.path) == True

    frameRangeLength = int(project.frameRange[1]-project.frameRange[0])
    assert frameRangeLength > 0

    for cam in project.cameras:
        assert cam != None
        assert isinstance(cam, cdo.MMCameraData)
        assert cam._software != None
        assert cam._software == cdo.softwareType.mm
        assert cam._units != None
        assert cam._units == cdo.units.mm
        assert cam.name != None
        assert cam.index != None
        assert cam.index > 0
        assert cam.focalLength != None
        assert cam.focalLength.length > 0
        assert cam.focal != None
        assert cam.focal.length > 0
        assert cam.distortion != None
        assert cam.distortion.length > 0
        assert cam.pixelAspectRatio != None
        assert cam.pixelAspectRatio > 0.0
        assert cam.imageAspectRatio != None
        assert cam.imageAspectRatio > 0.0
        assert cam.filmbackWidth != None
        assert cam.filmbackWidth > 0.0
        assert cam.filmbackHeight != None
        assert cam.filmbackHeight > 0.0

    for seq in project.sequences:
        assert seq != None
        assert isinstance(seq, cdo.MMSequenceData)
        assert seq._software != None
        assert seq._software == cdo.softwareType.mm
        assert seq.name != None
        assert seq.index != None
        assert seq.index > 0
        hasCam = False
        camIndex = -1
        camName = None
        for cam in project.cameras:
            assert isinstance(cam, cdo.MMCameraData)
            if cam.index == seq.cameraIndex:
                hasCam = True
                camIndex = cam.index
                camName = cam.name
        assert hasCam == True
        assert camIndex > 0
        assert camName != None
        assert seq.width != None
        assert seq.height != None
        assert seq.imageAspectRatio != None
        assert seq.imageAspectRatio > 0.0
        assert seq.imagePath != None
        assert isinstance(seq.imagePath, str)
        assert seq.frameRange != None
        assert len(seq.frameRange) == 3

    return True
