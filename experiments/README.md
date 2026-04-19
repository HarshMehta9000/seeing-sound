# Experiments

This folder is the trail. It's not organized, it's not clean, and some of the files load the wrong MIDI despite their names. That's the point of keeping it.

If you want the working pipeline, look in `src/`. If you want to see how I got there, read on.

## Rough chronology

The files roughly follow the order I wrote them. I didn't use branches. I just made a new file every time I wanted to try something.

**`Exp1.py` through `Exp9ee.py`** are incremental attempts at the same basic task: parse MIDI, turn it into a DataFrame, plot it. Each one changes one thing. Each one breaks something else. By `Exp9ee` the shape of what became `final_analysis.py` is visible.

**`ExpBohemianRhapsody.py`** and **`ExperimentCharlieParker.py`** are the genre comparison work. They're almost identical scripts. The file names are also wrong: `ExperimentCharlieParker.py` loads Bohemian Rhapsody, `ExpBohemianRhapsody.py` loads Donna Lee. I noticed this months later. It didn't change what the code did, but it's a good reminder that file names lie if you let them.

**`ExpCh.py`, `ExpCl.py`, `ExpCll.py`, `ExpFi.py`** are variations on chord and octave extraction. Some worked. `ExpFi.py` eventually became `FinalExpFi.py` which became `src/final_analysis.py`.

**`ExpSpotify1.py`, `ExpSpotifyP1.py`** were a short-lived attempt to pull audio features from Spotify's API and compare them to the MIDI-derived features. Didn't finish. Worth knowing it happened.

**`BohemianRhapsodyParse.py`** and **`ParseGPT.py`** are the polar-coordinate pipeline. These were a parallel track, not iterations of the plotting work. They use `music21` instead of `mido` because I needed the music-theoretic abstractions (chords, tempo, explicit durations) to compute the polar mapping cleanly.

## What's missing

I deleted a few files before this got pushed. Two reasons: they contained API keys I forgot about, or they were trying to load files I don't have anymore. Nothing load-bearing.

## If you're reading this to learn

The honest lesson from this folder isn't technical. It's that the distance between "I have an idea" and "the idea works" is almost always paved with a lot of files named `Exp7a_v2_final_ACTUAL.py`. Leaving that visible is the only way the clean version in `src/` tells the truth.
