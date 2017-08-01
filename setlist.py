#!/usr/bin/python
from __future__ import print_function
import os, sys, glob, copy
'''
Convert a list of text files into a html page.

The purpose of this is to turn a direction of txt lyric files into a single html file.
'''

class Song (object):
  def __init__ (self, name, set = None):
    self.name = name
    self.set = set

songList = []
statusString = None
setListName = "default"
songIx = 1

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

def populateSongs ( ):
  global songIx
  songIx = 1
  songList = []
  re = "*.txt"

  matchList = glob.glob (re)
  for s in matchList:
    song = Song (s, None)
    songList.append (song)

  return songList

def displayUI ():
  os.system ('clear')
  global songIx, setListName
  print ("Setlist:", setListName)
  index = 0
  for s in songList:
    index += 1
    print ("%s%4s %-25s %s" % ("> " if index == songIx else "  ",
                               "?"  if not s.set else s.set,
                               s.name [:-4],
                               "< " if index == songIx else "  "), end = "")
    if index % 4 == 0:
      print ("")
  print ("")

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

def sortList ():
  global songList
  sList = []
  for set in (1, 2, 3, 4, None):
    for s in songList:
      if s.set == set:
        sList.append (s)
  songList = sList

songList = populateSongs()
displayUI()
while True:
  ch = getInput()
  if ch == "DOWN":
    songIx += 4
  elif ch == "RIGHT":
    songIx += 1
  elif ch == "UP":
    songIx -= 4
  elif ch == "LEFT":
    songIx -= 1
  elif songIx < 1:
    songIx = 1
  elif songIx > len (songList):
    songIx = len (songList)
  elif ch == 'q':
    exit()
  elif ch == '1':
    songList [songIx - 1].set = 1
  elif ch == '2':
    songList [songIx - 1].set = 2
  elif ch == '3':
    songList [songIx - 1].set = 3
  elif ch == '4':
    songList [songIx - 1].set = 4
  elif ch == ' ':
    songList [songIx - 1].set = None
  elif ch == 's':
    saveList()
  elif ch == 'o':
    sortList ()
  elif ch == 'r':
    setListName = raw_input ('Enter set list name:')


  displayUI()
