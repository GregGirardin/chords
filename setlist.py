#!/usr/bin/python
from __future__ import print_function
import os, glob, copy, pickle, json, sys

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

# These are additional song/lyric data that we store separately so
# The user doesn't have to put them in the lyric file.
songParams = ( "Artist", "Key", "Tempo", "Year", "Genre", "Length" )
SP_ARTIST = 0
SP_KEY = 1
SP_TEMPO = 2
SP_YEAR = 3
SP_GENRE = 4
SP_LENGTH = 5

helpString = bcolors.WARNING + \
  "Commands:\n" \
  "hjkl  - Navigate.\n" \
  "df    - Back/forward multiple.\n" \
  "aA    - Add/delete a set.\n" \
  "os    - Open/save.\n" \
  "mM    - Move song/set.\n" \
  "nN    - Name the set/list.\n" \
  "cCp   - Copy to/Clear/Paste Clipboard.\n" \
  "D     - Remove song from setlist.\n" \
  "x     - Export setlist.\n" \
  "t     - Annotation.\n" \
  "~1234 - Go to library/set.\n" \
  "H     - Toggle highlight.\n" \
  "S     - Clone set.\n" \
  "e     - Edit song data.\n" \
  "y     - Medley.\n" \
  "[]    - Show song by File/Artist/Key/etc.\n" \
  "/     - Search.\n" \
  "q     - Quit." + bcolors.ENDC

sieHelpString = bcolors.WARNING + \
  "Commands:\n" \
  "space - Edit value\n" \
  "df    - Back/forward multiple.\n" \
  "s     - Save song data.\n" \
  "e     - Exit to set list editor.\n" \
  "/     - Search for song.\n" \
  "n     - Next occurrence of search.\n" \
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

    elements = {}
    for p in songParams:
      elements[ p ] = None
    self.elements = elements # dict keyed by songParams
    self.count = 0 # Highlight duplicate songs with count
    self.highLight = HIGHLIGHT_NONE
    self.medley = False

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
annotation = None
showBy = None

SONG_COLUMNS = 4
LIBRARY_ROWS = 8
MAX_SETS = 8

# Song Info Editor
cursorSong = 0
cursorParam = 0
searchFor = ""
sieFileName = "lyricMetadata.json"

# Input modes
MODE_MOVE_NORMAL  = 0
MODE_MOVE_SONG    = 1
MODE_MOVE_SET     = 2

HIGHLIGHT_NONE = 0
HIGHLIGHT_ON = 1

operMode = MODE_MOVE_NORMAL

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

# Update song info from library. What's copied in the setlist may have been updated.
# Note that a Song in the setlist does have some parameters which can differ
# from what's in the library.
def updateSongDataFromLibrary():
  for set in setLists:
    for song in set.songList:
      for libSong in songLibrary:
        if libSong.fileName == song.fileName:
          song.elements = libSong.elements
          # fwd compatibility. Create new elements if not in the .set
          if not hasattr( song, 'medley' ):
            song.medley = False

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

def loadSetList():
  global statusString, setLists, setListName, annotation, currentSong, currentSet

  selectedfileIx = 0
  re = "./*.set"

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
      updateSongDataFromLibrary()
      return
    if c == "DOWN" or c == "j":
      if selectedfileIx < len( matchList ) - 1:
        selectedfileIx += 1
    if c == "UP" or c == "k":
      if selectedfileIx > 0:
        selectedfileIx -= 1

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
  global statusString, setLists, showBy

  os.system( 'clear' )

  song = None
  if currentSet == LIBRARY_SET:
    song = songLibrary[ librarySong ]
  elif currentSong is not None:
    song = setLists[ currentSet ].songList[ currentSong ]

  print( "File:" + setListName, end="" )
  if operMode == MODE_MOVE_SONG:
    print( bcolors.WARNING + " Song Move Mode" + bcolors.ENDC, end="" )
  elif operMode == MODE_MOVE_SET:
    print( bcolors.WARNING + " Set Move Mode" + bcolors.ENDC, end="" )

  print()

  if song:
    print( "Song:\"" + song.songName.strip() + "\"", end="" )
    if "Artist" in song.elements:
      if song.elements[ songParams [ SP_ARTIST ] ]:
        print( " by " + song.elements[ songParams [ SP_ARTIST ] ], end="" )
      if song.elements[ songParams [ SP_KEY ] ]:
        print( " key " + song.elements[ songParams [ SP_KEY ] ], end="" )
      if song.elements[ songParams [ SP_TEMPO ] ]:
        print( " " + song.elements[ songParams [ SP_TEMPO ] ] + "bpm", end="" )
      if song.elements[ songParams [ SP_YEAR ] ]:
        print( " " + song.elements[ songParams [ SP_YEAR ] ], end="" )
      if song.elements[ songParams [ SP_GENRE ] ]:
        print( " " + song.elements[ songParams [ SP_GENRE ] ], end="" )
      if song.elements[ songParams[ SP_LENGTH ] ]:
        print( " length " + song.elements[ songParams[ SP_LENGTH ] ], end="" )
  print()
  if showBy is not None:
    print( "Show by " + songParams[ showBy ] )
  else:
    print()

  if annotation:
    print( annotation )

  setNumber = 0
  libSongName = None

  if currentSet == LIBRARY_SET:
    libSongName = songLibrary[ librarySong ].fileName

  for l in setLists:
    if l.name:
      print( "\n-", l.name, "-", "/", len( l.songList ) )
    else:
      print( "\nSet:", setNumber + 1, "/", len( l.songList ) )

    songIx = 0
    for s in l.songList:
      if songIx and songIx % SONG_COLUMNS == 0:
        print()

      cursor = True if setNumber == currentSet and songIx == currentSong else False
      if cursor or s.fileName == libSongName:
        print( bcolors.REVERSE, end="" )
      elif s.highLight == HIGHLIGHT_ON and showBy is None:
        print( bcolors.RED, end="" )
      elif s.count > 1:
        print( bcolors.BLUE, end="" )

      if showBy is None:
        songString = s.fileName[ : -4 ]
        if s.medley:
          songString += " " + u"\u2192" # right arrow
        songString += bcolors.ENDC
        print( "%-28s" % ( songString ), end="" )
      else:
        v = s.elements[ songParams [ showBy ] ]
        if v is None:
          v = "---"
        elif v == song.elements[ songParams [ showBy ] ]:
          print( bcolors.RED, end="" )
        print( "%-28s" % ( v ) + bcolors.ENDC, end="" )

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
    if first_row < 0:
      first_row = 0

  for songIx in range( first_row * SONG_COLUMNS, ( last_row + 1 ) * SONG_COLUMNS ):
    if songIx >= len( songLibrary ):
      break
    if songIx != ( first_row * 4 ) and songIx % SONG_COLUMNS == 0:
      print()
    cursor = True if currentSet == LIBRARY_SET and songIx == librarySong else False
    if cursor:
      print( bcolors.REVERSE, end="" )

    if showBy is None:
      print( "%-24s" % ( songLibrary[ songIx ].fileName[ : -4 ] ), end="" )
    else:
      v = songLibrary[ songIx ].elements[ songParams[ showBy ] ]
      if v is None:
        v = "---"
      elif v == song.elements[ songParams[ showBy ] ]:
        print( bcolors.RED, end="" )
      print( "%-24s" % ( v ), end = "" )
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

def saveList ():
  global setListName, setLists, statusString, annotation

  fileName = setListName + ".set"
  setLists[ 0 ].annonation = annotation

  with open( fileName, 'wb' ) as f:
    pickle.dump( setLists, f )
    statusString = "Saved."

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
        currentSong = 0 if len( setLists[ currentSet ].songList ) else None

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
        currentSong = 0 if( len( setLists[ currentSet ].songList ) ) else None
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
    elif currentSong >= l:
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
      currentSong = None if l == 0 else currentSong - 1

def copyToClipboard():
  global clipboard, librarySong, statusString

  if currentSet == LIBRARY_SET:
    for s in clipboard:
      if s.fileName == songLibrary[ librarySong ].fileName:
        statusString = "Song is already in the clipboard."
        return
    s = copy.deepcopy( songLibrary[ librarySong ] )
    clipboard.append( s )
  else:
    statusString = "Not in Library."

def pasteClipboard():
  global currentSet, currentSong, clipboard, statusString

  if len( clipboard ) == 0:
    statusString = "Clipboard empty."
    return

  if currentSet != LIBRARY_SET:
    currentSong = 0 if currentSong == None else currentSong + 1

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

  fname = setListName + ".html"
  f = open( fname, "w" )
  f.write( """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
""" )
  f.write( "<title>%s</title>" % ( setListName ) )
  f.write( """
<style>
.accordion
{
  border: 1px solid white;
  background-color: #def;
  color: #444;
  cursor: pointer;
  padding: 6px;
  text-align: left;
  outline: none;
  font-size: 16px;
  transition: 0.4s;
  min-width: 100%;
}

.accordion:hover
{
  background-color: #fcc;
}

.panel
{
  padding: 0 18px;
  display: none;
  overflow: hidden;
  font-size: 20px;
  background-color: #fee;
  text-align: left;
}

.medleyStart
{
  position:relative;
  overflow:hidden;
  background: #ddf;
  clip-path: polygon( 0% 0%, 90% 0, 100% 50%, 90% 100%, 0% 100% );
}

.medleyCont
{
  position:relative;
  overflow:hidden;
  background: #ddf;
  clip-path: polygon( 0 20%, 100% 20%, 100% 80%, 0% 80% );
}

.medleyEnd
{
  position:relative;
  overflow:hidden;
  background: #ddf;
  clip-path: polygon( 0% 0%, 100% 0%, 90% 50%, 100% 100%, 0% 100% );
}

.highlight
{
  color: #d33;
}

.selectNext
{
  background-color: #fee;
  color: #444;
  cursor: pointer;
  padding: 10px;
  width: 90%;
  text-align: left;
  outline: none;
  font-size: 15px;
  transition: 0.4s;
}

.topButtons
{
  background-color: #fdd;
  padding: 10px;
  font-size: 16px;
}

</style>
</head>

<body align="center">
<button class="topButtons" id="fontButton+" onclick="fontPlus();">Font +</button>
<button class="topButtons" id="fontButton-" onclick="fontMinus();">Font -</button>
<button id="fontSizeButton">Size</button>
<button class="topButtons" id="verticalButton+" onclick="displayPlus();">Expand</button>
<button class="topButtons" id="verticalButton-" onclick="displayMinus();">Shrink</button>
 """ )

  if annotation:
    f.write( annotation + "\n" )

  ffState = False # Fixed Font state

  # Songs
  setNumber = 1
  for l in setLists[ 0 : len( setLists ) ]:
    f.write( "<hr><div class='setname'>%s</div>\n" % ( l.name if l.name else setNumber ) )
    songNumber = 1
    inMedley = False
    for s in l.songList:
      try:
        sName = s.fileName
        if not os.path.exists( sName ):
          print( sName, "does not exist." )
          exit()
        
        sf = open( sName, "r" )
        fLines = sf.readlines()
        sf.close()
        fileLine = 0
        ffManual = False

        for line in fLines:
          if line[ 0 : 2 ] == "f!": # Explicity toggle fixed font. Stay fixed until end of song.
            ffManual = True if ffManual == False else False
            continue # Don't output that line.

          # if tablature or chords. "E|", "A|" etc or "I: A E D", "C: A D". Use a fixed font.
          ffAuto = True if line[ 1 : 2 ] in ( "|", ":" ) else False

          if ffAuto or ffManual: # We want to use a fixed font?
            if not ffState:
              f.write( "<font style='font-family:courier;'>\n" )
              ffState = True
          elif ffState: # Don't want fixed font. Fixed is harder to read for lyrics.
            f.write( "</font>\n" )
            ffState = False

          if fileLine == 0: # Assume first line is song title
            classString = "accordion"
            if s.highLight == HIGHLIGHT_ON:
              classString += " highlight"

            if s.medley:
              if not inMedley:
                classString += " medleyStart"
                inMedley = True
              else:
                classString += " medleyCont"
            else:
              if( inMedley ):
                classString += " medleyEnd"
              inMedley = False

            f.write( "<button class='%s'>" % ( classString ) )
            songName = line.rstrip()

            f.write( "%s. %s</button>\n" % ( songNumber, songName ) )

            f.write( "<div class='panel'>\n" )

            # Add song meta data if present (artist / key / tempo / year)
            # You can also just put in html in the txt since it's pasted directly.
            # songInfo = ""
            # for param in( SP_ARTIST, SP_KEY, SP_TEMPO, SP_YEAR, SP_GENRE, SP_LENGTH ):
            #   if s.elements[ songParams[ param ] ]:
            #     songInfo += s.elements[ songParams[ param ] ] + " "
            #     if param == SP_TEMPO:
            #       songInfo += "bpm"
            # if len( songInfo ):
            #   f.write( "<div class=\"songInfo\">" + songInfo + "</div><br>\n" )
          # Bold lines starting with !
          elif line[ 0 : 1 ] == "!":
            f.write( "<b>- %s -</b><br>\n" % ( line[ 1 : ].rstrip() ) )
          # Ignore 2nd line if empty. It's unnecessary space in the html
          elif fileLine > 1 or line != "\n": # add spaces
            nLine = ""
            numSpaces = 0
            for c in line:
              if c == " ":
                numSpaces += 1
              else:
                if numSpaces == 1:
                  nLine += " "
                elif numSpaces > 1:
                  for _ in range( 0, numSpaces ):
                    nLine += "&nbsp" # replace spaces in the line so the browser doesn't skip it.
                numSpaces = 0
                nLine += c
            f.write( "%s<br>\n" % ( nLine.rstrip() ) )

          fileLine += 1
      except:
        print( "Exception:", sys.exc_info() )
        exit()
      if s.medley:
        f.write( "<font size='4'> &#8595;</font>" ) # Big down arrow
      f.write( "</div>\n\n" )
      songNumber += 1
    setNumber += 1

  f.write( """
<script>

var fontSize = 16;

////////////////////////// ////////////////////////// //////////////////////////
function fontPlus()
{
  fontSize += 2;
  if( fontSize > 22 )
    fontSize = 22;

  setFontProperty( fontSize );
}

function fontMinus()
{
  fontSize -= 2;
  if( fontSize < 14 )
    fontSize = 14;

  setFontProperty( fontSize );
}

////////////////////////// ////////////////////////// //////////////////////////
function setFontProperty()
{
  var fontSizeStr = fontSize.toString() + "px";
  var elem = document.getElementById( "fontSizeButton" );
  elem.style.fontSize = fontSizeStr;
  elem.innerHTML = fontSizeStr;

  for( var i = 0;i < acc.length;i++ )
    acc[ i ].nextElementSibling.style.fontSize = fontSizeStr;
}

var displayFormat = 3;

function displayPlus()
{
  displayFormat++;
  if( displayFormat > 3 )
    displayFormat = 3;
  displaySet();
}

function displayMinus()
{
  displayFormat--;
  if( displayFormat < 0 )
    displayFormat = 0;
  displaySet();
}

function closeAll()
{
  // Close all accordions
  for( var i = 0;i < acc.length;i++ )
  {
    acc[ i ].nextElementSibling.style.display = "none"; 
    acc[ i ].classList.remove( "active" );
  }
}

////////////////////////// ////////////////////////// //////////////////////////
function displaySet()
{
  var minWProp = undefined;
  var subStr = 100;
  var fSize = "16px"; // Font size of song names in accordions
  var slFontSize; // set list font size

  closeAll();

  switch( displayFormat )
  {
    case 0: minWProp =  "0%"; fSize = "20px";break;
    case 1: minWProp =  "9%"; fSize = "10px"; break;
    case 2: minWProp = "24%"; slFontSize = "100%"; break;
    case 3: minWProp = "50%"; slFontSize = "150%"; break;
  }

  var sets = document.getElementsByClassName( "setname" );
  for( var i = 0;i < sets.length;i++ )
    if( slFontSize )
    {
      sets[ i ].style.fontSize = slFontSize;
      sets[ i ].style.display = "block";
    }
    else
      sets[ i ].style.display = "none";

  for( var i = 0;i < acc.length;i++ )
  {
    acc[ i ].style.minWidth = minWProp;

    var strName;
    if( displayFormat == 0 )
    {
      if( songNames[ i ][ 1 ] == '.' ) // chop off the song number
        strName = songNames[ i ].substr( 0, 1 );
      else
        strName = songNames[ i ].substr( 0, 2 );
    }
    else if( displayFormat == 1 )
    {
      if( songNames[ i ][ 1 ] == '.' )
        strName = songNames[ i ].substr( 2, 10 );
      else
        strName = songNames[ i ].substr( 3, 11 );
    }
    else if( displayFormat == 2 )
      strName = songNames[ i ].substr( 0, 20 );
    else
      strName = songNames[ i ];

    acc[ i ].innerHTML = strName;
    acc[ i ].style.fontSize = fSize;
  }
}

/*
  Open or close the accordion element
  if the song is in a medley, open the whole thing and scroll to the current element.
  only close a medley if it's the first song in a medley, otherwise scroll to that song.
*/
function accordionClick( elem )
{
  var wasOpen = elem.classList.contains( "active" );

  if( wasOpen && ( elem.classList.contains( "medleyCont" ) || elem.classList.contains( "medleyEnd" ) ) )
  {
    elem.scrollIntoView();
    return;
  }

  closeAll();
  displaySet(); 

  var scrollToElem = elem;

  // Go to head of medley and open the whole thing.
  while( elem.classList.contains( "medleyCont" ) || elem.classList.contains( "medleyEnd" ) )
    elem = acc[ elem.accIndex - 1 ];

  // Open this one if it was closed before.
  inMedley = elem.classList.contains( "medleyStart" );

  if( !wasOpen )
    while( elem )
    {
      elem.classList.add( "active" );

      // make the song name visible in the compressed modes. Need to clear this when minimizing in displaySet() above
      acc[ elem.accIndex ].innerHTML = songNames[ elem.accIndex ];
      if( displayFormat != 3 )
        acc[ elem.accIndex ].style.minWidth = "0%";

      var panel = elem.nextElementSibling;
      setFontProperty(); // w/o this the font change only applies to the open song. Possibly desirable.
      panel.style.display = "block";
      if( inMedley )
      {
        elem = acc[ elem.accIndex + 1 ];
        if( elem.classList.contains( "medleyEnd" ) )
          inMedley = false;
      }
      else
        elem = undefined;
    }

  scrollToElem.scrollIntoView();
}

var acc = document.getElementsByClassName( "accordion" );

songNames = [];

for( var i = 0;i < acc.length;i++ )
{
  songNames[ i ] = acc[ i ].innerHTML;
  acc[ i ].addEventListener( "click", function() { accordionClick( this ); } );
  acc[ i ].nextElementSibling.addEventListener( "click", function() { this.previousElementSibling.scrollIntoView(); } );
  acc[ i ].accIndex = i; // add a next property for opening medleys.
}

displaySet();

</script>
</body>
</html>""" )
  f.close()
  statusString = "Export complete."

# "Song Information Editor" functions.
# Additional song info not contained in the .txt file is saved as json. Artist, key, etc.

# Open the file and add the information to the song data
def openSieJson():
  global sieFileName, songLibrary

  if os.path.isfile( sieFileName ):
    with open( sieFileName ) as jFile:
      dataDict = json.load( jFile )

      for s in songLibrary:
        if s.fileName in dataDict:
          s.elements = dataDict[ s.fileName ]

def exportJsonDict(): # Save song meta data as json
  global statusString, sieFileName

  dataDict = {} # Copy the songInfoList into this dict of dicts and save. Will lose element order.
  for e in songLibrary:
    dataDict[ e.fileName ] = e.elements

  with open( sieFileName, 'w' ) as f:
    json.dump( dataDict, f )

  statusString = "Saved."

def sieRangeCheck( param, newVal ):

  if param == songParams[ SP_TEMPO ]:
    try:
      t = int( newVal )
      if t < 1:
        t = 1
      elif t > 999:
        t = 999
      newVal = str( t )
    except:
      newVal = ""
  elif param == songParams[ SP_YEAR ]:
    try:
      t = int( newVal )
      if t < 1:
        t = 1
      elif t > 2100:
        t = 2100
      newVal = str( t )
    except:
      newVal = ""
  elif param == songParams[ SP_KEY ]:
    if len( newVal ) > 5:
      newVal = newVal[ 0 : 5 ]

  return newVal

def sieDisplayUI():
  global statusString, songParams

  os.system( 'clear' )
  print( "Additional song data." )
  print( "-------------------- ------------------ ------- ----- ------ ----------- --------" )
  print( "File                 Artist             Key     Tempo Year   Genre       Length"   )
  print( "-------------------- ------------------ ------- ----- ------ ----------- --------" )

  first = cursorSong - 10
  if first < 0:
    first = 0

  for ix in range( first, first + 21 ):
    if ix == len( songLibrary ):
      break

    for paramIndex in range( 0, len( songLibrary[ ix ].elements ) ):
      di = {} # DisplayInfo
      for param in songParams:
        if param in songLibrary[ ix ].elements:
          tmpStr = songLibrary[ ix ].elements[ param ]
          if tmpStr == None:
            tmpStr = "---"
        else:
          tmpStr = "???" # Added a new param or possibly mangled JSON file

        if ix == cursorSong and songParams[ cursorParam ] == param:
          tmpStr = '>' + tmpStr + '<'
        else:
          tmpStr = ' ' + tmpStr + ' '

        di[ param ] = tmpStr

    if ix == cursorSong:
      print( bcolors.BOLD, end="" )
    print( "%-20s " % ( songLibrary[ ix ].fileName.split( "." )[ 0 ][ 0 : 19 ] ), end="" )
    if ix == cursorSong:
      print( bcolors.ENDC, end="" )

    print( "%-18s %-7s %-5s %-6s %-11s %-7s" % ( di[ songParams[ SP_ARTIST  ] ][ 0 : 18 ],
                                                 di[ songParams[ SP_KEY     ] ][ 0 :  7 ],
                                                 di[ songParams[ SP_TEMPO   ] ][ 0 :  5 ],
                                                 di[ songParams[ SP_YEAR    ] ],
                                                 di[ songParams[ SP_GENRE   ] ][ 0 : 11 ],
                                                 di[ songParams[ SP_LENGTH  ] ][ 0 :  8 ] ) )
  print( "--------------------------------------------------------------------------------" )

  if statusString:
    print( "\n" + bcolors.WARNING + statusString + bcolors.ENDC )
    statusString = None

def sieMain():
  global cursorSong, cursorParam, searchFor, statusString

  sieEdited = False

  # Start of main loop.
  sieDisplayUI()
  while True:
    ch = getInput()

    if ch == "DOWN" or ch == "j":
      if cursorSong == None: # Go to first element
        cursorSong = 0
        cursorParam = None
      else:
        if cursorSong < len( songLibrary ) - 1: # Go back to the end.
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
    elif ch == '0':
      cursorSong = 0
    elif ch == 'f':
      cursorSong += 10
      if cursorSong >= len( songLibrary ) - 1:  # Go back to the end.
        cursorSong = len( songLibrary ) - 1
    elif ch == 'd':
      cursorSong -= 10
      if cursorSong < 0:
        cursorSong = 0
    elif ch == ' ': # Edit
      if cursorSong is not None:
        sieEdited = True
        newVal = raw_input( 'Enter new value:' )
        newVal = sieRangeCheck( songParams[ cursorParam ], newVal )
        if newVal == "":
          newVal = None
        songLibrary[ cursorSong ].elements[ songParams[ cursorParam ] ] = newVal
    elif ch == 's':
      sieEdited = False
      exportJsonDict()
    elif ch == '/' or ch == 'n':
      found = False
      if ch == '/':
        searchFor = raw_input( 'Search:' )
      for ix in range( cursorSong + 1, len( songLibrary) ):
        if songLibrary[ ix ].fileName.lower()[ 0 : len( searchFor ) ] == searchFor.lower():
          cursorSong = ix
          found = True
          break
      if not found:
        for ix in range( 0, cursorSong ):
          if songLibrary[ ix ].fileName.lower()[ 0 : len( searchFor ) ] == searchFor.lower():
            cursorSong = ix
            found = True
            break
        if not found:
          statusString = "Not Found."
    elif ch == '?':
      print( sieHelpString )
      foo = getInput()
    elif ch == 'e':
      if sieEdited:
        statusString = "Song data not saved."
        updateSongDataFromLibrary()
      return()
    elif ch == 'q':
      exit()

    sieDisplayUI()

# Start of main loop.
songLibrary = getLocalSongs()
if len( songLibrary ) == 0:
  print( "No songs in local directory." )
  exit()

openSieJson()

displayUI()
while True:
  ch = getInput()
  if ch == "DOWN" or ch == "j":
    if operMode == MODE_MOVE_SET:
      if currentSet < len( setLists ) - 1:
        s = setLists[ currentSet + 1 ]
        setLists[ currentSet + 1 ] = setLists[ currentSet ]
        setLists[ currentSet ] = s
        currentSet += 1
    else:
      songFwd( SONG_COLUMNS )
  elif ch == "UP" or ch == "k":
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
    else:
      operMode = MODE_MOVE_NORMAL
  elif ch == 'M':
    if operMode != MODE_MOVE_SET and currentSet != LIBRARY_SET:
      operMode = MODE_MOVE_SET
    else:
      operMode = MODE_MOVE_NORMAL
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
  elif ch == 'e':
    sieMain()
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
      s.highLight = HIGHLIGHT_ON if s.highLight == HIGHLIGHT_NONE else HIGHLIGHT_NONE
    else:
      statusString = "In Library."
  elif ch == 'y':
    if currentSet != LIBRARY_SET:
      s = setLists[ currentSet ].songList[ currentSong ]
      s.medley = True if s.medley == False else False
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
  elif ch == '[':
    if showBy is not None:
      if showBy > 0:
        showBy -= 1
      else:
        showBy = None
  elif ch == ']':
    if showBy is None:
      showBy = 0
    elif showBy < len( songParams ) - 1:
      showBy += 1
  elif ch == '?':
    os.system( 'clear' )
    print( helpString )
    foo = getInput()
  elif ch == 'q':
    exit()

  calcSongCounts()
  displayUI()