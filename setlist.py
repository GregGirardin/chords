#!/usr/bin/python
from __future__ import print_function
import os, glob, copy, pickle, json

class bcolors:
  BLUE      = '\033[94m'
  RED       = '\033[91m'
  GREEN     = '\033[92m'
  WARNING   = '\033[93m'
  BOLD      = '\033[1m'
  UNDERLINE = '\033[4m'
  REVERSE   = '\033[7m'
  ENDC      = '\033[0m'

DEFAULT_SETLIST_NAME = "setList"

helpString = bcolors.WARNING +     \
  "\n" \
  "hjkl  - Navigate (or use arrows).\n" \
  "df    - Back/forward multiple.\n" \
  "aA    - Add/delete a set.\n" \
  "os    - Open/save.\n" \
  "mM    - Move song/set.\n" \
  "nN    - Name the set/list.\n" \
  "cCp   - Copy To/Clear/Paste from Library.\n" \
  "D     - Remove song.\n" \
  "x     - Export.\n" \
  "t     - Annotation.\n" \
  "~1234 - Go to library/set.\n" \
  "H     - Toggle highlight.\n" \
  "S     - Clone set.\n" \
  "/     - Search.\n" \
  "q     - Quit." + bcolors.ENDC

class SetClass( object ):
  def __init__( self, name=None ):
    self.name = name
    self.length = None
    self.songList = []

class Song( object ):
  # Song is just a name for now but may add attributes later
  def __init__( self, fileName, songName ):
    self.fileName = fileName
    self.songName = songName

    # To limit mangling the song text with tags, we'll get these attributes from a json file
    self.artist = None
    self.key = None
    self.length = None
    self.tempo = None

    self.count = 0 # Highlight duplicate songs with count
    self.highLight = HIGHLIGHT_NONE

setLists = []
clipboard = []
songLibrary = []
statusString = None
setListName = DEFAULT_SETLIST_NAME

LIBRARY_SET = -1 # if currentSet == LIBRARY_SET then you're in the library

# Cursor location
currentSet = LIBRARY_SET
currentSong = None
librarySong = 0 # Library always has at least 1 song or program will exit.
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

operMode = MODE_MOVE_NORMAL

def loadSetList():
  global statusString, setLists, setListName, annotation, currentSong, currentSet

  selectedfileIx = 0
  re = "./*" + setListExt

  matchList = glob.glob( re )

  if not matchList:
    statusString = "No setlists."
    return None

  currentSong = 0
  currentSet = LIBRARY_SET

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

def getSetByName( name ):
  for s in setLists:
    if s.name == name:
      return s
  return None

# Count instances of all songs to display duplicates
def calcSongCounts():
  for l in setLists:
    for s in l.songList:
      s.count = 0 # Note that we compare against self below, so we'll get at least 1.

  for l in setLists:
    for s in l.songList: # For every song
      for l2 in setLists:
        for s2 in l2.songList:
          if s.fileName == s2.fileName:
            s.count += 1

def getLocalSongs():
  songList = []
  re = "*.txt"
  matchList = glob.glob( re )

  for fName in matchList:
    # Parse song txts for Name.
    sf = open( fName, "r" )
    fLines = sf.readlines()
    sf.close()

    if len( fLines ) > 0:
      songName = fLines[ 0 ]
      songList.append( Song( fName, songName ) )

  def getKey( item ):
    return item.fileName

  songList.sort( key=getKey )
  return songList

def displayUI():
  global statusString, setLists

  os.system( 'clear' )

  song = None
  if currentSet == LIBRARY_SET:
    song = songLibrary[ librarySong ]
  elif currentSong is not None:
    song = setLists[ currentSet ].songList[ currentSong ]

  print( "File:" + setListName )
  if song:
    print( "Song:\"" + song.songName.strip() + "\"", end="" )
    if song.artist:
      print( " - " + song.artist.strip(), end="" )
  print()
  if annotation:
    print( annotation )

  setNumber = 0
  libSongName = None

  if currentSet == LIBRARY_SET:
    libSongName = songLibrary[ librarySong ].fileName

  for l in setLists:
    if setNumber == currentSet: # Highlight the current set
      if operMode == MODE_MOVE_SET:
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
        print( bcolors.REVERSE if operMode == MODE_MOVE_SONG else bcolors.BOLD, end="" )
      if s.fileName == libSongName:
        print( bcolors.REVERSE, end="" )
      elif s.highLight == HIGHLIGHT_ON:
        print( bcolors.RED, end="" )
      elif s.count > 1:
        print( bcolors.BLUE, end="" )

      print( "%-24s" % ( s.fileName[ : -4 ] ), end = "" )
      print( bcolors.ENDC, end="" )
      songIx += 1

    print()
    setNumber += 1

  # Display library
  print( "\n---- Library ----" )
  song_row = int( librarySong / SONG_COLUMNS )
  first_row = int( song_row - LIBRARY_ROWS / 2 )
  last_row = int( song_row + LIBRARY_ROWS / 2 )
  if first_row < 0:
    last_row -= first_row
    first_row = 0
  if last_row >= len( songLibrary ) / SONG_COLUMNS:
    diff = int( last_row - len( songLibrary ) / SONG_COLUMNS )
    last_row -= diff
    first_row -= diff
    if( first_row < 0 ):
      first_row = 0

  for songIx in range( first_row * SONG_COLUMNS, ( last_row + 1 ) * SONG_COLUMNS ):
    if songIx >= len( songLibrary ):
      break
    if songIx != ( first_row * 4 ) and songIx % SONG_COLUMNS == 0:
      print()
    cursor = True if currentSet == LIBRARY_SET and songIx == librarySong else False
    if cursor:
      print( bcolors.BOLD, end="" )
    print( "%-24s" % ( songLibrary[ songIx ].fileName[ : -4 ] ), end="" )
    if cursor:
      print( bcolors.ENDC, end="" )
    songIx += 1

  # Clipboard
  if clipboard:
    print( "\n\n-- Clipboard --" )
    songIx = 0
    for s in clipboard:
      print( "%-24s " % ( s.fileName[ : -4 ] ), end = "" )
      if( songIx + 1 ) % SONG_COLUMNS == 0:
        print()
      songIx += 1

  if statusString:
    print( "\n" + bcolors.WARNING + statusString + bcolors.ENDC )
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

    if currentSet != LIBRARY_SET and operMode == MODE_MOVE_SONG and currentSong is not None:
      tmpSet = currentSet
      tmpSong = currentSong
      temp = setLists[ tmpSet ].songList[ tmpSong ]

      func( *args, **kwargs )

      if currentSet != LIBRARY_SET:
        del setLists[ tmpSet ].songList[ tmpSong ]
        if tmpSet == currentSet:
          setLists[ currentSet ].songList.insert( currentSong, temp )
        else:
          if currentSong is None:
            currentSong = 0
          if( currentSong == len( setLists[ currentSet ].songList ) - 1 ):
            currentSong += 1
          setLists[ currentSet ].songList.insert( currentSong, temp )
    else:
      func( *args, **kwargs )

  return decor

@cursorMover
def songFwd( count ):
  global currentSong, librarySong, currentSet, statusString

  if( ( operMode == MODE_MOVE_SONG ) and
      ( currentSet == len( setLists ) - 1 ) and
      ( currentSong is not None ) and
      ( currentSong == len( setLists[ currentSet ].songList ) - 1 ) ):
    return # Can't move a song into the library

  if currentSet == LIBRARY_SET:
    librarySong += count
    if librarySong > len( songLibrary ) - 1:
      librarySong = len( songLibrary ) - 1
  else:
    if currentSong is not None:
      currentSong += count
    if( currentSong is None ) or ( currentSong >= len( setLists[ currentSet ].songList ) ):
      if currentSet == len( setLists ) - 1:
        currentSet = LIBRARY_SET
        librarySong = 0
      else:
        currentSet += 1
        if len( setLists[ currentSet ].songList ):
          currentSong = 0
        else:
          currentSong = None

@cursorMover
def songBack( count ):
  global currentSong, librarySong, currentSet

  if currentSet == LIBRARY_SET:
    if librarySong >= count:
      librarySong -= count
    elif librarySong > 0:
      librarySong = 0
    else:
      l = len( setLists )
      if l > 0:
        currentSet = l - 1 # jump to the last one
        l = len( setLists[ currentSet ].songList )
        currentSong = l - 1 if l > 0 else None
  else:
    if currentSong is not None:
      currentSong -= count
    if currentSong is None or currentSong < 0: # Need to go back a set.
      if currentSet == 0: # Already in the first set
        if( len( setLists[ currentSet ].songList ) ):
          currentSong = 0
        else:
          currentSong = None
      else:
        currentSet -= 1
        l = len( setLists[ currentSet ].songList )
        currentSong = l - 1 if l > 0 else None

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
    else:
      currentSong = l - 1

def deleteSet():
  global currentSet, currentSong

  l = len( setLists )
  if l > 0:
    del setLists[ currentSet ]
    currentSet = LIBRARY_SET
    currentSong = None

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

def copyToClipboard():
  global clipboard, librarySong, statusString

  if currentSet == LIBRARY_SET:
    for s in clipboard:
      if s.fileName == songLibrary[ librarySong ].fileName:
        statusString = "Song is already in the clipboard."
        return
    s = copy.deepcopy( songLibrary[ librarySong ] )
    clipboard.append(s)
  else:
    statusString = "Not in Library."

def pasteClipboard():
  global currentSet, currentSong, clipboard, statusString

  if len( clipboard ) == 0:
    statusString = "Clipboard empty."
    return

  if currentSet != LIBRARY_SET:
    if currentSong == None:
      currentSong = 0
    else:
      currentSong += 1

    for s in clipboard:
      setLists[ currentSet ].songList.insert( currentSong, s )
      currentSong += 1

    if currentSong == len( setLists[ currentSet ].songList ):
      currentSong -= 1

    clipboard = []
  else:
    statusString = "Can't paste to Library."

def exportSet():
  global statusString, setLists, annotation
  tabMode = False

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
  if annotation:
    f.write( annotation )
    f.write( "\n" )

  # Songs
  setNumber = 1
  for l in setLists[ 0 : len( setLists ) ]:
    f.write( "<hr><h2>%s</h2>\n" % ( l.name if l.name else setNumber ) )
    songNumber = 1
    for s in l.songList:
      try:
        sName = s.fileName
        sf = open( sName, "r" )
        fLines = sf.readlines()
        sf.close()
        fileLine = 0

        for line in fLines:
          pf = line[ : 2 ] # prefix
          if fileLine == 0: # Assume first line is song title
            f.write( "<button class=\"accordion\">" )
            if s.highLight == HIGHLIGHT_ON:
              f.write( "%s) <font color=\"red\">%s</font>\n" % ( songNumber, line.rstrip() ) )
            else:
              f.write( "%s) %s</button>\n" % ( songNumber, line.rstrip() ) )
            f.write( "</button> <div class=\"panel\">\n" )

          # Shortcuts that can be embedded in the lyric text
          # You can also just put in html in the txt since it's pasted directly.
          elif pf == "t!": # Tab, use fixed font
            if tabMode == True:
              f.write( "</font>\n" )
              tabMode = False
            else:
              f.write( "<font style=\"font-family:courier;\" size=\"2\">\n" )
              tabMode = True
          elif( pf == "T!" or pf == "k!" or pf == "l!" or pf == "a!" ):
            pass # These will be added to the top of the song.
          elif pf == "s!": # Solo
            f.write( "<b><font style=\"font-family:courier;\" size=\"2\">&nbsp Solo</font></b><br>\n" )
          elif pf == "c!": # Chorus
            f.write( "<b><font style=\"font-family:courier;\" size=\"2\">&nbsp Chorus</font></b><br>\n" )
          elif pf == "h!": # Harmonica
            f.write( "<b><font style=\"font-family:courier;\" size=\"3\" color=\"red\" >&nbsp Harmonica : " )
            f.write( line[ 2 : ] )
            f.write( "</font></b><br>\n" )
          # Ignore 2nd line if empty. It's unnecessary space in the html
          elif fileLine > 1 or line != "\n": # add spaces
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
           "for( i = 0;i < acc.length;i++ ) {\n"
           "  acc[ i ].addEventListener(\"click\", function() {\n"
           "    this.classList.toggle(\"active\");\n"
           "    var panel = this.nextElementSibling;\n"
           "    if( panel.style.display === \"block\" ) {\n"
           "      panel.style.display = \"none\";\n"
           "    }\n"
           "    else {\n"
           "      panel.style.display = \"block\";\n"
           "    }\n"
           "  } );\n"
           "}\n"
           "</script>\n"
           "</body></html>\n" )
  f.close()
  statusString = "Export complete."

# Start of main loop.
songLibrary = getLocalSongs()
if len( songLibrary ) == 0:
  print( "No songs in local directory." )
  exit()

displayUI()
while True:
  ch = getInput()
  if( ch == "DOWN" or ch == "j" ):
    if operMode == MODE_MOVE_SET:
      if currentSet < len( setLists ) - 1:
        s = setLists[ currentSet + 1 ]
        setLists[ currentSet + 1 ] = setLists[ currentSet ]
        setLists[ currentSet ] = s
        currentSet += 1
    else:
      songFwd( SONG_COLUMNS )
  elif( ch == "UP" or ch == "k" ):
    if operMode == MODE_MOVE_SET:
      if currentSet > 0 and currentSet < len( setLists ):
        s = setLists[ currentSet - 1 ]
        setLists[ currentSet - 1 ] = setLists[ currentSet ]
        setLists[ currentSet ] = s
        currentSet -= 1
    else:
      songBack( SONG_COLUMNS )
  elif( ch == "RIGHT" or ch == "l" ) and operMode != MODE_MOVE_SET:
    songFwd( 1 )
  elif( ch == "LEFT" or ch == "h" ) and operMode != MODE_MOVE_SET:
    songBack( 1 )
  elif ch == 'd' and operMode != MODE_MOVE_SET:
    songBack( SONG_COLUMNS * 5 )
  elif ch == 'f' and operMode != MODE_MOVE_SET:
    songFwd( SONG_COLUMNS * 5 )
  elif ch == 's':
    saveList()
  elif ch == 'o':
    loadSetList()
  elif ch == 'm':
    if currentSong == None:
      statusString = "No song selected."
    elif operMode != MODE_MOVE_SONG:
      operMode = MODE_MOVE_SONG
      statusString = "Song move mode."
    else:
      operMode = MODE_MOVE_NORMAL
      statusString = "Cursor move mode."
  elif ch == 'M':
    if operMode != MODE_MOVE_SET and currentSet != LIBRARY_SET:
      operMode = MODE_MOVE_SET
      statusString = "Set move mode."
    else:
      operMode = MODE_MOVE_NORMAL
      statusString = "Cursor move mode."
  elif ch == 'a':
    if currentSet == MAX_SETS:
      statusString = "Max sets exceeded."
    else:
      setLists.insert( currentSet + 1, SetClass() )
  elif ch == 'A':
    deleteSet()
  elif ch == 'c' and operMode == MODE_MOVE_NORMAL:
    copyToClipboard()
  elif ch == 'C':
    clipboard = []
  elif ch == 'p':
    pasteClipboard()
  elif ch == 'x':
    exportSet()
  elif ch == 'D':
    deleteSong()
  elif ch == 'S': # Clone a set
    newSet = copy.deepcopy( setLists[ currentSet ] )
    setLists.insert( currentSet, newSet )
  elif ch == 'n':
    if currentSet != LIBRARY_SET:
      sName = raw_input( 'Enter set name:' )
      setLists[ currentSet ].name = sName if sName else None
  elif ch == 'N':
    setListName = raw_input( 'Enter set list name:' )
    if setListName == "":
      setListName = DEFAULT_SETLIST_NAME
  elif ch == 'H':
    if currentSet != LIBRARY_SET:
      s = setLists[ currentSet ].songList[ currentSong ]
      if s.highLight == HIGHLIGHT_NONE:
        s.highLight = HIGHLIGHT_ON
      else:
        s.highLight = HIGHLIGHT_NONE
    else:
      statusString = "In Library."
  elif ch == 't':
    annotation = raw_input( 'Enter annotation:' )
    if annotation == "":
      annotation = None
  elif ch == '`':
    currentSet = LIBRARY_SET
  elif ch >= '1' and ch <= '9':
    moveToSet( int( ch ) - 1 )
  elif ch == '/':
    searchFor = raw_input( 'Search:' )
    newLibIndex = 0
    for s in songLibrary:
      if s.fileName.lower()[ 0 : len( searchFor ) ] == searchFor.lower():
        librarySong = newLibIndex
        currentSet = LIBRARY_SET
        break
      newLibIndex += 1
  elif ch == '?':
    print( helpString )
    foo = getInput()
  elif ch == 'q':
    exit()

  calcSongCounts()

  displayUI()