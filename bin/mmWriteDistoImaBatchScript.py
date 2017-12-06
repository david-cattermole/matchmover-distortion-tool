"""Writes a batch script to undistort/distort image files, using DistoIma."""

# Copyright David Cattermole, 2013
# Licensed under the GNU General Public License, 
# see "COPYING.txt" for more details.

import os
import os.path as p
import math
import multiprocessing as mp
import platform

import commonDataObjects as cdo

# get Number of CPU Cores.
cpuNum = 1
try:
    cpuNum = mp.cpu_count()
except NotImplementedError:
    pass


def lookupNiceDistortionName(action):
    actionStr = 'Unknown Distortion Action'
    if action == '-u':
        actionStr = 'Undistorted'
    elif action == '-d':
        actionStr = 'Distorted'
    return actionStr


def lookupOverscanFlag(action):
    actionStr = ''
    if action == 'none':
        pass
    elif action == 'auto':
        actionStr = '-c'
    return actionStr


def getDistoImaExec():
    """Returns the path name of the DistoIma executable."""
    execPath = 'distoIma.exe'
    return execPath


def getScriptFileExt(opsys=None):
    if opsys == None:
        opsys = str(platform.system()).lower()
    ext = 'sh'
    if opsys == 'windows':
        ext = 'bat'
    return ext


def getScriptHeader(opsys=None):
    if opsys == None:
        opsys = str(platform.system()).lower()
    header = '#! /bin/bash'+os.linesep+os.linesep
    if opsys == 'windows':
        header = "@ECHO OFF"+os.linesep+os.linesep
    return header


def getRunCommand(opsys=None):
    """Get the operating system specific run (with forking) command."""
    if opsys == None:
        opsys = str(platform.system()).lower()
    runCmd = 'wine start /Unix %s &'+os.linesep
    if opsys == 'windows':
        runCmd = 'START %s'+os.linesep
    return runCmd


def getScriptCommentChar(opsys=None):
    if opsys == None:
        opsys = str(platform.system()).lower()
    char = '#'
    if opsys == 'windows':
        char = '::'
    return char


def getScriptPreActionCommand(action, opsys=None):
    if opsys == None:
        opsys = str(platform.system()).lower()
    actionStr = lookupNiceDistortionName(action)
    cmd = ("echo Creating "+actionStr+" Plate..."+os.linesep)
    if opsys == 'windows':
        cmd = ("ECHO Creating "+actionStr+" Plate..."+os.linesep)
    return cmd

def getScriptFooter(action, opsys=None):
    if opsys == None:
        opsys = str(platform.system()).lower()
    actionStr = lookupNiceDistortionName(action)
    footer = ("echo Finshed "+actionStr+" Plate!"+os.linesep)
    if opsys == 'windows':
        footer = ("ECHO Finished "+actionStr+" Plate!"+os.linesep+
                  "EXIT"+os.linesep)
    return footer


class Options(object):
    """Options that can be passed to the Warp Batch Script exporter."""
    def __init__(self):
        self.filePath = None
        self.time = None
        self.outDir = '<same>' # <same>, <current>, any path.
        self.useOverscan = 'none'

        # appended to the file path output, before '(un)distort'.
        self.fileSuffix = '_warp4'
        
        # output Image Extension, JPEG is default.
        # if None, use input image extension.
        self.outImageExt = 'jpg'


def main(cam, options):
    filePath = options.filePath
    assert filePath != None
    outDir = options.outDir
    timeList = cdo.parseTimeString(options.time)
    
    assert isinstance(cam, cdo.MMCameraData)
    seq = cdo.MMSequenceData()
    if len(cam.sequences) > 0:
        seq = cam.sequences[0]

    invalidImageMsg = ("DistoIma Script could not be written, "
                       "image path given is invalid, '%s'.")
    if seq.imagePath == None:
        print(invalidImageMsg % seq.imagePath)
        return True

    # Get Image Sequence variables.
    imageSeq = seq.imagePath
    images = cdo.getAllImageSequence(seq.imagePath)
    if len(images) <= 0:
        print(invalidImageMsg % seq.imagePath)
        return True
    seqPad = cdo.getImageSequencePadding(seq.imagePath)
    seqStart, seqEnd = cdo.splitImageSequencePath(seq.imagePath)
    offset = cdo.getImageSequenceStartFrame(seq.imagePath)
    # print 'offset:', repr(offset)

    # get script file syntax, changes based on Operating System.
    binPath = getDistoImaExec()
    scriptExt = getScriptFileExt(opsys='windows')
    comChar = getScriptCommentChar(opsys='windows')
    scriptHeader = getScriptHeader(opsys='windows')
    starterScriptExt = getScriptFileExt()
    starterComChar = getScriptCommentChar()
    starterScriptHeader = getScriptHeader()
    starterRunScript = getRunCommand()

    args = list()
    args.append(binPath)
    args.append('!ACTION FLAG!')
    args.append('!DISTO!')
    args.append('-v')
    args.append('!OVERSCAN FLAG!')
    args.append('-f')
    args.append('!FOCAL!')
    args.append('-k')
    args.append('%.15f' % cam.filmbackWidth)
    args.append('-a')
    args.append('%.15f' % cam.pixelAspectRatio)
    args.append('-p')
    args.append('%.15f,%.15f' % (cam.lensCentreX*cam.width,
                                 cam.lensCentreY*cam.height))
    args.append('-q') # JPEG Quality, 100.
    args.append('100')
    args.append('-b')
    args.append('!FRAME!')
    args.append('-e')
    args.append('!FRAME!')
    args.append('"!IN!"')
    args.append('"!OUT!"')

    actions = ['-u',
               '-d']
    descriptions = [cdo.exportDesc.mmUndistortScript,
                    cdo.exportDesc.mmDistortScript]
    suffixes = ['undistort',
                'distort']
    for i in range(len(actions)):
        action = actions[i]
        desc = descriptions[i]
        suffix = options.fileSuffix+'_'+suffixes[i]
        preAction = getScriptPreActionCommand(action, opsys='windows')
        scriptFooter = getScriptFooter(action, opsys='windows')
        starterPreAction = getScriptPreActionCommand(action)
        starterScriptFooter = getScriptFooter(action)

        # Get the output file path
        outFilePath = cdo.createOutFileName(filePath, cam.name, desc, scriptExt, outDir)
        outFileName = p.split(outFilePath)[1]
        msg = "Writing DistoIma Script file to '%s'."
        print(msg % outFileName)

        # create command string
        cmdTemplate = str()
        for arg in args:
            cmdTemplate += '%s ' % arg
            
        # Write the start-up script.
        starterFilePath = str(outFilePath)
        assert starterFilePath.endswith('.'+scriptExt)
        if scriptExt != starterScriptExt:
            endExt = len(starterFilePath)-len(scriptExt)
            starterFilePath = starterFilePath[:endExt]+starterScriptExt
        cmdStarterFilePath = p.abspath(starterFilePath.replace('!CPU!', 'start'))
        f = open(cmdStarterFilePath, "w")
        if not f.closed:
            f.write(scriptHeader)
            for cpu in range(cpuNum):
                cmdFilePath = p.abspath(outFilePath.replace('!CPU!', str(cpu)))
                f.write(starterRunScript % cmdFilePath)
            f.close()

        # loop over number of cores, to write multiple files out.
        imagePathsCutUp = list()
        totalImages = len(images)
        chunkSize = float(totalImages)/cpuNum
        for cpu in range(cpuNum):
            startIndex = int(math.ceil(chunkSize*cpu))
            endIndex = int(math.ceil(chunkSize*(cpu+1)))-1
            imagePathsCutUp = images[startIndex:endIndex+1]
            cmdFilePath = p.abspath(outFilePath.replace('!CPU!', str(cpu)))

            f = open(cmdFilePath, "w")
            if not f.closed:
                f.write(scriptHeader)
                f.write(comChar+' Camera Name: '+str(cam.name)+os.linesep)
                f.write(preAction)

                # write distortion parameters
                focalData = cam.focalLength
                focalData.simplifyData()

                # write out per-frame commands.
                for imgPath in imagePathsCutUp:
                    overscan = lookupOverscanFlag(options.useOverscan)
                    cmd = str(cmdTemplate)
                    cmd = cmd.replace('!ACTION FLAG!', action)
                    cmd = cmd.replace('!OVERSCAN FLAG!', overscan)

                    # Get the frame number from image path.
                    frameNum = cdo.getImagePathFrameNumber(imageSeq, imgPath)
                    # print 'frameNum:', repr(frameNum)

                    # only output frames that are valid.
                    if cdo.isFrameInTimeList(frameNum, timeList):

                        # Set Distortion Parameter.
                        d = 0.0
                        if isinstance(cam.distortion, cdo.KeyframeData):
                            d = cam.distortion.getValue(frameNum)
                            assert d != None
                        cmd = cmd.replace('!DISTO!', str(d))

                        # Set Focal Length
                        fl = 0.0
                        if isinstance(focalData, cdo.KeyframeData):
                            fl = focalData.getValue(frameNum)
                            assert fl != None
                        cmd = cmd.replace('!FOCAL!', str(fl))

                        # Get image paths
                        outImgPath = str()
                        inImgPath = str()
                        padStr = '#'*seqPad
                        frameStr = str(frameNum).zfill(seqPad)
                        if seqStart.endswith('.'):
                            outImgPath = seqStart[:-1]+suffix+'.'
                        elif seqStart.endswith('_'):
                            outImgPath = seqStart[:-1]+suffix+'_'
                        elif seqStart.endswith('-'):
                            outImgPath = seqStart[:-1]+suffix+'-'
                        else:
                            outImgPath = seqStart+suffix
                        # inImgPath = seqStart+padStr+seqEnd
                        # outImgPath = outImgPath+padStr+'.'+options.outImageExt
                        inImgPath = seqStart+frameStr+seqEnd
                        outImgPath = outImgPath+frameStr+'.'+options.outImageExt

                        # Replace in/out paths.
                        cmd = cmd.replace('!FRAME!', str(frameNum))
                        cmd = cmd.replace('!IN!', cdo.convertUnixToWinePath(inImgPath))
                        cmd = cmd.replace('!OUT!', cdo.convertUnixToWinePath(outImgPath))
                        f.write(cmd+os.linesep+os.linesep)

                f.write(scriptFooter)
                f.close()
    return True
