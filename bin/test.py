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
import mmDistortionConverter

import commonDataObjects_test
import mmFileReader_test
import converter_test
import tdeWriteLensFile_test
import tdeWriteRawText_test
import tdeWriteWetaNukeDistortionNode_test
import mmDistortionConverter_test


def getAllRZMLTestFiles():
    """Get all RZML files for testing."""
    filePaths = list()
    searchDir = p.abspath('testFiles')
    if p.isdir(searchDir):
        fileNames = os.listdir(searchDir)
        for fileName in fileNames:
            if fileName.endswith('.rzml'):
                filePath = p.join(searchDir, fileName)
                if p.isfile(filePath):
                    filePaths.append(filePath)
    else:
        msg = ("Error: Could not find testFiles, "
               "please run this script from the 'bin' directory.")
        print(msg)
    return filePaths


def main():
    """Run all unit tests."""
    filePaths = getAllRZMLTestFiles()
    for filePath in filePaths:
        msg = ("-----------------------\n"
               "Testing  '%s'.\n"
               "-----------------------")
        print(msg) % p.split(filePath)[1]

        commonDataObjects_test.main(filePath)
        mmFileReader_test.main(filePath)
        converter_test.main(filePath)
        tdeWriteLensFile_test.main(filePath)
        tdeWriteRawText_test.main(filePath)
        tdeWriteWetaNukeDistortionNode_test.main(filePath)
        mmDistortionConverter_test.main(filePath)
    return True


if __name__ == '__main__':
    main()
    
