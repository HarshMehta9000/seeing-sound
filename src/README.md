# src/

The clean versions. Two scripts, two different paths through the problem.

- **`final_analysis.py`** produces seven statistical visualizations (piano roll hexbin, velocity distribution, velocity over time, note frequency, octave counts, swarm by octave, normalized frequency heatmap) from a MIDI file. Built on `mido`.

- **`polar_mapping.py`** writes a CSV of (x, y, velocity, duration, note, instrument) where x and y are the polar-mapped note positions. This is the Tableau fuel. Built on `music21` so it can handle chords and tempo properly.

Both take a MIDI path as their first argument and are safe to run on any `.mid` file in `data/midi/`. If you want the history, the experiments folder has the 20-odd versions that got me here.
