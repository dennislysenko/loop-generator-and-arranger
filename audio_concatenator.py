#!/usr/bin/env python3
"""
Audio Concatenator Script
Concatenates 4 audio files in customizable patterns using ffmpeg
"""

import subprocess
import os
import sys
import argparse

def get_audio_files(folder_path=None):
    """Get the 4 audio files from the specified folder or current directory"""
    base_name = "replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m"
    files = []
    
    for i in range(4):
        if folder_path:
            filename = os.path.join(folder_path, f"{base_name}-{i}.wav")
        else:
            filename = f"{base_name}-{i}.wav"
        
        if not os.path.exists(filename):
            print(f"Error: {filename} not found!")
            sys.exit(1)
        files.append(filename)
    return files

def validate_pattern(pattern):
    """Validate that the pattern only contains A, B, C, D"""
    valid_chars = set('ABCD')
    pattern_chars = set(pattern.upper())
    
    if not pattern_chars.issubset(valid_chars):
        invalid_chars = pattern_chars - valid_chars
        raise ValueError(f"Invalid characters in pattern: {invalid_chars}. Only A, B, C, D are allowed.")
    
    return pattern.upper()

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
    print(f"Sequence: {' -> '.join([os.path.basename(audio_files[pattern_map[c]]) for c in pattern])}")
    print(f"Total segments: {len(pattern)}")
    
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
        print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"Size: {size:,} bytes ({size/1024/1024:.1f} MB)")
        return duration
    except Exception as e:
        print(f"Could not get output file info: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Concatenate audio files in custom patterns")
    parser.add_argument("folder", nargs='?', help="Folder containing audio files (optional)")
    parser.add_argument("--pattern", "-p", default="AABBAACCDDAA", help="Pattern for concatenation (default: AABBAACCDDAA)")
    
    args = parser.parse_args()
    
    print("Audio Concatenator - Custom Pattern Support")
    print("=" * 45)
    
    # Validate and normalize pattern
    try:
        pattern = validate_pattern(args.pattern)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Check for folder path
    folder_path = args.folder
    if folder_path and not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' not found!")
        sys.exit(1)
    
    if folder_path:
        print(f"Using folder: {folder_path}")
    else:
        print("Using current directory")
    
    # Get audio files
    audio_files = get_audio_files(folder_path)
    print(f"\nFound audio files:")
    for i, file in enumerate(audio_files):
        print(f"  {chr(65+i)} ({i}): {os.path.basename(file)}")
    
    # Create concat file
    print(f"\nUsing pattern: {pattern}")
    concat_file = create_concat_file(audio_files, pattern)
    
    # Generate output filename
    if folder_path:
        folder_name = os.path.basename(folder_path.rstrip(os.sep))
        output_file = f"concatenated_{folder_name}_{pattern}.wav"
    else:
        output_file = f"concatenated_{pattern}.wav"
    
    print(f"\nOutput file: {output_file}")
    
    # Concatenate
    success = concatenate_audio(concat_file, output_file)
    
    if success:
        duration = get_output_info(output_file)
        
        # Clean up
        os.remove(concat_file)
        print(f"Cleaned up temporary file: {concat_file}")
        
        print(f"\n✅ Successfully created: {output_file}")
        print(f"Pattern used: {pattern}")
        if duration:
            avg_segment_duration = duration / len(pattern)
            print(f"Average segment duration: {avg_segment_duration:.1f} seconds")
    else:
        print("❌ Concatenation failed")

if __name__ == "__main__":
    main() 