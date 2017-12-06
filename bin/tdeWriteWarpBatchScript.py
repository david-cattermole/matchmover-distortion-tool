"""Writes a batch script to undistort/distort images, using Warp4."""

# Copyright David Cattermole, 2013
# Licensed under the GNU General Public License, 
# see "COPYING.txt" for more details.

import os
import os.path as p
import math
import multiprocessing as mp
import platform

import commonDataObjects as cdo

lensModelName = '3DE Classic LD Model'
distPara = 'Distortion'
defParas = ['Anamorphic Squeeze',
            'Curvature X',
            'Curvature Y',
            'Quartic Distortion']

# get Number of CPU Cores.
cpuNum = 1
try:
    cpuNum = mp.cpu_count()
except NotImplementedError:
    pass


def lookupNiceDistortionName(action):
    actionStr = 'Unknown Distortion Action'
    if action == 'remove_distortion':
        actionStr = 'Undistorted'
    elif action == 'apply_distortion':
        actionStr = 'Distorted'
    return actionStr


def getWarpExec():
    """Returns the path name of the Warp executable."""
    opsys = str(platform.system()).lower()
    execPath = 'warp4'
    if opsys == 'windows':
        execPath = execPath + '.exe'
    return execPath


def getScriptFileExt():
    """Get OS dependant script file extension."""
    opsys = str(platform.system()).lower()
    ext = 'sh'
    if opsys == 'windows':
        ext = 'bat'
    return ext


def getScriptHeader():
    opsys = str(platform.system()).lower()
    header = '#! /bin/bash'+os.linesep+os.linesep
    if opsys == 'windows':
        header = "@ECHO OFF"+os.linesep+os.linesep
    return header


def getRunCommand():
    """Get the operating system specific run (with forking) command."""
    opsys = str(platform.system()).lower()
    runCmd = 'bash %s &'+os.linesep
    if opsys == 'windows':
        runCmd = 'START %s'+os.linesep
    return runCmd


def getScriptCommentChar():
    """Get script specific comment character."""
    opsys = str(platform.system()).lower()
    char = '#'
    if opsys == 'windows':
        char = '::'
    return char


def getScriptPreActionCommand(action):
    opsys = str(platform.system()).lower()
    actionStr = lookupNiceDistortionName(action)
    cmd = ("echo Creating "+actionStr+" Plate..."+os.linesep)
    if opsys == 'windows':
        cmd = ("ECHO Creating "+actionStr+" Plate..."+os.linesep)
    return cmd


def getScriptFooter(action):
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
        # self.offset = None
        self.outDir = '<same>' # <same>, <current>, any path.
        self.useOverscan = 'none'

        # appended to the file path output, before '(un)distort'.
        self.fileSuffix = '_warp4'
        

def main(cam, options):
    filePath = options.filePath
    # offset = options.offset
    outDir = options.outDir
    # if offset == None or not isinstance(offset, int):
    #     offset = 0
    assert filePath != None
    timeList = cdo.parseTimeString(options.time)
    
    assert isinstance(cam, cdo.TDECameraData)
    seq = cdo.TDESequenceData()
    if len(cam.sequences) > 0:
        seq = cam.sequences[0]

    invalidImageMsg = ("Warp Script could not be written, "
                       "image path given is invalid, '%s'.")
    if seq.imagePath == None:
        print(invalidImageMsg % seq.imagePath)
        return True

    # Get Image Sequence variables.
    images = cdo.getAllImageSequence(seq.imagePath)
    if len(images) <= 0:
        print(invalidImageMsg % repr(seq.imagePath))
        return True
    seqPad = cdo.getImageSequencePadding(seq.imagePath)
    seqStart, seqEnd = cdo.splitImageSequencePath(seq.imagePath)

    # get script file syntax, changes based on Operating System.
    binPath = getWarpExec()
    scriptExt = getScriptFileExt()
    comChar = getScriptCommentChar()
    scriptHeader = getScriptHeader()
    runScript = getRunCommand()

    args = list()
    args.append(binPath)
    args.append('-in')
    args.append('"!IN!"')
    args.append('-out')
    args.append('"!OUT!"')
    args.append('-action')
    args.append('!ACTION!')
    args.append('-model')
    args.append('"%s"' % lensModelName)
    args.append('-parameters')
    args.append('!%s!' % distPara.upper())
    for para in defParas:
        args.append('!%s!' % para.upper())
    args.append('-pixel_aspect')
    args.append('%.15f' % cam.pixelAspectRatio)
    args.append('-lco')
    args.append('%.15f' % cam.lensCentreX)
    args.append('%.15f' % cam.lensCentreY)
    args.append('-filmback')
    args.append('%.15f' % cam.filmbackWidth)
    args.append('%.15f' % cam.filmbackHeight)
    args.append('-overscan')
    args.append('!OVERSCAN!')
    args.append('-verbose')

    actions = ['remove_distortion',
               'apply_distortion']
    descriptions = [cdo.exportDesc.tdeUndistortScript,
                    cdo.exportDesc.tdeDistortScript]
    suffixes = ['undistort',
                'distort']
    for i in range(len(actions)):
        action = actions[i]
        desc = descriptions[i]
        suffix = options.fileSuffix+'_'+suffixes[i]
        preAction = getScriptPreActionCommand(action)
        scriptFooter = getScriptFooter(action)

        # Get the output file path
        outFilePath = cdo.createOutFileName(filePath,
                                            cam.name, desc,
                                            scriptExt, outDir)
        outFileName = p.split(outFilePath)[1]
        msg = "Writing Warp Script file to '%s'."
        print(msg % outFileName)

        # create command string
        cmdTemplate = str()
        for arg in args:
            cmdTemplate += '%s ' % arg

        # Write the start-up script.
        cmdStarterFilePath = p.abspath(outFilePath.replace('!CPU!', 'start'))
        f = open(cmdStarterFilePath, "w")
        if not f.closed:
            f.write(scriptHeader)
            for cpu in range(cpuNum):
                cmdFilePath = p.abspath(outFilePath.replace('!CPU!', str(cpu)))
                f.write(runScript % cmdFilePath)
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
                    cmd = str(cmdTemplate)
                    cmd = cmd.replace('!ACTION!', action)
                    cmd = cmd.replace('!OVERSCAN!', options.useOverscan)

                    # Get the frame number from image path.
                    frameNum = cdo.getImagePathFrameNumber(seq.imagePath, imgPath)

                    # only output frames that are valid.
                    if cdo.isFrameInTimeList(frameNum, timeList):

                        # Set Distortion Parameter.
                        d = 0.0
                        if isinstance(cam.distortion, cdo.KeyframeData):
                            d = cam.distortion.getValue(frameNum)
                            assert d != None
                        paraStr = '!%s!' % distPara.upper()
                        cmd = cmd.replace(paraStr, str(d))

                        # Set Default Parameters.
                        for para in defParas:
                            d = 0.0
                            if para == 'Anamorphic Squeeze':
                                d = 1.0
                            paraStr = '!%s!' % para.upper()
                            cmd = cmd.replace(paraStr, str(d))

                        # Get image path
                        outImgPath = str()
                        frameStr = str(frameNum).zfill(seqPad)
                        if seqStart.endswith('.'):
                            outImgPath = seqStart[:-1]+suffix+'.'
                        elif seqStart.endswith('_'):
                            outImgPath = seqStart[:-1]+suffix+'_'
                        elif seqStart.endswith('-'):
                            outImgPath = seqStart[:-1]+suffix+'-'
                        else:
                            outImgPath = seqStart+suffix
                        outImgPath = outImgPath+frameStr+seqEnd

                        # Replace in/out paths.
                        cmd = cmd.replace('!IN!', imgPath)
                        cmd = cmd.replace('!OUT!', outImgPath)
                        f.write(cmd+os.linesep+os.linesep)

                f.write(scriptFooter)
                f.close()
    return True
