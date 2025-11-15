"""
test.py - Quick CLI tool to test audio file exports with custom parameters.

Usage:
    python test.py <filename> -gain <float> -bits <"16"|"24"|"32"> -samplerate <int>

Examples:
    python test.py audio.wav -gain 3.5 -bits "32" -samplerate "48000"
    python test.py audio.wav -bits "24" -samplerate "48000"
    python test.py audio.wav -gain 2.0
"""

import argparse
import os
import sys
from pathlib import Path

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "pydub", "pydub-master"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.acceptable_formats import (
    VALID_BITS_PER_SAMPLE,
    VALID_SAMPLE_RATE,
)

from pydub import AudioSegment
from reset import reformat_by_config, reformat_by_config_with_gain


def get_sample_width_from_bits(bits):
    """Convert bit depth string to sample width (bytes)."""
    bit_to_width = {"16": 2, "24": 3, "32": 4}
    return bit_to_width.get(bits, 4)


def main():
    parser = argparse.ArgumentParser(
        description="Test audio file export with custom parameters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test.py audio.wav -gain 3.5 -bits "32" -samplerate "48000"
  python test.py audio.wav -bits "24" -samplerate "48000"
  python test.py audio.wav -gain 2.0
        """,
    )

    parser.add_argument("filename", type=str, help="Path to the audio file to test")
    parser.add_argument(
        "-gain",
        type=float,
        default=None,
        help="Gain adjustment in dB (e.g., 3.5, -2.0)",
    )
    parser.add_argument(
        "-bits",
        type=str,
        choices=["16", "24", "32"],
        default=VALID_BITS_PER_SAMPLE,
        help='Bit depth: "16", "24", or "32" (default: from config)',
    )
    parser.add_argument(
        "-samplerate",
        type=str,
        default=VALID_SAMPLE_RATE,
        help='Sample rate in Hz (default: from config)',
    )
    parser.add_argument(
        "-output",
        type=str,
        default="test_output.wav",
        help="Output filename (default: test_output.wav)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.filename):
        print(f"❌ Error: File '{args.filename}' not found.")
        sys.exit(1)

    sample_width = get_sample_width_from_bits(args.bits)
    frame_rate = int(args.samplerate)

    print("\n" + "=" * 80)
    print("AUDIO FILE TEST EXPORT".center(80))
    print("=" * 80 + "\n")

    print(f"Input File     : {args.filename}")
    print(f"Bit Depth      : {args.bits}-bit (sample_width={sample_width} bytes)")
    print(f"Sample Rate    : {frame_rate} Hz")
    if args.gain is not None:
        print(f"Gain Adjustment: {args.gain:+.2f} dB")
    else:
        print("Gain Adjustment: None")
    print(f"Output File    : {args.output}")
    print("\n" + "-" * 80 + "\n")

    # Load audio file
    try:
        print(f"Loading {args.filename}...")
        sound = AudioSegment.from_file(args.filename)
        print(f"✓ Loaded successfully")
        print(f"  Original loudness: {sound.dBFS:.2f} dBFS")
        print(f"  Original sample rate: {sound.frame_rate} Hz")
        print(f"  Original bit depth: {sound.sample_width * 8} bit")
        print()
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        sys.exit(1)

    try:
        if args.gain is not None:
            print(f"Applying gain and reformatting...")
            conversion = reformat_by_config_with_gain(
                sound, args.gain, args.filename, sample_width, frame_rate
            )
        else:
            print(f"Reformatting without gain...")
            conversion = reformat_by_config(sound, sample_width, frame_rate)

        print(f"\nExporting to {args.output}...")
        if sample_width == 3:  # 24-bit
            conversion.export(
                args.output, format="wav", parameters=["-acodec", "pcm_s24le"]
            )
        else:
            conversion.export(args.output, format="wav")

        print(f"✓ Export complete!")
        print(f"\nFinal loudness: {conversion.dBFS:.2f} dBFS")
        print(f"Final sample rate: {conversion.frame_rate} Hz")
        print(f"Final bit depth: {conversion.sample_width * 8} bit")
        print("\n" + "=" * 80 + "\n")

    except Exception as e:
        print(f"❌ Error during export: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
