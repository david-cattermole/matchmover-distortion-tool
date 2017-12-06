"""Test the package, run unit tests."""

# Copyright David Cattermole, 2013
# Licensed under the GNU General Public License, 
# see "COPYING.txt" for more details.

import os
import os.path as p
import math

import commonDataObjects as cdo
import mmFileReader
import converter
import tdeWriteLensFile
import tdeWriteRawText
import tdeWriteWetaNukeDistortionNode
import mmDistortionConverter as mdc

def main(filePath):
    projData = mmFileReader.readRZML(filePath)
    cams = projData.cameras
    for cam in projData.cameras:
        tdeCam = converter.convertCamera(cam, cdo.softwareType.tde)
        tdeWriteLensFile.main(tdeCam, filePath)
    return True
