"""Defines common Classes and Functions.

Internally, all data should be stored as millimetres,
and converted when being read."""

# Copyright David Cattermole, 2013
# Licensed under the GNU General Public License, 
# see "COPYING.txt" for more details.

import sys
import os
import os.path as p
import glob
import platform

projectName = 'MatchMover Distortion Tool'
projectVersion = 'v0.3.0'
projectAuthor = 'David Cattermole'
projectEmail = 'cattermole91@gmail.com'
projectTitle = projectName+' - '+projectVersion
projectSubtitle = 'Written by '+projectAuthor+' ('+projectEmail+')'


def floatIsEqual(x, y):
    # A small number, but still quite large, this sure ensure that "static"
    # values are treated as such.

    # float equality
    if x == y:
        return True

    # float equality, with an epsilon
    eps = sys.float_info.epsilon*100.0
    if x < (y+eps) and x > (y-eps):
        return True

    # string equality, with nine decimal places.
    xStr = '%.9f' % float(x)
    yStr = '%.9f' % float(y)
    if xStr == yStr:
        return True

    return False


class SoftwareType(object):
    """Contains entries for all supported software,
    uses these rather than the string names themselves."""
    def __init__(self):
        self.tde = "3DEqualizer4"
        self.mm = "Matchmover"
softwareType = SoftwareType()


class Units(object):
    """All string equivalents of Units that can be used."""
    def __init__(self):
        self.mm = 'mm'
        self.cm = 'cm'
        self.m = 'm'
units = Units()


class ExportFileDescription(object):
    def __init__(self):
        self.tdeRawText = '3deRawText'
        self.tdeLens = '3deLens'
        self.nukeWetaNode = 'wetaDistortionNode'
        self.mmDistortScript = 'mmDistortScript_!CPU!'
        self.mmUndistortScript = 'mmUndistortScript_!CPU!'
        self.tdeDistortScript = 'tdeDistortScript_!CPU!'
        self.tdeUndistortScript = 'tdeUndistortScript_!CPU!'
exportDesc = ExportFileDescription()


def createOutFileName(inFile, cameraName,
                      suffix, outExt):
    assert isinstance(inFile, str) or isinstance(inFile, unicode)
    assert isinstance(cameraName, str)
    assert isinstance(suffix, str)
    assert isinstance(outExt, str)

    inFile = p.abspath(str(inFile))

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


def getAllImageSequence(cameraImagePath):
    """Try to get all image files from an image sequence path."""
    images = list()

    imagePath = p.abspath(str(cameraImagePath))
    globPath = str()
    if imagePath.find('#') != -1:
        globPath = imagePath.replace('#', '[0-9]')
    elif imagePath.find('@') != -1:
        globPath = imagePath.replace('@', '[0-9][0-9][0-9][0-9]')

    if globPath == str():
        msg = "Warning: Could not parse image sequence path, '%s'."
        print(msg % repr(cameraImagePath))
        return images

    images = glob.glob(globPath)
    
    if len(images) == 0:
        msg = "Warning: Could not get image paths from sequence path, '%s'."
        print(msg % repr(cameraImagePath))
        return images

    images.sort()
    return images


def splitImageSequencePath(cameraImagePath):
    """Split an image sequence path where the frame number should have been."""
    seqStart = None
    seqEnd = None
    imagePath = str(cameraImagePath)
    if imagePath.find('#') != -1:
        padSplit = imagePath.split('#')
        seqStart = padSplit[0]
        seqEnd = padSplit[-1]
    elif imagePath.find('@') != -1:
        padSplit = imagePath.split('@')
        seqStart = padSplit[0]
        seqEnd = padSplit[-1]
    if seqStart == None or seqEnd == None:
        msg = "Warning: Could not split the image sequence, '%s'"
        print(msg % cameraImagePath)
    # assert seqStart != None
    # assert seqEnd != None
    return (seqStart, seqEnd)


def getImagePathFrameNumber(seqPath, imagePath):
    """Given the sequence and image path, give the frame number of the image path."""
    frameNum = None
    seqStart, seqEnd = splitImageSequencePath(seqPath)
    if seqStart != None and seqEnd != None:
        startNum = len(seqStart)
        endNum = startNum+len(seqEnd)
        frameStr = imagePath[startNum:endNum]
        try:
            frameNum = int(frameStr)
        except ValueError:
            pass
    return frameNum


def getImageSequencePadding(cameraImagePath):
    """Returns the padding of the image sequence path."""
    pad = None
    imagePath = str(cameraImagePath)
    if imagePath.find('#') != -1:
        pad = imagePath.count('#')
    elif imagePath.find('@') != -1:
        pad = int(imagePath.count('@')*4)
    if pad == None:
        msg = "Warning: Could not get the padding for the image sequence, '%s'"
        print(msg % cameraImagePath)
    assert isinstance(pad, int) or pad == None
    return pad


def convertUnixToWinePath(filePath):
    """Converts a Unix-type file path to a
    Windows Emulator (Wine) file path."""
    if str(platform.system()).lower() == 'windows':
        return filePath
    pathSep = '\\'
    winePathStarter = 'Z:\\'
    winePath = str(filePath).replace(os.sep, pathSep)

    # remove the first character if it is a '\'
    if winePath.startswith(pathSep):
        winePath = winePath[1:]
    winePath = winePathStarter+winePath
    return winePath


def getClosestFrame(frame, value):
    """Get the closest frame in the dictionary value.

    frame - An int for the frame to look up.
    value - A dict with keys as the frames to look up.

    Returns the closest frame in the dict value."""
    # TODO: This function is quite slow, it should be improved.
    keys = value.keys()
    intKeys = list()
    for key in keys:
        intKeys.append(int(key))
    keys = sorted(intKeys)
    diff = int()
    closestFrame = None
    for key in keys:
        if closestFrame == None:
            closestFrame = key
            diff = frame-closestFrame
        if (key <= frame) and (key > closestFrame):
            closestFrame = key
        # if (key >= frame) and (key < closestFrame):
        #     closestFrame = key
        diff = closestFrame-frame
    keys.reverse()
    closestFrameRev = None
    for key in keys:
        if closestFrameRev == None:
            closestFrameRev = key
            diff = frame-closestFrameRev
        # if (key <= frame) and (key > closestFrameRev):
        #     closestFrameRev = key
        if (key >= frame) and (key < closestFrameRev):
            closestFrameRev = key
        diff = closestFrameRev-frame    
    diffRef = abs(closestFrameRev-frame)
    diff = abs(closestFrame-frame)
    if diffRef < diff:
        closestFrame = closestFrameRev
    return closestFrame


class KeyframeData(object):
    """Keyframe data, used to store animated (or static) data."""
    def __init__(self, static=False, initialValue=None):
        self.static = static
        self.startFrame = 0
        self.endFrame = 0
        self.length = 0
        self.value = None
        if initialValue != None:
            self.setValue(initialValue, 0)

    def getValue(self, frame):
        "Get the key value at frame. frame is an integer."
        # TODO: Should we get the closest frame, 
        #  if the frame does not not exist?
        value = None
        # lookupFrame = frame - self.startFrame
        if self.static == True:
            value = self.value
        elif self.static == False:
            assert isinstance(self.value, dict)
            if isinstance(self.value, dict):
                key = str(frame)
                if self.value.has_key(key):
                    value = self.value[key]
                else:
                    # there is no key on the frame, find the closest frame.
                    frame = getClosestFrame(frame, self.value)
                    key = str(frame)
                    if self.value.has_key(key):
                        value = self.value[key]

        return value

    def getKeyValues(self):
        keyValues = list()
        if isinstance(self.value, dict):
            # Sort keys, based on int values, not string.
            keys = self.value.keys()            
            intKeys = list()
            for key in keys:
                intKeys.append(int(key))
            keys = sorted(intKeys)

            # Create key/value pairs.
            for key in keys:
                keyValue = [int(key),
                            self.getValue(int(key))]
                keyValues.append(keyValue)
        else:
            assert isinstance(self.startFrame, int)
            keyValue = [self.startFrame, self.getValue(0)]
            keyValues.append(keyValue)
        return keyValues

    def getTimeValues(self):
        """Get all times, should be first half of getKeyValues."""
        timeValues = list()
        keyValues = self.getKeyValues()
        for kv in keyValues:
            timeValues.append(kv[0])
        return timeValues

    def getValues(self):
        """Get all values, should be second half of getKeyValues."""
        values = list()
        keyValues = self.getKeyValues()
        for kv in keyValues:
            values.append(kv[1])
        return values

    def setValue(self, x, f):
        """Set the value x, at frame f."""

        if self.static == False:
            # Initialise the value to a dict
            if self.value == None:
                self.value = dict()

            if self.value.has_key(str(f)) and \
               self.value[str(f)] == x:
                return True

            # Set the value.
            self.value[str(f)] = x

            # set start and end frame and length
            if self.value[str(f)] == x:
                self.length = self.length + 1
                if self.startFrame > f:
                    self.startFrame = f
                if self.endFrame < f:
                    self.endFrame = f
        else:
            # Set the value, overwrites values without checking.
            self.value = x

            # set start and end frame and length
            if self.value == x:
                self.length = 1
                self.startFrame = 0
                self.endFrame = 1

        return True

    def simplifyData(self):
        """Tries to convert the keyframe data into
        static if all values are the same."""

        if self.static == False:
            assert isinstance(self.value, dict)
            initial = None
            total = float() # assume it's a float?
            totalNum = int()
            for key in iter(self.value):
                if initial == None:
                    initial = self.value[key]
                total = total+self.value[key]
                totalNum = totalNum + 1
            average = total/totalNum
            if floatIsEqual(average, initial):
                self.value = average
                self.static = True
                self.length = 1
                self.startFrame = 0
                self.endFrame = 0
        else:
            self.length = 1
            self.startFrame = 0
            self.endFrame = 0
        return True


class CameraData(object):
    """Camera Data base class."""
    def __init__(self):
        self.name = None
        self.index = None
        self._software = None
        self._units = None
        self.focalLength = None
        self.filmbackWidth = None
        self.filmbackHeight = None
        self.filmAspectRatio = None
        self.lensCentreX = None
        self.lensCentreY = None
        self.width = None
        self.height = None
        self.imageAspectRatio = None
        self.pixelAspectRatio = None
        self.distortion = None
        self.sequences = list()


class MMCameraData(CameraData):
    """Used to store data of a matchmover camera."""
    def __init__(self):
        CameraData.__init__(self)
        self._software = softwareType.mm
        self._units = units.mm
        self.focal = None


class TDECameraData(CameraData):
    """Used to store data of a 3DE camera."""
    def __init__(self):
        CameraData.__init__(self)
        self._software = softwareType.tde
        self._units = units.cm
        self.offset = None


class SequenceData(object):
    """Sequence Data base class.

    Data about the images being tracked."""
    def __init__(self):
        self.name = None
        self.index = None
        self._software = None
        self.cameraName = None
        self.cameraIndex = None
        self.width = None
        self.height = None
        self.imageAspectRatio = None
        self.imagePath = None
        self.frameRange = None


class MMSequenceData(SequenceData):
    """Used to store data of a matchmover sequence."""
    def __init__(self):
        SequenceData.__init__(self)
        self._software = softwareType.mm


class TDESequenceData(SequenceData):
    """Used to store data of a matchmover sequence."""
    def __init__(self):
        SequenceData.__init__(self)
        self._software = softwareType.tde
        

class SceneData(object):
    """Scene Data base class.

    Scene Data can also be called project data because it will store all
    information about a tracking software project data."""
    def __init__(self):
        self.name = None
        self.index = None
        self.path = None
        self._software = None
        self._units = None
        self.frameRange = None
        self.cameras = None
        self.sequences = None


class MMSceneData(SceneData):
    """Used to store all data of a matchmover project file."""
    def __init__(self):
        SceneData.__init__(self)
        self._software = softwareType.mm
        self._units = units.mm


class TDESceneData(SceneData):
    """Used to store all data of a 3DE project file."""
    def __init__(self):
        SceneData.__init__(self)
        self._software = softwareType.tde
        self._units = units.cm
