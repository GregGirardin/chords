#!/usr/bin/python
from __future__ import print_function
import os, sys, glob, copy, json

class bcolors:
  BLUE      = '\033[94m'
  RED       = '\033[91m'
  GREEN     = '\033[92m'
  WARNING   = '\033[93m'
  BOLD      = '\033[1m'
  UNDERLINE = '\033[4m'
  REVERSE   = '\033[7m'
  ENDC      = '\033[0m'

cursorElement = 0
cursorParam = 0
cursorPos = 0

class entry( object ):
  def __init__( self, name, elements ):
    self.name = name
    self.elements = elements

class pV( object ): # param : value
  def __init__( self, param, value ):
    self.param = param
    self.value = value

DEFAULT_FILE_NAME = "jsonData"

helpString = bcolors.WARNING + \
  "\n" \
  "hjkl  - Navigate (or use arrows).\n" \
  "ad    - Add/Delete entry.\n" \
  "e     - Edit value\n" \
  "os    - Open/save.\n" \
  "n     - Name the file.\n" \
  "/     - Search for entry.\n" \
  "?     - Show all attributes.\n" \
  "q     - Quit." + bcolors.ENDC

'''
  List of entry.
  Not using a dictionary so we can sort the order more easily.
'''
entryList = [
            entry( "Entry1", [ pV( "param1", "value1" ),
                               pV( "param2", "value2" ),
                               pV( "param3", "value3" ) ] ),
            entry( "Entry2", [ pV( "param1", "value1" ),
                               pV( "param2", "value2" ),
                               pV( "param3", "value3" ) ] ),
            entry( "Entry3", [ pV( "param1", "value1" ),
                               pV( "param2", "value2" ),
                               pV( "param3", "value3" ) ] ),
            ]

statusString = None
fileName = DEFAULT_FILE_NAME

# Cursor location

# Return a list of files that we want to associate metadata with
def getLocalFiles():
  re = "*.txt" # For now we'll only work with .txt files. TBD, do all files except the meta data file
  matchList = glob.glob( re )

  def getKey( item ):
    return item.fileName

  matchList.sort( key=getKey )
  return matchList

def displayUI():
  global statusString

  os.system( 'clear' )
  print( "JSON generator" )

  first = cursorElement - 2
  if first < 0:
    first = 0

  for ix in range( first, first + 5 ):
    if ix == len( entryList ):
      break

    if( ix == cursorElement ) and ( cursorParam == None ):
      print( bcolors.REVERSE + entryList[ ix ].name + bcolors.ENDC )
    else:
      print( entryList[ ix ].name )

    for elemIx in range( 0, len( entryList[ ix ].elements ) ):
      if( cursorElement == ix ) and ( cursorParam == elemIx ):
        if( cursorPos == 0 ):
          print( " " + bcolors.REVERSE + entryList[ ix ].elements[ elemIx ].param + bcolors.ENDC + ">" +
                 entryList[ ix ].elements[ elemIx ].value )
        else:
          print( " " + entryList[ ix ].elements[ elemIx ].param + ">" +
                 bcolors.REVERSE + entryList[ ix ].elements[ elemIx ].value + bcolors.ENDC )
      else:
        print( " " + entryList[ ix ].elements[ elemIx ].param + ">" + entryList[ ix ].elements[ elemIx ].value )

def getInput():
  # Copied from http://stackoverflow.com/questions/983354/how-do-i-make-python-to-wait-for-a-pressed-key
  import termios, fcntl, sys, os
  fd = sys.stdin.fileno()
  flags_save = fcntl.fcntl( fd, fcntl.F_GETFL )
  attrs_save = termios.tcgetattr( fd )
  attrs = list( attrs_save )
  attrs[ 0 ] &= ~( termios.IGNBRK | termios.BRKINT | termios.PARMRK | termios.ISTRIP |
                   termios.INLCR  | termios.IGNCR  | termios.ICRNL  | termios.IXON )
  attrs[ 1 ] &= ~termios.OPOST
  attrs[ 2 ] &= ~( termios.CSIZE | termios.PARENB )
  attrs[ 2 ] |= termios.CS8
  attrs[ 3 ] &= ~( termios.ECHONL | termios.ECHO | termios.ICANON | termios.ISIG | termios.IEXTEN )
  termios.tcsetattr( fd, termios.TCSANOW, attrs )
  fcntl.fcntl( fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK )
  try:
    ret = sys.stdin.read( 1 )
    if ord( ret ) == 27: # Escape
      ret = sys.stdin.read( 1 )
      ret = sys.stdin.read( 1 )
      if ret == 'A':
        ret = 'UP'
      elif ret == 'B':
        ret = 'DOWN'
      elif ret == 'C':
        ret = 'RIGHT'
      elif ret == 'D':
        ret = 'LEFT'
      else:
        print( int( ret ) )
        exit()

  except KeyboardInterrupt:
    ret = 0
  finally:
    termios.tcsetattr( fd, termios.TCSAFLUSH, attrs_save )
    fcntl.fcntl( fd, fcntl.F_SETFL, flags_save )
  return ret

# Start of main loop.
displayUI()
while True:
  ch = getInput()

  if( ch == "DOWN" or ch == "j" ):
    if len( entryList ) == 0: # List is empty
      assert( cursorElement == None )
      assert( cursorParam == None )
    elif cursorElement == None: # Go to first element
      cursorElement = 0
      cursorParam = None
      cursorPos = 0
    else: # Go to next param
      cursorParam = 0 if cursorParam is None else cursorParam + 1

      numParams = len( entryList[ cursorElement ].elements )

      if cursorParam == numParams:
        cursorElement += 1
        cursorParam = None

      if cursorElement == len( entryList ): # Go back to the end.
        cursorElement = len( entryList ) - 1
        cursorParam = len( entryList[ cursorElement ].elements ) - 1
  elif( ch == "UP" or ch == "k" ):
    if cursorParam > 0:
      cursorParam -= 1
    elif cursorParam == 0:
      cursorParam = None
    elif cursorElement > 0:
      cursorElement -= 1
      cursorParam = len( entryList[ cursorElement ].elements ) - 1
  elif( ch == "RIGHT" or ch == "l" ):
    cursorPos = 1
  elif( ch == "LEFT" or ch == "h" ):
    cursorPos = 0
  elif ch == 'n':
    fileName = raw_input( 'Enter file name:' )
    if fileName == "":
      fileName = DEFAULT_FILE_NAME
  elif ch == 'e':
    if cursorElement is not None:
      newVal = raw_input( 'Enter new value:' )
      if cursorParam == None:
        entryList[ cursorElement ].name = newVal
      elif cursorPos == 0:
        entryList[ cursorElement ].elements[ cursorParam ].param = newVal
      else:
        entryList[ cursorElement ].elements[ cursorParam ].value = newVal

  elif ch == '/':
    searchFor = raw_input( 'Search:' )

  elif ch == '?':
    print( helpString )
    foo = getInput()
  elif ch == 'q':
    exit()

  displayUI()