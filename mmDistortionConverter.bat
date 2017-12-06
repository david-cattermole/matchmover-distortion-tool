:: Copyright David Cattermole, 2013
:: Licensed under the GNU General Public License, 
:: see "COPYING.txt" for more details.

@echo off

setlocal 

set py_exists=0

:: python 2.7 test
if %py_exists%==0 (
   if EXIST "C:\Python27\python.exe" (
      set py_exists=1
      set PY="C:\Python27\python.exe"
      echo Found Python 2.7, great!!!
   ) else (
      if %py_exists%==0 (
      	 set py_exists=0
      )
      echo Python 2.7 doesn't exist on this computer
   )
)

:: python 2.6 test
if %py_exists%==0 (
   if EXIST "C:\Python26\python.exe" (
      set py_exists=1
      set PY="C:\Python26\python.exe"
      echo Found Python 2.6, great!!!
   ) else (
      if %py_exists%==0 (
      	 set py_exists=0
      )
      echo Python 2.6 doesn't exist on this computer
   )
)

:: python 2.5 test
if %py_exists%==0 (
   if EXIST "C:\Python25\python.exe" (
      set py_exists=1
      set PY="C:\Python25\python.exe"
      echo Found Python 2.5, great!!!
   ) else (
      if %py_exists%==0 (
      	 set py_exists=0
      )
      echo Python 2.5 doesn't exist on this computer
   )
)

:: run the program
if %py_exists%==1 (
   %PY% ./bin/mmDistortionConverter.py
) else (
   echo Python does not seem to be installed on this computer,
   echo I'm sorry, we can not run the program.
)

pause

endlocal
