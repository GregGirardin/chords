#!/usr/bin/python

import random

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


Keys
arrow keys forward backward one beat, up/ down strings
[] forward/back one measure
space = insert rest
d = delete beat
0-9 = insert note
e jump to end of song

'''

songExt = ".pytab"

version = "v1.0"

MAX_WIDTH = 120

# wrapper around a list.
# The api is 1 based, even though the lists are 0 based.
# A song begins with measure 1, a measure with beat 1, note with string 1
class pytabContainer (object):

  def __init__ (self):
    self.objects = []

  def rangeCheck (self, index):
    if not index:
      return True

    if index >= len (self.objects) + 1:
      return False

    return True

  def set (self, obj, index = None):
    # if index is none then append.
    # create the measure if necessary.

    if index and index < 1:
      assert 0, "Bad index."

    if index:
      index -= 1 # make 0 based
      # add empty entries if necessary, ex: we're adding measure 10 to a new song.
      while index >= self.count ():
        self.objects.append (None)
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
    return (set (None, index))

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

  def addBeat (self, beat = None):
    if beat:
      assert beat <= 64, "Max 64 beats per measure."
      assert beat > 0, "First beat is 1."
    return self.set (pytabBeat (), beat)

class pytabSong (pytabContainer):

  def __init__ (self, name):
    self.songName = name
    pytabContainer.__init__(self)

  def addMeasure (self, measure = None):
    if measure:
      assert measure <= 500, "Beyond max measure."
      assert measure > 0, "First measure is 1."
    return self.set (pytabMeasure (), measure)

# class pytabUtil (object):
  '''
    This class handles UI, file IO
  '''
def load (name):
  song = pytabSong (name)
  fileName = song.songName + songExt
  try:
    f = open (fileName, 'r')
  except:
    print "Could not open", fileName
    return None

  content = [line.rstrip('\n') for line in f.readlines()]
  f.close ()

  if content [0] != version:
    print "Unsupported version", content [0]
    return None

  for line in content [1:]:
    beatline = line.split ()
    mbs = beatline [0][1:].split ('b')
    measure = int (mbs [0])
    beat = int (mbs [1])

    # create measure if necessary
    if song.get (measure) == None:
      print "Adding measure", measure
      song.addMeasure (measure)

    songmeasure = song.get (measure)
    if songmeasure.get (beat) == None:
      print "Adding beat", beat
      songmeasure.addBeat (beat)

    songbeat = songmeasure.get (beat)
    for note in beatline [1:]:
      sf = note[1:].split ('f')
      print "Adding note", int (sf[0]), int (sf [1])
      songbeat.addNote (int (sf[0]), int (sf [1]))

  return song

def save (song):

  fileName = song.songName + songExt

  try:
    f = open (fileName, 'w')
  except:
    print "Could not open", fileName
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

def export (song):
  pass
  # save in human readable format

  # open

  #

def displayUI (self, song):
  pass

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
  # generate test song
  # add some stuff
  # save it
  # load it and save that
  # make sure they're the same.
  songName1 = "testsong1"
  songName2 = "testsong2"
  testsong = pytabSong (songName1)
  numMeasures = 16
  numBeats = 16
  testBeat = 5

  # add beats to a test measure
  testMeasure = numMeasures / 2
  for testMeasure in (1,3,5):
    tm = testsong.addMeasure (testMeasure)
    assert tm is not None, "Test measure was None."

    for testBeat in (1,2,4):
      tb = tm.addBeat (testBeat)
      assert tb is not None, "Test beat was None."

      # add notes to test beat
      for testNote in range(1, 6):
        tb.addNote (testNote, testNote + testMeasure)

  # verify addMeasure adds empty measures up to the measure you're creating.
  testsong.addMeasure (numMeasures * 2)

  assert testsong.count() == numMeasures * 2, "Wrong number of measures."
  assert testsong.get (numMeasures * 2) is not None, "Test measure was None."
  assert testsong.get (numMeasures * 2 - 1) is None, "Fill measure was not None."

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

pytabTest()

# main loop