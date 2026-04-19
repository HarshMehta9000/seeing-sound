import seaborn as sns
import pandas as pd
from mido import MidiFile
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# Load MIDI file
mid = MidiFile(r"C:\Users\Dell\Downloads\Queen - Bohemian Rhapsody.mid")

# Mapping MIDI note numbers to note names with octaves
note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
def note_number_to_name_octave(note_number):
    name = note_names[note_number % 12]
    octave = note_number // 12 - 1
    return f"{name}{octave}"

# Process MIDI messages
message_list, message_strings_split = [], []
for i in mid.tracks[1][1:-1]:
    message_list.append(i)
for message in message_list:
    split_str = str(message).split(" ")
    message_strings_split.append(split_str)

# Extract message types and attributes
message_type = [item[0] for item in message_strings_split]
df1 = pd.DataFrame(message_type, columns=['message_type'])
attributes_dict = []
for item in message_strings_split:
    attr_dict = {i.split("=")[0]: i.split("=")[1] for i in item[1:]}
    attributes_dict.append(attr_dict)
df2 = pd.DataFrame.from_dict(attributes_dict)

# Combine DataFrames and convert columns
df_final = pd.concat([df1, df2], axis=1)
df_final['time'] = df_final['time'].astype(float)
df_final['note'] = pd.to_numeric(df_final['note'], errors='coerce').fillna(0).astype(int)
df_final['velocity'] = pd.to_numeric(df_final['velocity'], errors='coerce').fillna(0)

# Engineer features
df_final['time_elapsed'] = df_final['time'].cumsum()
df_final['note_name_octave'] = df_final['note'].apply(note_number_to_name_octave)
df_final['time_elapsed_minutes'] = df_final['time_elapsed'] / 60
# Aggregate data to count occurrences of each note_name_octave
note_frequencies = df_final.groupby('note_name_octave').size().reset_index(name='frequency')
df_final = pd.merge(df_final, note_frequencies, how='left', on='note_name_octave')

# Assuming `mid.ticks_per_beat` gives you the PPQN and `default_tempo` is in microseconds per beat
ticks_per_beat = mid.ticks_per_beat
default_tempo = 500000  # This represents 120 BPM; adjust as necessary
microseconds_per_tick = default_tempo / ticks_per_beat

df_final['time'] = df_final['time'].astype(int)
df_final['time_seconds'] = (df_final['time'] * microseconds_per_tick) / 1_000_000
df_final['time_elapsed_seconds'] = df_final['time_seconds'].cumsum()
df_final['time_elapsed_minutes'] = df_final['time_elapsed_seconds'] / 60

# Now, if the duration exceeds 10 minutes, you might want to scale it down.
max_duration_minutes = df_final['time_elapsed_minutes'].max()
scaling_factor = 10 / max_duration_minutes if max_duration_minutes > 10 else 1

df_final['time_elapsed_minutes'] = df_final['time_elapsed_minutes'] * scaling_factor

# Create a DataFrame with all possible notes in the piece's octave range
all_notes = []
for octave in range(-1, 10):  # Adjust the range according to the octaves present in your MIDI file
    for note in note_names:
        all_notes.append(f"{note}{octave}")

all_notes_df = pd.DataFrame(all_notes, columns=['note_name_octave'])

# Merge with the note frequencies, filling missing values with 0
complete_note_frequencies = pd.merge(all_notes_df, note_frequencies, on='note_name_octave', how='left')
complete_note_frequencies['frequency'] = complete_note_frequencies['frequency'].fillna(0)

# Merge this back with df_final to ensure all notes are represented
df_final_with_all_notes = pd.merge(df_final, complete_note_frequencies, on='note_name_octave', how='right')

# Now you can plot with the corrected time scale.


# First Visualization (High-Definition Density Plot)
fig_hd = px.density_heatmap(df_final, x='time_elapsed_minutes', y='note_name_octave',
                            nbinsx=40, nbinsy=12, title="Charlie Parker - Donna Lee.mid (inDepth Visualization)",
                            labels={'time_elapsed_minutes': 'Duration (Minutes)', 'note_name_octave': 'Note'})
fig_hd.update_layout(height=600, width=800)
fig_hd.show()

# Second Visualization (3D Scatter Plot with Time Duration in Minutes)
fig_3d_scatter = px.scatter_3d(df_final, x='time_elapsed_minutes', y='note_name_octave', z='frequency',
                               color='velocity', size='frequency', hover_name='message_type',
                               title="Charlie Parker - Donna Lee.mid (inDepth Visualization)",
                               labels={'time_elapsed_minutes': 'Duration (Minutes)', 'note_name_octave': 'Note', 'frequency': 'Note Count'})

fig_3d_scatter.update_layout(scene=dict(xaxis_title='Duration (Minutes)',
                                        yaxis_title='Notes',
                                        zaxis_title='Note Count'),
                             margin=dict(l=0, r=0, b=0, t=30), height=600, width=800)

fig_3d_scatter.show()