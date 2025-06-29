# Audio Concatenator

Concatenates 4 audio files in AABBAACCDDAA pattern using ffmpeg.

## Quick Start

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Run the script
python audio_concatenator.py
```

## Output
- Creates: `concatenated_AABBAACCDDAA.wav`
- Pattern: A-A-B-B-A-A-C-C-D-D-A-A (where A=file-0, B=file-1, C=file-2, D=file-3) 