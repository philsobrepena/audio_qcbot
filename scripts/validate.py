import sys
import os
import json
from pathlib import Path

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "pydub", "pydub-master"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.acceptable_formats import (
    LOUDNESS_THRESHOLD_MIN,
    LOUDNESS_TARGET,
    VALID_FORMAT_NAMES,
    VALID_SAMPLE_RATES,
    VALID_BITS_PER_SAMPLE,
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
    for i in audioinfo:
        if audioinfo[i]["loudness"] < LOUDNESS_THRESHOLD_MIN:
            cur = audioinfo[i]["loudness"]
            difference = LOUDNESS_TARGET - cur
            needs_gain[i] = [difference, i]
    return needs_gain


def validate_cache_formats():
    needs_reformatting = set()
    for i in content:
        info = audioinfo[i]
        if info["format_name"] not in VALID_FORMAT_NAMES:
            print(f"🫨 {info['format_name']} file found.")
        if (
            info["sample_rate"] not in VALID_SAMPLE_RATES
            or info["bits_per_sample"] not in VALID_BITS_PER_SAMPLE
        ):
            needs_reformatting.add(i)
    return needs_reformatting


def validate_low_sample_rates():
    """
    Detect files with sample rates below the acceptable rate.
    Returns a dict with filename and original sample rate for reporting.
    """
    low_sample_rate_files = {}
    acceptable_rate = int(VALID_SAMPLE_RATES[0])

    for i in content:
        info = audioinfo[i]
        current_rate = int(info["sample_rate"])

        if current_rate < acceptable_rate:
            low_sample_rate_files[i] = {
                "original_sample_rate": current_rate,
                "target_sample_rate": acceptable_rate,
            }

    return low_sample_rate_files


def validate_all():
    validate_cache_formats()
    validate_cache_loudness()


validate_all()
