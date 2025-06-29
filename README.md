# Music Generator and Audio Concatenator

This project generates music loops using Replicate's musicgen-looper model and concatenates them into a longer audio file with a specific pattern.

## Overview

1. **Music Generator** (`music_generator.py`) - Uses Replicate to generate 4 audio files
2. **Audio Concatenator** (`audio_concatenator.py`) - Combines files in AABBAACCDDAA pattern

## Prerequisites

1. **Replicate API Token** - Get one from https://replicate.com/account/api-tokens
2. **Python Dependencies** - Install with: `pip install -r requirements.txt`

## Setup

1. Set your API token:
   ```bash
   export REPLICATE_API_TOKEN=your_token_here
   ```
   Or create a `.env` file:
   ```
   REPLICATE_API_TOKEN=your_token_here
   ```

## Music Generator Parameters

The music generator supports extensive customization:

### Basic Parameters
- `--prompt, -p` - Text description of the music to generate
- `--bpm, -b` - Beats per minute (default: 120, range: 40-300)
- `--variations, -v` - Number of variations (default: 4, range: 1-20)

### Advanced Generation Controls  
- `--max-duration, -d` - Maximum duration per loop in seconds (default: 8, range: 2-20)
- `--model-version, -m` - Model size: `medium` or `large` (default: medium)
- `--temperature, -t` - Controls diversity/creativity (default: 1.0, higher = more diverse)
- `--classifier-free-guidance` - How closely output follows prompt (default: 3, higher = more adherent)
- `--seed` - Seed for reproducible results (default: -1 for random)
- `--output-format` - Output format: `wav` or `mp3` (default: wav)

### Utility Parameters
- `--prediction-id` - Reuse existing prediction ID to save credits during development

## Usage Examples

### Basic Usage (Interactive)
```bash
python music_generator.py
```

### Command Line with Basic Parameters
```bash
python music_generator.py --prompt "dark ambient electronic" --bpm 100 --variations 4
```

### Advanced Creative Control
```bash
# High creativity, longer loops
python music_generator.py \
  --prompt "jazzy hip-hop beat with vinyl crackle" \
  --bpm 85 \
  --max-duration 12 \
  --temperature 1.5 \
  --model-version large

# Precise adherence to prompt
python music_generator.py \
  --prompt "minimalist piano melody" \
  --classifier-free-guidance 8 \
  --temperature 0.7 \
  --seed 12345
```

### Development with Credit Saving
```bash
# Generate once
python music_generator.py --prompt "upbeat techno" --bpm 128

# Reuse the same prediction (saves credits)
python music_generator.py --prediction-id 0tm5rsx815rj40cqqppsfr1j10
```

## Parameter Guide

### Temperature (`--temperature`)
- **0.5-0.8**: Conservative, stays close to training patterns
- **1.0**: Balanced creativity (default)
- **1.2-2.0**: More experimental and diverse

### Classifier-Free Guidance (`--classifier-free-guidance`)
- **1-2**: Loose interpretation of prompt
- **3**: Balanced adherence (default)  
- **5-10**: Strict adherence to prompt

### Model Version (`--model-version`)
- **medium**: Faster, good quality (default)
- **large**: Slower, higher quality and more nuanced

### Max Duration (`--max-duration`)
- **2-4 seconds**: Short, punchy loops
- **8 seconds**: Standard loops (default)
- **12-20 seconds**: Longer, more developed phrases

## Generated File Structure

Each generation creates a folder:
```
generation_abc12345/
├── replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m-0.wav
├── replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m-1.wav  
├── replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m-2.wav
├── replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m-3.wav
└── metadata.txt
```

## Audio Concatenation

After generating, concatenate the files:

```bash
python audio_concatenator.py generation_abc12345
```

This creates a file using the **AABBAACCDDAA** pattern:
- **A** = File 0, **B** = File 1, **C** = File 2, **D** = File 3
- Pattern repeats each file multiple times for musical development

### Duration Calculation

Total concatenated duration = `max_duration × 12`
- 8-second loops → 96 seconds (1.6 minutes)
- 12-second loops → 144 seconds (2.4 minutes)
- 20-second loops → 240 seconds (4 minutes)

## Complete Workflow Example

```bash
# 1. Generate creative jazz loops
python music_generator.py \
  --prompt "smooth jazz trio with upright bass" \
  --bpm 90 \
  --max-duration 10 \
  --temperature 1.3 \
  --model-version large

# 2. Concatenate (assuming it created generation_xyz789)
python audio_concatenator.py generation_xyz789

# Output: concatenated_generation_xyz789_AABBAACCDDAA.wav
```

## Tips for Best Results

1. **Creative Prompts**: Be specific but not overly restrictive
   - ✅ "lo-fi hip hop with vinyl warmth and soft piano"
   - ❌ "C major scale played on Yamaha piano at exactly 120 BPM"

2. **Parameter Balance**: 
   - High temperature + High CFG = Creative but focused
   - Low temperature + Low CFG = Predictable variations

3. **Development Workflow**:
   - Use `--prediction-id` to reuse generations while testing concatenation
   - Start with medium model, upgrade to large for final versions

4. **Duration Planning**:
   - Shorter loops (4-6s) for energetic, repetitive music
   - Longer loops (12-16s) for complex, evolving compositions

## File Organization

After generation, your directory will look like this:
```
project/
├── generation_abc12345/
│   ├── replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m-0.wav
│   ├── replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m-1.wav
│   ├── replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m-2.wav
│   ├── replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m-3.wav
│   └── metadata.txt
├── concatenated_generation_abc12345_AABBAACCDDAA.wav
├── music_generator.py
├── audio_concatenator.py
└── .env
``` 