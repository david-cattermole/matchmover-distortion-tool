"""Test the package, run unit tests."""

# Copyright David Cattermole, 2013
# Licensed under the GNU General Public License, 
# see "COPYING.txt" for more details.

import sys
import math
import os
import os.path as p


import commonDataObjects as cdo
import mmFileReader
import converter
import tdeWriteLensFile
import tdeWriteWetaNukeDistortionNode
import mmDistortionConverter


def main(filePath):
    assert cdo.floatIsEqual(float(), float())
    assert cdo.floatIsEqual(float(), sys.float_info.epsilon*10000.0)
    assert cdo.floatIsEqual(float(), sys.float_info.epsilon*99999.9)
    assert cdo.floatIsEqual(float(), sys.float_info.epsilon*19999.9)

    # Test KeyframeData, static and initial
    keyData = cdo.KeyframeData(static=True,
                               initialValue=1.0)
    assert keyData.getValue(0) == 1.0
    assert keyData.static == True
    assert len(keyData.getTimeValues()) == 1

    # Test KeyframeData, static
    keyData = cdo.KeyframeData(static=True)
    assert keyData.getValue(0) == None
    assert keyData.static == True
    assert len(keyData.getTimeValues()) == 1

    # Test KeyframeData, initial value
    keyData = cdo.KeyframeData(initialValue=1.0)
    assert keyData.getValue(0) == 1.0
    assert keyData.static == False
    assert len(keyData.getTimeValues()) == 1

    # Test KeyframeData, consistent variables, when simplifying data.
    keyData = cdo.KeyframeData(static=False)
    assert keyData.length == 0
    keyData.setValue(1.0, 0)
    assert keyData.length == 1
    assert keyData.startFrame == 0
    assert keyData.endFrame == 0
    keyData.setValue(1.0, -1) # negative time value.
    keyData.setValue(1.0, 10)
    assert keyData.length == 3
    ok = keyData.simplifyData()
    assert ok == True
    assert keyData.static == True
    assert keyData.length == 1
    assert keyData.startFrame == 0
    assert keyData.endFrame == 0
    ok = keyData.simplifyData()
    assert ok == True

    # Test KeyframeData, consistent variables, when animated keyframes.
    keyData = cdo.KeyframeData(static=False)
    keyData.setValue(1.0, 0)
    keyData.setValue(1.0, 1)
    keyData.setValue(1.0, 10)
    keyData.setValue(0.0, 20)
    assert keyData.static == False
    ok = keyData.simplifyData()
    assert ok == True
    assert keyData.static == False
    assert keyData.length == 4
    assert keyData.startFrame == 0
    assert keyData.endFrame == 20
    ok = keyData.simplifyData()
    assert ok == True

    # Test KeyframeData, duplicate frame number/value pairs, overwriting keys.
    keyData = cdo.KeyframeData()
    keyData.setValue(1.0, 0)
    keyData.setValue(1.0, 0)
    keyData.setValue(1.0, 0)
    assert keyData.length == 1
    values = keyData.getValues()
    assert len(values) == 1
    ok = keyData.simplifyData()
    assert ok == True
    values = keyData.getValues()
    assert len(values) == 1

    # Test getClosestFrame
    value = {'10':0.0,
             '12':0.0,
             '13':0.0,
             '15':0.0,
             '45':0.0,
             '44':0.0,
             '110':0.0}
    assert cdo.getClosestFrame(10, value) == 10
    assert cdo.getClosestFrame(0, value) == 10
    assert cdo.getClosestFrame(50, value) == 45
    assert cdo.getClosestFrame(2000, value) == 110
    assert cdo.getClosestFrame(14, value) == 13 or 15
    assert cdo.getClosestFrame(28, value) == 15
    assert cdo.getClosestFrame(29, value) == 15
    assert cdo.getClosestFrame(30, value) == 44 
    assert cdo.getClosestFrame(31, value) == 44
    assert cdo.getClosestFrame(32, value) == 44
    assert cdo.getClosestFrame(43, value) == 44
    assert cdo.getClosestFrame(30, value) == 44
    assert cdo.getClosestFrame(-1, value) == 10
    
    return True
