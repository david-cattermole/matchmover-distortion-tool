"""Reads a Matchmover rzml file and outputs camera data for the file.

The Matchmover fovx parameter is caclulated like this
(2.0*math.atan((3.2*1.5)/(2.0*5.9828)))* (180.0/math.pi)

To calculate a focal length from a FOV like this
(0.5*filmbackWidth*pixelAspectRatio) / (math.tan((math.pi/360.0)*fov))
"""
# Copyright David Cattermole, 2013
# Licensed under the GNU General Public License,
# see "COPYING.txt" for more details.

import math
import os
import os.path as p

import commonDataObjects as cdo

import xml.dom.minidom as xdm


def getKey(attrs, key, dataType, default=None):
    """Get the key from the attrs, with the dataType wanted."""
    assert isinstance(attrs, dict)
    assert isinstance(key, str)
    assert isinstance(dataType, str)

    # get the value, or default if we can't.
    value = default
    if attrs.has_key(key):
        value = attrs[key]

    # convert into dataType, if we can.
    if value != None:
        if dataType == 'str':
            value = str(value)
        elif dataType == 'int':
            value = int(value)
        elif dataType == 'float':
            value = float(value)
    return value


def getAttrs(node):
    """Get the attributes from the node. """
    assert isinstance(node, xdm.Element)
    attrs = dict()
    hasAttrs = node.hasAttributes()
    if hasAttrs:
        ats = node.attributes
        for i in range(ats.length):
            at = ats.item(i)
            attrs[at.name] = at.nodeValue
    return attrs


def getGlobalFrameRange(dom):
    """Return the global time range of the file as a tuple (start, end, fps)."""
    trng = dom.getElementsByTagName("TRNG")
    for node in trng:

        # Only get the time range that is "global"
        # (has RZML tag as a parent).
        parNode = node.parentNode
        if parNode != None and parNode.nodeName == 'RZML':
            attrs = getAttrs(node)

    trim = getKey(attrs, 't', 'int')
    length = getKey(attrs, 'd', 'int')

    startFrame = int()
    endFrame = int()
    startFrame = trim
    if length != None:
        endFrame = trim+(length-1)

    fps = getKey(attrs, 'f', 'int')
    assert startFrame < endFrame
    assert fps >= 0
    return (startFrame, endFrame, fps)


def getCameras(dom):
    cams = list()
    cinfs = dom.getElementsByTagName("CINF")
    for node in cinfs:
        attrs = getAttrs(node)

        # create camera object and fill in information.
        cam = cdo.MMCameraData()

        cam.name = getKey(attrs, 'n', 'str')
        cam.index = getKey(attrs, 'i', 'int')

        cam.width = getKey(attrs, 'sw', 'int', default=512)
        cam.height = getKey(attrs, 'sh', 'int', default=512)
        cam.imageAspectRatio = float(cam.width)/float(cam.height)

        cam.filmbackHeight = getKey(attrs, 'fbh', 'float', default=24.0)
        cam.pixelAspectRatio = getKey(attrs, 'a', 'float', default=1.0)
        cam.filmbackWidth = float(cam.filmbackHeight*cam.imageAspectRatio)
        cam.filmAspectRatio = float(cam.filmbackWidth/cam.filmbackHeight)

        cam.focalLength = cdo.KeyframeData(static=True)
        cam.focalLength.setValue(30.0, 0)
        assert cam.focalLength.length == 1

        cam.focal = cdo.KeyframeData(static=True)
        cam.focal.setValue(1550.0, 0)
        assert cam.focal.length == 1

        cam.distortion = cdo.KeyframeData(static=True)
        cam.distortion.setValue(0.0, 0)
        assert cam.distortion.length == 1

        cams.append(cam)
    return cams


def getShots(dom, cams):
    seqDataList = list()
    shotTag = dom.getElementsByTagName("SHOT")
    # constant used in the loop.
    piTwoRad = math.pi/360.0
    for node in shotTag:
        shotAttrs = getAttrs(node)

        shot = cdo.MMSequenceData()

        # Get cam index from shot, loop over cams
        # and get the camera that this shot links to.
        shotCam = None
        camIndex = getKey(shotAttrs, 'ci', 'int', default=1)
        if camIndex != 0:
            for cam in cams:
                if cam.index == camIndex:
                    shotCam = cam
                    shot.cameraIndex = int(camIndex)
        shot.cameraName = str(cam.name)

        # put shot data into shot object.
        shot.name = str(getKey(shotAttrs, 'n', 'str'))
        shot.index = str(getKey(shotAttrs, 'i', 'str'))

        shot.width = int(getKey(shotAttrs, 'w', 'int'))
        shot.height = int(getKey(shotAttrs, 'h', 'int'))
        shot.imageAspectRatio = float(shot.width)/float(shot.height)

        shotCam.focalLength = cdo.KeyframeData()
        shotCam.focal = cdo.KeyframeData()
        shotCam.distortion = cdo.KeyframeData()

        # # initialise list of sequences for camera.
        # shotCam.sequences = list()

        # loop over all frames in the shot.
        halfFbWidth = 0.5*shotCam.filmbackWidth
        for childNode in node.childNodes:
            if childNode.nodeName == 'IPLN':
                imgAttrs = getAttrs(childNode)
                shot.imagePath = getKey(imgAttrs, 'img', 'str')
            elif childNode.nodeName == 'TRNG':
                trngAttrs = getAttrs(childNode)
                trim = getKey(trngAttrs, 't', 'int')
                length = getKey(trngAttrs, 'd', 'int')
                startFrame = int()
                endFrame = int()
                startFrame = trim
                if length != None:
                    endFrame = trim+(length-1)
                fps = getKey(trngAttrs, 'f', 'float')
                shot.frameRange = (startFrame, endFrame, fps)
            elif childNode.nodeName == 'CFRM':
                frameAttrs = getAttrs(childNode)

                frame = getKey(frameAttrs, 't', 'int')
                if frame == None:
                    frame = int(0)
                assert frame >= 0

                fovx = getKey(frameAttrs, 'fovx', 'float')
                pixelRatio = getKey(frameAttrs, 'pr', 'float', default=float(1))
                dst = getKey(frameAttrs, 'rd', 'float', default=0.0)
                fovy = float(fovx)/float(pixelRatio)

                # calculate focal length (from the FOV) and the "focal" attribute.
                assert isinstance(shotCam.filmbackWidth, float)
                focalLength = (halfFbWidth)/(math.tan(piTwoRad*fovx))
                focal = (focalLength*float(shot.width))/shotCam.filmbackWidth

                shotCam.focal.setValue(focal, frame)
                shotCam.focalLength.setValue(focalLength, frame)
                shotCam.distortion.setValue(dst, frame)

        shotCam.focalLength.simplifyData()
        shotCam.focal.simplifyData()
        shotCam.distortion.simplifyData()

        shotCam.sequences.append(shot)

        seqDataList.append(shot)

    assert isinstance(shotCam.sequences, list)
    return seqDataList


def readRZML(fileName):
    dom = xdm.parse(fileName)

    rzml = dom.getElementsByTagName("RZML")

    globalFrameRange = getGlobalFrameRange(dom)
    cameras = getCameras(dom)
    shots = getShots(dom, cameras)

    project = cdo.MMSceneData()
    project.name = p.split(fileName)[1]
    project.index = int()
    project.path = fileName
    project.cameras = cameras
    project.sequences = shots
    project.frameRange = globalFrameRange
    return project
