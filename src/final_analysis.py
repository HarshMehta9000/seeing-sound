"""
Statistical analysis and visualization of a MIDI file.

Parses a MIDI file with `mido`, extracts note-on events with velocity and
timing, and produces seven visualizations:

    1. Hexbin density of notes over time
    2. Velocity distribution (60-100 range) with peak annotations
    3. Velocity over time line plot
    4. Note frequency bar chart
    5. Note occurrences by octave
    6. Swarm plot of notes across octaves
    7. Normalized frequency heatmap (note x octave)

Usage:
    python src/final_analysis.py data/midi/your_file.mid

Outputs PNGs to visualizations/gallery/, named after the input file.

This is the cleaned-up descendant of experiments/FinalExpFi.py.
"""

import argparse
import os
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from mido import MidiFile

# Dark theme, consistent across all figures
mpl.rcParams["figure.facecolor"] = "black"
mpl.rcParams["axes.facecolor"] = "black"
mpl.rcParams["savefig.facecolor"] = "black"
mpl.rcParams["text.color"] = "white"
mpl.rcParams["axes.labelcolor"] = "white"
mpl.rcParams["xtick.color"] = "white"
mpl.rcParams["ytick.color"] = "white"

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_number_to_name(note_number: int) -> str:
    """Turn a MIDI note number into a name with octave, e.g. 60 -> 'C4'."""
    octave = note_number // 12 - 1
    return f"{NOTE_NAMES[note_number % 12]}{octave}"


def note_number_to_name_no_octave(note_number: int) -> str:
    return NOTE_NAMES[note_number % 12]


def parse_midi(midi_path: str, track_index: int = 1) -> pd.DataFrame:
    """Read a MIDI file and return a DataFrame of note-on events.

    Defaults to track 1 because track 0 is typically metadata. If your file
    has its notes elsewhere, pass a different track_index.
    """
    mid = MidiFile(midi_path)

    # Extract the messages as strings, then split into type and attribute pairs
    messages = [str(msg) for msg in mid.tracks[track_index][1:-1]]
    split = [m.split(" ") for m in messages]

    types = [m[0] for m in split]
    attrs = []
    for m in split:
        d = {}
        for pair in m[1:]:
            if "=" in pair:
                k, v = pair.split("=", 1)
                d[k] = v
        attrs.append(d)

    df = pd.concat([pd.DataFrame(types, columns=["message_type"]), pd.DataFrame(attrs)], axis=1)

    # Coerce the columns we care about
    df["note"] = pd.to_numeric(df.get("note", 0), errors="coerce").fillna(0).astype(int)
    df["time"] = pd.to_numeric(df.get("time", 0), errors="coerce").fillna(0).astype(float)
    df["velocity"] = pd.to_numeric(df.get("velocity", 0), errors="coerce").fillna(0).astype(int)
    df["time_elapsed"] = df["time"].cumsum()

    # Keep only note-ons with non-zero velocity (MIDI's way of saying "actually played")
    df = df[(df["message_type"] == "note_on") & (df["velocity"] > 0)].copy()

    # Add padding rows so plots span the full note range consistently
    first = pd.DataFrame([{"message_type": "note_on", "note": 0, "velocity": 0, "time_elapsed": 0}])
    last = pd.DataFrame(
        [
            {
                "message_type": "note_on",
                "note": 127,
                "velocity": 0,
                "time_elapsed": df["time_elapsed"].iloc[-1] * 1.05 if len(df) else 1,
            }
        ]
    )
    df = pd.concat([first, df, last], ignore_index=True)

    # Enrich with derived columns
    df["note_name"] = df["note"].apply(note_number_to_name)
    df["note_name_no_octave"] = df["note"].apply(note_number_to_name_no_octave)
    df["octave"] = df["note"] // 12 - 1
    df["note_pos"] = df["note_name_no_octave"].map({n: i for i, n in enumerate(NOTE_NAMES)})

    # Rescale elapsed time using the MIDI's actual duration
    duration_minutes = mid.length / 60
    max_time = df["time_elapsed"].max()
    if max_time > 0:
        df["time_elapsed_min"] = df["time_elapsed"] * duration_minutes / max_time
    else:
        df["time_elapsed_min"] = 0

    return df


def plot_all(df: pd.DataFrame, base_name: str, out_dir: str) -> None:
    """Produce the seven visualizations and save them to out_dir."""
    os.makedirs(out_dir, exist_ok=True)
    note_to_pos = {n: i for i, n in enumerate(NOTE_NAMES)}

    # 1. Hexbin density of notes over time
    df_plot = df[df["time_elapsed_min"].between(1, 10)].dropna(subset=["time_elapsed_min", "note_pos"])
    if not df_plot.empty:
        g = sns.jointplot(
            data=df_plot,
            x="time_elapsed_min",
            y="note_pos",
            kind="hex",
            cmap="viridis",
            joint_kws={"gridsize": 50},
            space=0,
            height=10,
        )
        g.ax_joint.set_yticks(list(note_to_pos.values()))
        g.ax_joint.set_yticklabels(list(note_to_pos.keys()))
        g.fig.savefig(f"{out_dir}/{base_name}_01_hexbin.png", dpi=200, bbox_inches="tight")
        plt.close(g.fig)

    # 2. Velocity distribution (60-100)
    df_vel = df[(df["velocity"] >= 60) & (df["velocity"] <= 100)]
    if not df_vel.empty:
        plt.figure(figsize=(12, 8))
        sns.histplot(data=df_vel, x="velocity", bins=30, color="skyblue")
        plt.title("Distribution of Note Velocities (60-100)", fontsize=18)
        plt.xlabel("Velocity", fontsize=14)
        plt.ylabel("Frequency", fontsize=14)
        plt.savefig(f"{out_dir}/{base_name}_02_velocity_dist.png", dpi=200, bbox_inches="tight")
        plt.close()

    # 3. Velocity over time
    plt.figure(figsize=(20, 8))
    plt.plot(df["time_elapsed_min"], df["velocity"], marker="o", linestyle="-", markersize=4, linewidth=1.5, color="purple")
    plt.title("Note Velocity Over Time", fontsize=20)
    plt.xlabel("Time Elapsed (minutes)", fontsize=16)
    plt.ylabel("Velocity", fontsize=16)
    plt.savefig(f"{out_dir}/{base_name}_03_velocity_over_time.png", dpi=200, bbox_inches="tight")
    plt.close()

    # 4. Note frequency
    plt.figure(figsize=(20, 10))
    note_counts = df["note_name"].value_counts().sort_index()
    sns.barplot(x=note_counts.values, y=note_counts.index, orient="h", color="cyan", edgecolor="white", linewidth=0.8)
    plt.title("Frequency of Each Note", fontsize=24)
    plt.xlabel("Count", fontsize=18)
    plt.ylabel("Note", fontsize=18)
    plt.savefig(f"{out_dir}/{base_name}_04_note_freq.png", dpi=200, bbox_inches="tight")
    plt.close()

    # 5. Occurrences by octave
    plt.figure(figsize=(16, 8))
    octaves = sorted(df["octave"].unique())
    sns.countplot(x="octave", data=df, color="lightblue", order=octaves, edgecolor="white", linewidth=1.2)
    plt.title("Note Occurrences by Octave", fontsize=24)
    plt.xlabel("Octave", fontsize=18)
    plt.ylabel("Occurrences", fontsize=18)
    plt.savefig(f"{out_dir}/{base_name}_05_octave_counts.png", dpi=200, bbox_inches="tight")
    plt.close()

    # 6. Swarm plot of notes by octave
    plt.figure(figsize=(16, 12))
    sns.swarmplot(x="octave", y="note_name", data=df, palette="viridis", size=1, edgecolor="white", linewidth=0.3)
    plt.title("Note Names by Octave", fontsize=24)
    plt.xlabel("Octave", fontsize=18)
    plt.ylabel("Note Name", fontsize=18)
    plt.savefig(f"{out_dir}/{base_name}_06_swarm.png", dpi=200, bbox_inches="tight")
    plt.close()

    # 7. Normalized frequency heatmap
    plt.figure(figsize=(16, 12))
    heatmap_data = df.groupby(["note_name", "octave"]).size().unstack(fill_value=0)
    heatmap_norm = heatmap_data.div(heatmap_data.sum(axis=1).replace(0, 1), axis=0)
    ax = sns.heatmap(heatmap_norm, cmap="magma", cbar_kws={"label": "Normalized Frequency"}, linewidths=0.5, linecolor="white")
    ax.set_title("Heatmap of Normalized Note Frequencies by Octave", fontsize=24)
    ax.xaxis.tick_top()
    plt.gca().invert_yaxis()
    plt.savefig(f"{out_dir}/{base_name}_07_heatmap.png", dpi=200, bbox_inches="tight")
    plt.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Visualize a MIDI file seven different ways.")
    parser.add_argument("midi_path", help="Path to the .mid file")
    parser.add_argument("--out", default="visualizations/gallery", help="Output directory for PNGs")
    parser.add_argument("--track", type=int, default=1, help="Which MIDI track to read (default: 1)")
    args = parser.parse_args()

    if not os.path.exists(args.midi_path):
        print(f"File not found: {args.midi_path}", file=sys.stderr)
        return 1

    base_name = os.path.splitext(os.path.basename(args.midi_path))[0]
    print(f"Parsing {args.midi_path}...")
    df = parse_midi(args.midi_path, track_index=args.track)
    print(f"Got {len(df)} note events. Plotting...")
    plot_all(df, base_name, args.out)
    print(f"Saved to {args.out}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
