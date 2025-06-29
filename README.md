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

Each generation creates a timestamped folder:
```
generation_20241201_143022_123/
├── replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m-0.wav
├── replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m-1.wav  
├── replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m-2.wav
├── replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m-3.wav
├── ...
├── replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m-19.wav (if variations=20)
└── metadata.txt (contains all generation parameters)
```

**Folder naming**: `generation_YYYYMMDD_HHMMSS_mmm` (includes milliseconds for uniqueness)

## Audio Concatenation

The audio concatenator supports flexible custom patterns and can work with up to 20 audio files (A-T).

### Basic Usage

```bash
python audio_concatenator.py generation_abc12345
```

### Custom Pattern Usage

```bash
# Use custom pattern
python audio_concatenator.py generation_abc12345 --pattern "ABCDEFGHIJKLMNOPQRST"

# Short punchy pattern
python audio_concatenator.py generation_abc12345 --pattern "ABAB"

# Complex musical development
python audio_concatenator.py generation_abc12345 --pattern "AABBCCDDAACCBBDDAABBCCDD"

# Call and response style
python audio_concatenator.py generation_abc12345 --pattern "ABACADABACAD"
```

### Pattern System

- **Letters** represent audio files: A=File 0, B=File 1, C=File 2, D=File 3, etc.
- **Default pattern**: `AABBAACCDDAA` (12 segments)
- **Supports up to 20 files**: A through T (if you generate that many variations)
- **Any length**: Create patterns from 2 to 100+ segments

### Common Pattern Examples

| Pattern | Description | Use Case |
|---------|-------------|----------|
| `AABBAACCDDAA` | Default (12 segments) | Balanced musical development |
| `ABCDABCDABCD` | Simple rotation | Even exposure to all variations |
| `AABBCCDDAABBCCDD` | Extended phrases | Longer musical phrases |
| `ABACADABACAD` | Call & response | Interactive musical dialog |
| `ABCDEFABCDEF` | 6-file rotation | Using first 6 variations |
| `AAAABBBBCCCCDDDD` | Grouped sections | Distinct musical sections |
| `ABCDEFGHIJKLMNOPQRST` | All 20 variations | Maximum variety showcase |
| `ABCDEFAGFSADGAS` | Complex asymmetric | Unpredictable musical flow |

### Advanced Pattern Techniques

**Build-up patterns**: `AAAABBBBAAAABBBBCCCCDDDD` - Gradually introduce new elements  
**Breakdown patterns**: `ABCDEFGHIJKLMNOPQRST...DCBA` - Complex then simple  
**Rhythmic patterns**: `ABABCDCDEFEFGHGH` - Create rhythmic emphasis  
**Story patterns**: `ABCDEFGFEDCBA` - Musical narrative with return journey  
**Chaos patterns**: `AFBGCHDIEJE...` - Intentionally unpredictable for experimental music

### Duration Calculation

Total duration = `max_duration × pattern_length`

Examples with 8-second loops:
- `AABBAACCDDAA` (12 chars) → 96 seconds (1.6 minutes)
- `ABCDABCDABCD` (12 chars) → 96 seconds (1.6 minutes)  
- `ABCDEFABCDEF` (12 chars) → 96 seconds (1.6 minutes)
- `AABBCCDDAABBCCDDAABBCCDD` (24 chars) → 192 seconds (3.2 minutes)

## Complete Workflow Examples

### Example 1: Creative Jazz with Custom Pattern

```bash
# 1. Generate creative jazz loops
python music_generator.py \
  --prompt "smooth jazz trio with upright bass" \
  --bpm 90 \
  --max-duration 10 \
  --temperature 1.3 \
  --model-version large

# 2. Concatenate with call-and-response pattern (assuming it created generation_20241201_143022_123)
python audio_concatenator.py generation_20241201_143022_123 --pattern "ABACADABACAD"

# Output: concatenated_generation_20241201_143022_123_ABACADABACAD.wav
```

### Example 2: Electronic Music with Extended Development

```bash
# 1. Generate high-variation electronic loops
python music_generator.py \
  --prompt "dark techno with industrial sounds" \
  --bpm 128 \
  --variations 8 \
  --max-duration 6 \
  --temperature 1.8

# 2. Use complex pattern with 8 variations
python audio_concatenator.py generation_20241201_143515_456 \
  --pattern "AABBCCDDEEFFGGHHIIJJAABBCCDDEEFFGGHH"

# Output: concatenated_generation_20241201_143515_456_AABBCCDDEEFFGGHHIIJJAABBCCDDEEFFGGHH.wav
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

After generation and concatenation, your directory will look like this:
```
project/
├── generation_20241201_143022_123/
│   ├── replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m-0.wav
│   ├── replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m-1.wav
│   ├── replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m-2.wav
│   ├── replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m-3.wav
│   ├── ... (up to 20 files depending on variations)
│   └── metadata.txt
├── concatenated_generation_20241201_143022_123_AABBAACCDDAA.wav
├── concatenated_generation_20241201_143022_123_ABACADABACAD.wav
├── concatenated_generation_20241201_143515_456_AABBCCDDEEFFGGHH.wav
├── music_generator.py
├── audio_concatenator.py
└── .env
```

**Note**: Multiple concatenated files can be created from the same generation folder using different patterns. 