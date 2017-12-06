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
import tdeWriteRawText
import tdeWriteWetaNukeDistortionNode
import mmDistortionConverter as mdc
import test

def main(filePath):
    outDirs = test.outDirTests()
    times = test.timeStringTests()
    for time, outDir in zip(times, outDirs):
        readOptions = mfr.Options()
        readOptions.filePath = filePath
        readOptions.time = time
        projData = mfr.readRZML(readOptions)
        cams = projData.cameras
        for cam in projData.cameras:
            tdeCam = converter.convertCamera(cam, cdo.softwareType.tde)
            rawOptions = tdeWriteRawText.Options()
            rawOptions.filePath = filePath
            rawOptions.time = time
            rawOptions.outDir = outDir
            tdeWriteRawText.main(tdeCam, rawOptions)
    return True
