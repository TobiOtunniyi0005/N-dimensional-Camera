import os
import sys
import subprocess
import numpy as np
import pandas as pd
import librosa
import imageio_ffmpeg

# ============================
# INPUT HANDLING
# ============================
if len(sys.argv) < 2:
    print("Usage: python music.py <video_file.mp4>")
    sys.exit(1)

MP4_FILE = sys.argv[1]
TEMP_WAV = "temp_audio.wav"
OUTPUT_EXCEL = "audio_features.xlsx"

FRAME_LENGTH = 2048
HOP_LENGTH = 512

# ============================
# GET BUNDLED FFMPEG
# ============================
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

# ============================
# EXTRACT AUDIO
# ============================
print("Extracting audio (bundled FFmpeg)...")

cmd = [
    ffmpeg_path,
    "-y",
    "-i", MP4_FILE,
    "-vn",
    "-ac", "1",
    "-ar", "22050",
    TEMP_WAV
]

subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if not os.path.exists(TEMP_WAV):
    print("ERROR: Audio extraction failed.")
    sys.exit(1)

# ============================
# LOAD AUDIO
# ============================
print("Loading audio...")
y, sr = librosa.load(TEMP_WAV, sr=None)

# ============================
# FEATURE EXTRACTION
# ============================
print("Extracting features...")

rms = librosa.feature.rms(y=y, frame_length=FRAME_LENGTH, hop_length=HOP_LENGTH)[0]
zcr = librosa.feature.zero_crossing_rate(y, frame_length=FRAME_LENGTH, hop_length=HOP_LENGTH)[0]

spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=HOP_LENGTH)[0]
spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, hop_length=HOP_LENGTH)[0]
spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=HOP_LENGTH)[0]

mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=HOP_LENGTH)

f0, _, _ = librosa.pyin(
    y,
    fmin=librosa.note_to_hz("C2"),
    fmax=librosa.note_to_hz("C7"),
    hop_length=HOP_LENGTH
)

times = librosa.frames_to_time(
    np.arange(len(rms)),
    sr=sr,
    hop_length=HOP_LENGTH
)

# ============================
# BUILD DATAFRAME
# ============================
data = {
    "time_sec": times,
    "rms_energy": rms,
    "zero_crossing_rate": zcr,
    "spectral_centroid_hz": spectral_centroid,
    "spectral_bandwidth_hz": spectral_bandwidth,
    "spectral_rolloff_hz": spectral_rolloff,
    "fundamental_frequency_hz": f0
}

for i in range(mfcc.shape[0]):
    data["mfcc_" + str(i + 1)] = mfcc[i]

df = pd.DataFrame(data)

# ============================
# EXPORT TO EXCEL
# ============================
print("Writing Excel file...")
df.to_excel(OUTPUT_EXCEL, index=False)

# ============================
# CLEANUP
# ============================
os.remove(TEMP_WAV)

print("DONE ✔")
print("Saved:", OUTPUT_EXCEL)
print("Frames:", len(df))
print("Sample rate:", sr)
