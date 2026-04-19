from music21 import converter, note, chord, tempo
import math
import csv

# Path to your MIDI file (change this to your actual Pink Floyd MIDI file path)
midi_file = "C:\\Users\\Dell\\Downloads\\Monk. Thelonious - Blue Monk___WWW.MIDISFREE.COM.mid"

# Parse the MIDI file
score = converter.parse(midi_file)

# Get the first tempo marking from the score
# If there are multiple tempos throughout the piece, this will take more complex handling
tempo_markings = score.flatten().getElementsByClass(tempo.MetronomeMark)
if tempo_markings:
    first_tempo = tempo_markings[0].number  # Beats per minute
else:
    first_tempo = 120  # Default tempo (if not found in the MIDI file)

# The duration of a quarter note in seconds
quarter_note_duration_sec = 60 / first_tempo

# Access notes, chords, and rests
elements = score.flatten().notesAndRests

# Lists to hold note data
onsets = []
pitches = []
velocities = []
durations_seconds = []  # Store durations in seconds
note_names = []

for element in elements:
    if isinstance(element, note.Note):
        onsets.append(element.offset)
        pitches.append(element.pitch.midi)
        velocities.append(element.volume.velocity)  # Getting the velocity of the note
        durations_seconds.append(element.duration.quarterLength * quarter_note_duration_sec)  # Getting the duration of the note in seconds
        note_names.append(element.pitch.nameWithOctave)  # Getting the name of the note
    elif isinstance(element, chord.Chord):
        # Assuming you want to record each note in the chord separately
        for n in element.notes:
            onsets.append(element.offset)
            pitches.append(n.pitch.midi)
            note_names.append(n.pitch.nameWithOctave)
            # Assuming all notes in the chord have the same duration and velocity
            velocities.append(max(n.volume.velocity for n in element.notes))  # Max velocity of the notes in the chord
            durations_seconds.append(element.duration.quarterLength * quarter_note_duration_sec)  # Duration of the chord in seconds

# Convert onset times to angles and pitches to radii, then to Cartesian coordinates
min_onset = min(onsets)
max_onset = max(onsets)
min_pitch = min(pitches)
max_pitch = max(pitches)

def onset_to_angle(onset):
    return (onset - min_onset) / (max_onset - min_onset) * 360

def pitch_to_radius(pitch):
    radius_scale = 10  # Adjust as necessary for your visualization scale
    return (pitch - min_pitch) / (max_pitch - min_pitch) * radius_scale

def polar_to_cartesian(r, theta_deg):
    theta_rad = math.radians(theta_deg)
    return r * math.cos(theta_rad), r * math.sin(theta_rad)

# Prepare data for CSV output
data_for_csv = []
for angle, pitch, velocity, duration_seconds, name in zip(onsets, pitches, velocities, durations_seconds, note_names):
    r = pitch_to_radius(pitch)
    x, y = polar_to_cartesian(r, onset_to_angle(angle))
    # Format the duration as a string with fixed decimal places to avoid auto-formatting as date
    duration_str = "{:.4f}".format(duration_seconds)
    data_for_csv.append([x, y, velocity, duration_str, name])


# Write the coordinates to a CSV file
with open('Bluemonk.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['X', 'Y', 'Velocity', 'DurationSeconds', 'NoteName'])
    writer.writerows(data_for_csv)
