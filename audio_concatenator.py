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
    """Get all available audio files from the specified folder or current directory"""
    base_name = "replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m"
    files = []
    
    # Check for files 0-19 (supporting up to 20 variations)
    for i in range(20):
        if folder_path:
            filename = os.path.join(folder_path, f"{base_name}-{i}.wav")
        else:
            filename = f"{base_name}-{i}.wav"
        
        if os.path.exists(filename):
            files.append(filename)
        else:
            break  # Stop at first missing file (assumes sequential naming)
    
    if len(files) < 2:
        print(f"Error: Need at least 2 files for concatenation, found {len(files)}")
        sys.exit(1)
        
    return files

def validate_pattern(pattern, num_files):
    """Validate that the pattern only contains valid letters for available files"""
    # Generate valid characters based on number of files (A, B, C, D, E, F, ...)
    valid_chars = set(chr(65 + i) for i in range(num_files))  # A=65, B=66, etc.
    pattern_chars = set(pattern.upper())
    
    if not pattern_chars.issubset(valid_chars):
        invalid_chars = pattern_chars - valid_chars
        available = ', '.join(sorted(valid_chars))
        raise ValueError(f"Invalid characters in pattern: {invalid_chars}. Available letters: {available}")
    
    return pattern.upper()

def create_concat_file(audio_files, pattern="AABBAACCDDAA"):
    """Create a text file for ffmpeg concat demuxer"""
    # Map pattern letters to file indices based on available files
    pattern_map = {chr(65 + i): i for i in range(len(audio_files))}  # A=0, B=1, C=2, etc.
    
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
    
    # Get audio files first to know how many we have
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
    
    # Validate and normalize pattern based on available files
    try:
        pattern = validate_pattern(args.pattern, len(audio_files))
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
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