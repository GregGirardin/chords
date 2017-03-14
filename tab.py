#!/usr/bin/python

import os, sys, glob, copy
'''
A basic tablature editing utility.

Greg Girardin
Nashua NH, USA
November, 2016

A song will be modeled as a list of measures.
Each measure contains a list of beats.
Each beat is a list of simultaneous notes, empty list indicates a rest
Each note is a value representing the fret and string

File format

One line per beat. If a measure ends with a rest we need to create it to
preserve the number of beats in the measure.

m1b2 s6f0 # measure 1 beat 2. String 6 fret 0
m1a Verse 1 starts here # annotation of measure 1
m1b2a Comment # annotation of m1b2
m1b3 s5f2 s4f2 # this beat has two notes
m1b4 s3f0
m1p # page break (for export)
m2b6 # this beat has no notes, but it's the last beat of the measure

If you give it a command line parameter that's the song name
ex: ./tab.py mynewsong
'''
songExt = ".pytab"

version = "v1.0"

unsavedChgStr = 'Unsaved changes. Continue? (y/n)'

statusString = None
selectedfileIx = 0

OFFSET_MODE_NORMAL = 0
OFFSET_MODE_MIDDLE = 1
OFFSET_MODE_OCTAVE = 2

offsetMode = OFFSET_MODE_NORMAL
MAX_WIDTH = 120
MAX_BEATS_PER_MEAS = 32 #
DISPLAY_BEATS = 32 # number of beats we can display on a line
'''
 Wrapper around a list.
 This api is 1 based
'''
class pytabContainer (object):

  def __init__ (self):
    self.objects = []
    self.annotation = None # place to allow comments

  def rangeCheck (self, index):
    if not index:
      return True

    if index >= len (self.objects) + 1:
      return False

    return True

  def set (self, obj, index = None, insert = False):
    # if index is none then append. Create if necessary.

    if index is None and insert == True:
      assert 0, "Must provide index to insert"

    if index and index < 1:
      assert 0, "Bad index."

    if index:
      index -= 1 # make 0 based
      # add empty entries if necessary, ex: we're adding measure 10 to a new song.
      while self.count () <= index:
        self.objects.append (None)

      if insert:
        self.objects.insert (index, obj)
      else:
        self.objects [index] = obj
    else:
      self.objects.append (obj)

    return obj

  def pop (self, index):
    if index < 1 or index > len (self.objects):
      return None

    self.objects.pop (index - 1)
    return True

  def clr (self, index):
    return (self.set (None, index))

  def get (self, index = None):
    # get an object or entire list.
    if index:
      assert index > 0, "Index must be > 0."
      if index > len (self.objects):
        return None
      index -= 1
      return self.objects [index]
    else:
      return self.objects

  def count (self):
    return len (self.objects)

class pytabNote (object):

  def __init__ (self, string, fret):
    self.string = string
    self.fret = fret

class pytabBeat (pytabContainer):

  def addNote (self, string, fret):
    assert string >= 1 and string <= 6, "Valid strings are 1-6"
    assert fret >= 0 and fret <= 24, "Valid frets are 0-24"
    return self.set (pytabNote (string, fret), string)

class pytabMeasure (pytabContainer):

  def __init__ (self):
    self.pageBreak = False
    pytabContainer.__init__(self)

  def addBeat (self, beat = None, insert = False):
    if beat:
      assert beat <= MAX_BEATS_PER_MEAS, "Exceeded max beats per measure."
      assert beat > 0, "First beat is 1."
    return self.set (pytabBeat (), beat, insert)

class pytabSong (pytabContainer):

  def __init__ (self, name):
    self.songName = name
    pytabContainer.__init__(self)

  def addMeasure (self, measure = None, insert = False):

    if measure:
      assert measure <= 500, "Beyond max measure."
      assert measure > 0, "First measure is 1."
    return self.set (pytabMeasure (), measure, insert)

def load (name):
  global statusString

  song = pytabSong (name)
  fileName = song.songName + songExt
  try:
    f = open (fileName, 'r')
  except:
    statusString = "Could not open: " + fileName
    return None

  content = [line.rstrip('\n') for line in f.readlines()]
  f.close ()

  if content [0] != version:
    statusString = "Unsupported version" + content [0]
    return None

  for line in content [1:]:
    linenocomment = line.split ('#')[0] # strip comment
    linefields = linenocomment.split ()
    if linefields [0][-1:] == 'p': # This is a page Break
      f = linefields[0][1:-1] # first field minus the m and trailing b
      measure = int (f)
      if song.get (measure) == None:
        song.addMeasure (measure)
      song.get (measure).pageBreak = True
    elif linefields [0][-1:] == 'a': # This is an annotation
      annotation = linenocomment [len (linefields[0]) + 1:]
      f = linefields[0][1:-1] # first field minus the m and trailing a
      if not 'b' in f: # annotation of a measure
        measure = int (f)
        if song.get (measure) == None:
          song.addMeasure (measure)
        song.get (measure).annotation = annotation
      else: # .. of a beat
        mbs = f.split ('b')
        measure = int (mbs [0])
        beat = int (mbs [1])

        if song.get (measure) == None:
          song.addMeasure (measure)
        m = song.get (measure)
        if m.get (beat) == None:
          m.addBeat (beat)

        m.get (beat).annotation = annotation

    else: # This line is a sequence of notes.
      mbs = linefields [0][1:].split ('b')
      measure = int (mbs [0])
      beat = int (mbs [1])

      # create measure if necessary
      if song.get (measure) == None:
        song.addMeasure (measure)

      m = song.get (measure)
      if m.get (beat) == None:
        m.addBeat (beat)

      songbeat = m.get (beat)
      for note in linefields [1:]:
        sf = note[1:].split ('f')
        songbeat.addNote (int (sf[0]), int (sf [1]))

  return song

def save (song):
  global statusString
  fileName = song.songName + songExt

  try:
    f = open (fileName, 'w')
  except:
    statusString = "Could not open:" + fileName
    return

  f.write (version + "\n")

  curMeasure = 1

  for m in song.get ():
    if m: # All measures should be valid
      if m.pageBreak:
        f.write ("m%dp\n" % curMeasure)

      if m.annotation:
        f.write ("m%da %s\n" % (curMeasure, m.annotation))

      curBeat = 1
      for b in m.get():
        dispMandB = False
        if b:
          if b.annotation:
            f.write ("m%db%da %s\n" % (curMeasure, curBeat, b.annotation))
          for n in b.get():
            if n:
              if not dispMandB:
                f.write ("m%db%d" % (curMeasure, curBeat))
                dispMandB = True
              f.write (" s%df%d" % (n.string, n.fret))

        curBeat += 1
        if dispMandB:
          f.write ("\n")
      # if last beat in measure has no notes, save it to preserve measure length.
      lastBeat = m.get (m.count())
      if lastBeat == None or (lastBeat and lastBeat.count() == 0):
        f.write ("m%db%d\n" % (curMeasure, m.count()))

    curMeasure += 1

  f.close ()
  statusString = "Saved."

def annotate (o, h, ANN_IX, BEAT_IX):
  ''' Display annotation if it won't overwrite a previous one.
      o is the object that may have an annotation (measure or beat)
      h is the header to be modified, we're also passed the indexes since
      they vary between the UI and export
      We use the 'beat' line as a way to determine the current x position '''
  OFFSET = 1
  if o:
    if o.annotation:
      if len (h [ANN_IX]) < len (h [BEAT_IX]) + OFFSET:
        while len (h [ANN_IX]) < len (h [BEAT_IX]) + OFFSET:
          h [ANN_IX] += ' '
        h [ANN_IX] += o.annotation

def export (song):
  global statusString
  # Save in human readable format. Could probably refactor with displayUI()
  fileName = song.songName + ".txt"

  try:
    f = open (fileName, 'w')
  except:
    statusString = "Could not open" + fileName
    return

  MEAS_IX = 0
  ANN_IX  = 1
  BEAT_IX = 2

  f.write (song.songName + "\n")
  measure = 1

  while measure <= song.count ():
    headerLines = ['  ', # measures
                   '',   # annotations
                   '  '] # beats

    fretboardLines = [ 'E ', 'B ', 'G ', 'D ', 'A ', 'E ']

    def endOfMeasure ():
      for s in range (6):
        fretboardLines [s] += '|'

      headerLines [MEAS_IX] += ' '
      headerLines [BEAT_IX] += ' '

    while True:
      if measure <= song.count () and len (fretboardLines [0]) < MAX_WIDTH:
        m = song.get (measure)
        if m == None:
          endOfMeasure ()
        else:
          annotate (m, headerLines, ANN_IX, BEAT_IX)

          # display measure
          curBeatNum = 1
          for b in m.get():
            annotate (b, headerLines, ANN_IX, BEAT_IX)

            for curString in range (1,7):
              if b:
                note = b.get (curString)
              else:
                note = None
              fieldString = "-"

              if note == None:
                fieldString += "--"
              else:
                if note.fret > 9:
                  fieldString += "%2d" % (note.fret)
                else:
                  fieldString += "-%d" % (note.fret)

              fretboardLines [curString - 1] += fieldString
            if curBeatNum == 1:
              headerLines [MEAS_IX] += "%-3d" % (measure)
            else:
              headerLines [MEAS_IX] += '   '
            headerLines [BEAT_IX] += '  .'
            curBeatNum += 1

          endOfMeasure ()
      else:
        break
      measure += 1
      if song.get (measure):
        if song.get (measure).pageBreak:
          break

    for line in headerLines:
      f.write (line)
      f.write ("\n")

    for line in fretboardLines:
      f.write (line)
      f.write ("\n")
    f.write("\n")

  statusString = "Exported."
  f.close()

def displayUI (song, measure, cursor_m, cursor_b, cursor_s):
  ''' display starting from current measure
      display MAX_WIDTH characters, so that's about MAX_WIDTH/3 beats
      each beat takes 3 spaces, plus the measure delimiter
  '''
  global statusString, offsetMode
  assert cursor_m >= measure, "Cursor before current measure."

  SUMMARY_IX = 0 # header lines
  STATUS_IX  = 1
  MEAS_IX    = 2
  ANN_IX     = 3
  BEAT_IX    = 4

  headerLines = ['Name:', # Song name, number of measures. Beats
                 '',      # Status
                 '  ',    # Measures
                 '',      # Annotations
                 '  ' ]   # Beats

  fretboardLines = [ 'E ', 'B ', 'G ', 'D ', 'A ', 'E ']

  instructions = [ '',
                   'Use arrows to move cursor',
                   '><  Forward / back measure',
                   '`1234567890-= note at (0-12, 7-18, 12-24)',
                   'o   Offset',
                   'a/i Add/Insert beat',
                   'd   Delete beat',
                   'sp  Clear note',
                   'm   Add measure',
                   'c/p Copy/Paste',
                   'n   Annotate',
                   'r   Rename song',
                   'b   Page break',
                   's   Save',
                   'l/L Load/Reload',
                   'x   Export',
                   'q   Quit']

  headerLines [SUMMARY_IX] += song.songName + ", " + \
                              str (song.count()) + " measures, " + \
                              "%d beats in measure." % (song.get (cursorMeasure).count())

  if statusString is not None:
    headerLines [STATUS_IX] += statusString
  else:
    if offsetMode == OFFSET_MODE_MIDDLE:
      headerLines [STATUS_IX] += "7-18"
    elif offsetMode == OFFSET_MODE_OCTAVE:
      headerLines [STATUS_IX] += "12-24"

  statusString = None

  def endOfMeasure (pageBreak = False):
    if pageBreak:
      bc = '/'
    else:
      bc = '|'

    for s in range (6):
      fretboardLines [s] += bc
    headerLines [MEAS_IX] += ' ' # Measures
    headerLines [BEAT_IX] += ' ' # Beats

  # Display measures
  while True:
    if measure <= song.count () and len (headerLines [MEAS_IX]) < MAX_WIDTH:
      m = song.get (measure)
      if m == None:
        endOfMeasure ()
      else:
        annotate (m, headerLines, ANN_IX, BEAT_IX)
        curBeatNum = 1
        for b in m.get():
          annotate (b, headerLines, ANN_IX, BEAT_IX)

          for curString in range (1, 7):
            if b:
              note = b.get (curString)
            else:
              note = None
            if measure == cursor_m and curBeatNum == cursor_b and curString == cursor_s:
              cursorPos = True
            else:
              cursorPos = False

            fieldString = ""

            if note == None:
              if cursorPos:
                fieldString += "<->"
              else:
                fieldString += "---"
            else:
              if note.fret > 9:
                fieldString += "%2d" % (note.fret)
              else:
                fieldString += "-%d" % (note.fret)
              if cursorPos:
                fieldString += ">"
              else:
                fieldString += "-"

            fretboardLines [curString - 1] += fieldString
          if curBeatNum == 1:
            headerLines [MEAS_IX] += "%-3d" % (measure)
          else:
            headerLines [MEAS_IX] += '   '
          headerLines [BEAT_IX] += ' . '
          curBeatNum += 1

        pb = False
        if measure + 1 <= song.count():
          nm = song.get (measure + 1)
          if nm and nm.pageBreak:
            pb = nm.pageBreak

        endOfMeasure (pb)
    else:
      break
    measure += 1

  os.system ('clear')
  for line in headerLines:
    print line [0 : MAX_WIDTH]
  for line in fretboardLines:
    print line [0 : MAX_WIDTH]
  for line in instructions:
    print line

def getInput ():
  # Copied from http://stackoverflow.com/questions/983354/how-do-i-make-python-to-wait-for-a-pressed-key
  import termios, fcntl, sys, os
  fd = sys.stdin.fileno()
  flags_save = fcntl.fcntl (fd, fcntl.F_GETFL)
  attrs_save = termios.tcgetattr (fd)
  attrs = list (attrs_save)
  attrs [0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK | termios.ISTRIP | termios.INLCR |
                 termios.IGNCR | termios.ICRNL | termios.IXON)
  attrs [1] &= ~termios.OPOST
  attrs [2] &= ~(termios.CSIZE | termios.PARENB)
  attrs [2] |= termios.CS8
  attrs [3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON | termios.ISIG | termios.IEXTEN)
  termios.tcsetattr(fd, termios.TCSANOW, attrs)
  fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)
  try:
    ret = sys.stdin.read (1)
    if ord (ret) == 27: # Escape
      ret = sys.stdin.read (1)
      ret = sys.stdin.read (1)
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
    termios.tcsetattr (fd, termios.TCSAFLUSH, attrs_save)
    fcntl.fcntl (fd, fcntl.F_SETFL, flags_save)
  return ret

def pytabTest ():
  # generate test song, add some stuff, do some sanity checks, save it
  # load it and save that, make sure they're the same.
  songName1 = "testsong1"
  songName2 = "testsong2"
  testsong = pytabSong (songName1)
  numMeasures = 8

  # add beats to a test measure
  for testMeasure in (1, 3, 5):
    tm = testsong.addMeasure (testMeasure)
    assert tm is not None, "Test measure was None."

    for testBeat in (1, 2, 4):
      tb = tm.addBeat (testBeat)
      assert tb is not None, "Test beat was None."

      # add notes to test beat
      for testNote in range (1, 6):
        tb.addNote (testNote, testNote + testMeasure)

  # verify addMeasure adds empty measures up to the measure you're creating.
  testsong.addMeasure (numMeasures)

  assert testsong.count() == numMeasures, "Wrong number of measures."
  assert testsong.get (numMeasures) is not None, "Test measure was None."
  assert testsong.get (numMeasures - 1) is None, "Fill measure was not None."

  save (testsong)

  # open
  testsong2 = load (songName1)
  # compare
  # rather than walk through the lists comparing note by note, just diff the files for now.
  testsong2.songName = songName2
  save (testsong2)

  fileName = songName1 + songExt
  try:
    f = open (fileName, 'r')
  except:
    print "Could not open", fileName
    assert 0

  content1 = f.readlines()
  f.close ()

  fileName = songName2 + songExt
  try:
    f = open (fileName, 'r')
  except:
    print "Could not open", fileName
    assert 0

  content2 = f.readlines()
  f.close ()

  assert content1 == content2, "Files differ."

  # can't validate export

def findPrevBeat (song, curMeasure, curBeat):
  if curBeat > 1:
    curBeat -= 1
  elif curMeasure > 1:
    curMeasure -= 1
    curBeat = song.get (curMeasure).count()

  return curMeasure, curBeat

def findNextBeat (song, curMeasure, curBeat):
  if song.count() > 0:
    if curBeat < song.get (curMeasure).count():
      curBeat += 1
    elif curMeasure < song.count():
      curMeasure += 1
      curBeat = 1
    elif not measureEmpty (song, curMeasure):
      # create new empty measure if you scroll right passed a non-empty measure
      curMeasure += 1
      curBeat = 1
      m = song.addMeasure ()
      m.addBeat ()

  return curMeasure, curBeat

def findPrevMeasure (song, curMeasure, curBeat):
  if curMeasure > 1:
    curMeasure -= 1
    if curBeat > song.get (curMeasure).count():
      curBeat = song.get (curMeasure).count()

  return curMeasure, curBeat

def findNextMeasure (song, curMeasure, curBeat):
  if song.count() > curMeasure:
    curMeasure += 1
    if curBeat > song.get (curMeasure).count():
      curBeat = song.get (curMeasure).count()

  return curMeasure, curBeat

def findSong ():
  global statusString, selectedfileIx
  re = "./*" + songExt

  matchList = glob.glob (re)

  if not matchList:
    statusString = "No files."
    return None

  if selectedfileIx >= len (matchList):
    selectedfileIx = len (matchList) - 1

  while True:
    os.system ('clear')
    print "Use arrow keys to select or exit.\n"
    index = 0
    for s in matchList:
      line = "  "
      if index == selectedfileIx:
        line = "> "
      line += s [2:].split (".")[0]
      index += 1

      print line

    c = getInput()
    if c == "LEFT":
      return None
    if c == "RIGHT":
      return matchList [selectedfileIx][2:].split (".")[0]
    if c == "DOWN":
      if selectedfileIx < len (matchList) - 1:
        selectedfileIx += 1
    if c == "UP":
      if selectedfileIx > 0:
        selectedfileIx -= 1

def handleCopy (song, measure, beat):
  global statusString
  bList = []
  print "Beats to copy? (1-9,c,m)"
  numBeats = 0
  beatsCopied = 0

  c = getInput()
  if c >= '1' and c <= '9':
    numBeats = int (c)
  elif c == '0':
    numBeats = 10
  elif c == 'c':
    numBeats = 1
  elif c == 'm':
    numBeats = song.get (measure).count()
    beat = 1

  if not numBeats:
    statusString = "Invalid input for copy."
    return None
  while numBeats:
    m = song.get (measure)
    if m:
      b = m.get (beat)
      bList.append (b)
      beatsCopied += 1
    beat += 1
    if beat > m.count():
      measure += 1
      beat = 1
    if measure > song.count():
      break

    numBeats -= 1

  statusString = "%d beats copied." % (beatsCopied)

  return bList

def measureEmpty (song, measure):

  empty = False

  m = song.get (measure)

  if m.count() == 1:
    b = m.get (1)
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

def handlePaste (song, beats, measure, beat):
  global statusString, MAX_BEATS_PER_MEAS

  if song is None:
    statusString = "Invalid song."
    return 0
  if beats is None:
    statusString = "Nothing to paste."
    return 0
  m = song.get (measure)
  if not m:
    statusString = "Invalid measure."
    return 0

  emptyMeasure = measureEmpty (song, measure)

  # Normally paste after current beat
  # but if the measure is empty we'll handle it differently.

  if not emptyMeasure:
    beat += 1
  else:
    m.pop (1)

  if beat == m.count() + 1:
    inserting = False
  else:
    inserting = True

  beatsPasted = 0
  for b in beats:
    if m.count() >= MAX_BEATS_PER_MEAS:
      statusString = "Hit max measure length."
      return beatsPasted

    if inserting:
      m.set (copy.deepcopy (b), beat, True)
    else:
      m.set (copy.deepcopy (b))

    beat += 1
    beatsPasted += 1

  if beatsPasted:
    statusString = "Pasted %d beats." % beatsPasted

  return beatsPasted

# pytabTest()

# main loop
songName = "Song"

if len (sys.argv) == 2:
  songName = sys.argv [1].split (".")[0]

currentSong = load (songName)
if not currentSong:
  currentSong = pytabSong (songName)
  currentSong.addMeasure ()
  currentSong.get (1).addBeat()

currentMeasure = 1 # Where the UI starts displaying from

cursorMeasure = 1 # Cursor position
cursorBeat = 1
cursorString = 1
unsavedChange = False

cpBuf = []

def setNote (fret):
  if offsetMode == OFFSET_MODE_OCTAVE:
    fret += 12
  elif offsetMode == OFFSET_MODE_MIDDLE:
    if fret < 7:
      fret += 12

  m = currentSong.get (cursorMeasure)
  if not m.get (cursorBeat):
    m.addBeat (cursorBeat)
  b = m.get (cursorBeat)
  b.addNote (cursorString, fret)
  unsavedChange = True

while True:
  displayUI (currentSong, currentMeasure, cursorMeasure, cursorBeat, cursorString)
  ch = getInput()
  if ch == 'q':
    if unsavedChange:
      print (unsavedChgStr)
      verify = getInput ()
      if verify == 'y':
        exit()
    else:
      exit()
  elif ch == 'RIGHT': # go to the next beat if one exists
    cursorMeasure, cursorBeat = findNextBeat (currentSong, cursorMeasure, cursorBeat)
  elif ch == 'LEFT': # go to the previous beat if possible
    cursorMeasure, cursorBeat = findPrevBeat (currentSong, cursorMeasure, cursorBeat)
  elif ch == 'UP':
    if cursorString > 1:
      cursorString -= 1
  elif ch == 'DOWN':
    if cursorString < 6:
      cursorString += 1
  elif ch == ',':
    cursorMeasure, cursorBeat = findPrevMeasure (currentSong, cursorMeasure, cursorBeat)
  elif ch == '.':
    cursorMeasure, cursorBeat = findNextMeasure (currentSong, cursorMeasure, cursorBeat)
  elif ch == 'a' or ch == 'i': # add/insert beat
    if ch == 'a':
      offset = 1
    else:
      offset = 0
    m = currentSong.get (cursorMeasure)

    if not m:
      m = currentSong.addMeasure (cursorMeasure)
    if m.count() == MAX_BEATS_PER_MEAS:
      statusString = "Max beats reached."
    elif cursorBeat == m.count() and ch == 'a':
      m.addBeat ()
    else:
      m.addBeat (cursorBeat + offset, insert = True)
    unsavedChange = True
  elif ch == 'b': # toggle page break
    m = currentSong.get (cursorMeasure)
    if m:
      if m.pageBreak == True:
        m.pageBreak = False
      else:
        m.pageBreak = True
  elif ch == 'd': # delete beat.
    m = currentSong.get (cursorMeasure)
    if currentSong.count() > 1 or m.count () > 1:
      m.pop (cursorBeat)
      if m.count () == 0: # delete measure
        currentSong.pop (cursorMeasure)
        if cursorMeasure > 1:
          cursorMeasure -= 1
          cursorBeat = currentSong.get (cursorMeasure).count ()
      else:
        if cursorBeat > m.count ():
          cursorBeat = m.count ()
      unsavedChange = True
  elif ch == ' ': # clear note
    m = currentSong.get (cursorMeasure)
    b = m.get (cursorBeat)
    b.clr (cursorString)
    unsavedChange = True
  elif ch == 'm': # add a measure after the current one
    if cursorMeasure == currentSong.count ():
      m = currentSong.addMeasure ()
    else:
      m = currentSong.addMeasure (cursorMeasure + 1, insert = True)
    # Create as many beats as exist in the current measure
    for _ in range (currentSong.get (cursorMeasure).count ()):
      m.addBeat ()
    unsavedChange = True
  elif ch == 'r': # rename song
    songName = raw_input ('Enter song name:')
    currentSong.songName = songName
    unsavedChange = True
  elif ch == 'n': # Annotate beat
    annotation = raw_input ("Enter beat annotation:")
    if len (annotation) == 0: # clear
      annotation = None
    m = currentSong.get (cursorMeasure)
    if not m:
      m = currentSong.addMeasure (cursorMeasure)
    if m:
        b = m.get (cursorBeat)
        if b:
          b.annotation = annotation
        else:
          statusString = "Invalid beat."
    else:
      statusString = "Invalid measure."
  elif ch == 'N': # Annotate measure
    annotation = raw_input ("Enter measure annotation:")
    if len (annotation) == 0: # clear
      annotation = None
    m = currentSong.get (cursorMeasure)
    if not m:
      m = currentSong.addMeasure (cursorMeasure)
    if m:
        m.annotation = annotation
    else:
      statusString = "Invalid measure."

  elif ch == '`': # various notes follow `1234567890-= represent fretboard 0-12.
    setNote (0)
  elif ch >= '1' and ch <= '9':
    fret = int (ch)
    setNote (fret)
  elif ch == '0':
    setNote (10)
  elif ch == '-':
    setNote (11)
  elif ch == '=':
    setNote (12)

  elif ch == 'o': # Toggle 0-12, 7-16 or 12-24
    if offsetMode == OFFSET_MODE_OCTAVE:
      offsetMode = OFFSET_MODE_NORMAL
    else:
      offsetMode += 1
  elif ch == 's': # save
    save (currentSong)
    unsavedChange = False

  elif ch == 'x': # export
    export (currentSong)
  elif ch == 'L': # re-load
    if unsavedChange:
      print (unsavedChgStr)
      verify = getInput()
      if verify != 'y':
        continue
    loadedSong = load (songName)
    if loadedSong is not None:
      currentSong = loadedSong
      unsavedChange = False
  elif ch == 'l': # load
    if unsavedChange:
      print (unsavedChgStr)
      verify = getInput()
      if verify != 'y':
        continue
    newSongName = findSong ()
    if newSongName:
      loadedSong = load (newSongName)
      if loadedSong is not None:
        currentSong = loadedSong
        songName = newSongName
        unsavedChange = False
    cursorMeasure = 1
    cursorBeat = 1
    cursorString = 1
  elif ch == 'c': # copy
    cpBuf = handleCopy (currentSong, cursorMeasure, cursorBeat)
  elif ch == 'p': # paste
    cursorBeat += handlePaste (currentSong, cpBuf, cursorMeasure, cursorBeat)
    if cursorBeat > currentSong.get (cursorMeasure).count():
      cursorBeat = currentSong.get (cursorMeasure).count()
    # ^ corner case because of how we handle pasting into empty measures.

  # Calculate currentMeasure
  displayBeats = 0
  currentMeasure = cursorMeasure
  testMeasure = cursorMeasure

  m = currentSong.get (testMeasure)
  if m:
    displayBeats = m.count()
  testMeasure -= 1

  while testMeasure >= 1:
    m = currentSong.get (testMeasure)
    if m:
      displayBeats += m.count()
    displayBeats += 1 # the end of measure line takes up some space
    if displayBeats >= DISPLAY_BEATS:
      break
    currentMeasure = testMeasure
    testMeasure -= 1