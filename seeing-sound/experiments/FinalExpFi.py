import pandas as pd
import seaborn as sns
from mido import MidiFile
import matplotlib.pyplot as plt
import matplotlib as mpl

# Set the default background color to black
mpl.rcParams['figure.facecolor'] = 'black'
mpl.rcParams['axes.facecolor'] = 'black'
mpl.rcParams['savefig.facecolor'] = 'black'
mpl.rcParams['text.color'] = 'white'
mpl.rcParams['axes.labelcolor'] = 'white'
mpl.rcParams['xtick.color'] = 'white'
mpl.rcParams['ytick.color'] = 'white'

# Load the MIDI file
midi_file = "C:\\Users\\Dell\\Downloads\\Parker. Charlie - Donna Lee___WWW.MIDISFREE.COM.mid"
mid = MidiFile(midi_file)

def note_number_to_name(note_number):
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = note_number // 12 - 1
    return note_names[note_number % 12] + str(octave)

note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
message_list = [str(msg) for msg in mid.tracks[1][1:-1]]
message_strings_split = [message.split(" ") for message in message_list]
message_type = [msg[0] for msg in message_strings_split]
attributes = [msg[1:] for msg in message_strings_split]

attributes_dict = []
for attr_list in attributes:
    attr_dict = {attr.split("=")[0]: attr.split("=")[1] for attr in attr_list}
    attributes_dict.append(attr_dict)

df1 = pd.DataFrame(message_type, columns=['message_type'])
df2 = pd.DataFrame(attributes_dict)
df_complete = pd.concat([df1, df2], axis=1)

df_complete['note'] = df_complete['note'].fillna(0).astype(int)
df_complete['time'] = df_complete['time'].astype(float)
df_complete['time_elapsed'] = df_complete['time'].cumsum()

df_filtered = df_complete[(df_complete['message_type'] == 'note_on') & (df_complete['velocity'] != '0')].copy()
df_filtered.drop(['channel', 'value', 'control', 'time'], axis=1, inplace=True)

first_row = pd.DataFrame([{'message_type': 'note_on', 'note': 0, 'velocity': 0, 'time_elapsed': 0}])
last_row = pd.DataFrame([{'message_type': 'note_on', 'note': 127, 'velocity': 0, 'time_elapsed': df_filtered['time_elapsed'].iloc[-1] * 1.05}])
df_final = pd.concat([first_row, df_filtered, last_row], ignore_index=True)

df_final['note_name'] = df_final['note'].apply(note_number_to_name)
df_final['octave'] = df_final['note'] // 12 - 1
df_final['velocity'] = df_final['velocity'].astype(int)

def note_number_to_name_no_octave(note_number):
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return note_names[note_number % 12]

df_final['note_name_no_octave'] = df_final['note'].apply(note_number_to_name_no_octave)
note_to_pos = {note: i for i, note in enumerate(note_names)}
df_final['note_pos'] = df_final['note_name_no_octave'].map(note_to_pos)
df_final['time_elapsed_min'] = df_final['time_elapsed'] / 60

# Get the total duration of the MIDI file in seconds
duration_seconds = mid.length

# Convert duration to minutes
duration_minutes = duration_seconds / 60

# Calculate the time elapsed in minutes based on the duration
df_final['time_elapsed_min'] = df_final['time_elapsed'] * duration_minutes / df_final['time_elapsed'].max()

# Visualization 1: Hexbin plot of notes over time
df_plot = df_final[df_final['time_elapsed_min'].between(1, 10)]

# Check data types
print("Data types:")
print(df_plot['time_elapsed_min'].dtype)
# Print the first few rows of df_plot
print("First few rows of df_plot:")
print(df_plot.head())

# Check for missing values
print("\nMissing values:")
print(df_plot.isnull().sum())
# Convert columns to numeric data types
df_plot['time_elapsed_min'] = pd.to_numeric(df_plot['time_elapsed_min'], errors='coerce')
df_plot['note_pos'] = pd.to_numeric(df_plot['note_pos'], errors='coerce')
# Drop rows with missing values
df_plot = df_plot.dropna(subset=['time_elapsed_min', 'note_pos'])

# Add the print statements here
print(f"Number of notes within the time range: {len(df_plot)}")
print(f"Minimum time elapsed: {df_plot['time_elapsed_min'].min()}")
print(f"Maximum time elapsed: {df_plot['time_elapsed_min'].max()}")
print(f"Minimum note position: {df_plot['note_pos'].min()}")
print(f"Maximum note position: {df_plot['note_pos'].max()}")

if not df_plot.empty:
    # Print the first few rows of df_plot
    print("First few rows of df_plot:")
    print(df_plot.head())

    plt.figure(figsize=(20, 12))
    g = sns.jointplot(data=df_plot, x='time_elapsed_min', y='note_pos', kind='hex', cmap='viridis',
                      joint_kws={'gridsize': 50}, space=0, height=10)
    
    # Set the y-axis tick labels to note names
    g.ax_joint.set_yticks(list(note_to_pos.values()))
    g.ax_joint.set_yticklabels(list(note_to_pos.keys()))
    
    # ... (rest of the code for Visualization 1)
else:
    print("No notes found within the specified time range (1-10 minutes).")

if not df_plot.empty:
    plt.figure(figsize=(10, 6))
    plt.scatter(df_plot['time_elapsed_min'], df_plot['note_pos'], color='white', alpha=0.7)
    plt.xlabel('Time Elapsed (minutes)')
    plt.ylabel('Note')
    plt.yticks(list(note_to_pos.values()), list(note_to_pos.keys()))
    plt.title('Notes over Time')
    plt.show()
else:
    print("No notes found within the specified time range (1-10 minutes).")


# Visualization 2: Distribution of Note Velocities (60-100)
plt.figure(figsize=(12, 8))
velocity_range = (60, 100)
df_velocity_range = df_final[(df_final['velocity'] >= velocity_range[0]) & (df_final['velocity'] <= velocity_range[1])]

if not df_velocity_range.empty:
    sns.histplot(data=df_velocity_range, x='velocity', bins=30, color='skyblue')
    plt.title('Distribution of Note Velocities (60-100)', color='white', fontsize=18)
    plt.xlabel('Velocity', fontsize=14, color='white')
    plt.ylabel('Frequency', fontsize=14, color='white')
    
    max_velocity = df_velocity_range['velocity'].max()
    max_velocity_notes = df_velocity_range[df_velocity_range['velocity'] == max_velocity]
    for _, row in max_velocity_notes.iterrows():
        note_name = row['note_name']
        octave = row['octave']
        plt.annotate(f"{note_name}{octave}", xy=(row['velocity'], 0), xytext=(0, 10),
                     textcoords='offset points', ha='center', va='bottom',
                     fontsize=12, color='red', rotation=90)
else:
    print("No notes found within the specified velocity range (60-100).")

# Visualization 3: Note Velocity Over Time (in minutes)
# Plot the note velocity over time in minutes
plt.figure(figsize=(20, 8))
plt.plot(df_final['time_elapsed_min'], df_final['velocity'], marker='o', linestyle='-', markersize=6, linewidth=2, color='purple')
plt.title('Note Velocity Over Time (in minutes)', color='white', fontsize=20)
plt.xlim(0, duration_minutes)
plt.xlabel('Time Elapsed (minutes)', fontsize=16, color='white')
plt.ylabel('Velocity', fontsize=16, color='white')

# Visualization 4: Frequency of Each Note
plt.figure(figsize=(20, 10))
note_counts = df_final['note_name'].value_counts().sort_index()
sns.barplot(x=note_counts.values, y=note_counts.index, orient='h', color="cyan", saturation=1, width=0.8, edgecolor='white', linewidth=0.8)
plt.title('Frequency of Each Note', color='white', fontsize=24)
plt.xlabel('Count', fontsize=18, color='white')
plt.ylabel('Note', fontsize=18, color='white')
plt.xticks(fontsize=14, color='white')
plt.yticks(fontsize=14, color='white')
plt.grid(True, color='gray', linestyle='-', linewidth=0.5, alpha=0.5, axis='x')

# Visualization 5: Note Occurrences by Octave
plt.figure(figsize=(16, 8))
octaves = sorted(df_final['octave'].unique())
sns.countplot(x='octave', data=df_final, color='lightblue', order=octaves, saturation=1, edgecolor='white', linewidth=1.2)
plt.title('Note Occurrences by Octave', color='white', fontsize=24)
plt.xlabel('Octave', fontsize=18, color='white')
plt.ylabel('Occurrences', fontsize=18, color='white')
plt.xticks(fontsize=14, color='white')
plt.yticks(fontsize=14, color='white')
for p in plt.gca().patches:
    plt.gca().annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height()),
                       ha='center', va='center', fontsize=14, color='white', xytext=(0, 5),
                       textcoords='offset points')
plt.grid(True, color='gray', linestyle='-', linewidth=0.5, alpha=0.5, axis='y')

# Visualization 6: Swarmplot of Note Names by Octave
plt.figure(figsize=(16, 12))
octaves_range = range(10)
df_octaves = pd.DataFrame({'octave': octaves_range})
df_merged = pd.merge(df_octaves, df_final, on='octave', how='left')
sns.swarmplot(x='octave', y='note_name', data=df_merged, palette="viridis", size=1, edgecolor='white', linewidth=0.3)
plt.title('Note Names by Octave', color='white', fontsize=24)
plt.xlabel('Octave', fontsize=18, color='white')
plt.ylabel('Note Name', fontsize=18, color='white')
plt.xticks(fontsize=14, color='white')
plt.yticks(fontsize=14, color='white')
plt.grid(True, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)

# Visualization 7: Heatmap of Normalized Note Frequencies by Octave
plt.figure(figsize=(16, 12))
heatmap_data = df_final.groupby(['note_name', 'octave']).size().unstack(fill_value=0)
heatmap_data_normalized = heatmap_data.div(heatmap_data.sum(axis=1), axis=0)

ax = sns.heatmap(heatmap_data_normalized, cmap='magma', cbar_kws={'label': 'Normalized Frequency'}, linewidths=0.5, linecolor='white')
ax.set_title('Heatmap of Normalized Note Frequencies by Octave', color='white', fontsize=24)
ax.set_xlabel('Octave', fontsize=18, color='white')
ax.set_ylabel('Note Name', fontsize=18, color='white')
ax.xaxis.tick_top()
plt.xticks(fontsize=14, color='white', rotation=45, ha='left')
plt.yticks(fontsize=14, color='white')
cbar = ax.collections[0].colorbar
cbar.set_label('Normalized Frequency', color='white', fontsize=16)
cbar.ax.yaxis.label.set_color('white')
cbar.ax.tick_params(colors='white', labelsize=14)
plt.gca().invert_yaxis()
plt.grid(True, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)

# Extract the MIDI file name without the .mid extension
midi_file_name = midi_file.split("\\")[-1].replace(".mid", "")

# Save the visualizations with the MIDI file name and high resolution
plt.figure(1)
plt.savefig(f"{midi_file_name}_Visualization1.png", dpi=300, bbox_inches='tight')
plt.figure(2)
plt.savefig(f"{midi_file_name}_Visualization2.png", dpi=300, bbox_inches='tight')
plt.figure(3)
plt.savefig(f"{midi_file_name}_Visualization3.png", dpi=300, bbox_inches='tight')
plt.figure(4)
plt.savefig(f"{midi_file_name}_Visualization4.png", dpi=300, bbox_inches='tight')
plt.figure(5)
plt.savefig(f"{midi_file_name}_Visualization5.png", dpi=300, bbox_inches='tight')
plt.figure(6)
plt.savefig(f"{midi_file_name}_Visualization6.png", dpi=300, bbox_inches='tight')
plt.figure(7)
plt.savefig(f"{midi_file_name}_Visualization7.png", dpi=300, bbox_inches='tight')

plt.show()