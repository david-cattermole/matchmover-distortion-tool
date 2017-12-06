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
import tdeWriteWarpBatchScript_test
import mmWriteDistoImaBatchScript_test
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


def getAllTestImageSequences():
    """Get all image sequence files for testing."""
    seqs = list()
    searchDir = p.abspath('testFiles')
    if p.isdir(searchDir):
        seq = p.join(searchDir, 'imageSequence.####.png')
        seqs.append(seq)

        seq = p.join(searchDir, 'imageSequence.@.png')
        seqs.append(seq)

        seq = p.join(searchDir, 'imageSequence.%04d.png')
        seqs.append(seq)

        # incorrect in order to trigger an error.
        seq = p.join(searchDir, 'imageSequence.$.png')
        seqs.append(seq)
    else:
        msg = ("Error: Could not find testFiles, "
               "please run this script from the 'bin' directory.")
        print(msg)
    return seqs


def main():
    """Run all unit tests."""
    # Test RZML File Input/Output and Conversion
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
        tdeWriteWarpBatchScript_test.main(filePath)
        mmWriteDistoImaBatchScript_test.main(filePath)
        mmDistortionConverter_test.main(filePath)

    # Test Image Sequence Paths
    imgSeqs = getAllTestImageSequences()
    for imgSeq in imgSeqs:
        msg = ("-----------------------\n"
               "Testing  '%s'.\n"
               "-----------------------")
        print(msg) % p.split(imgSeq)[1]
        images = cdo.getAllImageSequence(imgSeq)
        seqStart, seqEnd = cdo.splitImageSequencePath(imgSeq)
        if imgSeq.find('#') != -1:
            assert cdo.getImageSequencePadding(imgSeq) == 4
            assert len(images) == 3
            assert seqStart != ''
            assert seqEnd != ''
            assert p.isdir(p.dirname(seqStart))
        if imgSeq.find('@') != -1:
            assert cdo.getImageSequencePadding(imgSeq) == 4
            assert len(images) == 3
            assert seqStart != ''
            assert seqEnd != ''
            assert p.isdir(p.dirname(seqStart))
        if imgSeq.find('$') != -1:
            assert cdo.getImageSequencePadding(imgSeq) == None
            assert len(images) == 0
            assert seqStart == None and seqEnd == None
        for image in images:
            assert p.isfile(image) == True
            frameNum = cdo.getImagePathFrameNumber(imgSeq, image)
            assert frameNum >= 0
            assert frameNum < 3

    return True


if __name__ == '__main__':
    main()
    
