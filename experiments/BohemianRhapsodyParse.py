from music21 import converter, note, chord, tempo, instrument
import math
import csv

# Path to your MIDI file
midi_file = r"C:\\Users\\Dell\\Downloads\\Monk. Thelonious - Blue Monk___WWW.MIDISFREE.COM.mid"

# Parse the MIDI file
score = converter.parse(midi_file)

# Get the first tempo marking from the score
tempo_markings = score.flatten().getElementsByClass(tempo.MetronomeMark)
if tempo_markings:
    first_tempo = tempo_markings[0].number  # Beats per minute
else:
    first_tempo = 120  # Default tempo

# The duration of a quarter note in seconds
quarter_note_duration_sec = 60 / first_tempo

# Lists to hold note data for all parts
onsets = []
pitches = []
velocities = []
durations_seconds = []  # Store durations in seconds
note_names = []
instruments = []

# Process each part to extract note information
for part in score.parts:
    # Use `.recurse()` to find the first Instrument object in the part
    for el in part.recurse():
        if isinstance(el, instrument.Instrument):
            instr_name = el.instrumentName  # Get the instrument name
            break
    else:
        instr_name = "Unknown Instrument"  # Use a default if no instrument is found

    # Access notes, chords, and rests
    elements = part.recurse().notesAndRests
    for element in elements:
        if isinstance(element, note.Note):
            onsets.append(element.offset)
            pitches.append(element.pitch.midi)
            velocities.append(element.volume.velocity)
            durations_seconds.append(element.duration.quarterLength * quarter_note_duration_sec)
            note_names.append(element.pitch.nameWithOctave)
            instruments.append(instr_name)
        elif isinstance(element, chord.Chord):
            for n in element.notes:
                onsets.append(element.offset)
                pitches.append(n.pitch.midi)
                velocities.append(element.volume.velocity)
                durations_seconds.append(element.duration.quarterLength * quarter_note_duration_sec)
                note_names.append(n.pitch.nameWithOctave)
                instruments.append(instr_name)

# Calculate the minimum and maximum for onset times and pitches
min_onset = min(onsets)
max_onset = max(onsets)
min_pitch = min(pitches)
max_pitch = max(pitches)

def onset_to_angle(onset):
    return (onset - min_onset) / (max_onset - min_onset) * 360

def pitch_to_radius(pitch, radius_scale=10):
    return (pitch - min_pitch) / (max_pitch - min_pitch) * radius_scale

def polar_to_cartesian(r, theta_deg):
    theta_rad = math.radians(theta_deg)
    return r * math.cos(theta_rad), r * math.sin(theta_rad)

# Prepare data for CSV output
data_for_csv = []
for onset, pitch, velocity, duration_seconds, name, instr_name in zip(onsets, pitches, velocities, durations_seconds, note_names, instruments):
    angle = onset_to_angle(onset)
    radius = pitch_to_radius(pitch)
    x, y = polar_to_cartesian(radius, angle)
    duration_str = "{:.4f}".format(duration_seconds)
    data_for_csv.append([x, y, velocity, duration_str, name, instr_name])

# Write the coordinates to a CSV file
csv_headers = ['X', 'Y', 'Velocity', 'DurationSeconds', 'NoteName', 'Instrument']
with open('BlueMonkI.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(csv_headers)
    writer.writerows(data_for_csv)
