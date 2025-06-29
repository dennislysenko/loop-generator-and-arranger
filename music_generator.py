#!/usr/bin/env python3
"""
Music Generator Script
Uses Replicate's musicgen-looper model to generate 4 audio files
"""

import os
import sys
import replicate
from typing import List, Optional, Tuple
import time
import argparse
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_replicate_token():
    """Check if REPLICATE_API_TOKEN is set"""
    token = os.getenv('REPLICATE_API_TOKEN')
    if not token:
        print("❌ Error: REPLICATE_API_TOKEN environment variable not set!")
        print("Please set it with: export REPLICATE_API_TOKEN=<your-token>")
        print("Get your token from: https://replicate.com/account/api-tokens")
        sys.exit(1)
    return token

def get_existing_prediction(prediction_id: str) -> Tuple[List, str]:
    """
    Fetch results from an existing prediction
    
    Args:
        prediction_id: Existing prediction ID to fetch
    
    Returns:
        Tuple of (file outputs, prediction_id)
    """
    
    print(f"🔄 Fetching existing prediction: {prediction_id}")
    
    try:
        prediction = replicate.predictions.get(prediction_id)
        
        if prediction.status == 'succeeded':
            print(f"✅ Found completed prediction with {len(prediction.output)} audio files")
            return prediction.output, prediction_id
        elif prediction.status in ['starting', 'processing']:
            print(f"⏳ Prediction is still running (status: {prediction.status}), waiting...")
            prediction.wait()
            if prediction.status == 'succeeded':
                print(f"✅ Prediction completed with {len(prediction.output)} audio files")
                return prediction.output, prediction_id
            else:
                print(f"❌ Prediction failed with status: {prediction.status}")
                return [], ""
        else:
            print(f"❌ Prediction has status: {prediction.status}")
            return [], ""
        
    except Exception as e:
        print(f"❌ Error fetching prediction: {e}")
        return [], ""

def generate_music_loop(config: dict) -> Tuple[List, str]:
    """
    Generate music loop using musicgen-looper model
    
    Args:
        config: Dictionary containing all generation parameters
    
    Returns:
        Tuple of (file outputs, prediction_id)
    """
    
    print(f"🎵 Generating music with prompt: '{config['prompt']}'")
    print(f"   BPM: {config['bpm']}, Variations: {config['variations']}")
    print(f"   Max Duration: {config['max_duration']}s, Model: {config['model_version']}")
    print(f"   Temperature: {config['temperature']}, CFG: {config['classifier_free_guidance']}")
    
    try:
        # Use replicate.run with specific version hash
        output = replicate.run(
            "andreasjansson/musicgen-looper:f8140d0457c2b39ad8728a80736fea9a67a0ec0cd37b35f40b68cce507db2366",
            input=config
        )
        
        print(f"✅ Successfully generated {len(output)} audio files")
        
        # Generate a timestamp-based ID since we don't have prediction ID
        timestamp_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return output, timestamp_id
        
    except Exception as e:
        print(f"❌ Error generating music: {e}")
        return [], ""

def download_audio_files(file_outputs: List, prediction_id: str, prompt: str = "", config: dict = None) -> Tuple[bool, str]:
    """
    Download audio files and save them in organized folders
    
    Args:
        file_outputs: List of URLs or FileOutput objects from Replicate
        prediction_id: Prediction ID from Replicate
        prompt: Music prompt used for folder naming
    
    Returns:
        Tuple of (success, folder_path)
    """
    
    if not file_outputs:
        print("❌ No audio files to download")
        return False, ""
    
    # Process the model output
    
    # Handle different output formats
    if isinstance(file_outputs, dict):
        print(f"🎵 Found {len(file_outputs)} variations: {', '.join(list(file_outputs.keys())[:5])}{'...' if len(file_outputs) > 5 else ''}")
        # Filter out None values and convert to list
        valid_outputs = [v for v in file_outputs.values() if v is not None]
        print(f"📁 {len(valid_outputs)} variations contain audio files, {len(file_outputs) - len(valid_outputs)} are empty")
        file_outputs = valid_outputs
    elif hasattr(file_outputs, '__iter__') and not isinstance(file_outputs, str):
        file_outputs = list(file_outputs)
        print(f"🔍 Processing {len(file_outputs)} files from iterable")
    else:
        print(f"❌ Unexpected file_outputs format: {type(file_outputs)}")
        return False, ""
    
    # Create folder name using prediction ID or timestamp as fallback
    if prediction_id:
        folder_name = f"generation_{prediction_id[:8]}"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"generation_{timestamp}"
    
    # Create the folder
    try:
        os.makedirs(folder_name, exist_ok=True)
        print(f"📁 Created folder: {folder_name}")
    except Exception as e:
        print(f"❌ Error creating folder: {e}")
        return False, ""
    
    print(f"📥 Downloading all {len(file_outputs)} audio files...")
    
    success_count = 0
    base_name = "replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m"
    
    for i, file_output in enumerate(file_outputs):
        filename = f"{base_name}-{i}.wav"
        filepath = os.path.join(folder_name, filename)
        
        try:
            print(f"   Downloading {filepath}...")
            
            # Handle both URL strings and FileOutput objects
            if isinstance(file_output, str):
                # It's a URL string, download it
                response = requests.get(file_output, stream=True)
                response.raise_for_status()
                audio_data = response.content
            else:
                # It's a FileOutput object, read it
                audio_data = file_output.read()
            
            # Write to file
            with open(filepath, 'wb') as f:
                f.write(audio_data)
            
            # Check file size
            file_size = os.path.getsize(filepath)
            print(f"   ✅ {filepath} saved ({file_size:,} bytes)")
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ Error downloading {filepath}: {e}")
    
    # Save metadata
    try:
        metadata_file = os.path.join(folder_name, "metadata.txt")
        with open(metadata_file, 'w') as f:
            f.write(f"Prediction ID: {prediction_id}\n")
            f.write(f"Prompt: {prompt}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Files downloaded: {success_count}\n")
            f.write(f"Total files from prediction: {len(file_outputs)}\n")
            
            # Add configuration details if available
            if config:
                f.write(f"\nGeneration Parameters:\n")
                f.write(f"  BPM: {config.get('bpm', 'N/A')}\n")
                f.write(f"  Variations: {config.get('variations', 'N/A')}\n")
                f.write(f"  Max Duration: {config.get('max_duration', 'N/A')}s\n")
                f.write(f"  Model Version: {config.get('model_version', 'N/A')}\n")
                f.write(f"  Temperature: {config.get('temperature', 'N/A')}\n")
                f.write(f"  CFG Scale: {config.get('classifier_free_guidance', 'N/A')}\n")
                f.write(f"  Output Format: {config.get('output_format', 'N/A')}\n")
                if config.get('seed', -1) != -1:
                    f.write(f"  Seed: {config.get('seed')}\n")
                
        print(f"   📄 Metadata saved to {metadata_file}")
    except Exception as e:
        print(f"   ⚠️  Could not save metadata: {e}")
    
    if success_count == len(file_outputs):
        print(f"🎉 All {success_count} files downloaded successfully!")
        return True, folder_name
    else:
        print(f"⚠️  Only {success_count}/{len(file_outputs)} files downloaded successfully")
        return False, folder_name

def get_file_info(filepath: str):
    """Get basic info about a downloaded file"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        return f"{filepath}: {size:,} bytes ({size/1024/1024:.1f} MB)"
    return f"{filepath}: File not found"

def main():
    parser = argparse.ArgumentParser(description="Generate music using Replicate musicgen-looper")
    parser.add_argument("--prompt", "-p", type=str, help="Music prompt")
    parser.add_argument("--bpm", "-b", type=int, default=120, help="BPM (default: 120, range: 40-300)")
    parser.add_argument("--variations", "-v", type=int, default=4, help="Number of variations (default: 4, range: 1-20)")
    parser.add_argument("--max-duration", "-d", type=int, default=8, help="Max duration per loop in seconds (default: 8, range: 2-20)")
    parser.add_argument("--model-version", "-m", type=str, default="medium", choices=["medium", "large"], help="Model version (default: medium)")
    parser.add_argument("--temperature", "-t", type=float, default=1.0, help="Temperature for diversity (default: 1.0, higher = more diverse)")
    parser.add_argument("--classifier-free-guidance", type=int, default=3, help="Adherence to prompt (default: 3, higher = more adherent)")
    parser.add_argument("--seed", type=int, default=-1, help="Seed for reproducibility (default: -1 for random)")
    parser.add_argument("--output-format", type=str, default="wav", choices=["wav", "mp3"], help="Output format (default: wav)")
    parser.add_argument("--prediction-id", type=str, help="Reuse existing prediction ID (saves credits)")
    
    args = parser.parse_args()
    
    print("🎼 Music Generator using Replicate musicgen-looper")
    print("=" * 50)
    
    # Check API token
    token = check_replicate_token()
    print(f"✅ Replicate API token found")
    
    # Configuration - use command line args or interactive prompts
    if args.prediction_id:
        # When reusing prediction, we don't need these parameters
        print(f"\n🔄 Reusing existing prediction: {args.prediction_id}")
        print("   (All parameters from original prediction)")
        config = None
    else:
        # Interactive mode for new generation
        if args.prompt:
            prompt = args.prompt
        else:
            prompt = input("Enter music prompt (or press Enter for default): ").strip()
            if not prompt:
                prompt = "upbeat electronic dance music loop"
        
        bpm = args.bpm
        if not args.prompt:  # Only ask for BPM if we're in interactive mode
            bpm_input = input(f"Enter BPM (or press Enter for {bpm}): ").strip()
            try:
                if bpm_input:
                    bpm = int(bpm_input)
            except ValueError:
                print(f"Invalid BPM, using default {bpm}")
        
        # Build configuration from args
        config = {
            "prompt": prompt,
            "bpm": bpm,
            "variations": args.variations,
            "max_duration": args.max_duration,
            "model_version": args.model_version,
            "temperature": args.temperature,
            "classifier_free_guidance": args.classifier_free_guidance,
            "output_format": args.output_format
        }
        
        # Add seed if specified
        if args.seed != -1:
            config["seed"] = args.seed
        
        print(f"\nConfiguration:")
        print(f"  Prompt: {config['prompt']}")
        print(f"  BPM: {config['bpm']}")
        print(f"  Variations: {config['variations']}")
        print(f"  Max Duration: {config['max_duration']}s")
        print(f"  Model Version: {config['model_version']}")
        print(f"  Temperature: {config['temperature']}")
        print(f"  CFG Scale: {config['classifier_free_guidance']}")
        print(f"  Output Format: {config['output_format']}")
        if args.seed != -1:
            print(f"  Seed: {config['seed']}")
    
    print()
    
    # Generate or fetch music
    start_time = time.time()
    
    if args.prediction_id:
        # Reuse existing prediction
        file_outputs, prediction_id = get_existing_prediction(args.prediction_id)
        if not file_outputs:
            print("❌ Failed to fetch existing prediction")
            sys.exit(1)
        print(f"🔄 Using existing prediction: {prediction_id}")
    else:
        # Generate new music
        file_outputs, prediction_id = generate_music_loop(config)
        if not file_outputs:
            print("❌ Failed to generate music files")
            sys.exit(1)
        
        generation_time = time.time() - start_time
        print(f"⏱️  Generation took {generation_time:.1f} seconds")
    
    # Download files
    success, folder_path = download_audio_files(file_outputs, prediction_id, config['prompt'] if config else "N/A", config)
    
    if success:
        print(f"\n📊 File Summary:")
        base_name = "replicate-prediction-ey6ew4zgddrj40cqqkcr4xnt0m"
        
        # Show all downloaded files to understand the structure
        files_found = []
        for filename in os.listdir(folder_path):
            if filename.startswith(base_name) and filename.endswith('.wav'):
                filepath = os.path.join(folder_path, filename)
                files_found.append(filename)
                print(f"  {get_file_info(filepath)}")
        
        print(f"\n🎯 Analysis:")
        print(f"   Total files downloaded: {len(files_found)}")
        print(f"   Folder: {folder_path}/")
        
        if len(files_found) >= 4:
            print(f"   ✅ Enough files for concatenator (needs 4, found {len(files_found)})")
            print(f"   Run concatenator with: python audio_concatenator.py {folder_path}")
            print(f"   Expected pattern: AABBAACCDDAA (uses first 4 files)")
            
            # Estimate total duration based on max_duration if available
            if config:
                estimated_duration = config['max_duration'] * 12  # AABBAACCDDAA pattern = 12 segments
                print(f"\n💡 With {config['max_duration']}s loops:")
                print(f"   Total concatenated duration: ~{estimated_duration} seconds ({estimated_duration/60:.1f} minutes)")
            else:
                print(f"\n💡 If each loop is ~8 seconds:")
                print(f"   Total concatenated duration: ~96 seconds (1.6 minutes)")
        else:
            print(f"   ⚠️  Not enough files for concatenator (needs 4, found {len(files_found)})")
        
    else:
        print("❌ Some files failed to download")
        sys.exit(1)

if __name__ == "__main__":
    main() 