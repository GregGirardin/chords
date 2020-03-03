#!/usr/bin/python

'''
Chords
Greg Girardin
girardin1972@hotmail.com
'''

from __future__ import print_function
import os, sys
from functools import partial
if sys.version_info.major == 2:
  from Tkinter import *
  import tkFont
else:
  from tkinter import *
  import tkinter.font as tkFont

instrumentMap = {
  'Mandolin' :   { "t": ( "E", "A", "D", "G" ),           "f" : ( 0, 0, 0, 0 ) },
  'Guitar' :     { "t": ( "E", "B", "G", "D", "A", "E" ), "f" : ( 0, 0, 0, 0, 0, 0 ) },
  'Dropped D' :  { "t": ( "E", "B", "G", "D", "A", "D" ), "f" : ( 0, 0, 0, 0, 0, 0 ) },
  'Bass' :       { "t": ( "G", "D", "A", "E" ),           "f" : ( 0, 0, 0, 0 ) },
  '5StringBass' :{ "t": ( "G", "D", "A", "E", "B" ),      "f" : ( 0, 0, 0, 0, 0 ) },
  'Uke' :        { "t": ( "A", "E", "C", "G" ),           "f" : ( 0, 0, 0, 0 ) },
  'Stick' :      { "t": ( "D", "A", "E", "B", "F#", "C", "G", "D", "A", "E" ), "f":
    ( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ) }, # Classic tuning
  'Stick-4ths':  { "t": ("C", "G", "D", "A", "E", "B", "E", "A", "D", "G", "C", "F" ), "f":
    ( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ) },
  'Banjo' :      { "t": ( "D", "B", "G", "D", "G" ),      "f" : ( 0, 0, 0, 0, 5 ) } }

# Pick the instruments you care about
instruments = ( 'Guitar', 'Bass', 'Dropped D', 'Uke', 'Mandolin', 'Banjo', '5StringBass', 'Stick', 'Stick-4ths' )

intervals = { 0 : ( 'R', 'b2', '2', 'b3', '3',  '4', 'b5', '5',  'b6',  '6', 'b7', '7' ),
              1 : ( 'R', 'b9', '9', 'b3', '3', '11', 'b5', '5', 'b13', '13', 'b7', '7' ) }

# display with a #/b if that's how we'd display the major key.
dispKeyList    = ( 'C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B' )
keyListSharps  = ( 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B' )
keyListFlats   = ( 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B' )
bKeys          = ( 'F', 'Bb', 'Eb','Ab', 'Db' ) # keys to be displayed as having flats

# spellingMap is a dictionary of names for the spelling and a tuple of intervals members.
# if you add an entry, also add it to spellings tuple below.
spellingMap = { "major" :    ( 'R',  '3',  '5' ),
                "minor" :    ( 'R', 'b3',  '5' ),
                "sus2" :     ( 'R',  '2',  '5' ),
                "sus4" :     ( 'R',  '4',  '5' ),
                "6" :        ( 'R',  '3',  '5',  '6' ),
                "m6" :       ( 'R', 'b3',  '5',  '6' ),
                "7" :        ( 'R',  '3',  '5', 'b7' ),
                "m7" :       ( 'R', 'b3',  '5', 'b7' ),
                "M7" :       ( 'R',  '3',  '5',  '7' ),
                "9" :        ( 'R',  '3',  '5', 'b7',  '9' ),
                "m9" :       ( 'R', 'b3',  '5', 'b7',  '9' ),
                "M9" :       ( 'R',  '3',  '5',  '7',  '9' ),
                "11" :       ( 'R',  '3',  '5', 'b7',  '9', '11' ),
                "m11" :      ( 'R', 'b3',  '5', 'b7',  '9', '11' ),
                "M11" :      ( 'R',  '3',  '5',  '7',  '9', '11' ),
                "13" :       ( 'R',  '3',  '5', 'b7',  '9', '11', '13' ),
                "m13" :      ( 'R', 'b3',  '5', 'b7',  '9', '11', '13' ),
                "M13" :      ( 'R',  '3',  '5',  '7',  '9', '11', '13' ),
                "dim" :      ( 'R', 'b3', 'b5',  '6' ),
                "m7-5" :     ( 'R', 'b3', 'b5', 'b7' ),
                "Maj-Key" :  ( 'R',  '2',  '3',  '4',  '5',  '6',  '7' ),
                "Min-Key" :  ( 'R',  '2', 'b3',  '4',  '5', 'b6', 'b7' ),
                "Pent-Min" : ( 'R', 'b3',  '4',  '5', 'b7' ),
                "Pent-Maj" : ( 'R',  '2',  '3',  '5',  '6' ),
                "mBlues" :   ( 'R', 'b3',  '4', 'b5',  '5', 'b7' ),
                "MBlues" :   ( 'R',  '2', 'b3',  '3',  '5',  '6' ),
                # Harmonizations
                "I":       ('R', '3', '5'),
                "ii":      ('2', '4', '6'),
                "iii":     ('3', '5', '7'),
                "IV":      ('4', '6', 'R'),
                "V":       ('5', '7', '2'),
                "vi":      ('6', 'R', '3'),
                "vii dim": ('7', '2', '4'),
                "i":       ('1', 'b3', '5'),
                "ii dim":  ('2', '4', 'b6'),
                "bIII":    ('b3', '5', 'b7'),
                "iv":      ('4', 'b6', 'R'),
                "v":       ('5', 'b7', '2'),
                "bVI":     ('b6', 'R', 'b3'),
                "bVII":    ('b7', '2', '4'),
                }

# Pick the spellings (keys in spellingMap) you care about.
spellings = ( 'major', 'minor', 'sus2',  'sus4', '6', 'm6', '7',  'm7',  'M7',
              '9',  'm9',  'M9', '11', 'm11', 'M11', '13', 'm13', 'M13', 'dim', 'm7-5',
              'Maj-Key', 'Min-Key', 'Pent-Min', 'Pent-Maj', 'mBlues', 'MBlues' )

# spellings that can be harmonized
harmonization = {
                  "Maj-Key" : ( "I", "ii", "iii", "IV", "V", "vi", "vii dim" ),
                  "Min-Key" : ( "i", "ii dim", "bIII", "iv", "v", "bVI", "bVII" ),
                }

extChords = ( '9', 'm9', 'M9','11', 'm11', 'M11', '13', 'm13', 'M13' )
extIntervals = ( '9', '11', '13' )
minorSpellings = ( 'm', 'm7', 'm9', 'm11', 'm13', 'm-Key' )
num_frets = 15

disFont = { 0 : ( "TkFixedFont", 18, "bold italic" ),
            1 : ( "TkFixedFont", 14, "" ) }

class runGui():

  def showWithSharps( self, key, spelling ):
    # return True if we should show this key/spelling as having sharps (vs flats)

    def relMajor( key ):
      # input is a minor key, returns the relative major key
      index = ( dispKeyList.index( key ) + 3 ) % 12
      key = dispKeyList[ index ]
      return key

    if spelling in ( 'mBlues', 'MBlues' ):  # Blues is always flats
      return False

    if spelling in minorSpellings:
      key = relMajor( key )

    return key not in bKeys

  def calcNote( self, root, fret ):
    rootNum = ( dispKeyList.index( root ) + fret ) % 12
    return dispKeyList[ rootNum ]

  def calcInterval( self, note, key ):
    noteNum = dispKeyList.index( note ) + 12  # C = 12, C# = 13, etc
    keyNum = dispKeyList.index( key )  # C = 0, C# = 1
    intNum = ( noteNum - keyNum ) % 12  # (if C) C = 0, C# = 1
    return intNum

  def fretInfoGen( self, root, fret, fretOffset, key, spelling ):
    '''
    Generate a dictionary entry about the given fret.
    root is the string's fretOffset fret note. Usually fret 0 (open).
    fret is the fret number relative to a zero offset string note is the text of the note
    '''
    assert fret >= fretOffset, "Fret below fret offset."

    fretInfo = { 'root': root, 'fret': fret, 'note': self.calcNote( root, fret - fretOffset ) }
    interval = self.calcInterval( fretInfo[ 'note' ], key )
    x = 1 if spelling in extChords else 0
    fretInfo[ 'interval' ] = intervals[ x ][ interval ]
    fretInfo[ 'inSpelling' ] = intervals[ x ][ interval ] in spellingMap[ spelling ]

    # convert note for display
    curKeyList = keyListSharps if self.showWithSharps( key, spelling ) else keyListFlats
    fretInfo[ 'note' ] = curKeyList[ dispKeyList.index( fretInfo[ 'note' ] ) ]

    return fretInfo

  def generateFretboard( self, inst, key, spelling ):
    '''
    Returns a dictionary with everything we care about
    strings are keyed by string number (1 - N) and contain a list of dictionaries for each fret
    There are also some other 'global' kinda things.. numStrings, instrument, etc.

    This could be removed. There is no reason to generate the fretboard in advance,
    just generate frets on the fly while displaying.
    '''

    strings = instrumentMap[ inst ][ 't' ]

    fretBoard = { 'numStrings': len( strings ),
                  'instrument': inst,
                  'spelling':   spelling,
                  'fretOffset': instrumentMap[ inst ][ 'f' ] }

    for string in range( 1, len( strings ) + 1 ):
      stringList = []
      rootNote = strings[ string - 1 ]
      offset = instrumentMap[ inst ][ 'f' ][ string - 1 ]

      for fret in range( offset, num_frets + 1 ):
        fretInfo = self.fretInfoGen( rootNote, fret, offset, key, spelling )
        stringList.append( fretInfo )

      fretBoard[ string ] = stringList

    return fretBoard

  def displayFretboards( self, frame ):
    dFont = tkFont.Font( family='Courier', size=16 )

    def generateFB( dispKey ):
      for stringNum in range( 1, numStrings + 1 ):
        string = fretboard[ stringNum ]
        dispLine = string[ 0 ][ 'root' ] + " "
        if len( dispLine ) == 2:
          dispLine += " "

        dispLine += ( "   " * fretboard[ 'fretOffset' ][ stringNum - 1 ] )

        for fret in string:
          if fretboard[ 'fretOffset' ][ stringNum - 1 ] == fret[ 'fret' ]:
            fretChar = u'\u258c' + u'\u2015'
          else:
            fretChar = "|" # u'\u2502'

          d = True
          if fret[ 'interval' ] in extIntervals and stringNum > ( numStrings / 2 ):
            d = False

          if fret[ 'inSpelling' ] and d:
            value = fret[ dispKey ]
            if( dispKey == 'note' and self.fretsNotes ) or value == 'R':
              value = u'\u25cf'
            if len( value ) == 1:
              value += "-"
            dispLine += "%s%s" % ( value, fretChar )
          else:
            dispLine += u'\u2015' + u'\u2015' + "%s" % fretChar

        s = Label( frame, text=dispLine, font=dFont )
        s.pack( side=TOP, pady=0 )

        if( ( stringNum == 5 and self.instrument == instruments[ 7 ] ) or
            ( stringNum == 6 and self.instrument == instruments[ 8 ] ) ):
          s = Label( frame, text="", font=dFont )
          s.pack( side=TOP, pady=0 )

    for widget in frame.winfo_children():
      widget.destroy()

    fretboard = self.generateFretboard( self.instrument, self.key, self.spelling )
    numStrings = fretboard[ 'numStrings' ]

    dispLine = " "
    for fret in range( 0, num_frets + 1 ):
      dispLine += ( " %2s" % fret )
      if fret == 0:
        dispLine += " "

    s = Label( frame, text=dispLine, font=dFont )
    s.pack( side=TOP )

    generateFB( 'note' )
    s = Label( frame, text="-------------------------------------------" )
    s.pack( side=TOP )
    generateFB( 'interval' )

  def instrumentChange( self, *args ):
    self.instrument = self.inst.get()
    self.displayFretboards( self.fretboardFrame )

  def keyChange( self, *args ):
    self.key = self.keysVar.get()
    self.displayFretboards( self.fretboardFrame )

  def spellingChange( self, *args ):
    self.spelling = self.spellingVar.get()
    self.displayFretboards( self.fretboardFrame )

  def fnToggle( self ):
    self.fretsNotes = not self.fretsNotes
    self.displayFretboards( self.fretboardFrame )

  def fretNumToggle( self ):
    global num_frets
    num_frets = 15 if num_frets == 24 else 24
    self.displayFretboards( self.fretboardFrame )

  def initMainframe( self ):
    self.inst = StringVar()
    self.inst.set( instruments[ 0 ] )
    self.inst.trace( 'w', self.instrumentChange )

    self.keysVar = StringVar()
    self.keysVar.set( dispKeyList[ 0 ] )
    self.keysVar.trace( 'w', self.keyChange )

    self.spellingVar = StringVar()
    self.spellingVar.set( spellings[ 0 ] )
    self.spellingVar.trace( 'w', self.spellingChange )

  def displayMainframe( self ):
    for widget in self.mainFrame.winfo_children():
      widget.destroy()

    self.instMenu = OptionMenu( self.mainFrame, self.inst, *instruments )
    self.instMenu.pack( side=LEFT )

    self.keysMenu = OptionMenu( self.mainFrame, self.keysVar, *dispKeyList )
    self.keysMenu.pack( side=LEFT )

    self.spellingMenu = OptionMenu( self.mainFrame, self.spellingVar, *spellings )
    self.spellingMenu.pack( side=LEFT )

    self.fn = Button( self.mainFrame, text="Notes/Frets", font=disFont[ 1 ], command=self.fnToggle )
    self.fn.pack( side=LEFT )
    self.fb = Button( self.mainFrame, text="15/24", font=disFont[ 1 ], command=self.fretNumToggle )
    self.fb.pack( side=LEFT )

  def __init__( self ):
    self.instrument = instruments[ 0 ]
    self.key = dispKeyList[ 0 ]
    self.spelling = spellings[ 0 ]
    self.fretsNotes = False

    root = Tk()
    root.title( "Chords" )

    self.mainFrame = Frame( root )
    self.mainFrame.pack( side=TOP )

    self.initMainframe()
    self.displayMainframe()

    self.fretsFrame = Frame( root )
    self.fretsFrame.pack( side=TOP )
    self.fretboardFrame = Frame( root )
    self.fretboardFrame.pack( side=TOP )
    self.displayFretboards( self.fretboardFrame )

    root.mainloop()

runGui()