"""Defines common Classes and Functions.

Internally, all data should be stored as millimetres,
and converted when being read."""

# Copyright David Cattermole, 2013
# Licensed under the GNU General Public License, 
# see "COPYING.txt" for more details.

import sys

def floatIsEqual(x, y):
    # A small number, but still quite large, this sure ensure that "static"
    # values are treated as such.
    eps = sys.float_info.epsilon*100000.0
    if x == y:
        return True
    if x < (y+eps) and x > (y-eps):
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


class KeyframeData(object):
    """Keyframe data, used to store animated (or static) data."""
    def __init__(self, static=False):
        self.static = static
        self.startFrame = 0
        self.endFrame = 0
        self.length = 0
        self.value = None

    def getValue(self, frame):
        "Get the key value at frame. frame is an integer."
        # TODO: Should we get the closest frame, 
        #  if the frame doest not exist?
        value = None
        lookupFrame = frame - self.startFrame
        if self.static == True:
            value = self.value
        elif self.static == False:
            if isinstance(self.value, dict):
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
            keyValue = [0, self.getValue(0)]
            keyValues.append(keyValue)
        return keyValues

    def getTimeValues(self):
        timeValues = list()
        keyValues = self.getKeyValues()
        for kv in keyValues:
            timeValues.append(kv[0])
        return timeValues

    def getStart(self):
        return self.startFrame

    def getEnd(self):
        return self.endFrame

    def setValue(self, x, f):
        """Set the value x, at frame f."""

        if self.static == False:
            # Initialise the value to a dict
            if self.value == None:
                self.value = dict()

            # Set the value.
            succeed = False
            try:
                self.value[str(f)] = x
                succeed = True
            except ValueError:
                pass

            # set start and end frame and length
            if succeed:
                self.length = self.length + 1
                if self.startFrame > f:
                    self.startFrame = f
                if self.endFrame < f:
                    self.endFrame = f
        else:

            # Set the value, overwrites values without checking.
            succeed = False
            try:
                self.value = x
                succeed = True
            except ValueError:
                pass

            # set start and end frame and length
            if succeed:
                self.length = self.length + 1
                if self.startFrame < f:
                    self.startFrame = f
                if self.endFrame > f:
                    self.endFrame = f

        return True

    def simplifyData(self):
        """Tries to convert the keyframe data into
        static if all values are the same."""

        if self.static == False:
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
                self.endFrame = 1
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
        self.sequences = None


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
