"""
Valid and Invalid Definitions
"""

VALID_SAMPLE_RATE = "48000"

VALID_BITS_PER_SAMPLE = "32"

VALID_FORMAT_NAME = "wav"

"""
log notes for loudness threshold:

loundness of ONTARGET.wav: -29.484121424636406
loundness of ONTARGET_2.wav: -30.13800233726012
loundness of TOO_QUIET_by12lufs_2.wav: -44.70600091021485
loundness of TOO_QUIET_by_12lufs.wav: -42.41995866963251


loudness of 0dBFS-normalized-tooloud.wav: -22.87
loudness of 0dBFS-tooloud.wav: -22.00

declaring -32 as loudness threshold min
declaring -24 as loudness threshold max
"""

LOUDNESS_TARGET = -30.0
LOUDNESS_THRESHOLD_MIN = -32.0
LOUDNESS_THRESHOLD_MAX = -24.0

"""
log notes for bit depth threshold:

Converting from very low bit depths (e.g., 16-bit) to 32-bit can create artifacts.
The minimum acceptable bit depth is set to 24-bit to prevent upconversion artifacts.

declaring 24 as bit depth threshold min
"""

BIT_DEPTH_THRESHOLD_MIN = 24


cached_media_info_data = [
    "sample_rate",
    "bits_per_sample",
    "format_name",
    "size",
    "duration",
    "loudness",
]
