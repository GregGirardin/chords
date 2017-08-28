#!/usr/bin/python

'''
Chord Utility v1.0
by Greg Girardin
   Nashua NH
   girardin1972@hotmail.com

   I wrote everything except for the getInput function.

   These chord generators have existed for many years, but I wanted one I could easily configure the way I
   wanted.
'''

from __future__ import print_function
import os
import sys
from  Tkinter import *
from functools import partial
import tkFont

"""
Dictionary keyed by instrument name, value is a dictionary of instrument attributes
"tuning" is high to low.
"fretOffset" is the base fret of a string (for supporting instruments like Banjo)
  if the offset is 5 and the string is "G", then the 5th fret is a G.
"""

instrumentMap = \
  {
  'Mandolin':   {
                "tuning":      ("E", "A", "D", "G"),
                "fretOffset":  (0, 0, 0, 0)
                },
  'Guitar':     {
                "tuning":      ("E", "B", "G", "D", "A", "E"),
                "fretOffset":  (0, 0, 0, 0, 0, 0)
                },
  'Dropped D':  {
                "tuning":      ("E", "B", "G", "D", "A", "D"),
                "fretOffset":  (0, 0, 0, 0, 0, 0)
                },
  'DADGAD':     {
                "tuning":      ("D", "A", "G", "D", "A", "D"),
                "fretOffset":  (0, 0, 0, 0, 0, 0)
                },
  'Bass':       {
                "tuning":      ("G", "D", "A", "E"),
                "fretOffset":  (0, 0, 0, 0)
                },
  'Banjo':      {
                "tuning":      ("D", "B", "G", "D", "G"),
                "fretOffset":  (0, 0, 0, 0, 5)
                },
  'Stick-4ths': {
                "tuning":      ("C", "G", "D", "A", "E", "B",
                                "E", "A", "D", "G", "C", "F"),
                "fretOffset":   (0, 0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0)
                }
  }
# pick the instruments you care about
instruments = ('Mandolin', 'Guitar', 'Dropped D', 'DADGAD', 'Bass')
# instruments = instrumentMap.keys() # doesn't guarantee order

intervalList = ['R', 'b2', '2', 'b3', '3', '4', 'b5', '5', 'b6', '6', 'b7', '7', '8', 'b9', '9']
# display with a #/b if that's how we'd display the major key.
dispKeyList    = ('C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B')
keyListSharps  = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
keyListFlats   = ('C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B')
bKeys = ('F', 'Bb', 'Eb', 'Ab', 'Db') # (Major) keys to be displayed as having flats, (vs sharps)

# spellingMap is a dictionary of names for the spelling and a tuple of intervalList members.
# if you add an entry, also add it to spellings tuple below.
spellingMap = \
  {
  "M":     ('R',  '3', '5'),
  "m":     ('R', 'b3', '5'),
  "7":     ('R',  '3', '5', 'b7'),
  "m7":    ('R', 'b3', '5', 'b7'),
  "M7":    ('R',  '3', '5', '7'),
  "2":     ('R',  '2', '5'),
  "4":     ('R',  '4', '5'),
  "dim":   ('R', 'b3', 'b5', '6'),
  "M-Key": ('R',  '2', '3',  '4', '5',  '6', '7'),
  "m-Key": ('R',  '2', 'b3', '4', '5', 'b6', 'b7')
  }
spellings = ('M', 'm', '7', 'm7', 'M7', '2', '4', 'dim', 'M-Key', 'm-Key')
minorSpellings = ('m', 'm7', 'm-Key')
NUM_FRETS = 15

def showWithSharps (key, spelling):
  # return True if we should show this key/spelling as having sharps (vs flats)

  def relMajor (key):
    # input is a minor key, returns the relative major key
    index = dispKeyList.index (key)
    index += 3
    index %= 12
    key = dispKeyList [index]
    return key

  if spelling in minorSpellings:
    key = relMajor (key)

  return key not in bKeys

def calcNote (root, fret):
  rootNum = dispKeyList.index (root)
  rootNum += fret
  rootNum %= 12
  return dispKeyList [rootNum]

def calcInterval (note, key):
  noteNum = dispKeyList.index (note) + 12 # C = 12, C# = 13, etc
  keyNum = dispKeyList.index (key)        # C =  0, C# =  1
  intNum = (noteNum - keyNum) % 12        # (if C) C = 0, C# = 1
  return intNum

def fretInfoGen (root, fret, fretOffset, key, spelling):
  '''
  Generate a dictionary entry about the given fret.
  root is the string's fretOffset fret note. Usually fret 0 (open).
  fret is the fret number relative to a zero offset string
  note is the text of the note
  '''

  assert fret >= fretOffset, "Fret below fret offset."

  fretInfo = {
    'root': root,
    'fret': fret,
    'note': calcNote (root, fret - fretOffset)
  }
  interval = calcInterval (fretInfo ['note'], key)
  fretInfo ['interval'] = intervalList [interval]
  fretInfo ['inSpelling'] = intervalList [interval] in spellingMap [spelling]

  # convert note for display
  if showWithSharps (key, spelling):
    curKeyList = keyListSharps
  else:
    curKeyList = keyListFlats

  fretInfo ['note'] = curKeyList [dispKeyList.index (fretInfo ['note'])]

  return fretInfo

def generateFretboard (instrument, key, spelling):
  '''
  Returns a dictionary with everything we care about
  strings are keyed by string number (1 - N) and contain a list of dictionaries for each fret
  There are also some other 'global' kinda things.. numStrings, instrument, etc.

  TBD: This should be removed. There is no reason to generate the fretboard in advance,
  just generate frets on the fly while displaying.
  '''

  fretBoard = {}

  strings = instrumentMap [instrument]['tuning']

  for string in range (1, len (strings) + 1):
    stringList = []
    rootNote = strings [string - 1]
    offset = instrumentMap [instrument]['fretOffset'][string - 1]
    for fret in range (offset, NUM_FRETS + 1):
      fretInfo = fretInfoGen (rootNote, fret, offset, key, spelling)
      stringList.append (fretInfo)

    fretBoard [string] = stringList

  fretBoard.update({
    'numStrings': len (strings),
    'instrument': instrument,
    'spelling': spelling,
    'fretOffset': instrumentMap [instrument]['fretOffset']
  })

  return fretBoard

def displayFretboard (fretboard, interval = False):
  numStrings = fretboard ['numStrings']

  print ("\n  ", end = "")
  for fret in range (0, NUM_FRETS + 1):
    print ("%2s   " % fret, end = "")
    if fret == 9: # formatting hack
      print (" ", end="")

  print ()
  for stringNum in range (1, numStrings + 1):
    string = fretboard [stringNum]

    if stringNum == 7 and fretboard ['instrument'] == 'Stick-4ths':
      print () # space between bass and treble strings

    print (string [0]['note'], " ", end = "", sep = "")
    print ("     " * fretboard ['fretOffset'][stringNum - 1], end = "")

    for fret in string:
      if fretboard ['fretOffset'][stringNum - 1] == fret ['fret']:
        fretChar = "x"
      else:
        fretChar = "|"

      if fret ['inSpelling']:
        if interval:
          value = fret ['interval']
        else:
          value = fret ['note']

        if len (value) == 1:
          value += "-"

        print ("-%s-%s" % (value,fretChar), end = "", sep='')
      else:
        print ("----%s" % fretChar, end = "")
    print ()

def displayInfo (instrument, key, spelling):
  os.system ('clear')

  fretboard = generateFretboard (instrument, key, spelling)

  print (fretboard ['instrument'], key, fretboard ['spelling'])
  displayFretboard (fretboard)
  displayFretboard (fretboard, True)
  print ()

  # help
  print ("i : Instruments: ", end="")
  for inst in instruments:
    print (inst, "", end = "")
  print ()
  print ("mr7[] : Spellings: ", end = "")
  for spel in spellings:
    print (spel, "", end = "")
  print ()
  print ("a..g -= : Key")
  print ("q : quit")

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

def runCli ():
  keyIx = 0
  instrumentIx = 0
  spellingIx = 0

  while True:
    displayInfo (instruments [instrumentIx], dispKeyList [keyIx], spellings [spellingIx])

    ch = getInput ()
    if ch == 'q':
      exit()
    elif ch == 'i':
      instrumentIx += 1
      instrumentIx %= len (instruments)
    elif ch == ']':
      spellingIx += 1
      spellingIx %= len (spellings)
    elif ch == '[':
      if spellingIx > 0:
        spellingIx -= 1
      else:
        spellingIx = len (spellings) - 1
    elif ch == '=':
      keyIx += 1
      keyIx %= len (dispKeyList)
    elif ch == '-':
      if (keyIx > 0):
        keyIx -= 1
      else:
        keyIx = len (dispKeyList) - 1
    elif ch == 'm':
      spellingIx = spellings.index ('M-Key')
    elif ch == 'r':
      spellingIx = spellings.index ('m-Key')
    elif ch == '7':
      spellingIx = spellings.index ('7')
    elif ch.upper() in dispKeyList:
      keyIx = dispKeyList.index (ch.upper())

class runGui ():
  '''
    Spellings and Keys will be clickable

    ------------------------------
        Title
    -----------------------------
    Spelling1 Spelling2 Spelling3
    -----------------------------
    A A# B C.....
    -----------------------------

    Fretboard1

    Fretboard2

    ------------------------------
  '''

  def handleInstrument (self, newInstrument):
    self.instrument = newInstrument
    self.displayInstruments (self.instrumentsFrame)
    self.displayFretboards (self.fretboardFrame)

  def handleSpelling (self, newSpelling):
    self.spelling = newSpelling
    self.displaySpellings (self.spellingsFrame)
    self.displayFretboards (self.fretboardFrame)

  def handleKey (self, newKey):
    self.key = newKey
    self.displayKeys (self.keysFrame)
    self.displayFretboards (self.fretboardFrame)

  def displayInstruments (self, frame):
    for widget in frame.winfo_children():
      widget.destroy()

    for inst in instruments:
      if inst == self.instrument:
        disfont = ("TkFixedFont", 14, "bold italic")
      else:
        disfont = ("TkFixedFont", 10, "")

      actionAndArg = partial (self.handleInstrument, inst)

      b = Button (frame, text = inst, font = disfont, command = actionAndArg)
      b.pack (side = LEFT)

  def displaySpellings (self, frame):
    for widget in frame.winfo_children():
      widget.destroy()

    for spelling in spellings:
      if spelling == self.spelling:
        disfont = ("TkFixedFont", 14, "bold italic")
      else:
        disfont = ("TkFixedFont", 10, "")

      actionAndArg = partial (self.handleSpelling, spelling)

      b = Button (frame, text = spelling, font = disfont, command = actionAndArg)
      b.pack (side = LEFT)

  def displayKeys (self, frame):
    for widget in frame.winfo_children():
      widget.destroy()

    for key in dispKeyList:
      if key == self.key:
        disfont = ("TkFixedFont", 14, "bold italic")
      else:
        disfont = ("TkFixedFont", 10, "")

      actionAndArg = partial (self.handleKey, key)

      b = Button (frame, text = key, font = disfont, command = actionAndArg)
      b.pack (side = LEFT)

  def displayFretboards (self, frame):

    dFont = tkFont.Font (family = 'Courier', size = 12)

    def generateFB (dispKey):

      for stringNum in range (1, numStrings + 1):
        string = fretboard [stringNum]
        dispLine = string [0]['root'] + " "
        if len (dispLine) == 2:
          dispLine += " "

        dispLine += ("   " * fretboard ['fretOffset'][stringNum - 1])

        if stringNum == 7 and self.instrument == 'Stick-4ths':
          s = Label (frame, text = '-', font = dFont)
          s.pack (side = TOP)

        for fret in string:
          if fretboard ['fretOffset'][stringNum - 1] == fret ['fret']:
            fretChar = "X-"
          else:
            fretChar = "|"

          if fret ['inSpelling']:
            value = fret [dispKey]
            if len (value) == 1:
              value += "-"
            dispLine += "%s%s" % (value, fretChar)
          else:
            dispLine += "--%s" % fretChar

        s = Label (frame, text = dispLine, font = dFont)
        s.pack (side = TOP, pady=0)

    for widget in frame.winfo_children():
      widget.destroy()

    fretboard = generateFretboard (self.instrument, self.key, self.spelling)

    dispLine = "%s: %s %s" % (self.instrument, self.key, self.spelling)
    s = Label (frame, text = dispLine)
    s.pack (side = TOP)

    numStrings = fretboard ['numStrings']

    dispLine = " "
    for fret in range (0, NUM_FRETS + 1):
      dispLine += (" %2s" % fret)
      if fret == 0:
        dispLine += " "

    s = Label (frame, text = dispLine, font = dFont)
    s.pack (side = TOP)

    generateFB ('note')
    s = Label (frame, text = "---")
    s.pack (side = TOP)
    generateFB ('interval')

  def __init__ (self):

    self.instrument = instruments [0]
    self.key = dispKeyList [0]
    self.spelling = spellings [0]

    root = Tk()
    root.title ("Chords")

    self.instrumentsFrame = Frame (root)
    self.spellingsFrame = Frame (root)
    self.keysFrame = Frame (root)
    self.fretboardFrame = Frame (root)

    self.instrumentsFrame.pack (side = TOP)
    self.keysFrame.pack (side = TOP)
    self.spellingsFrame.pack (side = TOP)
    self.fretboardFrame.pack (side = TOP)

    self.displayInstruments (self.instrumentsFrame)
    self.displaySpellings (self.spellingsFrame)
    self.displayKeys (self.keysFrame)
    self.displayFretboards (self.fretboardFrame)
    root.mainloop ()

if 'c' in sys.argv:
  runCli()
else:
  runGui()
