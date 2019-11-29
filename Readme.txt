1. chords.py - A python fretboard display utility.
   Easily extensible by modifying the script.

2. tab.py - A python tablature creator for getting down ideas. Runs in a terminal.

3. setlist.py - A setlist generator.
   Scans the local directory for .txt files which are assumed to be lyrics.
   Allows you to organize them into sets, save the setlist, and
   export all the lyrics as a single contiguous html file for tablet viewing.

   To use, put all your lyrics as txt files in a directory. From a terminal window
   run setlist.py from your lyric directory. It will scan the local directory for files.

   Use ? for help.

    m   - Move modes : Cycle between cursor move mode, song move mode, and set move mode
    o,s - Open/Save setlist.
    a,d - Add/Delete a set.
    c,p - Cut/Paste clipboard.
    x,X - Export : x will export the file as html
                   X will export as 'flat' html with no javascript
    r, n - Name the list/set.
    N   - Add Note : Just a single line at the top of the setlist.
                     ex: describe the highlight meaning.
    R   - Remove song.
    S   - Scan directory for lyric files
    1-9 - Jump to set.
    A   - Alphabetize set.
    h,sb - RGB highlight, remove. : Highlight a song RGB
    C, L - Clone song, set
    q   - quit.

Greg Girardin
Nashua, NH
girardin1972@hotmail.com