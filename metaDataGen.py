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

lastSearch = None

class entry( object ):
  def __init__( self, name, elements ):
    self.name = name
    self.elements = elements

class pV( object ): # name : value
  def __init__( self, name, value ):
    self.name = name
    self.value = value

DEFAULT_FILE_NAME = "jsonData.json"

helpString = bcolors.WARNING + \
  "\n" \
  "ad - Add/Delete entry.\n" \
  "e  - Edit value\n" \
  "os - Open/save.\n" \
  "n  - Name the file.\n" \
  "/  - Search for entry.\n" \
  "q  - Quit." + bcolors.ENDC

'''
  List of entry.
  Not using a dictionary so we can sort the order more easily.
'''
entryList = [
              entry( "Entry1", [ pV( "param1", "value1" ), pV( "param2", "value2" ) ] ),
              entry( "Entry2", [ pV( "param1", "value1" ), pV( "param2", "value2" ) ] ),
            ]

statusString = None
fileName = DEFAULT_FILE_NAME

def displayUI():
  global statusString

  os.system( 'clear' )
  print( "Metadata generator" )
  print( "File: " + fileName )
  print( "----------------------------" )

  if len( entryList ) == 0:
    print( "No elements." )
    return

  if not cursorElement:
    first = 0
  else:
    first = cursorElement - 3
    if first < 0:
      first = 0

  for ix in range( first, first + 7 ):
    if ix == len( entryList ):
      break

    if ix == cursorElement and cursorParam == None:
      print( bcolors.REVERSE + entryList[ ix ].name + bcolors.ENDC )
    else:
      print( entryList[ ix ].name )

    for elemIx in range( 0, len( entryList[ ix ].elements ) ):
      if cursorElement == ix and cursorParam == elemIx:
        if cursorPos == 0:
          print( " " + bcolors.REVERSE +
                 entryList[ ix ].elements[ elemIx ].name + bcolors.ENDC + ":" +
                 entryList[ ix ].elements[ elemIx ].value )
        else:
          print( " " + entryList[ ix ].elements[ elemIx ].name + ":" +
                 bcolors.REVERSE + entryList[ ix ].elements[ elemIx ].value + bcolors.ENDC )
      else:
        print( " " + entryList[ ix ].elements[ elemIx ].name + ":" +
                     entryList[ ix ].elements[ elemIx ].value )

  print( "----------------------------" )
  print( str( len( entryList ) ) + " entries." )

  if statusString:
    print( "\n" + bcolors.WARNING + statusString + bcolors.ENDC )
    statusString = None

def openJson():
  global statusString, fileName, entryList

  selectedfileIx = 0
  re = "./*.json"

  matchList = glob.glob( re )

  if not matchList:
    statusString = "No files."
    return None

  while True:
    selSong = None
    os.system( 'clear' )
    print( "Use arrow keys to select or exit.\n" )
    index = 0
    for s in matchList:
      line = "  "
      if index == selectedfileIx:
        line = "> "
      line += s[ 2 : ].split( "." )[ 0 ]
      index += 1
      print( line )

    c = getInput()
    if c == "LEFT" or c == "h":
      return
    if c == "RIGHT" or c == "l":
      fileName = matchList[ selectedfileIx ]
      break
    if c == "DOWN" or c == "j":
      if selectedfileIx < len( matchList ) - 1:
        selectedfileIx += 1
    if c == "UP" or c == "k":
      if selectedfileIx > 0:
        selectedfileIx -= 1

  with open( fileName ) as jFile:
    entryList = []

    dataDict = json.load( jFile )
    for k1,v1 in dataDict.iteritems():
      l = []
      for k2, v2 in v1.iteritems():
        l.append( pV( k2, v2 ) )
      entryList.append( entry( k1, l ) )

def exportJsonDict():
  global statusString, fileName

  dataDict = {} # Copy the entryList into this dict of dicts and save. Will lose element order.
  for e in entryList:
    p = {}
    for param in e.elements:
      p[ param.name ] = param.value
    dataDict[ e.name ] = p

  with open( fileName, 'w' ) as f:
    json.dump( dataDict, f )

  statusString = "Saved."

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

  if ch == "DOWN" or ch == "j":
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
  elif ch == "UP" or ch == "k":
    if cursorParam > 0:
      cursorParam -= 1
    elif cursorParam == 0:
      cursorParam = None
    elif cursorElement > 0:
      cursorElement -= 1
      cursorParam = len( entryList[ cursorElement ].elements ) - 1
  elif ch == "RIGHT":
    if cursorParam is None: # On an element, jump to next element
      cursorElement += 1
    elif cursorPos == 0:
      cursorPos = 1
    else: # Already on the value field, jump to next element
      cursorPos = 0
      cursorParam = None
      cursorElement += 1
    if cursorElement == len( entryList ):
      cursorElement -= 1
  elif ch == "LEFT":
    if cursorPos == 1:
      cursorPos = 0
    elif cursorParam is not None:
      cursorParam = None
    else:
      if cursorElement > 0:
        cursorElement -= 1
  elif ch == 'n':
    fileName = raw_input( 'Enter file name:' )
    if fileName == "":
      fileName = DEFAULT_FILE_NAME
    else:
      if fileName[ -5 : ] != ".json":
        fileName = fileName + ".json"
  elif ch == 'e': # Edit
    if cursorElement is not None:
      newVal = raw_input( 'Enter new value:' )

      if cursorParam == None:

        for e in entryList:
          if e.name == newVal:
            # Since we save as dictionaries can't have duplicate keys.
            statusString = "Duplicate Entry."
            break
        entryList[ cursorElement ].name = newVal
      elif cursorPos == 0:

        for e in entryList[ cursorElement ].elements:
          if e.name == newVal:
            # Since we save as dictionaries can't have duplicate keys.
            statusString = "Duplicate Parameter."
            break

        entryList[ cursorElement ].elements[ cursorParam ].name = newVal
      else:
        entryList[ cursorElement ].elements[ cursorParam ].value = newVal
  elif ch == 'a': # add entry or element
    if cursorElement is None:
      newEntry = entry( "firstEntry", [ pV( "newParam", "newValue" ) ] )
      entryList.append( newEntry )
      cursorElement = 0
      cursorParam = None
    elif cursorParam is None:
      newEntry = entry( "newEntry", [ pV( "newParam", "newValue" ) ] )
      entryList.insert( cursorElement + 1, newEntry )
    else:
      newElem = pV( "newEntry", "newValue" )
      entryList[ cursorElement ].elements.insert( cursorParam + 1, newElem )
  elif ch == 'd': # delete element
    if cursorElement is not None:
      if cursorParam is None or len( entryList[ cursorElement ].elements) == 1:
        del( entryList[ cursorElement ] )
        cursorElement = None if cursorElement == 0 else cursorElement - 1
      else:
        del( entryList[ cursorElement ].elements[ cursorParam ] )
        cursorParam = None if cursorParam == 0 else cursorParam - 1
  elif ch == 'o':
    openJson()
  elif ch == 's':
    exportJsonDict()
  elif ch == '/':
    found = False
    searchFor = raw_input( 'Search:' )
    if searchFor == "" and lastSearch is not None:
      searchFor = lastSearch
    else:
      lastSearch = searchFor
    for ix in range( cursorElement + 1, len( entryList) ):
      if entryList[ ix ].name.lower()[ 0 : len( searchFor ) ] == searchFor.lower():
        cursorElement = ix
        cursorParam = None
        cursorPos = 0
        found = True
        break
    if not found:
      cursorElement = 0
      statusString = "Not Found."
  elif ch == '0':
    cursorElement = 0
    cursorParam = None
    cursorPos = 0

  elif ch == '?':
    print( helpString )
    foo = getInput()
  elif ch == 'q':
    exit()

  displayUI()