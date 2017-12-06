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
import mmDistortionConverter


def main(filePath):
    proj = mfr.readRZML(filePath)
    for cam in proj.cameras:
        mmCam = converter.convertCamera(cam, cdo.softwareType.mm)
        tdeCam = converter.convertCamera(cam, cdo.softwareType.tde)
        assert tdeCam != None
        assert tdeCam.name == cam.name
        assert tdeCam.index == cam.index
        assert tdeCam.filmAspectRatio == cam.filmAspectRatio
        assert tdeCam.width == cam.width
        assert tdeCam.height == cam.height
        assert tdeCam.imageAspectRatio == cam.imageAspectRatio
        assert isinstance(tdeCam.distortion, cdo.KeyframeData)
        assert isinstance(tdeCam.focalLength, cdo.KeyframeData)
        assert isinstance(cam.sequences, list)
        assert isinstance(tdeCam.sequences, list)
        assert tdeCam.sequences == cam.sequences
        assert tdeCam.distortion.getValue(0) != None
        assert tdeCam.focalLength.getValue(0) != None
        assert len(tdeCam.distortion.getTimeValues()) > 0
        assert len(tdeCam.focalLength.getTimeValues()) > 0

        # Test distortion converter.
        distortion = converter.convertDistortion(cam, cdo.softwareType.tde)
        distortion = converter.convertDistortion(cam, cdo.softwareType.mm)

        # Test unit conversion, on float values and KeyframeData objects
        # (static and not static).
        assert converter.convertValue(1.0, cdo.units.cm, cdo.units.mm) == 10.0
        assert converter.convertValue(1.0, cdo.units.mm, cdo.units.cm) == 0.1
        assert converter.convertValue(1.0, cdo.units.cm, cdo.units.cm) == 1.0
        assert converter.convertValue(1.0, cdo.units.mm, cdo.units.mm) == 1.0
        keyData = cdo.KeyframeData(static=True, initialValue=1.0)
        keyDataNew = converter.convertValue(keyData, cdo.units.mm, cdo.units.mm)
        assert keyDataNew.getValue(0) == 1.0
        keyDataNew = converter.convertValue(keyData, cdo.units.cm, cdo.units.mm)
        assert keyDataNew.getValue(0) == 10.0
        keyDataNew = converter.convertValue(keyData, cdo.units.mm, cdo.units.cm)
        assert keyDataNew.getValue(0) == 0.1
        keyData = cdo.KeyframeData()
        keyData.setValue(1.0, 2)
        keyData.setValue(2.0, 3)
        keyDataNew = converter.convertValue(keyData, cdo.units.mm, cdo.units.mm)
        assert keyDataNew.getValue(2) == 1.0
        keyDataNew = converter.convertValue(keyData, cdo.units.cm, cdo.units.mm)
        assert keyDataNew.getValue(2) == 10.0
        keyDataNew = converter.convertValue(keyData, cdo.units.mm, cdo.units.cm)
        assert keyDataNew.getValue(2) == 0.1        

    return True
