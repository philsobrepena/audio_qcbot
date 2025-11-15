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

import sys
import os
import json

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "pydub", "pydub-master"))

from pydub import AudioSegment
from validate import (
    validate_cache_formats,
    validate_cache_loudness,
    validate_low_sample_rates,
)
from config.acceptable_formats import LOUDNESS_TARGET
from reset import to_48k_32bit_wav_target_loudness, to_48k_32bit_wav

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


new_dir = "audio_reformatted"
needs_loudness = validate_cache_loudness()
needs_reformatting = validate_cache_formats()
low_sample_rate_files = validate_low_sample_rates()

filenames_for_loudness_and_autoformat = []
files_to_reformat = needs_reformatting - needs_loudness.keys()
skipped_low_sample_rate_files = {}

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

    convert_decision = input(
        "Convert these files to 48000 Hz? " "[Y] to convert, [N] to skip: "
    ).lower()

    if convert_decision != "y":
        print(
            "\n✓ Skipping conversion for low sample rate files. "
            "They will be noted in the report."
        )
        for filename in low_sample_rate_files.keys():
            skipped_low_sample_rate_files[filename] = low_sample_rate_files[filename]
            if filename in needs_reformatting:
                needs_reformatting.remove(filename)
        files_to_reformat = needs_reformatting - needs_loudness.keys()
    else:
        print("\n✓ Low sample rate files will be upsampled to 48000 Hz.")

    print("\n")
else:
    print("✓ All files meet the minimum sample rate requirement.\n")

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
    conversion = to_48k_32bit_wav_target_loudness(sound, difference, name)
    conversion.export(f"{new_dir}/{name}", format="wav")

for name in files_to_reformat:
    sound = AudioSegment.from_file(f"{directory}/{name}")
    conversion = to_48k_32bit_wav(sound, name)
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
        "sample_rate": "48000",
        "bits_per_sample": "32",
        "loudness": LOUDNESS_TARGET,
        "duration": audioinfo[filename]["duration"],
    }

for filename in files_to_reformat:
    exported_name = filename
    duration = float(audioinfo[filename]["duration"])
    total_duration_original += duration
    total_duration_fixed += duration
    report_data[exported_name] = {
        "sample_rate": "48000",
        "bits_per_sample": "32",
        "loudness": audioinfo[filename]["loudness"],
        "duration": audioinfo[filename]["duration"],
    }

for filename, info in audioinfo.items():
    if (
        filename not in filenames_for_loudness_and_autoformat
        and filename not in files_to_reformat
    ):
        total_duration_original += float(info["duration"])


def print_report(
    report_data,
    total_duration_original,
    total_duration_fixed,
    skipped_low_sample_rate_files,
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

    if skipped_low_sample_rate_files:
        num_skipped = len(skipped_low_sample_rate_files)
        print(f"\n⚠️  Files Skipped (Low Sample Rate): {num_skipped}")
        for filename, info in skipped_low_sample_rate_files.items():
            print(f"  • {filename} ({info['original_sample_rate']} Hz)")

    print("\nDuration Summary:")
    orig_mins = total_duration_original / 60
    fixed_mins = total_duration_fixed / 60
    coverage = total_duration_fixed / total_duration_original * 100
    print(
        f"  - Original Files (All): {total_duration_original:.2f} "
        f"seconds ({orig_mins:.2f} minutes)"
    )
    print(
        f"  - Fixed/Exported Files: {total_duration_fixed:.2f} "
        f"seconds ({fixed_mins:.2f} minutes)"
    )
    print(f"  - Coverage: {coverage:.1f}% of total duration")
    print("=" * 80 + "\n")

    for filename, data in report_data.items():
        print(f"File: {filename}")
        print(f"  Sample Rate    : {data['sample_rate']} Hz")
        print(f"  Bit Depth      : {data['bits_per_sample']} bit")
        print(f"  Loudness       : {data['loudness']:.2f} dBFS")
        print(f"  Duration       : {data['duration']} s")
        print("-" * 80 + "\n")


print_report(
    report_data,
    total_duration_original,
    total_duration_fixed,
    skipped_low_sample_rate_files,
)

save_report = input("\nSave report to JSON? [Y] or [N]: ").lower()
if save_report == "y":
    export_report = {
        "summary": {
            "total_files_original": len(audioinfo),
            "total_files_exported": len(report_data),
            "files_with_gain": len(filenames_for_loudness_and_autoformat),
            "files_reformat_only": len(files_to_reformat),
            "files_skipped_low_sample_rate": len(skipped_low_sample_rate_files),
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
        "skipped_files": {"low_sample_rate": skipped_low_sample_rate_files},
    }
    with open("export_report.json", "w") as f:
        json.dump(export_report, f, indent=4)
    print("✓ Report saved to export_report.json")
