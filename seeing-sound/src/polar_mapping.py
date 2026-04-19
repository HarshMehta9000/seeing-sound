"""
Polar coordinate mapping of MIDI notes.

Parses a MIDI file with `music21`, maps note onset time to an angle around
a circle and MIDI pitch to a radius, then writes the resulting (x, y)
coordinates to a CSV. The output feeds the Tableau workbooks and the
.trex extensions in visualizations/tableau/.

The geometric intuition: time wraps around the circle, pitch moves outward
from the center. Plotting the CSV as a scatter gives you a piano roll
wrapped into a ring. In retrospect this is a 2D embedding done by hand,
which is why it sits well next to the later ML work.

Usage:
    python src/polar_mapping.py data/midi/your_file.mid -o data/csv/your_file.csv

This is the cleaned-up descendant of experiments/BohemianRhapsodyParse.py
and experiments/ParseGPT.py.
"""

import argparse
import csv
import math
import os
import sys

from music21 import chord, converter, instrument, note, tempo


def parse_notes(midi_path: str):
    """Walk the score and pull onset, pitch, velocity, duration, name, instrument for every note."""
    score = converter.parse(midi_path)

    tempo_markings = score.flatten().getElementsByClass(tempo.MetronomeMark)
    bpm = tempo_markings[0].number if tempo_markings else 120
    quarter_note_seconds = 60 / bpm

    onsets, pitches, velocities, durations, names, instruments = [], [], [], [], [], []

    for part in score.parts:
        # Find the instrument assigned to this part, if any
        instr_name = "Unknown Instrument"
        for el in part.recurse():
            if isinstance(el, instrument.Instrument):
                instr_name = el.instrumentName or "Unknown Instrument"
                break

        for element in part.recurse().notesAndRests:
            if isinstance(element, note.Note):
                onsets.append(element.offset)
                pitches.append(element.pitch.midi)
                velocities.append(element.volume.velocity)
                durations.append(element.duration.quarterLength * quarter_note_seconds)
                names.append(element.pitch.nameWithOctave)
                instruments.append(instr_name)
            elif isinstance(element, chord.Chord):
                for n in element.notes:
                    onsets.append(element.offset)
                    pitches.append(n.pitch.midi)
                    velocities.append(element.volume.velocity)
                    durations.append(element.duration.quarterLength * quarter_note_seconds)
                    names.append(n.pitch.nameWithOctave)
                    instruments.append(instr_name)

    return onsets, pitches, velocities, durations, names, instruments


def to_polar_csv(midi_path: str, out_path: str, radius_scale: float = 10.0) -> int:
    """Produce the (x, y, velocity, duration, note, instrument) CSV."""
    onsets, pitches, velocities, durations, names, instruments = parse_notes(midi_path)

    if not onsets:
        print("No notes found.", file=sys.stderr)
        return 1

    min_onset, max_onset = min(onsets), max(onsets)
    min_pitch, max_pitch = min(pitches), max(pitches)
    onset_range = max_onset - min_onset or 1
    pitch_range = max_pitch - min_pitch or 1

    def onset_to_angle(o):
        return (o - min_onset) / onset_range * 360

    def pitch_to_radius(p):
        return (p - min_pitch) / pitch_range * radius_scale

    rows = []
    for onset, pitch, velocity, duration, name, instr in zip(onsets, pitches, velocities, durations, names, instruments):
        theta_rad = math.radians(onset_to_angle(onset))
        r = pitch_to_radius(pitch)
        x = r * math.cos(theta_rad)
        y = r * math.sin(theta_rad)
        rows.append([x, y, velocity, f"{duration:.4f}", name, instr])

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["X", "Y", "Velocity", "DurationSeconds", "NoteName", "Instrument"])
        writer.writerows(rows)

    print(f"Wrote {len(rows)} notes to {out_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Map a MIDI file into polar (x, y) coordinates for Tableau.")
    parser.add_argument("midi_path", help="Path to the .mid file")
    parser.add_argument("-o", "--output", help="CSV output path (default: data/csv/<name>.csv)")
    parser.add_argument("--radius-scale", type=float, default=10.0, help="How far out pitches project (default: 10)")
    args = parser.parse_args()

    if not os.path.exists(args.midi_path):
        print(f"File not found: {args.midi_path}", file=sys.stderr)
        return 1

    out = args.output or f"data/csv/{os.path.splitext(os.path.basename(args.midi_path))[0]}.csv"
    return to_polar_csv(args.midi_path, out, radius_scale=args.radius_scale)


if __name__ == "__main__":
    sys.exit(main())
