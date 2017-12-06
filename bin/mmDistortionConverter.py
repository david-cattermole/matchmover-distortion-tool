"""Asks for a file using Tkinter GUI, then converts the file and exits."""

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

# # IDLE custom Tkinter (Tabs)
# from idlelib.tabbedpages import TabbedPageSet

import commonDataObjects as cdo
import converter
import mmFileReader
import tdeWriteLensFile
import tdeWriteRawText
import tdeWriteWarpBatchScript
import mmWriteDistoImaBatchScript
import tdeWriteWetaNukeDistortionNode


class ConverterOptions(object):
    """Options that can be passed to MMDistortionConverter.exportData()."""
    def __init__(self):
        self.inputFile = None
        # self.outputDir = None
        self.exportNukeDistNode = None
        self.exportRawText = None
        self.exportTdeLens = None
        self.exportWarpBatch = None
        self.exportDistoBatch = None


class MMDistortionConverter(Frame):
    """Class that asks for a file path using a GUI."""

    def __init__ (self, master=None, path=None, export=None):
        """Creates the user interface if no path is given, 
        else uses export keyword to export file types or if export is not given, 
        exports every file format.

        master - Used by tkinter library.
        path - An input file name to convert.
        export - A dict mapping of export types with booleans, 
        for example, nukeDistNode:True.

        Returns nothing."""
        self.os = str(platform.system()).lower()

        # get the file path.
        if path != None:
            options = ConverterOptions()
            options.inputFile = str(path)
            if export == None:
                options.exportNukeDistNode = True
                options.exportRawText = True
                options.exportTdeLens = True
                options.exportWarpBatch = True
                options.exportDistoBatch = True
            else:
                options.exportNukeDistNode = False
                options.exportRawText = False
                options.exportTdeLens = False
                options.exportWarpBatch = False
                options.exportDistoBatch = False
                if export.has_key('nukeDistNode') and export['nukeDistNode'] == True:
                    options.exportNukeDistNode = True
                if export.has_key('rawText') and export['rawText'] == True:
                    options.exportRawText = True
                if export.has_key('tdeLens') and export['tdeLens'] == True:
                    options.exportTdeLens = True
                if export.has_key('warpBatch') and export['warpBatch'] == True:
                    options.exportWarpBatch = True
                if export.has_key('distoBatch') and export['distoBatch'] == True:
                    options.exportDistoBatch = True

            self.exportData(options)
            return

        # Start Options GUI 
        Frame.__init__(self, master)
        Pack.config(self)

        # The main Frame
        mainFrame = Frame(self)
        mainFrame.pack(fill=BOTH, expand=1, padx=5, pady=5)

        # Input/Output
        self.inputFile = StringVar()
        inOutFrame = LabelFrame(mainFrame, text='File/Directories...', relief=GROOVE, borderwidth=2)
        inOutFrame.pack(fill=BOTH,expand=1)

        # Input File
        inFileFrame = Frame(inOutFrame)
        inFileLabel = Label(inFileFrame, text='Input File:')
        inFileBtn = Button(inFileFrame, text='...', command=self.getFilePath)
        self.inFileEntry = Entry(inFileFrame, textvariable=self.inputFile)
        inFileFrame.pack(fill=BOTH,expand=1)
        inFileLabel.pack(side=LEFT, padx=5, pady=2)
        inFileBtn.pack(side=RIGHT, padx=5, pady=2)
        self.inFileEntry.pack(side=RIGHT, fill=X, expand=1, padx=5, pady=2)

        # # Output Directory
        # self.outputDir = StringVar()
        # outDirFrame = Frame(inOutFrame)
        # outDirLabel = Label(outDirFrame, text='Output Directory:')
        # outDirBtn = Button(outDirFrame, text='...', command=self.getDirectoryPath)
        # self.outDirEntry = Entry(outDirFrame, textvariable=self.outputDir)
        # outDirFrame.pack(fill=BOTH,expand=1)
        # outDirLabel.pack(side=LEFT, padx=5, pady=2)
        # outDirBtn.pack(side=RIGHT, padx=5, pady=2)
        # self.outDirEntry.pack(side=RIGHT, fill=X, expand=1, padx=5, pady=2)
        
        # Output Formats
        outFormatsFrame = LabelFrame(mainFrame, text='Export File Formats...', relief=GROOVE, borderwidth=2)
        outFormatsFrame.pack(fill=BOTH,expand=1)

        # Export Nuke Distortion Node
        self.exportNukeDistNode = BooleanVar()
        nukeDistFrame = Frame(outFormatsFrame)
        nukeDistChk = Checkbutton(nukeDistFrame, text='Nuke Distortion Node', variable=self.exportNukeDistNode)
        # nukeDistBtn = Button(nukeDistFrame, text='Options...', state='disabled', command=self.exportNukeDistNodeOptions)
        nukeDistFrame.pack(fill=BOTH,expand=1)
        nukeDistChk.pack(side=LEFT, padx=5, pady=2)
        # nukeDistBtn.pack(side=LEFT, fill=BOTH)

        # Export 3DE Lens File
        self.exportTdeLens = BooleanVar()
        tdeLensFrame = Frame(outFormatsFrame)
        tdeLensChk = Checkbutton(tdeLensFrame, text='3DE Lens File', variable=self.exportTdeLens)
        tdeLensFrame.pack(fill=BOTH,expand=1)
        tdeLensChk.pack(side=LEFT, padx=5, pady=2)

        # Export 3DE Raw Text (Human readable)
        self.exportRawText = BooleanVar()
        rawTextFrame = Frame(outFormatsFrame)
        rawTextChk = Checkbutton(rawTextFrame, text='3DE Human Readable Text', variable=self.exportRawText)
        rawTextFrame.pack(fill=BOTH,expand=1)
        rawTextChk.pack(side=LEFT, padx=5, pady=2)

        # Export Warp4 Batch Script
        self.exportWarpBatch = BooleanVar()
        warpBatchFrame = Frame(outFormatsFrame)
        warpBatchChk = Checkbutton(warpBatchFrame, text='Warp4 Batch Script', variable=self.exportWarpBatch)
        warpBatchBtn = Button(warpBatchFrame, text='Options...', state='disabled', command=self.exportWarpBatchOptions)
        warpBatchFrame.pack(fill=BOTH,expand=1)
        warpBatchChk.pack(side=LEFT, padx=5, pady=2)
        warpBatchBtn.pack(side=LEFT, fill=BOTH)

        # Export DistoIma Batch Script
        self.exportDistoBatch = BooleanVar()
        distoBatchFrame = Frame(outFormatsFrame)
        distoBatchChk = Checkbutton(distoBatchFrame, text='DistoIma Batch Script', variable=self.exportDistoBatch)
        distoBatchBtn = Button(distoBatchFrame, text='Options...', state='disabled', command=self.exportDistoBatchOptions)
        distoBatchFrame.pack(fill=BOTH,expand=1)
        distoBatchChk.pack(side=LEFT, padx=5, pady=2)
        distoBatchBtn.pack(side=LEFT, fill=BOTH)

        # # Export Maya 3D Camera
        # self.exportMayaCam = BooleanVar()
        # mayaCamFrame = Frame(outFormatsFrame)
        # mayaCamChk = Checkbutton(mayaCamFrame, text='Maya 3D Camera', variable=self.exportMayaCam)
        # mayaCamFrame.pack(fill=BOTH,expand=1)
        # mayaCamChk.pack(side=LEFT, padx=5, pady=2)

        # # Export Maya 2.5D Points
        # self.exportMaya25D = BooleanVar()
        # maya25DFrame = Frame(outFormatsFrame)
        # maya25DChk = Checkbutton(maya25DFrame, text='Maya 2.5D Points', variable=self.exportMaya25D)
        # maya25DFrame.pack(fill=BOTH,expand=1)
        # maya25DChk.pack(side=LEFT, padx=5, pady=2)

        # End Frame
        buttonsFrame = Frame(mainFrame, pady=2)
        okBtn = Button(buttonsFrame, text='Ok',
                       command=self.exportDataFromGui)
        exitBtn = Button(buttonsFrame, text='Exit',
                         command=self.quit,
                         padx=6, pady=3)
        buttonsFrame.pack(side=BOTTOM, fill=BOTH,expand=1)
        okBtn.pack(side=LEFT, fill=BOTH, padx=20, pady=3)
        exitBtn.pack(side=RIGHT, fill=BOTH, padx=20, pady=3)
        return

    def exportDataFromGui(self):
        options = ConverterOptions()
        options.inputFile = self.inputFile.get()
        # options.outputDir = self.outputDir.get()
        options.exportNukeDistNode = self.exportNukeDistNode.get()
        options.exportRawText = self.exportRawText.get()
        options.exportTdeLens = self.exportTdeLens.get()
        options.exportWarpBatch = self.exportWarpBatch.get()
        options.exportDistoBatch = self.exportDistoBatch.get()
        self.exportData(options)
        return

    def exportData(self, options):
        """Exports data.

        options - A ConverterOptions class that has all options 
        filled out correctly.

        Returns True or False."""
        assert options.inputFile != None
        # assert options.outputDir != None
        assert options.exportNukeDistNode != None
        assert options.exportRawText != None
        assert options.exportTdeLens != None
        assert options.exportWarpBatch != None
        assert options.exportDistoBatch != None
        
        if not options.inputFile.endswith('.rzml'):
            msg = 'Incorrect file extension, must end with ".rzml", file path: %s.'
            print msg % repr(options.inputFile)
            return

        # read the file, get camera data.
        fileName = p.split(options.inputFile)[1]
        print("Reading Matchmover File: '%s'" % fileName)
        projData = mmFileReader.readRZML(options.inputFile)

        cams = projData.cameras
        for cam in projData.cameras:
            print("Converting Camera: '%s'" % cam.name)
            tdeCam = converter.convertCamera(cam, cdo.softwareType.tde)
            if options.exportNukeDistNode:
                tdeWriteWetaNukeDistortionNode.main(tdeCam, options.inputFile)
            if options.exportRawText:
                tdeWriteRawText.main(tdeCam, options.inputFile)
            if options.exportTdeLens:
                tdeWriteLensFile.main(tdeCam, options.inputFile)
            if options.exportWarpBatch:
                tdeWriteWarpBatchScript.main(tdeCam, options.inputFile)
            if options.exportDistoBatch:
                mmWriteDistoImaBatchScript.main(cam, options.inputFile)
        
        print('Distortion Converter Finished!')
        return

    def exportNukeDistNodeOptions(self):
        print 'get the Nuke Distortion Node options!'
        return

    def exportWarpBatchOptions(self):
        print 'get the Warp4 options!'
        return

    def exportDistoBatchOptions(self):
        print 'get the DistoIma options!'
        return

    def getFilePath(self):
        """Asks the user for a file name."""
        filePath = None
        result = tkFileDialog.askopenfilename(filetypes=[('RZML', '*.rzml')],
                                              multiple=False, 
                                              title=cdo.projectTitle)
        if result == '':
            filePath = None
        else:
            filePath = result
            self.inputFile.set(filePath)
        # return filePath
        return

    def getDirectoryPath(self):
        """Asks the user for a file name."""
        dirPath = None
        # NOTE: Perhaps we should use an environment variable
        # to set the initial directory for this dialog?
        result = tkFileDialog.askdirectory(initialdir=os.getcwd,
                                           mustexist=False, 
                                           title=cdo.projectTitle)
        if result == '':
            dirPath = None
        else:
            dirPath = result
            self.outputDir.set(dirPath)
        return


if __name__ == '__main__':
    root = Tk()
    gui = MMDistortionConverter(master=root)
    gui.master.title(cdo.projectTitle)
    gui.mainloop()
