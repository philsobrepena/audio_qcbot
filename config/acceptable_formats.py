"""
Valid and Invalid Definitions
"""

VALID_SAMPLE_RATES = ["48000"]

VALID_BITS_PER_SAMPLE = ["32"]

VALID_FORMAT_NAMES = ["wav"]

"""
log notes for loudness threshold:
loundness of ONTARGET.wav: -29.484121424636406
loundness of ONTARGET_2.wav: -30.13800233726012
loundness of TOO_QUIET_by12lufs_2.wav: -44.70600091021485
loundness of TOO_QUIET_by_12lufs.wav: -42.41995866963251

declaring -32 as temp threshold minimum
"""

LOUDNESS_TARGET = -30.0
LOUDNESS_THRESHOLD_MIN = -32.0
LOUDNESS_THRESHOLD_MAX = None


cached_media_info_data = [
    "sample_rate",
    "bits_per_sample",
    "format_name",
    "size",
    "duration",
    "loudness",
]
