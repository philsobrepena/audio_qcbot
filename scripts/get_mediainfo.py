"""
get mediainfo for file collection and cache for use across modules
"""

import sys
import os
import json
from multiprocessing import Pool

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "pydub", "pydub-master"))
from pydub import AudioSegment
from pydub.utils import mediainfo
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config.acceptable_formats import VALID_FORMAT_NAMES

directory = sys.argv[1]
content = os.listdir(directory)

audioinfo = {}
media_info_data = ["sample_rate", "bits_per_sample", "format_name", "size", "duration"]

filename = "audioinfo.json"
if directory == "audio":
    filename = "audioinfo.json"
elif directory == "audio_reformatted":
    filename = "audioinfo_reformatted.json"


def process_single_file(args):
    """
    Process a single audio file - extracts metadata and calculates loudness.
    Runs in parallel workers. Returns warnings instead of printing to avoid collision.

    Args:
        args: tuple of (filename, directory)

    Returns:
        tuple: (filename, info_dict, warnings_list) or (filename, None, error_list)
    """
    file, directory = args
    warnings = []

    try:
        info = {}
        for field in media_info_data:
            value = mediainfo(f"{directory}/{file}")[field]
            info[field] = value
            if field == "format_name" and value not in VALID_FORMAT_NAMES:
                warnings.append(f"Non-standard format: {value}")

        sound = AudioSegment.from_file(f"{directory}/{file}")
        info["loudness"] = sound.dBFS

        return (file, info, warnings)

    except Exception as e:
        return (file, None, [f"Error: {str(e)}"])


if __name__ == "__main__":

    def clear():
        os.system("cls")

    print("\n" + "=" * 60)
    print(f"Processing {len(content)} audio files with 8 workers...")
    print("=" * 60 + "\n")

    audioinfo = {}

    with Pool(processes=8) as pool:
        file_args = [(file, directory) for file in content]

        for i, (file, info, warnings) in enumerate(
            pool.imap(process_single_file, file_args), 1
        ):
            if info is not None:
                audioinfo[file] = info

                clear()
                print(f"Progress: [{i}/{len(content)}]")
                print("=" * 60)
                print(f"✓ Completed: {file}")
                print("-" * 60)
                print(f"  Sample Rate : {info['sample_rate']} Hz")
                print(f"  Bit Depth   : {info['bits_per_sample']} bit")
                print(f"  Loudness    : {info['loudness']:.2f} dBFS")
                print(f"  Duration    : {info['duration']} s")

                # Display warnings from worker (safe - only main process prints)
                if warnings:
                    print("-" * 60)
                    for warning in warnings:
                        print(f"  🫨 {warning}")

                print("=" * 60 + "\n")
            else:
                # Display errors from worker
                print(f"\n⚠️  Skipped (error): {file}")
                for error in warnings:
                    print(f"     {error}")

    clear()
    print("\n" + "=" * 60)
    print("CACHING COMPLETE".center(60))
    print("=" * 60 + "\n")

    total_duration = 0
    successful_files = 0

    for file, info in audioinfo.items():
        total_duration += float(info["duration"])
        successful_files += 1

    failed_files = len(content) - successful_files

    print(f"  Total Files      : {len(content)}")
    print(f"  ✓ Successful     : {successful_files}")
    if failed_files > 0:
        print(f"  ❌ Failed        : {failed_files}")
    print(f"  Total Duration   : {total_duration:.2f} seconds")
    print(f"\n  Saving to: {filename}")
    print("=" * 60 + "\n")

    # Write cache to JSON
    with open(filename, "w") as json_file:
        json.dump(audioinfo, json_file, indent=4)

    print("✓ Cache saved successfully!\n")
