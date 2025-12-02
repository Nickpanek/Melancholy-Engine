# @title 🎹 The Melancholy Engine (Sad Piano Factory) - FINAL FIXED
# @markdown Click Play to generate your "Sad Piano" Library.

import os
import csv
import zipfile
import time
import random
import math

print("Installing Audio Engine...")
!pip install mido > /dev/null
import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
from google.colab import files # This is the tool we need

# ======================================================
# 1. CONFIGURATION (The "Emotional DNA")
# ======================================================

KEYS = {
    "A_Minor": 57,  # Deep, classic sad key
    "C_Minor": 60,  # Dramatic, serious
    "E_Minor": 64,  # Gentle, guitar-like
    "F_Minor": 65   # Dark, tragic
}

# Slow tempos for sadness (60-90 BPM)
BPMS = range(60, 95, 5)

# "Flow" = How busy the left hand arpeggios are (Low = Chords, High = Rolling)
FLOW_LEVELS = [30, 60, 90]

# "Sorrow" = Complexity of melody (Low = Simple/Childlike, High = Complex/Jazz)
SORROW_LEVELS = [2, 5, 8]

OUTPUT_DIR = "/content/Panek_Piano_Library"

# ======================================================
# 2. THE ALGORITHM (Whitepaper Compliant)
# ======================================================

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_piano_piece(key_name, root_note, bpm, flow, sorrow, filename):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Setup
    track.append(MetaMessage('track_name', name='Piano', time=0))
    track.append(Message('program_change', program=0, time=0)) # Acoustic Grand
    track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm)))

    # Harmonic Constraint (Natural Minor)
    scale = [0, 2, 3, 5, 7, 8, 10]

    # Helper: Get chord tones (Root, 3rd, 5th)
    def get_chord_notes(root):
        return [root, root+3, root+7]

    # --- THE LEFT HAND (ACCOMPANIMENT) ---
    left_hand_events = []

    # Prog: i - VI - III - VII (The "Sad Pop" Progression)
    progression = [0, 8, 3, 10]

    bars = 8 # Song length

    current_tick = 0

    for bar in range(bars):
        chord_root_offset = progression[bar % 4]
        chord_root = root_note + chord_root_offset - 12 # Octave lower

        # Arpeggio Logic
        notes = get_chord_notes(chord_root)

        # If Flow is high, play 8th notes. If low, play half notes.
        if flow > 60:
            step = 240 # 8th notes
            pattern = [0, 2, 1, 2] * 2 # Up-down pattern
        else:
            step = 960 # Half notes
            pattern = [0, 1]

        for p_idx in pattern:
            note = notes[p_idx % 3]
            vel = random.randint(45, 60) # Soft background
            dur = step - 10
            left_hand_events.append({'note': note, 'vel': vel, 'time': current_tick, 'dur': dur})
            current_tick += step

    # --- THE RIGHT HAND (MELODY) ---
    right_hand_events = []
    current_tick = 0

    for bar in range(bars):
        # Divide bar into 4 beats
        for beat in range(4):
            # Rubato: Slight timing drift (humanize)
            drift = int(math.sin(current_tick) * 10)

            # Note choice logic
            if random.randint(0, 10) < sorrow:
                # Play a note
                interval = random.choice(scale)
                # 30% chance to jump an octave up for "Longing"
                if random.random() < 0.3: interval += 12

                note = root_note + interval
                vel = random.randint(65, 85) # Louder than left hand (Melody)
                dur = 480 - 20 # Quarter note

                right_hand_events.append({'note': note, 'vel': vel, 'time': current_tick + drift, 'dur': dur})

            current_tick += 480

    # --- MERGE & WRITE ---
    all_events = left_hand_events + right_hand_events
    all_events.sort(key=lambda x: x['time'])

    last_time = 0
    for event in all_events:
        delta = event['time'] - last_time
        if delta < 0: delta = 0

        track.append(Message('note_on', note=event['note'], velocity=event['vel'], time=delta))
        track.append(Message('note_off', note=event['note'], velocity=0, time=event['dur']))

        last_time = event['time'] + event['dur']

    mid.save(filename)

# ======================================================
# 3. EXECUTION LOOP
# ======================================================

print("--- STARTING PIANO FACTORY ---")
ensure_dir(OUTPUT_DIR)
csv_filename = "/content/Panek_Piano_Manifest.csv"

with open(csv_filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Filename", "Key", "BPM", "Flow", "Sorrow", "Author"])

    count = 0
    for key_name, root in KEYS.items():
        for bpm in BPMS:
            for flow in FLOW_LEVELS:
                for sorrow in SORROW_LEVELS:
                    fname = f"Piano_{key_name}_{bpm}_{flow}_{sorrow}.mid"
                    full_path = os.path.join(OUTPUT_DIR, fname)

                    generate_piano_piece(key_name, root, bpm, flow, sorrow, full_path)
                    writer.writerow([fname, key_name, bpm, flow, sorrow, "Nick Panek"])

                    count += 1
                    if count % 50 == 0: print(f"Composed {count} pieces...")

print("--- ZIPPING ARCHIVE ---")
zip_name = "/content/NickPanek_Piano_Collection.zip"
with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(csv_filename, arcname="Panek_Piano_Manifest.csv")
    # BUG FIX: Changed loop variable from 'files' to 'filenames' to protect the import
    for root, dirs, filenames in os.walk(OUTPUT_DIR):
        for f in filenames:
            zipf.write(os.path.join(root, f), arcname=f)

print(f"SUCCESS. Downloading {zip_name} now...")
# Now 'files' refers correctly to the Google Colab module
files.download(zip_name)
