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
E -----0-------|--0-|----

A song will be modeled as a list of measures.
Each measure contains a list of beats.
Each beat is a list of notes that exist at that moment, empty list indicates a rest
Each note is a value representing the fret and string

Song
[
  Measure
  [
    Beat []
    Beat
    [
      Note
      [
        String 6, Fret 0
      ]
    ]
    Beat
    [
      Note
      [
        String 5
      ]
      Note
      [
        String 4
      ]
    ]
    Beat
    [
      Note
      [
        String  3
      ]
    ]
  Measure
  [
    Beat
    [
      Note
      [
      ]
  Measure
  [
    Beat
    [
      Note
      [
        String 2
      ]
    ]
  ]
]

A song file will be saved as ASCII and will essentially look as shown above

There'll be an option to export as human readable tab.


Keys
arrow keys forward backward one beat, up/ down strings
[] forward/back one measure
space = insert rest
del = delete beat
i = insert beat
0-9 = insert note
e jump to end of song

'''

songExt = ".gtab"

MAX_WIDTH = 120

# wrapper around a list, may not need.
class pytabContainer (object):

  def __init__ (self):
    self.objects = []

  def rangeCheck (self, index):
    if index and index >= len (self.objects):
      return False
    return True

  def set (self, obj, index = None):
    if index:
      # add empty entries if necessary, ex: we're adding measure 10 to a new song.
      while index + 1 > self.count ():
        self.objects.append (None)

    if index:
      self.objects [index] = obj
    else:
      self.objects.append (obj)
    return obj

  def pop (self, index):
    if not self.rangeCheck (index):
      return None

    self.objects.pop (index)
    return True

  def clr (self, index):
    return (set (None, index))

  def get (self, index = None):
    if index and not self.rangeCheck (index):
      return None

    if index:
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
    return self.set (pytabBeat (), beat)

class pytabSong (pytabContainer):

  def __init__ (self, name):
    self.songName = name
    pytabContainer.__init__(self)

  def addMeasure (self, measure = None):
    if measure:
      assert measure <= 500, "Beyond max measure."
    return self.set (pytabMeasure (), measure)

# class pytabUtil (object):
  '''
    This class handles UI, file IO
  '''
def open (song):
  pass
  # open

  # read

  # close

def save (song):

  try:
    f = open (song.songName, 'w')
  except:
    print "Could not open", song.songName
    return

  f.write ("pytab kicks ass.")
  f.close ()

  # save song in our proprietary format

  # open file

  # header stuff

  # close


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
  songName = "testsong"
  testsong = pytabSong(songName)
  numMeasures = 16
  numBeats = 16
  testBeat = 5

  for _ in range (numMeasures):
    testsong.addMeasure (None) # add to end

  assert testsong.count() == numMeasures, "Wrong count of measures."

  # add beats to a test measure
  testMeasure = numMeasures / 2
  tm = testsong.get (testMeasure)
  assert tm is not None, "Test measure was None."

  tm.addBeat (testBeat)

  tb = tm.get (testBeat)
  assert tb is not None, "Test beat was None."

  # add notes to test beat
  tb.addNote (1, 5)
  tb.addNote (2, 24)
  tb.addNote (1, 6)

  for n in tb.get():
    if n is not None:
      print "Note:", n.string, n.fret

  tb.pop (2)
  for n in tb.get():
    if n is not None:
      print "Note:", n.string, n.fret

  # verify addMeasure adds empty measures up to the measure you're creating.
  testsong.addMeasure (numMeasures * 2)

  assert testsong.count() == numMeasures * 2 + 1, "Wrong number of measures."
  assert testsong.get (numMeasures * 2) is not None, "Test measure was None."
  assert testsong.get (numMeasures * 2 - 1) is None, "Fill measure was not None."

  # save

  save (testsong)

  # export (this test can't validate that)

  # open

  # compare

pytabTest()

# main loop