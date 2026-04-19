import pandas as pd
from mido import MidiFile
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Load the MIDI file
midi_path = r"C:\\Users\\Dell\\Downloads\\Queen - Bohemian Rhapsody.mid"
mid = MidiFile(midi_path)

# Extract MIDI messages from the specified track
message_list = [str(msg) for msg in mid.tracks[1][1:-1]]

# Split each message into components
message_strings_split = [message.split(" ") for message in message_list]

# Extract message types and attributes
message_type = [msg[0] for msg in message_strings_split]
attributes = [msg[1:] for msg in message_strings_split]

# Convert attributes to a dictionary
attributes_dict = []
for attr_list in attributes:
    attr_dict = {}
    for attr in attr_list:
        key_value = attr.split("=")
        if len(key_value) == 2:
            attr_dict[key_value[0]] = key_value[1]
    attributes_dict.append(attr_dict)

# Create DataFrames and concatenate them
df1 = pd.DataFrame(message_type, columns=['message_type'])
df2 = pd.DataFrame(attributes_dict)
df_complete = pd.concat([df1, df2], axis=1)

# Data cleaning and conversion
if 'note' in df_complete:
    df_complete['note'] = df_complete['note'].fillna(0).astype(int)
df_complete['time'] = df_complete['time'].astype(float)
df_complete['time_elapsed'] = df_complete['time'].cumsum()

# ... (previous MIDI data processing code)

# Initialize the duration column to zero
df_complete['duration'] = 0

# Create a dictionary to store the start time of 'note_on' events
note_on_times = {}

# Iterate through the DataFrame to calculate the duration
for index, row in df_complete.iterrows():
    if row['message_type'] == 'note_on' and row.get('velocity', '0') != '0':
        # Store the start time of the note with channel information
        note_on_times[(row['note'], row.get('channel', '0'))] = row['time_elapsed']
    elif row['message_type'] == 'note_off' or (row['message_type'] == 'note_on' and row['velocity'] == '0'):
        note_key = (row['note'], row.get('channel', '0'))
        if note_key in note_on_times:
            # Calculate the duration and update the DataFrame
            start_time = note_on_times[note_key]
            duration = row['time_elapsed'] - start_time
            # Assign duration to all rows corresponding to the note-on event
            df_complete.loc[df_complete['time_elapsed'] >= start_time, 'duration'] = duration
            del note_on_times[note_key]  # Remove the note from the dictionary

# Now, filter out the DataFrame to contain only 'note_on' events with velocity > 0 (actual notes being played)
df_final = df_complete[(df_complete['message_type'] == 'note_on') & (df_complete['velocity'] != '0')]
df_final = df_complete[(df_complete['message_type'] == 'note_on') & (df_complete['velocity'] != '0')].copy()


# Prepare the figure with a black background
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(15, 8))

# Convert 'time_elapsed' to minutes for the X-axis
df_final['time_elapsed_min'] = df_final['time_elapsed'] / 60

# Plotting each note as a rectangle
for _, row in df_final.iterrows():
    rect_width = row['duration'] / 60  # Convert the duration to minutes
    note = row['note'] % 12
    octave = row['note'] // 12 - 1
    rect = patches.Rectangle((row['time_elapsed_min'], note), rect_width, 1,
                             edgecolor='white', facecolor='grey')
    ax.add_patch(rect)

# Customize the y-axis to show note names with octave numbers for notes outside the main octave
note_labels = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
ax.set_yticks(range(12))
ax.set_yticklabels(note_labels, color='white')

# Create a secondary y-axis to show octave numbers
ax2 = ax.twinx()
ax2.set_ylim(ax.get_ylim())
octave_ticks = [i * 12 for i in range(11)]  # 11 octaves including 0 (from -1 to 9)
ax2.set_yticks(octave_ticks)
ax2.set_yticklabels([str(i - 1) for i in range(11)], color='white')  # Octave numbers from -1 to 9
ax2.set_ylabel('Octave', color='white')

# Set labels and title with a white color for visibility
ax.set_xlabel('Time (minutes)', color='white')
ax.set_ylabel('Note', color='white')
ax.set_title('Piano Roll Visualization', color='white')

# Hide the spines and ticks for a cleaner look
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')

# Show the plot
plt.show()
