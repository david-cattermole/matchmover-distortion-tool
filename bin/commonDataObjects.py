"""Defines common Classes and Functions.

Internally, all data should be stored as millimetres,
and converted when being read."""

# Copyright David Cattermole, 2013
# Licensed under the GNU General Public License, 
# see "COPYING.txt" for more details.

import sys


projectName = 'MatchMover Distortion Tool'
projectVersion = 'v0.2.1'
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
    """ """
    def __init__(self):
        self.mm = 'mm'
        self.cm = 'cm'
        self.m = 'm'
units = Units()


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
