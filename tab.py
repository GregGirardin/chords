#!/usr/bin/python

import os
'''
A basic tablature editing utility.

Greg Girardin
Nashua NH, USA
November, 2016

The UI will look something like this:

  1            2   3      <- measures
   ^  ^  ^  ^    ^    ^   <- beats
   xx xx xx xx   xx   xx
E -------------|----|----
B -------------|----|----
G -----------0-|----|---X
D --------2----|----|----
A --------2----|----|--3-
E -----0-------|----|----

A song will be modeled as a list of measures.
Each measure contains a list of beats.
Each beat is a list of simultaneous notes, empty list indicates a rest
Each note is a value representing the fret and string

File format

One line per beat. If a measure ends with a rest we need to create it to
preserve the number of beats in the measure.

m1b2 s6f0 # measure 1 beat 2. String 6 fret 0
m1b3 s5f2 s4f2
m1b4 s3f0
m2b1 # rest

'''
songExt = ".pytab"

version = "v1.0"

statusString = None
insertMode = False # TBD. If true, move cursor after every note
octaveFlag = False
MAX_WIDTH = 120
'''
 Wrapper around a list.
 The api is 1 based
'''
class pytabContainer (object):

  def __init__ (self):
    self.objects = []

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

# class pytabUtil (object):
  '''
    This class handles UI, file IO
  '''

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
    beatline = line.split ()
    mbs = beatline [0][1:].split ('b')
    measure = int (mbs [0])
    beat = int (mbs [1])

    # create measure if necessary
    if song.get (measure) == None:
      # print "Adding measure", measure
      song.addMeasure (measure)

    songmeasure = song.get (measure)
    if songmeasure.get (beat) == None:
      # print "Adding beat", beat
      songmeasure.addBeat (beat)

    songbeat = songmeasure.get (beat)
    for note in beatline [1:]:
      sf = note[1:].split ('f')
      # print "Adding note", int (sf[0]), int (sf [1])
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

  # version
  f.write (version + "\n")

  curMeasure = 1

  for m in song.get ():
    if m: # only need to create measures that aren't empty
      curBeat = 1
      for b in m.get():
        dispMandB = False

        if b:
          for n in b.get():
            if n:
              if not dispMandB:
                f.write ("m%db%d" % (curMeasure, curBeat))
                dispMandB = True
              f.write (" s%df%d" % (n.string, n.fret))

        curBeat += 1
        if dispMandB:
          f.write ("\n")
      # if last beat in measure has no notes, create it.
      if m.get (m.count()) == None:
        f.write ("m%db%d XXX\n" % (curMeasure, m.count() + 1))
    curMeasure += 1
  f.close ()
  statusString = "Saved."

def export (song):
  global statusString
  # save in human readable format
  fileName = song.songName + ".txt"

  try:
    f = open (fileName, 'w')
  except:
    statusString = "Could not open" + fileName
    return

  f.write (song.songName + "\n\n")
  measure = 1

  while (measure <= song.count ()):

    headerLines = ['  ', # measures
                   '  ' ] # beats

    fretboardLines = [ 'E ', # string 1
                       'B ',
                       'G ',
                       'D ',
                       'A ',
                       'E ' ]

    def endOfMeasure ():
      for s in range (6):
        fretboardLines [s] += '|'

      headerLines [0] += ' ' # Measures
      headerLines [1] += ' ' # Beats

    # display a line of tab
    while True:
      if measure <= song.count () and len (fretboardLines [0]) < MAX_WIDTH:
        curMeasure = song.get (measure)
        if curMeasure == None:
          endOfMeasure ()
        else:
          # display measure
          curBeatNum = 1
          for curBeat in curMeasure.get():
            for curString in range (1,7):
              if curBeat is not None:
                note = curBeat.get (curString)
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
              headerLines [0] += "%-3d" % (measure)
            else:
              headerLines [0] += '   '
            headerLines [1] += '  .' # beat
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

def displayUI (song, measure,
               cursor_m, cursor_b, cursor_s):
  ''' display starting from current measure
      display MAX_WIDTH characters, so that's about MAX_WIDTH/3 beats
      each beat takes 3 spaces, plus the measure delimiter
  '''
  global statusString, octaveFlag, insertMode
  assert cursor_m >= measure, "Cursor before current measure."

  headerLines = ['Name:', # Song name
                 '',
                 '  ', # measures
                 '  ' ] # beats

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
                   'sp  Clear note.',
                   'm   Add a measure.',
                   'n   Rename song.',
                   'z   Save.',
                   'l   Load.',
                   'x   Export.',
                   'q   Quit.']

  headerLines [0] += song.songName + " " + str (song.count()) + " Measures."
  if statusString is not None:
    headerLines [1] += statusString
  else:
    if octaveFlag:
      headerLines [1] += "Octave "
    if insertMode:
      headerLines [1] += "Insert"

  statusString = None

  def endOfMeasure ():
    for s in range (6):
      fretboardLines [s] += '|'

    headerLines [2] += ' ' # Measures
    headerLines [3] += ' ' # Beats

  # keep displaying measures
  while True:
    if measure <= song.count () and len (headerLines [2]) < MAX_WIDTH:
      curMeasure = song.get (measure)
      if curMeasure == None:
        endOfMeasure ()
      else:
        # display measure
        curBeatNum = 1
        for curBeat in curMeasure.get():
          for curString in range (1,7):
            if curBeat is not None:
              note = curBeat.get (curString)
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
            headerLines [2] += "%-3d" % (measure)
          else:
            headerLines [2] += '   '
          headerLines [3] += '  .' # beat
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
    """
    Copied from http://stackoverflow.com/questions/983354/how-do-i-make-python-to-wait-for-a-pressed-key
    """
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

  # save
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
songName = "default"

currentSong = pytabSong (songName)
currentSong.addMeasure ()
currentSong.get (1).addBeat()

currentMeasure = 1 # Where the UI starts displaying from

cursorMeasure = 1 # Our cursor position
cursorBeat = 1
cursorString = 1
unsavedChange = False

def setNote (fret):
  if octaveFlag:
    fret += 12
  m = currentSong.get (cursorMeasure)
  b = m.get (cursorBeat)
  b.addNote (cursorString, fret)
  unsavedChange = True

while True:
  displayUI (currentSong,
             currentMeasure,
             cursorMeasure,
             cursorBeat,
             cursorString)
  ch = getInput()
  if ch == 'q':
    if unsavedChange:
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
    if cursorMeasure > 1 or cursorBeat > 1:
      m = currentSong.get (cursorMeasure)
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
  elif ch == 'n': # change name
    songName = raw_input ('Enter song name:')
    currentSong.songName = songName
    unsavedChange = True
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
  elif ch == 'z': # save
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