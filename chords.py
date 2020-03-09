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

instrumentMap =   {
  'Mandolin' :    { "t" : ( "E", "A", "D", "G" ),           "f" : ( 0, 0, 0, 0 ) },
  'Guitar' :      { "t" : ( "E", "B", "G", "D", "A", "E" ), "f" : ( 0, 0, 0, 0, 0, 0 ) },
  'Dropped D' :   { "t" : ( "E", "B", "G", "D", "A", "D" ), "f" : ( 0, 0, 0, 0, 0, 0 ) },
  'Bass' :        { "t" : ( "G", "D", "A", "E" ),           "f" : ( 0, 0, 0, 0 ) },
  '5StringBass' : { "t" : ( "G", "D", "A", "E", "B" ),      "f" : ( 0, 0, 0, 0, 0 ) },
  'Uke' :         { "t" : ( "A", "E", "C", "G" ),           "f" : ( 0, 0, 0, 0 ) },
  'Stick' :       { "t" : ( "D", "A", "E", "B", "F#", "C", "G", "D", "A", "E" ), "f" : ( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ) }, # Classic tuning
  'Stick-4ths':   { "t" : ("C", "G", "D", "A", "E", "B", "E", "A", "D", "G", "C", "F" ), "f" : ( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ) },
  'Banjo' :       { "t" : ( "D", "B", "G", "D", "G" ),      "f" : ( 0, 0, 0, 0, 5 ) }
  }

# Pick the instruments you care about
instruments = ( 'Guitar', 'Bass', 'Dropped D', 'Uke', 'Mandolin', 'Banjo', '5StringBass', 'Stick', 'Stick-4ths' )

intervals = { 0 : ( 'R', 'b2', '2', 'b3', '3',  '4', 'b5', '5',  'b6',  '6', 'b7', '7' ),
              1 : ( 'R', 'b9', '9', 'b3', '3', '11', 'b5', '5', 'b13', '13', 'b7', '7' ),
              2 : ( 'R', 'b2', '2', 'b3', '3',  '4', '#4', '5',  'b6',  '6', 'b7', '7' ) }

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
                "Ionian" :   ( 'R',  '2',  '3',  '4',  '5',  '6',  '7' ),
                "Dorian" :   ( 'R',  '2', 'b3',  '4',  '5',  '6', 'b7' ),
                "Phrygian" : ( 'R', 'b2', 'b3',  '4',  '5', 'b6', 'b7' ),
                "Lydian" :   ( 'R',  '2',  '3', '#4',  '5',  '6',  '7' ),
                "Mixolydian" :('R',  '2',  '3',  '4',  '5',  '6', 'b7' ),
                "Aeolian" :  ( 'R',  '2', 'b3',  '4',  '5', 'b6', 'b7' ),
                "Locrian" :  ( 'R', 'b2', 'b3',  '4', 'b5', 'b6', 'b7' ),
                "Melodic" :  ( 'R',  '2', 'b3',  '4',  '5', '6', '7' ),
                "Harmonic" : ( 'R',  '2', 'b3',  '4',  '5', 'b6', '7' ),
                "Pent-Min" : ( 'R', 'b3',  '4',  '5', 'b7' ),
                "Pent-Maj" : ( 'R',  '2',  '3',  '5',  '6' ),
                "mBlues" :   ( 'R', 'b3',  '4', 'b5',  '5', 'b7' ),
                "MBlues" :   ( 'R',  '2', 'b3',  '3',  '5',  '6' ),
                }

# Pick the spellings (keys in spellingMap) you care about.
spellings = ( 'major', 'minor', 'sus2', 'sus4', '6', 'm6', '7', 'm7', 'M7',
              '9', 'm9', 'M9', '11', 'm11', 'M11', '13', 'm13', 'M13', 'dim', 'm7-5',
              'Ionian', 'Dorian', 'Phrygian', 'Lydian', 'Mixolydian',
              'Aeolian', 'Locrian', 'Melodic', 'Harmonic',
              'Pent-Min', 'Pent-Maj', 'mBlues', 'MBlues' )

extChords = ( '9', 'm9', 'M9', '11', 'm11', 'M11', '13', 'm13', 'M13' )
extIntervals = ( '9', '11', '13' )
minorSpellings = ( 'm', 'm7', 'm9', 'm11', 'm13', 'm-Key', 'Aeolian' )
num_frets = 24

disFont = { 0 : ( "TkFixedFont", 18, "bold italic" ), 1 : ( "TkFixedFont", 14, "" ) }

class runGui():

  def showWithSharps( self, key, spelling ):
    # return True if we should show this key/spelling as having sharps (vs flats)

    def relMajor( key, off=3 ):
      # input is a minor key, returns the relative major key
      index = ( dispKeyList.index( key ) + off ) % 12
      key = dispKeyList[ index ]
      return key

    if spelling in( 'mBlues', 'MBlues' ):  # Blues is always flats
      return False

    if spelling == "Dorian":
      key = relMajor( key, 10 )
    elif spelling == "Phrygian":
      key = relMajor( key, 8 )
    elif spelling == "Lydian":
      key = relMajor( key, 7 )
    elif spelling == "Mixolydian":
      key = relMajor( key, 5 )
    elif spelling == "Locrian":
      key = relMajor( key, 1 )
    elif spelling in minorSpellings:
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

  def fretInfoGen( self, root, fret, fretOffset ):
    '''
    Generate a dictionary entry about the given fret.
    root is the string's fretOffset fret note. Usually fret 0 (open).
    fret is the fret number relative to a zero offset string note is the text of the note
    '''
    assert fret >= fretOffset, "Fret below fret offset."

    fretInfo = { 'root' : root,
                 'fret' : fret,
                 'note' : self.calcNote( root, fret - fretOffset ) }
    interval = self.calcInterval( fretInfo[ 'note' ], self.key )
    OLinterval = self.calcInterval( fretInfo[ 'note' ], self.OLkey )
    if self.spelling in extChords:
      x = 1
    elif self.spelling == 'Lydian':
      x = 2
    else:
      x = 0

    fretInfo[ 'interval' ] = intervals[ x ][ interval ]
    fretInfo[ 'inSpelling' ] = intervals[ x ][ interval ] in spellingMap[ self.spelling ]
    fretInfo[ 'inOLSpelling' ] = intervals[ x ][ OLinterval ] in spellingMap[ self.OLspelling ]

    # convert note for display
    curKeyList = keyListSharps if self.showWithSharps( self.key, self.spelling ) else keyListFlats
    fretInfo[ 'note' ] = curKeyList[ dispKeyList.index( fretInfo[ 'note' ] ) ]

    return fretInfo

  def generateFretboard( self ):
    '''
    Returns a dictionary with everything we care about
    strings are keyed by string number (1 - N) and contain a list of dictionaries for each fret
    There are also some other 'global' kinda things.. numStrings, instrument, etc.

    This could be removed. There is no reason to generate the fretboard in advance,
    just generate frets on the fly while displaying.
    '''

    strings = instrumentMap[ self.instrument ][ 't' ]

    fretBoard = { 'numStrings' : len( strings ),
                  'instrument' : self.instrument,
                  'spelling'   : self.spelling,
                  'fretOffset' : instrumentMap[ self.instrument ][ 'f' ] }

    for string in range( 1, len( strings ) + 1 ):
      stringList = []
      rootNote = strings[ string - 1 ]
      offset = instrumentMap[ self.instrument ][ 'f' ][ string - 1 ]

      for fret in range( offset, num_frets + 1 ):
        fretInfo = self.fretInfoGen( rootNote, fret, offset )
        stringList.append( fretInfo )

      fretBoard[ string ] = stringList

    return fretBoard

  def displayFretboards( self ):

    fretboard = self.generateFretboard()
    numStrings = fretboard[ 'numStrings' ]

    LEFT_BORDER = 30
    STR_SPC = 20
    FRET_SPACING = 30
    FRET_NUM_VERT_OFFSET = 20

    FRET1_TOP = FRET_NUM_VERT_OFFSET + 20
    FRET1_BOTTOM = FRET1_TOP + ( numStrings - 1 ) * STR_SPC

    FRET2_TOP = FRET1_BOTTOM + 40
    FRET2_BOTTOM = FRET2_TOP + ( numStrings - 1 ) * STR_SPC

    STRING_LEFT = LEFT_BORDER + 10
    STRING_RIGHT = STRING_LEFT + ( num_frets + 1 ) * FRET_SPACING

    HIDE_RAD = 9 # Hide radius

    self.canvas.delete( ALL )

    # Draw fret numbers and frets
    for fret in range( 0, num_frets + 1 ):
      xPos = LEFT_BORDER + FRET_SPACING + fret * FRET_SPACING

      txt = str( fret )
      self.canvas.create_text( xPos - STR_SPC / 2, FRET_NUM_VERT_OFFSET, text=txt ) # Fretboard numbering

      w = 1 if fret else 4
      self.canvas.create_rectangle( xPos, FRET1_TOP, xPos + w, FRET1_BOTTOM, fill="black" )
      self.canvas.create_rectangle( xPos, FRET2_TOP, xPos + w, FRET2_BOTTOM, fill="black" )

    if self.fretsNotes:
      for fretInd in( 3, 5, 7, 9, 12, 15 ):
        xPos = LEFT_BORDER + FRET_SPACING / 2 + fretInd * FRET_SPACING

        if fretInd == 12:
          yPos = ( FRET1_TOP + FRET1_BOTTOM ) / 3 # put 1/3 from top / bottom
          self.canvas.create_oval( xPos - 4, yPos - 4, xPos + 4, yPos + 4 )
          yPos = ( FRET1_TOP + FRET1_BOTTOM ) * 2/3
          self.canvas.create_oval( xPos - 4, yPos - 4, xPos + 4, yPos + 4 )
        else:
          yPos = ( FRET1_TOP + FRET1_BOTTOM ) / 2 # put in the middle
          self.canvas.create_oval( xPos - 4, yPos - 4, xPos + 4, yPos + 4 )

    # Draw strings
    for s in range( 0, numStrings ):
      self.canvas.create_text( STRING_LEFT - 20,
                               FRET1_TOP + s * STR_SPC,
                               text=fretboard[ s + 1 ][ 0 ][ 'root'] )
      self.canvas.create_text( STRING_LEFT - 20,
                               FRET2_TOP + s * STR_SPC,
                               text=fretboard[ s + 1 ][ 0 ][ 'root'] )
      self.canvas.create_line( STRING_LEFT,  FRET1_TOP + s * STR_SPC,
                               STRING_RIGHT, FRET1_TOP + s * STR_SPC )
      self.canvas.create_line( STRING_LEFT,  FRET2_TOP + s * STR_SPC,
                               STRING_RIGHT, FRET2_TOP + s * STR_SPC )

    # Populate individual frets
    for stringNum in range( 0, numStrings ):
      string = fretboard[ stringNum + 1 ]
      for fret in string:
        if fret[ 'interval' ] in extIntervals and stringNum > ( numStrings / 2 ):
          continue # Don't display ext intervals on bass strings

        xPos = LEFT_BORDER + FRET_SPACING / 2 + fret[ 'fret' ] * FRET_SPACING
        yPos = FRET1_TOP + stringNum * STR_SPC

        fill = None
        if self.overlay:
          if fret[ 'inSpelling' ] and fret[ 'inOLSpelling' ]:
            fill="#8ff" # blue-green if in both
          else:
            if fret[ 'inSpelling' ]:
              fill="#f88" # red-ish
            elif fret[ 'inOLSpelling' ]:
              fill="#88f" # blue-ish
        elif fret[ 'inSpelling' ]:
          fill="#f88"

        if fill:
          if self.fretsNotes: # Show frets?
            self.canvas.create_oval( xPos - 5, yPos - 5, xPos + 5, yPos + 5, fill=fill )
          else:
            self.canvas.create_oval( xPos - HIDE_RAD, yPos - HIDE_RAD,
                                     xPos + HIDE_RAD, yPos + HIDE_RAD,
                                     fill=fill )
            self.canvas.create_text( xPos, yPos, text=fret[ 'note' ] )

        # Bottom fretboard is just Chord 1's intervals.
        if fret[ 'inSpelling' ]:
          yPos = FRET2_TOP + stringNum * STR_SPC
          if fret[ 'interval' ] == 'R':
            self.canvas.create_oval( xPos - 5, yPos - 5, xPos + 5, yPos + 5, fill="black" )
          else:
            self.canvas.create_oval( xPos - HIDE_RAD, yPos - HIDE_RAD, xPos + HIDE_RAD, yPos + HIDE_RAD,
                                     fill="white", outline="black" ) # erase
            self.canvas.create_text( xPos, yPos, text=fret[ 'interval' ] )

  def instrumentChange( self, *args ):
    self.instrument = self.inst.get()
    self.displayFretboards( )

  def keyChange( self, *args ):
    self.key = self.keysVar.get()
    self.displayFretboards( )

  def OLkeyChange( self, *args ):
    self.OLkey = self.OLkeysVar.get()
    self.displayFretboards( )

  def spellingChange( self, *args ):
    self.spelling = self.spellingVar.get()
    self.displayFretboards( )

  def OLspellingChange( self, *args ):
    self.OLspelling = self.OLspellingVar.get()
    self.displayFretboards( )

  def fnToggle( self ):
    self.fretsNotes = not self.fretsNotes
    self.notesFrets.set( "Frets" if self.fretsNotes else "Notes" )

    self.displayFretboards()

  def fretNumToggle( self ):
    global num_frets
    num_frets = 15 if num_frets == 24 else 24
    self.btn1524txt.set( "15" if num_frets == 15 else "24" )

    self.displayFretboards()

  def overlayToggle( self ):
    self.overlay = not self.overlay
    self.overlayTxt.set( "-" if self.overlay else "+" )
    if self.overlay:
      self.OLkeysMenu[ "state" ] = "normal"
      self.OLspellingMenu[ "state" ] = "normal"
    else:
      self.OLkeysMenu[ "state" ] = "disable"
      self.OLspellingMenu[ "state" ] = "disable"

    self.displayFretboards()

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

    self.btn1524txt = StringVar()
    self.btn1524txt.set( "24" )

    self.overlayTxt = StringVar()
    self.overlayTxt.set( "+" )

    self.notesFrets = StringVar()
    self.notesFrets.set( "Notes" )

    self.OLkeysVar = StringVar()
    self.OLkeysVar.set( dispKeyList[ 0 ] )
    self.OLkeysVar.trace( 'w', self.OLkeyChange )

    self.OLspellingVar = StringVar()
    self.OLspellingVar.set( spellings[ 0 ] )
    self.OLspellingVar.trace( 'w', self.OLspellingChange )

  def displayMainframe( self ):
    for widget in self.mainFrame.winfo_children():
      widget.destroy()

    self.instMenu = OptionMenu( self.mainFrame, self.inst, *instruments )
    self.instMenu.pack( side=LEFT )

    self.keysMenu = OptionMenu( self.mainFrame, self.keysVar, *dispKeyList )
    self.keysMenu.pack( side=LEFT )

    self.spellingMenu = OptionMenu( self.mainFrame, self.spellingVar, *spellings )
    self.spellingMenu.pack( side=LEFT )

    self.overLayButton = Button( self.mainFrame,
                                 textvariable=self.overlayTxt,
                                 font=disFont[ 1 ],
                                 command=self.overlayToggle )
    self.overLayButton.pack( side=LEFT )

    self.OLkeysMenu = OptionMenu( self.mainFrame, self.OLkeysVar, *dispKeyList )
    self.OLkeysMenu.pack( side=LEFT )

    self.OLspellingMenu = OptionMenu( self.mainFrame, self.OLspellingVar, *spellings )
    self.OLspellingMenu.pack( side=LEFT )

    self.OLkeysMenu[ "state" ] = "disable"
    self.OLspellingMenu[ "state" ] = "disable"

    self.fn = Button( self.mainFrame,
                      textvariable=self.notesFrets,
                      font=disFont[ 1 ],
                      command=self.fnToggle )
    self.fn.pack( side=LEFT )

    self.fb = Button( self.mainFrame,
                      textvariable=self.btn1524txt,
                      font=disFont[ 1 ],
                      command=self.fretNumToggle )
    self.fb.pack( side=LEFT )

  def __init__( self ):
    self.instrument = instruments[ 0 ]
    self.key = dispKeyList[ 0 ]
    self.spelling = spellings[ 0 ]
    self.OLkey = dispKeyList[ 0 ] # Overlay
    self.OLspelling = spellings[ 0 ]
    self.fretsNotes = False
    self.overlay = False

    root = Tk()
    root.title( "Chords" )

    self.mainFrame = Frame( root )
    self.mainFrame.pack( side=TOP )

    self.initMainframe()
    self.displayMainframe()

    self.fretboardFrame = Frame( root )
    self.fretboardFrame.pack( side=TOP )

    self.canvas = Canvas( self.fretboardFrame, width=800, height=600 )
    self.canvas.pack()

    self.displayFretboards( )

    root.mainloop()

runGui()