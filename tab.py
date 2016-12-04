#!/usr/bin/python

import os
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
m2b6 # this beat has no notes, but it's the last beat of the measure

'''
songExt = ".pytab"

version = "v1.0"

statusString = None
insertMode = False # May implement. If true, move cursor after every note
octaveFlag = False
MAX_WIDTH = 120
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
      while index >= self.count ():
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

  def addBeat (self, beat = None, insert = False):
    if beat:
      assert beat <= 64, "Max 64 beats per measure."
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
    if linefields [0][-1:] == 'a': # This is an annotation
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
  if o:
    if o.annotation:
      if len (h [ANN_IX]) < len (h [BEAT_IX]):
        while len (h [ANN_IX]) < len (h [BEAT_IX]):
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

    fretboardLines = [ 'E ', # string 1
                       'B ',
                       'G ',
                       'D ',
                       'A ',
                       'E ' ]

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
  global statusString, octaveFlag, insertMode
  assert cursor_m >= measure, "Cursor before current measure."

  SUMMARY_IX = 0 # header lines
  STATUS_IX  = 1
  MEAS_IX    = 2
  ANN_IX     = 3
  BEAT_IX    = 4

  headerLines = ['Name:', # Song name, number of measures.
                 '',      # Status
                 '  ',    # Measures
                 '',      # Annotations
                 '  ' ]   # Beats

  fretboardLines = [ 'E ', # string 1
                     'B ',
                     'G ',
                     'D ',
                     'A ',
                     'E ' ]

  instructions = [ '',
                   'Use arrows to move cursor.',
                   '`1234567890-= Insert note at fret (0-12).',
                   'o   Toggle octave. Notes become 12-24.',
                   'a/i Add beat to measure.',
                   'd   Delete beat.',
                   'sb  Clear note.',
                   'm   Add a measure.',
                   'n   Annotate.',
                   'r   Rename song.',
                   's   Save.',
                   'l   Load.',
                   'x   Export as tablature.',
                   'q   Quit.']

  headerLines [SUMMARY_IX] += song.songName + " " + str (song.count()) + " Measures."
  if statusString is not None:
    headerLines [STATUS_IX] += statusString
  else:
    if octaveFlag:
      headerLines [STATUS_IX] += "Octave "
    if insertMode:
      headerLines [STATUS_IX] += "Insert"

  statusString = None

  def endOfMeasure ():
    for s in range (6):
      fretboardLines [s] += '|'
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

          for curString in range (1,7):
            if b:
              note = b.get (curString)
            else:
              note = None
            if measure == cursor_m and curBeatNum == cursor_b and curString == cursor_s:
              fieldString = "+"
            else:
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

  os.system ('clear')
  for line in headerLines:
    print line [0:MAX_WIDTH]
  for line in fretboardLines:
    print line [0:MAX_WIDTH]
  for line in instructions:
    print line

def getInput ():
    # Copied from http://stackoverflow.com/questions/983354/how-do-i-make-python-to-wait-for-a-pressed-key
    import termios, fcntl, sys, os
    fd = sys.stdin.fileno()
    flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
    attrs_save = termios.tcgetattr(fd)
    attrs = list(attrs_save)
    attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK | termios.ISTRIP | termios.INLCR |
                  termios.IGNCR | termios.ICRNL | termios.IXON )
    attrs[1] &= ~termios.OPOST
    attrs[2] &= ~(termios.CSIZE | termios.PARENB)
    attrs[2] |= termios.CS8
    attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON | termios.ISIG | termios.IEXTEN)
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)
    try:
      ret = sys.stdin.read(1)
    except KeyboardInterrupt:
      ret = 0
    finally:
      termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
      fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)
    return ret

def pytabTest ():
  # generate test song, add some stuff, do some sanity checks, save it
  # load it and save that, make sure they're the same.
  songName1 = "testsong1"
  songName2 = "testsong2"
  testsong = pytabSong (songName1)
  numMeasures = 8

  # add beats to a test measure
  for testMeasure in (1,3,5):
    tm = testsong.addMeasure (testMeasure)
    assert tm is not None, "Test measure was None."

    for testBeat in (1,2,4):
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

  # if you want to test the UI
  # displayUI (testsong, 1, 3, 4, 5)

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

  return curMeasure, curBeat

# pytabTest()

# main loop
songName = "Song"

currentSong = pytabSong (songName)
currentSong.addMeasure ()
currentSong.get (1).addBeat()

currentMeasure = 1 # Where the UI starts displaying from

cursorMeasure = 1 # Cursor position
cursorBeat = 1
cursorString = 1
unsavedChange = False

def setNote (fret):
  if octaveFlag:
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
    if unsavedChange   and False: # Disable this for now.
      verify = raw_input ('Unsaved changes, quit? (y/n)')
      if verify == 'y':
        exit()
    else:
      exit()
  # TBD: fix the arrow key escapes, (these work on my MAC)
  elif ch == 'C':  # go to the next beat if one exists
    cursorMeasure, cursorBeat = findNextBeat (currentSong, cursorMeasure, cursorBeat)
  elif ch == 'D': # go to the previous beat if possible
    cursorMeasure, cursorBeat = findPrevBeat (currentSong, cursorMeasure, cursorBeat)
  elif ch == 'A':
    if cursorString > 1:
      cursorString -= 1
  elif ch == 'B':
    if cursorString < 6:
      cursorString += 1

  elif ch == 'a' or ch == 'i': # add/insert beat
    if ch == 'a':
      offset = 1
    else:
      offset = 0
    m = currentSong.get (cursorMeasure)
    if m == None:
      m = currentSong.addMeasure (cursorMeasure)
    if cursorBeat == m.count():
      m.addBeat ()
    else:
      m.addBeat (cursorBeat + offset, insert = True)
    unsavedChange = True

  elif ch == 'd': # delete beat. Delete measure if empty
    m = currentSong.get (cursorMeasure)
    if cursorMeasure == 1 and cursorBeat == 1:
       if m.count():
         m.pop (cursorBeat)
    else:
      m.pop (cursorBeat)
      if m.count () == 0: # delete measure
        currentSong.pop (cursorMeasure)
        if cursorMeasure > 1:
          cursorMeasure -=1
          cursorBeat = currentSong.get (cursorMeasure).count()
      else:
        if cursorBeat > 1:
          cursorBeat -= 1
      unsavedChange = True

  elif ch == ' ': # clear note at cursor
    m = currentSong.get (cursorMeasure)
    b = m.get (cursorBeat)
    b.clr (cursorString)
    unsavedChange = True
  elif ch == 'm': # add a measure after the current one
    if cursorMeasure == currentSong.count():
      m = currentSong.addMeasure ()
    else:
      m = currentSong.addMeasure (cursorMeasure + 1, insert = True)
    # create as many beats as exist in the current measure
    for _ in range (currentSong.get (cursorMeasure).count()):
      m.addBeat ()
    unsavedChange = True
  elif ch == 'r': # rename
    songName = raw_input ('Enter song name:')
    currentSong.songName = songName
    unsavedChange = True
  elif ch == 'n':
    note = raw_input ("Enter annotation:")
    # if we're on beat 1, add the note to the measure, else to the beat
    if len (note) == 0: # clear
      note = None
    m = currentSong.get (cursorMeasure)
    if m:
      if cursorBeat == 1:
        m.annotation = note
      else:
        b = m.get (cursorBeat)
        if b:
          b.annotation = note
        else:
          statusString = "Invalid beat."
    else:
      statusString = "Invalid measure."
  elif ch == '`':
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
  elif ch == 'o':
    if octaveFlag:
      octaveFlag = False
    else:
      octaveFlag = True
  elif ch == 's': # save
    save (currentSong)
    unsavedChange = False
  elif ch == 'l': # load
    if unsavedChange:
      verify = raw_input ('Unsaved changes, Load? (y/n)')
      if verify != 'y':
        continue
    loadedSong = load (songName)
    if loadedSong is not None:
      currentSong = loadedSong
      unsavedChange = False
  elif ch == 'x': # export
    export (currentSong)

  # Calculate currentMeasure based on cursorMeasure.
  # May need to get a bit more intelligent about this computation in case of large measures.
  # ideally have a cursorMeasure a couple ahead of currentMeasure so you can
  # see measures on both sides of the cursor.
  if cursorMeasure > 3:
    currentMeasure = cursorMeasure - 3
  else:
    currentMeasure = 1