"""
export.py - Audio file export with format standardization and loudness
normalization.

natively pydub exports at 44.1k 16-bit
so we will always run a 48k / 32-bit export for all files regardless if
they are already 48k or 32-bit.

if gain changes do not need to be applied, we do not have to specify gain.

REFERENCE: assuming an export above 44.1 / 16-bit:

    GAIN ONLY changes need to reformat BIT DEPTH and SAMPLE RATE
    BIT DEPTH ONLY changes need to reformat BIT DEPTH and SAMPLE RATE
    SAMPLE RATE ONLY changes need to reformat BIT DEPTH and SAMPLE RATE

    SAMPLE RATE AND BIT DEPTH ONLY changes do NOT need gain applied.
"""

import json
import os
import sys
from pathlib import Path

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "pydub", "pydub-master"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.acceptable_formats import (
    LOUDNESS_TARGET,
    LOUDNESS_THRESHOLD_MAX,
    LOUDNESS_THRESHOLD_MIN,
    VALID_BITS_PER_SAMPLE,
    VALID_FORMAT_NAME,
    VALID_SAMPLE_RATE,
    BIT_DEPTH_THRESHOLD_MIN,
)

from pydub import AudioSegment
from reset import (
    reformat_by_config,
    reformat_by_config_with_gain,
)
from validate import (
    validate_cache_formats,
    validate_cache_loudness,
    validate_low_sample_rates,
    validate_low_bit_depth,
)

filename = "audioinfo.json"
audioinfo = None
try:
    with open(filename, "r") as f:
        audioinfo = json.load(f)
except FileNotFoundError:
    print(f"Error: {filename} not found. Run cache script first.")
    sys.exit(1)

directory = sys.argv[1]
content = os.listdir(directory)


def clear():
    os.system("cls")


def seconds_to_timecode(seconds):
    """Convert seconds to HH:MM:SS timecode format (no decimals)."""
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


new_dir = "audio_reformatted"
needs_loudness, too_loud = validate_cache_loudness()
needs_reformatting = validate_cache_formats()
low_sample_rate_files = validate_low_sample_rates()
low_bit_depth_files = validate_low_bit_depth()

filenames_for_loudness_and_autoformat = []
skipped_low_sample_rate_files = {}
skipped_low_bit_depth_files = {}
skipped_loud_files = {}
accepted_files = {}

if too_loud:
    print("\n" + "=" * 80)
    print("⚠️  EXCESSIVE LOUDNESS DETECTED".center(80))
    print("=" * 80 + "\n")
    num_files = len(too_loud)
    print(f"Found {num_files} file(s) exceeding loudness threshold ({LOUDNESS_THRESHOLD_MAX} dBFS):\n")

    for filename, info in too_loud.items():
        loudness_value = audioinfo[filename]['loudness']
        difference = info[0]
        print(f"  • {filename}")
        print(f"    Loudness: {loudness_value:.2f} dBFS → Exceeds by {difference:.2f} dB")

        skipped_loud_files[filename] = {
            'loudness': loudness_value,
            'threshold': LOUDNESS_THRESHOLD_MAX,
            'exceeds_by': difference
        }

        if filename in needs_loudness:
            del needs_loudness[filename]
        if filename in needs_reformatting:
            needs_reformatting.remove(filename)

    print("\n" + "-" * 80)
    print("\nNOTE: Files exceeding maximum loudness cannot be automatically fixed.")
    print("Manual adjustment or source file replacement is required.")
    print("-" * 80 + "\n")
    print("✓ Skipping export for excessively loud files. They will be noted in the report.\n")
else:
    print("✓ All files are within acceptable loudness range.\n")


files_to_reformat = needs_reformatting - needs_loudness.keys()

bits_per_sample = VALID_BITS_PER_SAMPLE

if bits_per_sample == "32":
    sample_width = 4
elif bits_per_sample == "24":
    sample_width = 3
elif bits_per_sample == "16":
    sample_width = 2
else:
    sample_width = 4  # Default to 32-bit

frame_rate = int(VALID_SAMPLE_RATE) if VALID_SAMPLE_RATE else 48000


if low_sample_rate_files:
    clear()
    print("\n" + "=" * 80)
    print("⚠️  LOW SAMPLE RATE FILES DETECTED".center(80))
    print("=" * 80 + "\n")
    num_files = len(low_sample_rate_files)
    print(f"Found {num_files} file(s) with sample rates below " f"48000 Hz:\n")

    for filename, info in low_sample_rate_files.items():
        print(f"  • {filename}")
        print(
            f"    Current: {info['original_sample_rate']} Hz → "
            f"Target: {info['target_sample_rate']} Hz"
        )

    print("\n" + "-" * 80)
    print(
        "\nNOTE: Upsampling from lower sample rates does not " "improve audio quality."
    )
    print(
        "It only converts the format but cannot recover missing "
        "frequency information."
    )
    print("-" * 80 + "\n")

    print(
        "\n✓ Skipping conversion for low sample rate files. "
        "They will be noted in the report."
    )
    for filename in low_sample_rate_files.keys():
        skipped_low_sample_rate_files[filename] = low_sample_rate_files[filename]
        if filename in needs_reformatting:
            needs_reformatting.remove(filename)
        if filename in needs_loudness:
            del needs_loudness[filename]
    files_to_reformat = needs_reformatting - needs_loudness.keys()

    print("\n")

else:
    print("✓ All files meet the minimum sample rate requirement.\n")

if low_bit_depth_files:
    print("\n" + "=" * 80)
    print("⚠️  LOW BIT DEPTH FILES DETECTED".center(80))
    print("=" * 80 + "\n")
    num_files = len(low_bit_depth_files)
    print(f"Found {num_files} file(s) with bit depth below {BIT_DEPTH_THRESHOLD_MIN}-bit:\n")

    for filename, info in low_bit_depth_files.items():
        print(f"  • {filename}")
        print(
            f"    Current: {info['original_bit_depth']}-bit → "
            f"Target: {info['target_bit_depth']}-bit"
        )

    print("\n" + "-" * 80)
    print(
        "\nNOTE: Converting from very low bit depths (e.g., 16-bit) to 32-bit"
    )
    print("can create artifacts. Source files should be re-recorded or replaced.")
    print("-" * 80 + "\n")

    print(
        "\n✓ Skipping conversion for low bit depth files. "
        "They will be noted in the report."
    )
    for filename in low_bit_depth_files.keys():
        skipped_low_bit_depth_files[filename] = low_bit_depth_files[filename]
        if filename in needs_reformatting:
            needs_reformatting.remove(filename)
        if filename in needs_loudness:
            del needs_loudness[filename]
    files_to_reformat = needs_reformatting - needs_loudness.keys()

    print("\n")

else:
    print("✓ All files meet the minimum bit depth requirement.\n")

for file in needs_loudness:
    print(
        f"""
    configuring {file} for loudness and checking requirements for
    auto-formatting...
    """
    )
    filenames_for_loudness_and_autoformat.append(file)

for filename in filenames_for_loudness_and_autoformat:
    args = needs_loudness[filename]
    sound = AudioSegment.from_file(f"{directory}/{filename}")
    difference = args[0]
    name = args[1]
    conversion = reformat_by_config_with_gain(sound, difference, name, sample_width, frame_rate)
    if sample_width == 3:
        conversion.export(f"{new_dir}/{name}", format="wav", parameters=["-acodec", "pcm_s24le"])
    else:
        conversion.export(f"{new_dir}/{name}", format="wav")

for name in files_to_reformat:
    sound = AudioSegment.from_file(f"{directory}/{name}")
    conversion = reformat_by_config(sound, sample_width, frame_rate)
    if sample_width == 3:
        conversion.export(f"{new_dir}/{name}", format="wav", parameters=["-acodec", "pcm_s24le"])
    else:
        conversion.export(f"{new_dir}/{name}", format="wav")


# Report data collection
#########################################################################

report_data = {}
total_duration_original = 0.0
total_duration_fixed = 0.0

for filename in filenames_for_loudness_and_autoformat:
    exported_name = filename
    duration = float(audioinfo[filename]["duration"])
    total_duration_original += duration
    total_duration_fixed += duration
    report_data[exported_name] = {
        "original": {
            "sample_rate": audioinfo[filename]["sample_rate"],
            "bits_per_sample": audioinfo[filename]["bits_per_sample"],
            "loudness": audioinfo[filename]["loudness"],
            "duration": audioinfo[filename]["duration"],
        },
        "exported": {
            "sample_rate": "48000",
            "bits_per_sample": "32",
            "loudness": LOUDNESS_TARGET,
            "duration": audioinfo[filename]["duration"],
        }
    }

for filename in files_to_reformat:
    exported_name = filename
    duration = float(audioinfo[filename]["duration"])
    total_duration_original += duration
    total_duration_fixed += duration
    report_data[exported_name] = {
        "original": {
            "sample_rate": audioinfo[filename]["sample_rate"],
            "bits_per_sample": audioinfo[filename]["bits_per_sample"],
            "loudness": audioinfo[filename]["loudness"],
            "duration": audioinfo[filename]["duration"],
        },
        "exported": {
            "sample_rate": "48000",
            "bits_per_sample": "32",
            "loudness": audioinfo[filename]["loudness"],
            "duration": audioinfo[filename]["duration"],
        }
    }

for filename, info in audioinfo.items():
    if (
        filename not in filenames_for_loudness_and_autoformat
        and filename not in files_to_reformat
        and filename not in skipped_low_sample_rate_files
        and filename not in skipped_low_bit_depth_files
        and filename not in skipped_loud_files
    ):
        total_duration_original += float(info["duration"])
        accepted_files[filename] = {
            "sample_rate": info["sample_rate"],
            "bits_per_sample": info["bits_per_sample"],
            "loudness": info["loudness"],
            "duration": info["duration"],
        }


def print_report(
    report_data,
    total_duration_original,
    total_duration_fixed,
    skipped_low_sample_rate_files,
    skipped_low_bit_depth_files,
    skipped_loud_files,
    accepted_files,
):
    clear()
    print("\n" + "=" * 80)
    print("EXPORT REPORT".center(80))
    print("=" * 80 + "\n")

    total_files = len(report_data)
    total_files_original = len(audioinfo)
    files_with_gain = len(filenames_for_loudness_and_autoformat)
    files_reformat_only = len(files_to_reformat)

    print(f"Total Files in Project: {total_files_original}")
    print(f"Total Files Exported: {total_files}")
    print(f"  - With Gain Applied: {files_with_gain}")
    print(f"  - Reformat Only: {files_reformat_only}")

    if accepted_files:
        num_accepted = len(accepted_files)
        print(f"\n✅ Files Accepted (Already Meet Standards): {num_accepted}")
        for filename, info in accepted_files.items():
            print(f"  • {filename} ({info['sample_rate']} Hz, {info['bits_per_sample']}-bit, {info['loudness']:.2f} dBFS)")

    if skipped_low_sample_rate_files:
        num_skipped = len(skipped_low_sample_rate_files)
        print(f"\n⚠️  Files Skipped (Low Sample Rate): {num_skipped}")
        for filename, info in skipped_low_sample_rate_files.items():
            print(f"  • {filename} ({info['original_sample_rate']} Hz)")
    if skipped_low_bit_depth_files:
        num_skipped = len(skipped_low_bit_depth_files)
        print(f"\n⚠️  Files Skipped (Low Bit Depth): {num_skipped}")
        for filename, info in skipped_low_bit_depth_files.items():
            print(f"  • {filename} ({info['original_bit_depth']}-bit)")
    if skipped_loud_files:
        num_skipped = len(skipped_loud_files)
        print(f"\n⚠️  Files Skipped (Excessive Loudness): {num_skipped}")
        for filename, info in skipped_loud_files.items():
            print(f"  • {filename} ({info['loudness']:.2f} dBFS, exceeds by {info['exceeds_by']:.2f} dB)")

    print("\nDuration Summary:")
    orig_mins = total_duration_original / 60
    fixed_mins = total_duration_fixed / 60
    orig_timecode = seconds_to_timecode(total_duration_original)
    fixed_timecode = seconds_to_timecode(total_duration_fixed)

    print(
        f"  - Original Files (All): {total_duration_original:.2f} "
        f"seconds ({orig_mins:.2f} minutes) [{orig_timecode}]"
    )
    print(
        f"  - Fixed/Exported Files: {total_duration_fixed:.2f} "
        f"seconds ({fixed_mins:.2f} minutes) [{fixed_timecode}]"
    )
    print("=" * 80 + "\n")

    for filename, data in report_data.items():
        print(f"File: {filename}")
        print(f"  Sample Rate    : {data['original']['sample_rate']} Hz → {data['exported']['sample_rate']} Hz")
        print(f"  Bit Depth      : {data['original']['bits_per_sample']} bit → {data['exported']['bits_per_sample']} bit")
        print(f"  Loudness       : {data['original']['loudness']:.2f} dBFS → {data['exported']['loudness']:.2f} dBFS")
        print(f"  Duration       : {data['original']['duration']} s")
        print("-" * 80 + "\n")


print_report(
    report_data,
    total_duration_original,
    total_duration_fixed,
    skipped_low_sample_rate_files,
    skipped_low_bit_depth_files,
    skipped_loud_files,
    accepted_files,
)

save_report = input("\nSave report to JSON? [Y] or [N]: ").lower()
if save_report == "y":
    export_report = {
        "summary": {
            "total_files_original": len(audioinfo),
            "total_files_exported": len(report_data),
            "files_accepted": len(accepted_files),
            "files_with_gain": len(filenames_for_loudness_and_autoformat),
            "files_reformat_only": len(files_to_reformat),
            "files_skipped_low_sample_rate": len(skipped_low_sample_rate_files),
            "files_skipped_low_bit_depth": len(skipped_low_bit_depth_files),
            "duration_original_seconds": round(total_duration_original, 2),
            "duration_original_minutes": round(total_duration_original / 60, 2),
            "duration_fixed_seconds": round(total_duration_fixed, 2),
            "duration_fixed_minutes": round(total_duration_fixed / 60, 2),
            "coverage_percentage": (
                round(
                    (total_duration_fixed / total_duration_original * 100),
                    2,
                )
                if total_duration_original > 0
                else 0
            ),
        },
        "exported_files": report_data,
        "accepted_files": accepted_files,
        "skipped_files": {
            "low_sample_rate": skipped_low_sample_rate_files,
            "low_bit_depth": skipped_low_bit_depth_files,
            "too_loud": skipped_loud_files
        },
    }
    with open("export_report.json", "w") as f:
        json.dump(export_report, f, indent=4)
    print("✓ Report saved to export_report.json")
