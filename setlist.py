#!/usr/bin/python
from __future__ import print_function
import os, sys, glob, copy
'''
Convert a list of text files into a html page.
'''
class bcolors:
  HEADER = '\033[95m'
  BLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

class Set (object):
  def __init__(self, name = None):
    self.name = name
    self.songList = []

class Song (object):
  def __init__ (self, name):
    self.name = name # file name

unassignedSetName = "Unassigned"
statusString = None
setLists = []
showName = "Set List"
currentSet = 0 # these represent the 'cursor'
currentSong = 0

SONG_COLUMNS = 4

# input modes
CURSOR_MODE_NORMAL = 0
CURSOR_MODE_MOVE = 1

inputMode = CURSOR_MODE_NORMAL

unassignedSet = Set (unassignedSetName)
setLists.append (unassignedSet)

def findSetlist ():
  global statusString, selectedfileIx
  re = "./*" + setListExt

  matchList = glob.glob (re)

  if not matchList:
    statusString = "No files."
    return None

  if selectedfileIx >= len (matchList):
    selectedfileIx = len (matchList) - 1

  while True:
    os.system ('clear')
    print ("Use arrow keys to select or exit.\n")
    index = 0
    for s in matchList:
      line = "  "
      if index == selectedfileIx:
        line = "> "
      line += s [2:].split (".")[0]
      index += 1

      print (line)

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

def getSetByName (name):
  for s in setLists:
    if s.name == name:
      return s
  return None

def getLocalSongs ():
  songList = []
  re = "*.txt"
  matchList = glob.glob (re)
  for s in matchList:
    song = Song (s)
    songList.append (song)

  return songList

def displayUI ():
  os.system ('clear')
  global songIx, showName, setLists
  print ("Setlist:", showName)

  setNumber = 0

  for l in setLists:
    if setNumber == currentSet and not len (setLists [currentSet].songList):
      print (bcolors.BOLD, end = "") # This set is empty, highlight the name
    print ("Set: %s" % (l.name if l.name else setNumber + 1))
    if setNumber == currentSet:
      print (bcolors.ENDC, end = "")
    songIx = 0
    for s in l.songList:
      cursor = True if setNumber == currentSet and songIx == currentSong else False
      if cursor:
        print (bcolors.BOLD if inputMode == CURSOR_MODE_NORMAL else bcolors.BLUE, end="" )
      print ("%-24s " % (s.name [:-4]), end = "")
      if cursor:
        print (bcolors.ENDC, end = "")
      if (songIx + 1) % SONG_COLUMNS == 0:
        print ("")
      songIx += 1
    print ("")
    setNumber += 1

  print (currentSet, currentSong)

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

def saveList():
  pass

s = getSetByName (unassignedSetName)
s.songList = getLocalSongs()

def songFwd (count):
  global currentSong, currentSet

  if (currentSet == len (setLists) - 1 and currentSong == len (setLists [currentSet].songList) - 1):
    return

  if inputMode == CURSOR_MODE_MOVE and currentSong is not None:
    temp = setLists [currentSet].songList [currentSong]
    del (setLists [currentSet].songList [currentSong])

    if currentSong == len (setLists [currentSet].songList):
      currentSet += 1
      currentSong = 0
    else:
      l = len (setLists [currentSet].songList)
      currentSong += count
      if currentSong >= l: # at the end of the set
        currentSong = l
    setLists [currentSet].songList.insert (currentSong, temp)
  else: # Normal mode (or on empty set)
    if currentSong == None:
      if currentSet < len (setLists):
        currentSet += 1
        if len (setLists [currentSet].songList):
          currentSong = 0
    else:
      l = len (setLists [currentSet].songList)
      if currentSong == l - 1: # at the end of the set
        if currentSet < len (setLists):
          currentSet += 1
          currentSong = 0
      elif currentSong + count < l:
        currentSong += count
      else:
        currentSong = l - 1

def songBack (count):
  global currentSong, currentSet

  if currentSet == 0 and (currentSong == 0 or currentSong == None):
    return

  if inputMode == CURSOR_MODE_MOVE and currentSong is not None:
    temp = setLists [currentSet].songList [currentSong]
    del (setLists [currentSet].songList [currentSong])

    if currentSong == 0:
      currentSet -= 1
      currentSong = len (setLists [currentSet].songList)
    else:
      currentSong -= count
      if currentSong < 0:
        currentSong = 0
    setLists [currentSet].songList.insert (currentSong, temp)
  else:
    if currentSong == None or currentSong == 0:
      if currentSet > 0:
        currentSet -= 1
        l = len (setLists [currentSet].songList)
        currentSong = l - 1 if l else None
    elif currentSong > count:
      currentSong -= count
    else:
      currentSong = 0

def newSet():
  global currentSet, setLists
  newSet = Set()
  setLists.insert (currentSet, newSet)
  currentSet += 1

def deleteSet():
  global currentSet, currentSong
  # move all songs to unassigned
  l = len (setLists)
  if l > 1 and currentSet < l - 1:
    u = getSetByName (unassignedSetName).songList
    for s in setLists [currentSet].songList:
      u.append (s)
    del setLists [currentSet]
    l = len( setLists[ currentSet ].songList )
    currentSong = 0 if l else None

def toggleMode ():
  global inputMode

  inputMode += 1
  if inputMode > CURSOR_MODE_MOVE:
    inputMode = 0

displayUI()
while True:
  ch = getInput()
  if ch == "DOWN":
    songFwd (SONG_COLUMNS)
  elif ch == "RIGHT":
    songFwd (1)
  elif ch == "UP":
    songBack (SONG_COLUMNS)
  elif ch == "LEFT":
    songBack (1)
  elif ch == 'q':
    exit()
  elif ch == 's':
    saveList()
  elif ch == 'r':
    setListName = raw_input ('Enter set list name:')
  elif ch == 'm':
    toggleMode()
  elif ch == 'n':
    newSet ()
  elif ch == 'd':
    deleteSet()


  displayUI()
