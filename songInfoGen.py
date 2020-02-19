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

cursorSong = 0
cursorParam = 0
lastSearch = None
songParams = ( "artist", "key", "tempo", "year" )

class songEntry( object ):
  def __init__( self, name, elements ):
    self.name = name # tbd, change to filename
    if elements:
      self.elements = elements # dict of song songParams
    else:
      e = {}
      for p in songParams:
        e[ p ] = "---"
      self.elements = e

helpString = bcolors.WARNING + \
  "\n" \
  "space - Edit value\n" \
  "s     - save.\n" \
  "e     - exit, return to set list.\n" \
  "/     - Search for song.\n" \
  "q     - Quit." + bcolors.ENDC

songInfoList = [] # A list of songEntry

statusString = None
fileName = "lyricMetadata.json"

def displaySigUI():
  global statusString

  os.system( 'clear' )
  print( "Additional Song data." )
  print( "-------------------------------------------------------------" )
  print( "File                 Artist                Key   Tempo Year" )
  print( "-------------------- --------------------- ----- ----- ------" )

  first = cursorSong - 10
  if first < 0:
    first = 0

  for ix in range( first, first + 21 ):
    if ix == len( songInfoList ):
      break

    for paramIndex in range( 0, len( songInfoList[ ix ].elements ) ):
      di = {} # DisplayInfo
      for param in songParams:
        if param in songInfoList[ ix ].elements:
          tmpStr = songInfoList[ ix ].elements[ param ]
        else:
          tmpStr = "?"

        if ix == cursorSong and songParams[ cursorParam ] == param:
          # tmpStr = bcolors.BOLD + tmpStr + bcolors.ENDC # highlight
          tmpStr = '>' + tmpStr + '<' # highlight
        else:
          tmpStr = ' ' + tmpStr + ' '

        di[ param ] = tmpStr

    print( "%-20s %-21s %-5s %-5s %-6s" % ( songInfoList[ ix ].name.split( "." )[ 0 ][ 0 : 19 ],
            di[ "artist" ], di[ "key" ], di[ "tempo" ], di[ "year" ] ) )

  print( "-------------------------------------------------------------" )
  print( str( len( songInfoList ) ) + " files." )

  if statusString:
    print( "\n" + bcolors.WARNING + statusString + bcolors.ENDC )
    statusString = None

def getKey( item ):
  return item.name

def openJson():
  global fileName, songInfoList

  if os.path.isfile( fileName ):
    with open( fileName ) as jFile:
      songInfoList = []

      dataDict = json.load( jFile )
      for k, v in dataDict.iteritems():
        songInfoList.append( songEntry( k, v ) )

      songInfoList.sort( key=getKey )

def exportJsonDict():
  global statusString, fileName

  dataDict = {} # Copy the songInfoList into this dict of dicts and save. Will lose element order.
  for e in songInfoList:
    dataDict[ e.name ] = e.elements

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

def rangeCheck( param, newVal ):

  if param == "tempo":
    try:
      t = int( newVal )
      if t < 10:
        t = 10
      elif t > 300:
        t = 300
      newVal = str( t )
    except:
      newVal = "---"
  elif param == "year":
    try:
      t = int( newVal )
      if t < 1500:
        t = 1500
      elif t > 2100:
        t = 2100
      newVal = str( t )
    except:
      newVal = "---"

  return newVal

firstTime = True

def sigMain():
  global cursorSong, cursorParam, firstTime

  if firstTime:
    firstTime = False

    openJson() # Open existing data file if present

    # Add any songs that aren't in songInfoList
    songList = glob.glob( "*.txt" )
    songList.sort()

    added = 0
    for s in songList:
      found = False
      for e in songInfoList:
        if e.name == s:
          found = True
          break # present

      if not found:
        songInfoList.append( songEntry( s, None ) )
        added += 1

    ''' tbd. Prune songs that aren't present.
    for e in songInfoList:
      for s in songList:
        if e.name == s:
          continue
        # If we got here then prune e.
        del e
    '''
  # Start of main loop.
  displaySigUI()
  while True:
    ch = getInput()

    if ch == "DOWN" or ch == "j":
      if cursorSong == None: # Go to first element
        cursorSong = 0
        cursorParam = None
      else:
        if cursorSong < len( songInfoList ) - 1: # Go back to the end.
          cursorSong += 1
    elif ch == "UP" or ch == "k":
      if cursorSong > 0:
        cursorSong -= 1
    elif ch == "RIGHT":
      if cursorParam is None: # On an element, jump to next element
        cursorParam = 1
      elif cursorParam < len( songParams ) - 1: # Already on the value field, jump to next element
        cursorParam += 1
    elif ch == "LEFT":
      if cursorParam > 0:
        cursorParam -= 1
    elif ch == ' ': # Edit
      if cursorSong is not None:
        newVal = raw_input( 'Enter new value:' )
        newVal = rangeCheck( songParams [ cursorParam ], newVal )
        if newVal == "":
          newVal = "---"
        songInfoList[ cursorSong ].elements[ songParams [ cursorParam ] ] = newVal
    elif ch == 's':
      exportJsonDict()
    elif ch == '/':
      found = False
      searchFor = raw_input( 'Search:' )
      if searchFor == "" and lastSearch is not None:
        searchFor = lastSearch
      else:
        lastSearch = searchFor
      for ix in range( cursorSong + 1, len( songInfoList) ):
        if songInfoList[ ix ].name.lower()[ 0 : len( searchFor ) ] == searchFor.lower():
          cursorSong = ix
          found = True
          break
      if not found:
        for ix in range( 0, cursorSong ):
          if songInfoList[ ix ].name.lower()[ 0 : len( searchFor ) ] == searchFor.lower():
            cursorSong = ix
            found = True
            break
        if not found:
          statusString = "Not Found."
    elif ch == '0':
      cursorSong = 0

    elif ch == '?':
      print( helpString )
      foo = getInput()
    elif ch == 'e':
      return()
    elif ch == 'q':
      exit()

    displaySigUI()