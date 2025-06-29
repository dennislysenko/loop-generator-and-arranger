#!/usr/bin/env python3
"""
Audio Concatenator Script
Concatenates 4 audio files in AABBAACCDDAA pattern using ffmpeg
"""

import subprocess
import os
import sys

def get_audio_files():
    """Get the 4 audio files in the current directory"""
    base_name = "replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m"
    files = []
    for i in range(4):
        filename = f"{base_name}-{i}.wav"
        if not os.path.exists(filename):
            print(f"Error: {filename} not found!")
            sys.exit(1)
        files.append(filename)
    return files

def create_concat_file(audio_files, pattern="AABBAACCDDAA"):
    """Create a text file for ffmpeg concat demuxer"""
    # Map pattern letters to file indices
    pattern_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    
    concat_list = []
    for char in pattern:
        if char in pattern_map:
            file_index = pattern_map[char]
            concat_list.append(audio_files[file_index])
    
    # Write concat file
    concat_filename = "concat_list.txt"
    with open(concat_filename, 'w') as f:
        for audio_file in concat_list:
            f.write(f"file '{audio_file}'\n")
    
    print(f"Created concat list with pattern: {pattern}")
    print(f"Sequence: {' -> '.join([audio_files[pattern_map[c]] for c in pattern])}")
    
    return concat_filename

def concatenate_audio(concat_file, output_file="concatenated_audio.wav"):
    """Use ffmpeg to concatenate the audio files"""
    cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-c', 'copy',  # Copy without re-encoding for speed
        '-y',  # Overwrite output file if it exists
        output_file
    ]
    
    print(f"Running ffmpeg command:")
    print(" ".join(cmd))
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Success! Created {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg: {e}")
        print(f"stderr: {e.stderr}")
        return False

def get_output_info(output_file):
    """Get information about the output file"""
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', output_file]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import json
        info = json.loads(result.stdout)
        duration = float(info['format']['duration'])
        size = int(info['format']['size'])
        print(f"\nOutput file info:")
        print(f"Duration: {duration:.1f} seconds")
        print(f"Size: {size:,} bytes ({size/1024/1024:.1f} MB)")
    except Exception as e:
        print(f"Could not get output file info: {e}")

def main():
    print("Audio Concatenator - AABBAACCDDAA Pattern")
    print("=" * 40)
    
    # Get audio files
    audio_files = get_audio_files()
    print(f"Found audio files:")
    for i, file in enumerate(audio_files):
        print(f"  {chr(65+i)} ({i}): {file}")
    
    # Create concat file
    concat_file = create_concat_file(audio_files)
    
    # Concatenate
    output_file = "concatenated_AABBAACCDDAA.wav"
    success = concatenate_audio(concat_file, output_file)
    
    if success:
        get_output_info(output_file)
        
        # Clean up
        os.remove(concat_file)
        print(f"\nCleaned up temporary file: {concat_file}")
        
        print(f"\n✅ Successfully created: {output_file}")
        print(f"Pattern used: AABBAACCDDAA")
        print(f"Expected duration: 12 files × 12 seconds = 144 seconds (2.4 minutes)")
    else:
        print("❌ Concatenation failed")

if __name__ == "__main__":
    main() 