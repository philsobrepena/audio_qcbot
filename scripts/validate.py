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

directory = sys.argv[1]
content = os.listdir(directory)


filename = "audioinfo.json"
audioinfo = None
try:
    with open(filename, "r") as f:
        audioinfo = json.load(f)
except FileNotFoundError:
    print(f"Error: {filename} not found. Run cache script first.")
    sys.exit(1)


def validate_cache_loudness():
    needs_gain = {}
    too_loud = {}
    for i in audioinfo:
        loudness = audioinfo[i]["loudness"]

        if loudness < LOUDNESS_THRESHOLD_MIN:
            difference = LOUDNESS_TARGET - loudness
            needs_gain[i] = [difference, i]

        if loudness > LOUDNESS_THRESHOLD_MAX:
            difference = loudness - LOUDNESS_THRESHOLD_MAX
            too_loud[i] = [difference, i]
            print(
                f"""{i} is too loud at {loudness}:
            Exceeds threshold {LOUDNESS_THRESHOLD_MAX} by {difference}
"""
            )
    return needs_gain, too_loud


def validate_cache_formats():
    needs_reformatting = set()
    for i in content:
        info = audioinfo[i]
        if info["format_name"] != VALID_FORMAT_NAME:
            print(f"🫨 {info['format_name']} file found.")
        if (
            info["sample_rate"] != VALID_SAMPLE_RATE
            or info["bits_per_sample"] != VALID_BITS_PER_SAMPLE
        ):
            needs_reformatting.add(i)
    return needs_reformatting


def validate_low_sample_rates():
    """
    Detect files with sample rates below the acceptable rate.
    Returns a dict with filename and original sample rate for reporting.
    """
    low_sample_rate_files = {}
    acceptable_rate = int(VALID_SAMPLE_RATE)

    for i in content:
        info = audioinfo[i]
        current_rate = int(info["sample_rate"])

        if current_rate < acceptable_rate:
            low_sample_rate_files[i] = {
                "original_sample_rate": current_rate,
                "target_sample_rate": acceptable_rate,
            }

    return low_sample_rate_files


def validate_low_bit_depth():
    """
    Detect files with bit depths below the minimum acceptable threshold.
    Converting from very low bit depths (like 16-bit) to 32-bit can create artifacts.
    Returns a dict with filename and original bit depth for reporting.
    """
    low_bit_depth_files = {}

    for i in content:
        info = audioinfo[i]
        current_bits = int(info["bits_per_sample"])

        if current_bits < BIT_DEPTH_THRESHOLD_MIN:
            low_bit_depth_files[i] = {
                "original_bit_depth": current_bits,
                "target_bit_depth": int(VALID_BITS_PER_SAMPLE),
            }

    return low_bit_depth_files


def validate_all():
    validate_cache_formats()
    validate_cache_loudness()


validate_all()
