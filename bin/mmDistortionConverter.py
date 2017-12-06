"""
Asks for a file using Tkinter GUI, then converts the file and exits.

Copyright David Cattermole, 2013

Author: David Cattermole
Email: cattermole91@gmail.com
Version: 0.2

How to use: ....
"""
# Copyright David Cattermole, 2013
# Licensed under the GNU General Public License, 
# see "COPYING.txt" for more details.

# base modules imports
import sys
import os 
import os.path as p
import platform
import math as m

# Tk GUI
from Tkinter import *
import tkFileDialog

import commonDataObjects as cdo
import converter
import mmFileReader
import tdeWriteLensFile
import tdeWriteRawText
import tdeWriteWetaNukeDistortionNode


def createOutFileName(inFile, cameraName,
                      suffix, outExt):
    assert isinstance(inFile, str) or isinstance(inFile, unicode)
    assert isinstance(cameraName, str)
    assert isinstance(suffix, str)
    assert isinstance(outExt, str)

    inFile = str(inFile)

    illegalChars = [' ']
    replaceChar = '_'
    for char in illegalChars:
        cameraName = cameraName.replace(char, replaceChar)

    inSplit = p.split(inFile)
    outDir = inSplit[0]
    outFileName = inSplit[1]
    
    extSplit = p.splitext(outFileName)
    outFileName = extSplit[0]
    oldExt = extSplit[1]

    if not outExt.startswith('.'):
        outExt = '.'+outExt

    outFileName = outFileName+'_'+cameraName+'_'+suffix+outExt
    outFilePath = p.join(outDir, outFileName)
    return outFilePath


class MMDistortionConverter(object):
    """Class that asks for a file path using a GUI."""

    def __init__ (self, path=None):
        self.os = str(platform.system()).lower()

        # get the file path.
        if path != None:
            filePath = str(path)
        else:
            filePath = self.getFilePath()
        if filePath == None:
            msg = 'User cancelled the file dialog, file path: %s.'
            print msg % repr(filePath)
            return
        if not filePath.endswith('.rzml'):
            msg = 'Incorrect file extension, must end with ".rzml", file path: %s.'
            print msg % repr(filePath)
            return

        # read the file, get camera data.
        fileName = p.split(filePath)[1]
        print("Reading Matchmover File: '%s'" % fileName)
        projData = mmFileReader.readRZML(filePath)

        cams = projData.cameras
        for cam in projData.cameras:
            print("Converting Camera: '%s'" % cam.name)
            tdeCam = converter.convertCamera(cam, cdo.softwareType.tde)

            outFilePath = createOutFileName(filePath, tdeCam.name, '3deRawText', 'txt')
            tdeWriteRawText.main(tdeCam, outFilePath)
            
            outFilePath = createOutFileName(filePath, tdeCam.name, '3deLens', 'txt')
            tdeWriteLensFile.main(tdeCam, outFilePath)
            
            outFilePath = createOutFileName(filePath, tdeCam.name, 'wetaDistortionNode', 'nk')
            tdeWriteWetaNukeDistortionNode.main(tdeCam, outFilePath)
        
        print('Distortion Converter Finished!')
        return

    def getFilePath(self):
        """Asks the user for a file name."""
        filePath = None
        result = tkFileDialog.askopenfilename(filetypes=[('RZML', '*.rzml')], # 
                                              multiple=False, 
                                              title=cdo.projectTitle)
        if result == '':
            filePath = None
        else:
            filePath = result
        return filePath

if __name__ == '__main__':
    gui = MMDistortionConverter()
