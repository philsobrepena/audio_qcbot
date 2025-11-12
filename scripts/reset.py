import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "pydub", "pydub-master"))

new_dir = "audio_reformatted"


def to_48k_32bit_wav(sound, name):
    conversion = sound.set_sample_width(4).set_frame_rate(48000)
    print(f"{sound} set to 32-bit - 48k")
    return conversion


def to_48k_32bit_wav_target_loudness(sound, difference, name):

    conversion = sound.apply_gain(difference).set_sample_width(4).set_frame_rate(48000)
    print(f"new loudness for {name}: {conversion.dBFS}")
    print(f"{name} set to 32-bit - 48k")
    return conversion
