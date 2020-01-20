These scripts use Python 2.7.16

1.  chords.py - A python fretboard display utility. Uses tkinter.

2.  tab.py - A python tablature creator for getting down ideas. Runs in a terminal.

3.  setlist.py - Allows you to generate an html setlist file from lyrics.

    Usage:

    Put your lyrics as txt files in a directory. Note the format below.

    From a terminal window run setlist.py from your lyrics directory.
    It will scan the local directory for lyrics (.txt files) and these will show up
    in the Library.

    Press '?' to see the available commands.

    Name your setlist by pressing 'r'.

    Add sets with "a". Navigate to the Library with the up/down/left/right/d/f

    You can jump to a specific set by pressing '12345..'. You can jump back to the
    library by pressing '`'

    Name your sets by pressing 'n' while the cursor is in the particular set.

    Navigate to the library. Add songs with to the clipboard by pressing 'c'
    with the cursor over the desired song.

    Paste the clipboard into the desired set by navigating to the desired set
    and pressing 'p'

    Songs in a set can be moved by moving the cursor over the song and pressing 'm'.
    Press 'm' again to return to normal mode.

    Once the setlist is done, press 's' to save and then 'x' or 'X' to Export the list.

    A file called "Setlist.html" will be in the current directory. This is your setlist.


    Lyrics file format:
    These are text files with a .txt extension.
    The first line is assumed to be the name of the song and is the tile of the song
    in the setlist.

    There a few shortcuts that can be put in lyric files that setlist.py will recognize.
      "c!" will be replaced with "Chorus"
      "s!" will be replaced with "Solo"
      "h!" will be replace with "harmonica"
      "t!" will start/stop usage of a fixed font for tablature

    You can also put in html as that will be pasted into the output and the broswer will
    simply interpret it.

    Example:

      song_file.txt

     1) Song name
     2)
     3) lyrics
     4) lyrics
     5) c! // chorus
     6) s! // solo
     7) lyrics


Greg Girardin
Nashua, NH
girardin1972@hotmail.com