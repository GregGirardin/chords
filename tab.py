#!/usr/bin/python

import os, sys, glob, copy, pickle
'''
A basic tablature editing utility.

Greg Girardin
Nashua NH, USA
November, 2020

A song will be modeled as a list tracks (e.g. guitar1, guitar2, bass)
Each track will contain a list of measures.
Each measure contains a list of beats.
Each beat is a list of simultaneous notes, empty list indicates a rest
Each note is a value representing the fret and string
'''

songExt = ".pytab"

statusString = None
selectedfileIx = 0

INST_GUITAR = 1
INST_BASS = 2

NOTE_NORMAL = 0
NOTE_HAMMER = 1
NOTE_PULLOFF = 2
NOTE_SLIDE = 3

instrument = INST_GUITAR

DISPLAY_BEATS = 32

class bcolors:
  BLUE    = '\033[94m'
  WARNING = '\033[93m'
  FAIL    = '\033[91m'
  ENDC    = '\033[0m'
  RED     = '\033[91m'

GLOBAL_TRACK = 1 # Things that apply to all tracks will be put in track 1, tbd, put in song

MAX_WIDTH = 120
MAX_BEATS_PER_MEAS = 32
MAX_TRACKS = 3
MAX_MEASURES = 500
DISPLAY_BEATS = 32 # number of beats we can display on a line

tuningsDict = { "Standard" : [ 'E ', 'B ', 'G ', 'D ', 'A ', 'E ' ],
                "Drop D"   : [ 'E ', 'B ', 'G ', 'D ', 'A ', 'D ' ],
                "DADGAD"   : [ 'D ', 'A ', 'G ', 'D ', 'A ', 'D ' ] }

tunings = [ "Standard", "Drop D", "DADGAD" ]
tuningIndex = 0

'''
  Wrapper around a list. This API is 1 based

  API

  set
  get
  pop
  clr
'''

class pytabContainer( object ):

  def __init__( self ):
    self.objects = []
    self.annotation = None # place to allow comments

  def set( self, obj, index=None, insert=False ):
    # If index is none then append. Create if necessary.
    if index is None and insert == True:
      assert 0, "Must provide index to insert"

    if index and index < 1:
      assert 0, "Bad index."

    if index:
      index -= 1 # make 0 based, API is 1 based
      # Add empty entries if necessary, ex: we're adding measure 10 to a new song.
      while self.count() <= index:
        self.objects.append( None )

      if insert:
        self.objects.insert( index, obj )
      else:
        self.objects[ index ] = obj
    else:
      self.objects.append( obj )

    return obj

  def get( self, index=None ):
    # get an object list.
    if index:
      assert index > 0, "Index must be > 0."
      if index > len( self.objects ):
        return None
      index -= 1 # make 0 based, API is 1 based.
      return self.objects[ index ]
    else:
      return self.objects

  def pop( self, index ):
    if index < 1 or index > len( self.objects ):
      return None

    self.objects.pop( index - 1 )
    return True

  def clr( self, index ):
    return( self.set( None, index ) )

  def count( self ):
    return len( self.objects )

class pytabNote( object ):

  def __init__( self, string, fret, noteType ):
    self.string = string
    self.fret = fret
    self.noteType = noteType

class pytabBeat( pytabContainer ):

  def addNote( self, string, fret, noteType ):
    assert string >= 1 and string <= 6, "Valid strings are 1-6" # tbd
    assert fret >= 0 and fret <= 24, "Valid frets are 0-24" # tbd
    return self.set( pytabNote( string, fret, noteType ), string )

class pytabMeasure( pytabContainer ):

  def __init__( self ):
    self.pageBreak = False
    self.repeat = False
    pytabContainer.__init__( self )

  def addBeat( self, beat=None, insert=False ):
    if beat:
      assert beat <= MAX_BEATS_PER_MEAS, "Exceeded max beats per measure."
      assert beat > 0, "First beat is 1."
    return self.set( pytabBeat(), beat, insert )

class pytabTrack( pytabContainer ):
  def __init__( self, name="Track" ):
    self.trackName = name
    #self.trackType = type # guitar, bass, etc
    pytabContainer.__init__( self )

  def addMeasure( self, measure=None, insert=False ):
    if measure:
      assert measure <= MAX_MEASURES, "Beyond max measure."
      assert measure > 0, "First measure is 1."
    return self.set( pytabMeasure(), measure, insert )

class pytabSong( pytabContainer ):

  def __init__( self, name ):
    self.songName = name
    self.tuningIndex = 0
    pytabContainer.__init__( self )

  def addTrack( self, track=None, insert=False, name="Track" ):

    if track:
      assert track <= MAX_TRACKS, "Beyond max track."
      assert track > 0, "First track is 1."
    return self.set( pytabTrack( name ), track, insert )

def loadSong( name ):
  global statusString
  fileName = name + songExt

  try:
    with open( fileName, 'rb' ) as f:
      song = pickle.load( f )
  except:
    statusString = "Could not open: " + fileName
    return None

  return song

def save( song ):
  global statusString
  fileName = song.songName + songExt

  with open( fileName, 'wb' ) as f:
    pickle.dump( song, f )

  statusString = "Saved."

def annotate( o, h, ANN_IX, curOff, html ):
  '''
  Display annotation if it won't overwrite a previous one.
  o is the object that may have an annotation ( measure or beat )
  h is the header to be modified, we're also passed the indexes since they vary between the UI and export
  '''
  if o:
    if o.annotation:
      if curOff[ 1 ] < curOff[ 0 ]:
        while curOff[ 1 ] < curOff[ 0 ]:
          if html:
            h[ ANN_IX ] += '&nbsp'
          else:
            h[ ANN_IX ] += ' '
          curOff[ 1 ] += 1

        h[ ANN_IX ] += o.annotation
        curOff[ 1 ] += len( o.annotation )

measure_spaces = 0

def export( song, html ):
  ''' Save in human readable format. Could probably refactor with displayUI() '''
  lstatusString = None # local status string.
  global instrument, measure_spaces
  fileName = song.songName + ( ".html" if html else ".txt" )

  try:
    f = open( fileName, 'w' )
  except:
    lstatusString = "Could not open" + fileName
    return lstatusString

  if html:
    f.write( "<!DOCTYPE html>\n"
             "<html><head><style type=\"text/css\">a {text-decoration: none}</style></head>\n"
             "<body><font style=\"font-family:courier;\" size=\"2\">\n<h2>\n")
  MEAS_IX = 0
  ANN_IX = 1
  f.write( song.songName + ( "<br>\n" if html else "\n" ) )
  if html:
    f.write( "</h2><hr>" )

  measure = 1

  while measure <= song.get( 1 ).count():
    headerLines = [ '&nbsp', '' ] if html else [ ' ', '' ] # [ measures, annotations ]
    curOff = [ 3, 0 ]  # current, where the space is
    fretboardLines = copy.copy( tuningsDict[ tunings[ currentSong.tuningIndex ] ] )

    def endOfMeasure( repeat=False ):
      global measure_spaces

      for s in( 0, 1, 4, 5 ):
        fretboardLines[ s ] += '|'

      ch = ':' if repeat else "|"
      fretboardLines[ 2 ] += ch
      fretboardLines[ 3 ] += ch

      measure_spaces += 1

    disBeats = DISPLAY_BEATS
    repeat = False

    while True:
      if measure <= song.get( 1 ).count() and disBeats > 0:
        m = song.get( 1 ).get( measure )
        if m == None:
          endOfMeasure( repeat )
          curOff[ 0 ] += 1
        else:
          repeat = m.repeat
          annotate( m, headerLines, ANN_IX, curOff, html )

          # Display measure
          curBeatNum = 1
          for b in m.get():
            disBeats -= 1
            annotate( b, headerLines, ANN_IX, curOff, html )

            for curString in range( 1 if instrument == INST_GUITAR else 3, 7 ):
              note = b.get( curString ) if b else None
              fieldString = ""

              if note == None:
                fieldString += "--"
              else:
                if note.fret > 9:
                  fieldString += "%2d" % ( note.fret )
                else:
                  if note.noteType == NOTE_NORMAL:
                    prefix = "-"
                  elif note.noteType == NOTE_HAMMER:
                    prefix = "h"
                  elif note.noteType == NOTE_SLIDE:
                    prefix = "\\"
                  else:
                    prefix = "p"
                  fieldString += prefix
                  fieldString += "%d" % ( note.fret )
              fieldString += "-"
              fretboardLines[ curString - 1 ] += fieldString

            if curBeatNum == 1:
              if measure < 10:
                measure_spaces += 2
              elif measure < 100:
                measure_spaces += 1

              headerLines[ MEAS_IX ] += ( "&nbsp" * measure_spaces if html else " " * measure_spaces ) + "%d" % ( measure )
              measure_spaces = 0
            else:
              measure_spaces += 3

            curOff[ 0 ] += 3
            curBeatNum += 1

          endOfMeasure( repeat )
          curOff[ 0 ] += 1
      else:
        break

      measure += 1
      if song.get( measure ):
        if song.get( measure ).pageBreak:
          break

    measure_spaces = 0

    for line in headerLines:
      f.write( line )
      if html:
        f.write( "<br>" )
      f.write ("\n")

    fl = fretboardLines if instrument == INST_GUITAR else fretboardLines[ 2 : ]

    for line in fl:
      f.write( line )
      if html:
        f.write( "<br>" )
      f.write( "\n" )
    f.write( "\n" )

  if html:
    f.write( "</font></body></html>\n" )
    lstatusString = "Exported HTML."
  else:
    lstatusString = "Exported txt."

  f.close()
  return lstatusString

def displayUI( song, measure, cursor_t, cursor_m, cursor_b, cursor_s ):
  ''' Display starting from current measure display DISPLAY_BEATS beats, so the width isn't quite fixed
      based on how many measures that is.
  '''
  global statusString, unsavedChange
  assert cursor_m >= measure, "Cursor before current measure."

  SUMMARY_IX = 0 # header lines
  STATUS_IX  = 1
  MEAS_IX    = 2
  ANN_IX     = 3
  BEAT_IX    = 4

  headerLines = [ 'Name:', # Song name, number of measures. Beats
                  '',      # Status
                  '  ',    # Measures
                  '',      # Annotations
                  '  ' ]   # Beats
  fretboardLines = copy.copy( tuningsDict[ tunings[ currentSong.tuningIndex ] ] )

  instructions = [ '\nUse arrows to move cursor',
                   '><  Fwd / back measure',
                   '123.. shift + 12 note',
                   't-= Add/move track  D   Delete track',
                   'a/i Add/Ins beat    d   Delete beat',
                   'q   quit            sp  Clear note',
                   'm   Add measure     c/p Copy/Paste',
                   'n   Annotate        h   hammer/pull/slide',
                   'r   Rename song     b   Page break',
                   'R   Repeat          s   Save',
                   'o   Open            x/X Export (txt/html)',
                   'I   Instrument      G   Tuning' ]

  headerLines[ SUMMARY_IX ] += song.songName +", " + str( song.get( 1 ).count() ) + " measures, " + \
                               "%d beats in measure. " % ( song.get( 1 ).get( cursorMeasure ).count() ) + \
                               ( bcolors.RED + "Edited" + bcolors.ENDC if unsavedChange else "" )

  if statusString is not None:
    headerLines[ STATUS_IX ] += bcolors.RED + statusString + bcolors.ENDC

  curOff = [ 3, 0 ]

  statusString = None

  def endOfMeasure( pageBreak=False, repeat=False ):
    global instrument
    bc = '/' if pageBreak else '|'

    strs = ( 0, 1, 4, 5 ) if instrument == INST_GUITAR else( 2, 5 )

    for s in strs:
      fretboardLines[ s ] += bc

    if repeat:
      bc = ":"
    elif pageBreak:
      bc = "/"
    else:
      bc = "|"

    strs = ( 2, 3 ) if instrument == INST_GUITAR else( 3, 4 )

    for s in strs:
      fretboardLines[ s ] += bc

    headerLines[ MEAS_IX ] += ' '
    headerLines[ BEAT_IX ] += ' '

  # Display measures
  disBeats = DISPLAY_BEATS
  repeat = False

  while True:
    if measure <= song.get( 1 ).count() and disBeats > 0:
      m = song.get( 1 ).get( measure )
      if m == None:
        endOfMeasure( repeat )
        curOff[ 0 ] += 1
      else:
        repeat = m.repeat

        annotate( m, headerLines, ANN_IX, curOff, False )
        curBeatNum = 1
        for b in m.get():
          disBeats -= 1
          annotate( b, headerLines, ANN_IX, curOff, False )

          for curString in range( 1, 7 ):
            note = b.get( curString ) if b else None
            if measure == cursor_m and curBeatNum == cursor_b and curString == cursor_s:
              cursorPos = True
            else:
              cursorPos = False

            fieldString = ""

            if note == None:
              fieldString += "<->" if cursorPos else "---"
            else:
              if note.fret > 9:
                fieldString += "%2d" % ( note.fret )
              else:
                if note.noteType == NOTE_NORMAL:
                  prefix = "-"
                elif note.noteType == NOTE_HAMMER:
                  prefix = "h"
                elif note.noteType == NOTE_SLIDE:
                  prefix = "\\"
                else:
                  prefix = "p"
                fieldString += "<" if cursorPos else prefix
                fieldString += "%d" % ( note.fret )
              fieldString += ">" if cursorPos else "-"

            fretboardLines[ curString - 1 ] += fieldString
          if curBeatNum == 1:
            headerLines[ MEAS_IX ] += "%-3d" %( measure )
          else:
            headerLines[ MEAS_IX ] += '   '
          headerLines[ BEAT_IX ] += ' . '
          curOff[ 0 ] += 3
          curBeatNum += 1

        pb = False
        if measure + 1 <= song.get( 1 ).count():
          nm = song.get( measure + 1 )
          if nm and nm.pageBreak:
            pb = nm.pageBreak

        endOfMeasure( pb, repeat )
        curOff[ 0 ] += 1
    else:
      break
    measure += 1

  os.system( 'clear' )
  for line in headerLines:
    print( line )
  fl = fretboardLines if instrument == INST_GUITAR else fretboardLines[ 2 : ]
  for line in fl:
    print( line )
  for line in instructions:
    print( line )

def getInput():
  # Copied from http://stackoverflow.com/questions/983354/how-do-i-make-python-to-wait-for-a-pressed-key
  import termios, fcntl, sys, os
  fd = sys.stdin.fileno()
  flags_save = fcntl.fcntl( fd, fcntl.F_GETFL )
  attrs_save = termios.tcgetattr( fd )
  attrs = list( attrs_save )
  attrs[ 0 ] &= ~( termios.IGNBRK | termios.BRKINT | termios.PARMRK | termios.ISTRIP | termios.INLCR | termios.IGNCR | termios.ICRNL | termios.IXON )
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

def findPrevBeat( song, curTrack, curMeasure, curBeat ):

  if curBeat > 1:
    curBeat -= 1
  elif curMeasure > 1:
    curMeasure -= 1
    curBeat = song.get( 1 ).get( curMeasure ).count()

  return curTrack, curMeasure, curBeat

def findNextBeat( song, curTrack, curMeasure, curBeat ):

  if song.get( 1 ).count() > 0:
    if curBeat < song.get( 1 ).get( curMeasure ).count():
      curBeat += 1
    elif curMeasure < song.get( 1 ).count():
      curMeasure += 1
      curBeat = 1
    elif not measureEmpty( song, curMeasure ):
      # create new empty measure if you scroll right passed a non-empty measure
      curMeasure += 1
      curBeat = 1
      m = song.get( 1 ).addMeasure()
      m.addBeat()

  return curTrack, curMeasure, curBeat

def findPrevMeasure( song, curMeasure, curBeat ):

  if curMeasure > 1:
    curMeasure -= 1
    if curBeat > song.get( 1 ).get( curMeasure ).count():
      curBeat = song.get( 1 ).get( curMeasure ).count()

  return curMeasure, curBeat

def findNextMeasure( song, curMeasure, curBeat ):

  if song.get( 1 ).count() > curMeasure:
    curMeasure += 1
    if curBeat > song.get( 1 ).get( curMeasure ).count():
      curBeat = song.get( 1 ).get( curMeasure ).count()

  return curMeasure, curBeat

def findSong():
  global statusString, selectedfileIx

  re = "./*" + songExt

  matchList = glob.glob( re )

  if not matchList:
    statusString = "No files."
    return None

  if selectedfileIx >= len( matchList ):
    selectedfileIx = len( matchList ) - 1

  while True:
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
    if c == "LEFT":
      return None
    if c == "RIGHT":
      return matchList[ selectedfileIx ][ 2 : ].split( "." )[ 0 ]
    if c == "DOWN":
      if selectedfileIx < len( matchList ) - 1:
        selectedfileIx += 1
    if c == "UP":
      if selectedfileIx > 0:
        selectedfileIx -= 1

def handleCopy( song, measure, beat ):
  global statusString

  bList = []
  print( "Beats to copy? (1-9,c,m)" )
  numBeats = 0
  beatsCopied = 0

  c = getInput()
  if c >= '1' and c <= '9':
    numBeats = int( c )
  elif c == '0':
    numBeats = 10
  elif c == 'c':
    numBeats = 1
  elif c == 'm':
    numBeats = song.get( measure ).count()
    beat = 1

  if not numBeats:
    statusString = "Invalid input for copy."
    return None

  while numBeats:
    m = song.get( measure )
    if m:
      b = m.get( beat )
      bList.append( b )
      beatsCopied += 1
    beat += 1
    if beat > m.count():
      measure += 1
      beat = 1
    if measure > song.count():
      break

    numBeats -= 1

  statusString = "%d beats copied." % ( beatsCopied )

  return bList

# An empty measure has 1 beat with no notes in it.
def measureEmpty( song, measure ):
  empty = False

  m = song.get( measure )

  if m.count() == 1:
    b = m.get( 1 )
    if b:
      nList = b.get()
      if not nList:
        empty = True
      else:
        anyNotes = False
        for n in nList:
          if n is not None:
            anyNotes = True
            break
        if not anyNotes:
          empty = True

  return empty

def handlePaste( song, beats, measure, beat ):
  global statusString, MAX_BEATS_PER_MEAS

  if song is None:
    statusString = "Invalid song."
    return 0
  if beats is None:
    statusString = "Nothing to paste."
    return 0
  m = song.get( measure )
  if not m:
    statusString = "Invalid measure."
    return 0

  emptyMeasure = measureEmpty( song, measure )

  # Normally paste after current beat but if the measure is empty we'll handle it differently.
  if not emptyMeasure:
    beat += 1
  else:
    m.pop( 1 )

  inserting = False if beat == m.count() + 1 else True

  beatsPasted = 0
  for b in beats:
    if m.count() >= MAX_BEATS_PER_MEAS:
      statusString = "Hit max measure length."
      return beatsPasted

    if inserting:
      m.set( copy.deepcopy( b ), beat, True )
    else:
      m.set( copy.deepcopy( b ) )

    beat += 1
    beatsPasted += 1

  if beatsPasted:
    statusString = "Pasted %d beats." % beatsPasted

  return beatsPasted

# Load default song if present
songName = "Song-2.0"

if len( sys.argv ) == 2:
  songName = sys.argv[ 1 ].split( "." )[ 0 ]

currentSong = loadSong( songName )
if not currentSong:
  currentSong = pytabSong( songName )
  trk = currentSong.addTrack( 1, name="Default" )
  meas = trk.addMeasure( 1 )
  meas.addBeat( 1 )

currentMeasure = 1 # Where the UI starts displaying from

cursorTrack = 1 # Cursor position
cursorMeasure = 1
cursorBeat = 1
cursorString = 4

unsavedChange = False

cpBuf = [] # List for copy/paste

def getNote(): # return the note at cursorTrack : cursorMeasure : cursorBeat : cursorString

  t = currentSong.get( cursorTrack )

  m = t.get( cursorMeasure )
  if not m:
    return None
  if not m.get( cursorBeat ):
    return None
  b = m.get( cursorBeat )
  return b.get( cursorString )

def setNote( fret ): # set the note at cursorTrack : cursorMeasure : cursorBeat : cursorString
  global unsavedChange

  t = currentSong.get( cursorTrack )

  m = t.get( cursorMeasure )
  if not m.get( cursorBeat ):
    m.addBeat( cursorBeat )
  b = m.get( cursorBeat )
  b.addNote( cursorString, fret, NOTE_NORMAL )
  unsavedChange = True

#############
# main loop #
#############

while True:
  displayUI( currentSong, currentMeasure, cursorTrack, cursorMeasure, cursorBeat, cursorString )

  ch = getInput()
  if ch == 'q':
    exit()
  elif ch == 't': # add track
    statusString = "Add Track"
  elif ch == 'D': # delete track
    statusString = "Delete Track"
  elif ch == '-': # move track up
    statusString = "Track up"
  elif ch == '=': # move track down
    statusString = "Track down"
  elif ch == 'RIGHT': # go to the next beat if one exists
    cursorTrack, cursorMeasure, cursorBeat = findNextBeat( currentSong, cursorTrack, cursorMeasure, cursorBeat )
  elif ch == 'LEFT':  # go to the previous beat if possible
    cursorTrack, cursorMeasure, cursorBeat = findPrevBeat( currentSong, cursorTrack, cursorMeasure, cursorBeat )
  elif ch == 'UP':
    if cursorString > ( 1 if instrument == INST_GUITAR else 3 ):
      cursorString -= 1
  elif ch == 'DOWN':
    if cursorString < 6:
      cursorString += 1
  elif ch == ',':
    # track doesn't change
    cursorMeasure, cursorBeat = findPrevMeasure( currentSong, cursorMeasure, cursorBeat )
  elif ch == '.':
    # track doesn't change
    cursorMeasure, cursorBeat = findNextMeasure( currentSong, cursorMeasure, cursorBeat )
  elif ch == 'a' or ch == 'i': # add/insert beat
    offset = 1 if ch == 'a' else 0
    m = currentSong.get( GLOBAL_TRACK ).get( cursorMeasure )
    if not m:
      m = currentSong.get( GLOBAL_TRACK ).addMeasure( cursorMeasure )
    if m.count() == MAX_BEATS_PER_MEAS:
      statusString = "Max beats reached."
    elif cursorBeat == m.count() and ch == 'a':
      m.addBeat()
    else:
      m.addBeat( cursorBeat + offset, insert=True )
    unsavedChange = True
  elif ch == 'b': # toggle page break
    m = currentSong.get( GLOBAL_TRACK ).get( cursorMeasure )
    if m:
      m.pageBreak = False if m.pageBreak == True else True
  elif ch == 'R': # toggle repeat
    m = currentSong.get( GLOBAL_TRACK ).get( cursorMeasure )
    if m:
      m.repeat = False if m.repeat == True else True
  elif ch == 'd': # delete beat.
    m = currentSong.get( GLOBAL_TRACK ).get( cursorMeasure )
    if currentSong.get( GLOBAL_TRACK ).count() > 1 or m.count() > 1:
      # tbd: all tracks
      m.pop( cursorBeat )
      if m.count() == 0: # delete measure
        currentSong.get( GLOBAL_TRACK ).pop( cursorMeasure )
        if cursorMeasure > 1:
          cursorMeasure -= 1
          cursorBeat = currentSong.get( GLOBAL_TRACK ).get( cursorMeasure ).count()
      else:
        if cursorBeat > m.count():
          cursorBeat = m.count()
      unsavedChange = True
  elif ch == ' ': # clear note
    m = currentSong.get( GLOBAL_TRACK ).get( cursorMeasure ) # tbd, all tracks
    b = m.get( cursorBeat )
    b.clr( cursorString )
    unsavedChange = True
  elif ch == 'm': # add a measure after the current one
    if cursorMeasure == currentSong.get( GLOBAL_TRACK ).count():
      m = currentSong.get( GLOBAL_TRACK ).addMeasure()
      # tbd, add to all tracks
    else:
      m = currentSong.get( GLOBAL_TRACK ).addMeasure( cursorMeasure + 1, insert=True )
    # Create as many beats as exist in the current measure
    for _ in range( currentSong.get( 1 ).get( cursorMeasure ).count() ):
      m.addBeat()
    unsavedChange = True
  elif ch == 'r': # Rename
    songName = raw_input( 'Enter song name:' )
    currentSong.get( GLOBAL_TRACK ).songName = songName
    unsavedChange = True
  elif ch == 'h': # Highlight
    n = getNote()
    if n:
      if n.noteType == NOTE_NORMAL:
        n.noteType = NOTE_HAMMER
        statusString = "Hammmer"
      elif n.noteType == NOTE_HAMMER:
        n.noteType = NOTE_PULLOFF
        statusString = "PullOff"
      elif n.noteType == NOTE_PULLOFF:
        n.noteType = NOTE_SLIDE
        statusString = "Slide"
      else:
        n.noteType = NOTE_NORMAL
  elif ch == 'n': # Annotate beat
    annotation = raw_input( "Enter beat annotation:" )
    if len( annotation ) == 0: # clear
      annotation = None
    m = currentSong.get( cursorTrack ).get( cursorMeasure )
    if not m:
      m = currentSong.get( 1 ).addMeasure( cursorMeasure )
      # tbd, add to all tracks
    if m:
      b = m.get( cursorBeat )
      if b:
        b.annotation = annotation
      else:
        statusString = "Invalid beat."
    else:
      statusString = "Invalid measure."
  elif ch == 'N': # Annotate measure
    annotation = raw_input( "Enter measure annotation:" )
    if len( annotation ) == 0: # clear
      annotation = None
    m = currentSong.get( GLOBAL_TRACK ).get( cursorMeasure )
    if not m:
      m = currentSong.get( GLOBAL_TRACK ).addMeasure( cursorMeasure )
      # tbd, add to all tracks
    if m:
      m.annotation = annotation
    else:
      statusString = "Invalid measure."
  elif ch == '`': # various notes follow `1234567890-= represent fretboard 0-12.
    setNote( 0 )
  elif ch >= '1' and ch <= '9':
    fret = int( ch )
    setNote( fret )
  elif ch == '0':
    setNote( 10 )
  elif ch == '-':
    setNote( 11 )
  elif ch == '=':
    setNote( 12 )
  elif ch == '!':
    setNote( 13 )
  elif ch == '@':
    setNote( 14 )
  elif ch == '#':
    setNote( 15 )
  elif ch == '$':
    setNote( 16 )
  elif ch == '%':
    setNote( 17 )
  elif ch == '^':
    setNote( 18 )
  elif ch == '&':
    setNote( 19 )
  elif ch == '*':
    setNote( 20 )
  elif ch == '(':
    setNote( 21 )
  elif ch == ')':
    setNote( 22 )
  elif ch == '_':
    setNote( 23 )
  elif ch == '+':
    setNote( 24 )
  elif ch == 's': # Save
    save( currentSong )
    unsavedChange = False
  elif ch == 'x':
    statusString = export( currentSong, False )
  elif ch == 'X':
    statusString = export( currentSong, True )
  elif ch == 'o': # open
    newSongName = findSong()
    if newSongName:
      loadedSong = loadSong( newSongName )
      if loadedSong is not None:
        currentSong = loadedSong
        songName = newSongName
        unsavedChange = False
    cursorMeasure = 1
    cursorBeat = 1
    cursorString = 4
  elif ch == 'c': # copy
    cpBuf = handleCopy( currentSong, cursorMeasure, cursorBeat )
  elif ch == 'p': # paste
    cursorBeat += handlePaste( currentSong, cpBuf, cursorMeasure, cursorBeat )
    if cursorBeat > currentSong.get( 1 ).get( cursorMeasure ).count():
      cursorBeat = currentSong.get( 1 ).get( cursorMeasure ).count()
    # ^ corner case because of how we handle pasting into empty measures.
  elif ch == 'I': # not destructive, only display, so no concern about unsaved
    if instrument == INST_GUITAR:
      instrument = INST_BASS
      if cursorString < 3:
        cursorString = 3
    else:
      instrument = INST_GUITAR
  elif ch == 'G': # TuninG
    currentSong.tuningIndex  += 1
    if currentSong.tuningIndex >= len( tunings ):
      currentSong.tuningIndex = 0
    statusString = tunings[ currentSong.tuningIndex ]

  # Calculate currentMeasure
  displayBeats = 0
  currentMeasure = cursorMeasure
  testMeasure = cursorMeasure

  m = currentSong.get( GLOBAL_TRACK ).get( testMeasure )
  if m:
    displayBeats = m.count()
  testMeasure -= 1

  while testMeasure >= 1:
    m = currentSong.get( GLOBAL_TRACK ).get( testMeasure )
    if m:
      displayBeats += m.count()
    displayBeats += 1 # the end of measure line takes up some space
    if displayBeats >= DISPLAY_BEATS:
      break
    currentMeasure = testMeasure
    testMeasure -= 1