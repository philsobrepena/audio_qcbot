import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "pydub", "pydub-master"))

new_dir = "audio_reformatted"


def to_48k_32bit_wav(sound):
    conversion = sound.set_sample_width(4).set_frame_rate(48000)
    print(f"{sound} set to 32-bit - 48k")
    return conversion


def to_48k_32bit_wav_target_loudness(sound, difference, name):
    conversion = sound.apply_gain(difference).set_sample_width(4).set_frame_rate(48000)
    print(f"new loudness for {name}: {conversion.dBFS}")
    print(f"{name} set to 32-bit - 48k")
    return conversion

def reformat_by_config_with_gain(sound, difference, name, sample_width, frame_rate):
    conversion = sound.apply_gain(difference).set_sample_width(sample_width).set_frame_rate(frame_rate)
    print(f"new loudness for {name}: {conversion.dBFS}")
    print(f"{name} set to {sample_width}-bit - {frame_rate}")
    return conversion

def reformat_by_config(sound, sample_width, frame_rate):
    conversion = sound.set_sample_width(sample_width).set_frame_rate(frame_rate)
    print(f"{sound} set to {sample_width}-bit - {frame_rate}")
    return conversion
