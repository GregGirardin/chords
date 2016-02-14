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

# dictionary keyed by instrument name, followed by tuning (high to low)
instrumentMap = \
  {
  'Mandolin':   ("E", "A", "D", "G"),
  'Guitar':     ("E", "B", "G", "D", "A", "E"),
  'Bass':       ("G", "D", "A", "E"),
  'Stick-4ths': ("C", "G", "D", "A", "E", "B",
                 "E", "A", "D", "G", "C" , "F")
  }
instruments = ('Mandolin', 'Guitar', 'Bass', 'Stick-4ths') # instrumentMap.keys() doesn't guarantee order

intervalList = ['R', 'b2', '2', 'b3', '3', '4', 'b5', '5', 'b6', '6', 'b7', '7', '8', 'b9', '9']
# display with a #/b if that's how we'd display the major key.
dispKeyList    = ('C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'A#', 'B')
keyListSharps  = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
keyListFlats   = ('C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B')
bKeys = ('F', 'Db', 'Eb', 'Ab', 'Db') # (Major) keys to be displayed as having flats, (vs sharps)

# spellingMap is a dictionary of names for the spelling and a tuple of intervalList members.
# if you add an entry, also add it to spellings tuple below.
spellingMap = \
  {
  "M":        ('R',  '3',  '5'),
  "m":        ('R', 'b3',  '5'),
  "7":        ('R',  '3',  '5', 'b7'),
  "m7":       ('R', 'b3',  '5', 'b7'),
  "M7":       ('R', 'b3',  '5', '7'),
  "2":        ('R',  '2',  '5'),
  "4":        ('R',  '4',  '5'),
  "dim":      ('R', 'b3',  'b5', '6'),
  "M-Key":    ('R',  '2',  '3', '4', '5',  '6',  '7'),
  "m-Key":    ('R',  '2', 'b3', '4', '5', 'b6', 'b7')
  }
spellings = ('M', 'm', '7', 'm7', 'M7', '2', '4', 'dim', 'M-Key', 'm-Key')
minorSpellings = ('m', 'm7', 'm-Key')
NUM_FRETS = 15

def relMajor (key):
  index = dispKeyList.index (key)
  index += 3
  index %= 12
  key = dispKeyList [index]
  return key

def showWithSharps (key, spelling):
  if spelling in minorSpellings:
    key = relMajor (key)

  if key in bKeys:
    return False
  return True

def calcNote (root, fret, keyList):
  rootNum = keyList.index (root)
  rootNum += fret
  rootNum %= 12
  return keyList [rootNum]

def calcInterval (note, key, keyList):
  noteNum = keyList.index (note) + 12 # C = 12, C# = 13, etc
  keyNum = keyList.index (key)        # C =  0, C# =  1
  intNum = (noteNum - keyNum) % 12    # (if C) C = 0, C# = 1
  return intNum

def fretInfoGen (root, fret, key, spelling):
  '''
  Generate a dictionary entry about the given fret.
  root is the string's "open" note
  '''
  fretInfo = {}
  fretInfo ['root'] = root
  fretInfo ['fret'] = fret

  if showWithSharps (key, spelling):
    curKeyList = keyListSharps
  else:
    curKeyList = keyListFlats

  key = curKeyList [dispKeyList.index (key)]

  fretInfo ['note'] = calcNote (root, fret, curKeyList)
  interval = calcInterval (fretInfo ['note'], key, curKeyList)
  fretInfo ['interval'] = intervalList [interval]
  if intervalList [interval] in spellingMap [spelling]:
    fretInfo ['highlight'] = True
  else:
    fretInfo ['highlight'] = False

  return fretInfo

def generateFretboard (instrument, key, spelling):
  '''
  Returns a dictionary with everything we care about
  strings are keyed by string number (1 - N) and contain a list of dictionaries for each fret
  There are also some other 'global' kinda things.. numStrings, instrument, etc.

  TBD: This should be removed. There is no reason to generate the fretboard in advance,
  just generate frets on the fly why displaying.
  '''

  fretBoard = {}

  strings = instrumentMap [instrument] # tuple of strings

  for string in range (1, len (strings) + 1):
    stringList = []
    rootNote = strings [string - 1]
    for fret in range (0, NUM_FRETS + 1):
      fretInfo = fretInfoGen (rootNote, fret, key, spelling)
      stringList.append (fretInfo)

    fretBoard [string] = stringList

  fretBoard ['numStrings'] = len (strings)
  fretBoard ['instrument'] = instrument
  fretBoard ['spelling'] = spelling

  return fretBoard

def displayFretboard (fretboard, interval = False):
  """
   Chord C-Mag
         1    2    3    4    5    6    7    8    9   10   11   12...
  E |-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|
  B |-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|
  G |-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|
  D |-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|
  A |-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|
  E |-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|-XX-|
  """

  numStrings = fretboard ['numStrings']

  print ("\n  ", end="")
  for fret in range (0, NUM_FRETS + 1):
    print ("%2s   " % fret, end="")
    if (fret == 9): # formatting hack
      print (" ", end="")

  print ()
  for stringNum in range (1, numStrings + 1):
    string = fretboard [stringNum]

    if (stringNum == 7) and (fretboard ['instrument'] == 'Stick-4ths'):
      print () # space between bass and treble strings

    print (string [0]['note'], " ", end = "", sep = "")

    for fret in string:
      if fret ['highlight'] == True:
        if interval == True:
          value = fret ['interval']
        else:
          value = fret ['note']
        if (len (value) == 1):
          value = value + "-"
        print ("-%s-|" % value, end = "", sep='')
      else:
        print ("----|", end = "")
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
                termios. IGNCR | termios.ICRNL | termios.IXON )
  attrs[1] &= ~termios.OPOST
  attrs[2] &= ~(termios.CSIZE | termios. PARENB)
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

  while (True):
    displayInfo (instruments [instrumentIx], dispKeyList [keyIx], spellings [spellingIx])

    ch = getInput ()
    if (ch == 'q'):
      exit()
    elif (ch == 'i'):
      instrumentIx += 1
      instrumentIx %= len (instruments)
    elif (ch == ']'):
      spellingIx += 1
      spellingIx %= len (spellings)
    elif (ch == '['):
      if (spellingIx > 0):
        spellingIx -= 1
      else:
        spellingIx = len (spellings) - 1
    elif (ch == '='):
      keyIx += 1
      keyIx %= len (dispKeyList)
    elif (ch == '-'):
      if (keyIx > 0):
        keyIx -= 1
      else:
        keyIx = len (dispKeyList) - 1
    elif (ch == 'm'):
      spellingIx = spellings.index ('M-Key')
    elif (ch == 'r'):
      spellingIx = spellings.index ('m-Key')
    elif (ch == '7'):
      spellingIx = spellings.index ('7')
    elif (ch.upper() in dispKeyList):
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
      if (spelling == self.spelling):
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
      if (key == self.key):
        disfont = ("TkFixedFont", 14, "bold italic")
      else:
        disfont = ("TkFixedFont", 10, "")

      actionAndArg = partial (self.handleKey, key)

      b = Button (frame, text = key, font = disfont, command = actionAndArg)
      b.pack (side = LEFT)

  def displayFretboards (self, frame):

    for widget in frame.winfo_children():
      widget.destroy()

    fretboard = generateFretboard (self.instrument, self.key, self.spelling)

    # s = Label (frame, text = "---")
    # s.pack (side = TOP)

    dispLine = "%s: %s %s" % (self.instrument, self.key, self.spelling)
    s = Label (frame, text = dispLine)
    s.pack (side = TOP)

    numStrings = fretboard ['numStrings']

    dispLine = " "
    for fret in range (0, NUM_FRETS + 1):
      dispLine += (" %2s" % fret)

    s = Label (frame, text = dispLine, font = "TkFixedFont")
    s.pack (side = TOP)

    def generateKB (key):

      dFont = tkFont.Font (family = 'Courier', size = 12)

      for stringNum in range (1, numStrings + 1):
        string = fretboard [stringNum]
        dispLine = string [0]['root'] + " "
        if len (dispLine) == 2:
          dispLine += " "

        if (stringNum == 7) and self.instrument == 'Stick-4ths':
          s = Label (frame, text = '-', font = dFont)
          s.pack (side = TOP)

        for fret in string:
          if fret ['highlight'] == True:
            value = fret [key]
            if (len (value) == 1):
              value += "-"
            dispLine += "%s|" % value
          else:
            dispLine += "--|"

        #s = Label (frame, text = dispLine, font = "TkFixedFont")
        s = Label (frame, text = dispLine, font = dFont)
        s.pack (side = TOP, pady=0)

    generateKB ('note')
    s = Label (frame, text = "---")
    s.pack (side = TOP)
    generateKB ('interval')

  def __init__ (self):

    self.instrument = instruments [0]
    self.key = dispKeyList [0]
    self.spelling = spellings [0]

    root = Tk()
    root.title ("Chord Utility")

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
  runGui ()