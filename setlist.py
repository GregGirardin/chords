#!/usr/bin/python
from __future__ import print_function
import os, sys, glob, copy, pickle
# Cat a list of .txt files into html

class bcolors:
  BLUE      = '\033[94m'
  RED       = '\033[91m'
  GREEN     = '\033[92m'
  WARNING   = '\033[93m'
  BOLD      = '\033[1m'
  UNDERLINE = '\033[4m'
  REVERSE   = '\033[7m'
  ENDC      = '\033[0m'

helpString = bcolors.WARNING +     \
  "\n"                             \
  "[]    - back/forward multiple\n" \
  "mM    - Song/Set move.\n"       \
  "os    - Open/Save.\n"           \
  "rn    - Rename the list/set.\n" \
  "ad    - Add/Delete a set.\n"    \
  "cCp   - Cut/Paste/Clr clip.\n"  \
  "x,X   - Export.\n"              \
  "N     - Add note.\n"            \
  "R     - Remove song.\n"         \
  "~1234 - Jump to library/set.\n"  \
  "h     - Highlight song\n"       \
  "S     - Clone set.\n"           \
  "q     - Quit." + bcolors.ENDC

class Set( object ):
  def __init__( self, name=None ):
    self.name = name
    self.songList = []

class Song( object ):
  # Song is just a name for now but may add attributes later
  def __init__( self, name ):
    self.name = name # file name
    self.count = 0 # Highlight dup songs with count
    self.highLight = HIGHLIGHT_NONE

setLists = []
clipboard = []
songLibrary = []

statusString = None
setListName = "SetList"

# Cursor location
LIBRARY_SET = -1 # if currentSet == LIBRARY_SET, you're in the library

currentSet = LIBRARY_SET
currentSong = 0
librarySong = 0
setListExt = ".set"
annotation = None

SONG_COLUMNS = 4
LIBRARY_ROWS = 10
MAX_SETS = 8

# Input modes
MODE_MOVE_NORMAL  = 0
MODE_MOVE_SONG    = 1
MODE_MOVE_SET     = 2

HIGHLIGHT_NONE = 0
HIGHLIGHT_ON = 1

inputMode = MODE_MOVE_NORMAL

def loadSetList():
  global statusString, setLists, setListName, annotation
  selectedfileIx = 0
  re = "./*" + setListExt

  matchList = glob.glob( re )

  if not matchList:
    statusString = "No setlists."
    return None

  if selectedfileIx >= len( matchList ):
    selectedfileIx = len( matchList ) - 1

  while True:
    selSong = None
    os.system( 'clear' )
    print( "Use arrow keys to select or exit.\n" )
    index = 0
    for s in matchList:
      line = "  "
      if index == selectedfileIx:
        line = "> "
        selSong = s
      line += s[ 2 : ].split( "." )[ 0 ]
      index += 1

      print( line )

    c = getInput()
    if c == "LEFT" or c == "h":
      return None
    if c == "RIGHT" or c == "l":
      with open( selSong, 'rb' ) as f:
        setLists = pickle.load( f )
      setListName = selSong[ 2 : ].split( "." )[ 0 ]
      annotation = setLists[ 0 ].annonation
      return
    if c == "DOWN" or c == "j":
      if selectedfileIx < len( matchList ) - 1:
        selectedfileIx += 1
    if c == "UP" or c == "k":
      if selectedfileIx > 0:
        selectedfileIx -= 1

    # add any local songs not in the list to unassigned

def getSetByName( name ):
  for s in setLists:
    if s.name == name:
      return s
  return None

# Calculate how many instances of a song are in all sets so
# we can indicate which songs are duplicates
def calcSongCounts():
  for l in setLists:
    for s in l.songList:
      s.count = 0 # Note that we compare against self below, so we'll get at least 1.

  for l in setLists:
    for s in l.songList: # For every song
      for l2 in setLists:
        for s2 in l2.songList:
          if s.name == s2.name:
            s.count += 1

def getLocalSongs():
  songList = []
  re = "*.txt"
  matchList = glob.glob( re )
  for s in matchList:
    song = Song( s )
    songList.append( song )

  def getKey( item ):
    return item.name
  songList.sort( key=getKey )
  return songList

def displayUI():
  global songIx, setListName, setLists, statusString, annotation

  os.system( 'clear' )

  print( "Setlist:%s" % ( setListName ) )
  if annotation and annotation != "":
    print( annotation )

  setNumber = 0

  for l in setLists:
    if setNumber == currentSet: # Highlight the current set
      if inputMode == MODE_MOVE_SET:
        print( bcolors.REVERSE, end="" )
      else:
        print( bcolors.UNDERLINE, end="" )

    if l.name:
      print( "\n-", l.name, "-", "/", len( l.songList ) )
    else:
      print( "\nSet:", setNumber + 1, "/", len( l.songList ) )

    if setNumber == currentSet:
      print( bcolors.ENDC, end="" )

    songIx = 0

    for s in l.songList:
      if songIx and songIx % SONG_COLUMNS == 0:
        print()

      cursor = True if setNumber == currentSet and songIx == currentSong else False
      if cursor:
        print( bcolors.REVERSE if inputMode == MODE_MOVE_SONG else bcolors.BOLD, end="" )
      if s.highLight == HIGHLIGHT_ON:
        print( bcolors.RED, end="" )
      elif s.count > 1:
        print( bcolors.BLUE, end="" )

      print( "%-24s" % ( s.name[ : -4 ] ), end = "" )
      if cursor or s.highLight == HIGHLIGHT_ON or s.count > 1:
        print( bcolors.ENDC, end="" )
      songIx += 1
    print()
    setNumber += 1

  # Display library
  print( "\n-- Library --" )

  song_row = librarySong / SONG_COLUMNS
  first_row = song_row - LIBRARY_ROWS / 2
  last_row = song_row + LIBRARY_ROWS / 2
  if( first_row < 0 ):
    last_row -= first_row
    first_row = 0
  if( last_row >= len( songLibrary ) / SONG_COLUMNS ):
    diff = last_row - len( songLibrary ) / SONG_COLUMNS
    last_row -= diff
    first_row -= diff
    if( first_row < 0 ):
      first_row = 0

  for songIx in range( first_row * SONG_COLUMNS, ( last_row + 1 ) * SONG_COLUMNS ):
    if( songIx >= len( songLibrary ) ):
      break
    if songIx != ( first_row * 4) and songIx % SONG_COLUMNS == 0:
      print()
    cursor = True if currentSet == LIBRARY_SET and songIx == librarySong else False
    if cursor:
      print( bcolors.BOLD, end="" )
    print( "%-24s" % ( songLibrary[ songIx ].name[ : -4 ] ), end="" )
    if cursor:
      print( bcolors.ENDC, end="" )
    songIx += 1

  # Clipboard
  if clipboard:
    print( "\n\n-- Clipboard --" )
    songIx = 0
    for s in clipboard:
      print( "%-24s " % ( s.name[ : -4 ] ), end = "" )
      if( songIx + 1 ) % SONG_COLUMNS == 0:
        print()
      songIx += 1

  if statusString:
    print( "\n" + bcolors.WARNING + statusString + bcolors.ENDC )
    #print( bcolors.ENDC, end = "" )

    statusString = None

  print()

def getInput ():
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

  except KeyboardInterrupt:
    ret = 0
  finally:
    termios.tcsetattr( fd, termios.TCSAFLUSH, attrs_save )
    fcntl.fcntl( fd, fcntl.F_SETFL, flags_save )
  return ret

def saveList ():
  global setListName, setListExt, setLists, statusString, annotation

  statusString = "Saved."
  fileName = setListName + setListExt
  setLists[ 0 ].annonation = annotation

  with open( fileName, 'wb' ) as f:
    pickle.dump( setLists, f )

# A decorator for functions that move the cursor to handle song move
def cursorMover( func ):
  def decor( *args, **kwargs ):
    global currentSet, currentSong

    if currentSet != LIBRARY_SET and inputMode == MODE_MOVE_SONG:
      tmpSet = currentSet
      tmpSong = currentSong
      temp = setLists[ tmpSet ].songList[ tmpSong ]

      func( *args, **kwargs )

      if currentSet != LIBRARY_SET:
        if tmpSet == currentSet:
          del setLists[ tmpSet ].songList[ tmpSong ]
          setLists[ currentSet ].songList.insert( currentSong, temp )
        else:
          if currentSong is None: # moved to empty set
            currentSong = 0
          del setLists[ tmpSet ].songList[ tmpSong ]
          setLists[ currentSet ].songList.insert( currentSong, temp )
    else:
      func( *args, **kwargs )

  return decor

@cursorMover
def songFwd( count ):
  global currentSong, librarySong, currentSet, statusString

  if( ( inputMode == MODE_MOVE_SONG ) and
      ( currentSet == len( setLists ) - 1 ) and
      ( currentSong == len( setLists[ currentSet ].songList ) - 1 ) ):
    return # Can't move a song into the library

  if currentSet == LIBRARY_SET:
    librarySong += count
    if librarySong > len( songLibrary ) - 1:
      librarySong = len( songLibrary ) - 1
  else:
    if not currentSong:
      currentSong = 0
    currentSong += count
    if( currentSong >= len( setLists[ currentSet ].songList ) ):
      if currentSet == len( setLists ) - 1:
        currentSet = LIBRARY_SET
        librarySong = 0
      else:
        currentSet += 1
        currentSong = 0

@cursorMover
def songBack( count ):
  global currentSong, librarySong, currentSet

  if currentSet == LIBRARY_SET:
    if librarySong >= count:
      librarySong -= count
    elif librarySong > 0:
      librarySong = 0
    else:
      librarySong = 0
      l = len( setLists )
      if l > 0:
        currentSet = l - 1  # jump to the last one
        l = len( setLists[ currentSet ].songList )
        currentSong = l - 1 if l > 0 else None
  else:
    if not currentSong:
      currentSong = 0
    currentSong -= count
    if currentSong < 0:
      if currentSet == 0: # Already in the first set
        currentSong = 0
      else:
        currentSet -= 1
        l = len( setLists[ currentSet ].songList )
        currentSong = l - 1 if l > 0 else 0

@cursorMover
def moveToSet( set ):
  global statusString, currentSet, currentSong

  if set >= len( setLists ):
    statusString = "Invalid set"
  else:
    currentSet = set
    l = len( setLists[ currentSet ].songList )
    if l == 0:
      currentSong = None
    elif currentSong >= l:
      currentSong = l - 1
    elif currentSong == None:
      currentSong = 0

def deleteSet():
  global currentSet, currentSong

  l = len( setLists )
  if l > 0:
    del setLists[ currentSet ]
    currentSet = LIBRARY_SET
    currentSong = 0

def deleteSong():
  global currentSet, currentSong

  if currentSet != LIBRARY_SET:
    if currentSong is not None:
      del( setLists[ currentSet ].songList[ currentSong ] )
      l = len( setLists[ currentSet ].songList )
      if l == 0:
        currentSong = None
      elif currentSong == l:
        currentSong -= 1
      calcSongCounts()

def copyToClipboard():
  global clipboard, librarySong, statusString

  if currentSet == LIBRARY_SET:
    for s in clipboard:
      if s.name == songLibrary[ librarySong ].name:
        statusString = "Already in clipboard."
        return
    s = copy.deepcopy( songLibrary[ librarySong ] )
    clipboard.append(s)
  else:
    statusString = "Not in library."

def pasteClipboard():
  global currentSet, currentSong, clipboard, statusString

  if currentSet != LIBRARY_SET:
    if currentSong == None:
      currentSong = 0
    else:
      currentSong += 1

    for s in clipboard:
      setLists[ currentSet ].songList.insert( currentSong, s )
      currentSong += 1

    clipboard = []
    calcSongCounts()
  else:
    statusString = "In Library"

tabMode = False

def exportSet():
  global statusString, setLists, annotation

  fname = setListName + ".html"
  f = open( fname, "w" )

  f.write( "<!DOCTYPE html>\n"
           "<html>\n"
           "<head>\n"
           "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
           "<style>\n"
           ".accordion\n"
           "{\n"
           "  background-color: #eee;\n"
           "  color: #444;\n"
           "  cursor: pointer;\n"
           "  padding: 5px;\n"
           "  width: 100%;\n"
           "  border: none;\n"
           "  text-align: left;\n"
           "  outline: none;\n"
           "  font-size: 15px;\n"
           "  transition: 0.4s;\n"
           "}\n"
           "\n"
           ".active, .accordion:hover\n"
           "{\n"
           "  background-color: #ccc;\n"
           "}\n"
           "\n"
           ".panel\n"
           "{\n"
           "  padding: 0 18px;\n"
           "  display: none;\n"
           "  background-color: white;\n"
           "  overflow: hidden;\n"
           "}\n"
           "</style>\n"
           "</head>\n"
           "<body>\n" )

  f.write( "<h1>%s</h1>\n" % ( setListName ) )
  if annotation and annotation != "":
    f.write( annotation )
    f.write( "\n" )

  # Songs
  setNumber = 1
  for l in setLists[ 0 : len( setLists ) ]:
    numSongs = len( l.songList )

    f.write( "<hr><h2>%s</h2>\n" % ( l.name if l.name else setNumber ) )
    songNumber = 1
    for s in l.songList:
      try:
        sName = s.name
        sf = open( sName, "r" )
        fLines = sf.readlines()
        sf.close()
        fileLine = 0

        def toggleTab( f ):
          global tabMode
          if tabMode == True:
            f.write( "</font>\n" )
            tabMode = False
          else:
            f.write( "<font style=\"font-family:courier;\" size=\"2\">\n" )
            tabMode = True

        for line in fLines:
          if fileLine == 0: # Assume first line is song title
            f.write( "<button class=\"accordion\">" )
            if s.highLight == HIGHLIGHT_ON:
              f.write( "%s) <font color=\"red\">%s</font>\n" % (songNumber, line.rstrip()) )
            else:
              f.write( "%s) %s</button>\n" % (songNumber, line.rstrip()) )
            f.write( "</button> <div class=\"panel\">\n" )

          # Shortcuts that can be put in the lyric text,
          # or you can also just put in html in the txt since we paste it directly.
          elif line[ : 2 ] == "t!": # Tab, use fixed font
            toggleTab( f )
          elif line[ : 2 ] == "s!": # Solo
            f.write( "<b><font style=\"font-family:courier;\" size=\"2\">&nbsp Solo</font></b><br>\n" )
          elif line[ : 2 ] == "c!": # Chorus
            f.write( "<b><font style=\"font-family:courier;\" size=\"2\">&nbsp Chorus</font></b><br>\n" )
          elif line[ : 2 ] == "h!": # Harmonica
            f.write( "<b><font style=\"font-family:courier;\" size=\"3\" color=\"red\" >&nbsp Harmonica : " )
            f.write( line [ 2 : ] )
            f.write( "</font></b><br>\n" )
          # ignore 2nd line if empty. It's unnecessary space in the html
          elif fileLine > 1 or line != "\n":
            # add spaces
            while line[ 0 ] == " ":
              line = line[ 1 : ]
              f.write( "&nbsp" )
            f.write( "%s<br>\n" % ( line.rstrip() ) )

          fileLine += 1
      except:
        print( "Exception.." )
      f.write( "</div>\n" )
      songNumber += 1
    setNumber += 1

  f.write( "<script>\n"
           "var acc = document.getElementsByClassName(\"accordion\");\n"
           "var i;\n"
           "\n"
           "for( i = 0;i < acc.length;i++ )\n"
           "{\n"
           "  acc[ i ].addEventListener(\"click\", function()\n"
           "  {\n"
           "    this.classList.toggle(\"active\");\n"
           "    var panel = this.nextElementSibling;\n"
           "    if( panel.style.display === \"block\" )\n"
           "    {\n"
           "      panel.style.display = \"none\";\n"
           "    }\n"
           "    else\n"
           "    {\n"
           "      panel.style.display = \"block\";\n"
           "    }\n"
           "  } );\n"
           "}\n"
           "</script>\n"
           "</body></html>\n" )
  f.close()
  statusString = "Export complete."

def exportSetFlat():
  global statusString, setLists

  fname = setListName + ".html"
  f = open( fname, "w" )

  f.write( "<!DOCTYPE html>\n"
           "<html>\n"
           "<head>\n"
           "<style type=\"text/css\">a {text-decoration: none}</style>\n"
           "</head>\n"
           "<body>\n"
           "<h1>%s</h1>\n" % ( setListName ) )
  # setlist summary
  setNumber = 1
  for l in setLists[0 : len( setLists ) ]:
    songNumber = 0
    f.write( "<h2>%s</h2><font size=\"5\">\n" % ( l.name if l.name else setNumber ) )
    for s in l.songList:
      f.write( "<a id=\"t%dt%d\" href=\"#s%ds%d\">%s</a><br>\n" %
              ( setNumber, songNumber, setNumber, songNumber, s.name[ 0 : -4 ] ) )
      songNumber += 1
    f.write( "</font></br>\n" )
    setNumber += 1
  # songs
  setNumber = 1
  for l in setLists[ 0 : len( setLists ) ]:
    numSongs = len( l.songList )

    f.write( "<hr><h2>%s</h2>\n" % ( l.name if l.name else setNumber ) )
    songNumber = 0
    for s in l.songList:
      try:
        sName = s.name
        sf = open( sName, "r" )
        fLines = sf.readlines()
        sf.close()
        fileLine = 0

        def toggleTab( f ):
          global tabMode
          if tabMode == True:
            f.write( "</font>\n" )
            tabMode = False
          else:
            f.write( "<font style=\"font-family:courier;\" size=\"2\">\n" )
            tabMode = True

        for line in fLines:
          if fileLine == 0: # Assume first line is song title
            f.write( "<h4 id=\"s%ds%d\">" % ( setNumber, songNumber ) )
            # Song name is link back to location in setlist
            f.write( "<a href=\"#t%dt%d\"> %s </a>\n" % ( setNumber, songNumber, line.rstrip() ) )
            f.write ("</h4>\n")

          # Shortcuts that can be put in the lyric text,
          # or you can also just put in html in the txt since we paste it directly.
          elif line[ : 2 ] == "t!": # Tab, use fixed font
            toggleTab( f )
          elif line[ : 2 ] == "s!": # Solo
            f.write( "<b><font style=\"font-family:courier;\" size=\"2\">&nbsp Solo</font></b><br>\n" )
          elif line[ : 2 ] == "c!": # Chorus
            f.write( "<b><font style=\"font-family:courier;\" size=\"2\">&nbsp Chorus</font></b><br>\n" )
          elif line[ : 2 ] == "h!": # Harmonica
            f.write( "<b><font style=\"font-family:courier;\" size=\"3\" color=\"red\" >&nbsp Harmonica : " )
            f.write( line [ 2 : ] )
            f.write( "</font></b><br>\n" )
          # ignore 2nd line if empty. It's unnecessary space in the html
          elif fileLine > 1 or line != "\n":
            # add spaces
            while line[ 0 ] == " ":
              line = line[ 1 : ]
              f.write( "&nbsp" )
            f.write( "%s<br>\n" % ( line.rstrip() ) )

          fileLine += 1
      except:
        print( "Exception.." )
      songNumber += 1
    setNumber += 1
  f.write( "</body></html>\n" )
  f.close()
  statusString = "Flat HTML export complete."

# Start of main loop.
# Populate library
songLibrary = getLocalSongs()
if len( songLibrary ) == 0:
  print("No songs in local directory.")
  exit()

displayUI()
while True:
  ch = getInput()
  if ch == "DOWN":
    if inputMode == MODE_MOVE_SET:
      if currentSet < len( setLists ) - 1:
        s = setLists[ currentSet + 1 ]
        setLists[ currentSet + 1 ] = setLists[ currentSet ]
        setLists[ currentSet ] = s
        currentSet += 1
    else:
      songFwd( SONG_COLUMNS )
  elif ch == "UP":
    if inputMode == MODE_MOVE_SET:
      if currentSet > 0 and currentSet < len( setLists ):
        s = setLists[ currentSet - 1 ]
        setLists[ currentSet - 1 ] = setLists[ currentSet ]
        setLists[ currentSet ] = s
        currentSet -= 1
    else:
      songBack( SONG_COLUMNS )
  elif ch == "RIGHT" and inputMode != MODE_MOVE_SET:
    songFwd( 1 )
  elif ch == "LEFT" and inputMode != MODE_MOVE_SET:
    songBack( 1 )
  elif ch == '[' and inputMode != MODE_MOVE_SET:
    songBack( SONG_COLUMNS * 5 )
  elif ch == ']' and inputMode != MODE_MOVE_SET:
    songFwd( SONG_COLUMNS * 5 )
#  elif ch == 'A':
#    def getKey( item ):
#      return item.name
#    if currentSet != LIBRARY_SET:
#      setLists[ currentSet ].songList.sort( key=getKey )
  elif ch == 's':
    saveList()
  elif ch == 'o':
    loadSetList()
  elif ch == 'r':
    setListName = raw_input( 'Enter set list name:' )
  elif ch == 'm':
    if currentSong == None:
      statusString = "No song selected."
    elif inputMode != MODE_MOVE_SONG:
      inputMode = MODE_MOVE_SONG
      statusString = "Song move mode."
    else:
      inputMode = MODE_MOVE_NORMAL
      statusString = "Cursor move mode."
  elif ch == 'M':
    if inputMode != MODE_MOVE_SET and currentSet != LIBRARY_SET:
      inputMode = MODE_MOVE_SET
      statusString = "Set move mode."
    else:
      inputMode = MODE_MOVE_NORMAL
      statusString = "Cursor move mode."
  elif ch == 'a':
    if currentSet == MAX_SETS:
      statusString = "Max sets exceeded."
    else:
      setLists.insert( currentSet, Set() )
      currentSet += 1
  elif ch == 'd':
    deleteSet()
  elif ch == 'c' and inputMode == MODE_MOVE_NORMAL:
    copyToClipboard()
  elif ch == 'C':
    clipboard = []
  elif ch == 'p':
    pasteClipboard()
  elif ch == 'X':
    exportSetFlat()
  elif ch == 'x':
    exportSet()
  elif ch == 'R':
    deleteSong()
  elif ch == 'S': # Clone a set
    newSet = copy.deepcopy( setLists[ currentSet ] )
    setLists.insert( currentSet, newSet )
    calcSongCounts()
  elif ch == 'n':
    if currentSet != LIBRARY_SET:
      sName = raw_input( 'Enter set name:' )
      setLists[ currentSet ].name = sName
  elif ch == 'q':
    exit()
  elif ch == 'h':
    if currentSet != LIBRARY_SET:
      s = setLists[ currentSet ].songList[ currentSong ]
      if s.highLight == HIGHLIGHT_NONE:
        s.highLight = HIGHLIGHT_ON
      else:
        s.highLight = HIGHLIGHT_NONE
    else:
      statusString = "In Library."
  elif ch == 'N':
    annotation = raw_input( 'Enter annotation:' )
  elif ch >= '1' and ch <= '9':
    moveToSet( int( ch ) - 1 )
  elif ch == '`':
    currentSet = LIBRARY_SET
  elif ch == '?' or ch == 'h':
    print( helpString )
    foo = getInput()

  displayUI()