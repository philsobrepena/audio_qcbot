import os, subprocess, sys, time


def type_text(text, delay=0.001):
    """Simulate typing effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def loading_bar(duration=2.0, width=50):
    """Animated loading bar"""
    steps = 20
    for i in range(steps + 1):
        filled = int(width * i / steps)
        bar = "█" * filled + "░" * (width - filled)
        percent = int(100 * i / steps)
        sys.stdout.write(f"\r  [{bar}] {percent}%")
        sys.stdout.flush()
        time.sleep(duration / steps)
    print("\n")


def clear():
    os.system("cls" if os.name == "nt" else "clear")


clear()
print("\n" + "=" * 80)
type_text("  🎵 AUDIO QC BOT 🤖", delay=0.05)
print("=" * 80 + "\n")
time.sleep(0.5)

type_text("  Automated quality control for audio files", delay=0.02)
time.sleep(0.3)
type_text("  48kHz | 32-bit | -30dB target loudness", delay=0.02)
print("\n" + "-" * 80 + "\n")
time.sleep(0.5)

type_text("  CAPABILITIES:", delay=0.03)
time.sleep(0.2)

capabilities = [
    "    ✓ Cache metadata (sample rate, bit depth, loudness)",
    "    ✓ Validate audio against quality standards",
    "    ✓ Reformat to 48kHz/32-bit WAV",
    "    ✓ Apply gain for loudness correction (-30dB target)",
    "    ✓ Generate detailed export reports",
]

for cap in capabilities:
    time.sleep(0.15)
    print(cap)

print("\n" + "-" * 80 + "\n")
time.sleep(0.5)

type_text("  WORKFLOW:", delay=0.03)
time.sleep(0.2)

workflow = [
    "    1. Scan audio directory and cache metadata",
    "    2. Validate files against quality standards",
    "    3. Export corrected files to audio_reformatted/",
    "    4. Generate optional report",
]

for step in workflow:
    time.sleep(0.15)
    print(step)

print("\n" + "=" * 80 + "\n")
time.sleep(0.3)

type_text("  Initializing system...", delay=0.03)
loading_bar(duration=1.5, width=60)


start = input("  Ready to begin? [Y/N]: ").lower()

if start == "y":
    print("\n" + "=" * 80)
    type_text("  🚀 Starting QC pipeline...", delay=0.04)
    print("=" * 80 + "\n")
    time.sleep(0.5)

    if not os.path.exists("audio"):
        type_text("  ❌ Error: 'audio' directory not found!", delay=0.02)
        type_text(
            "  Please create an 'audio' directory and add your audio files.", delay=0.02
        )
        sys.exit(1)

    audio_files = os.listdir("audio")
    if not audio_files:
        type_text("  ❌ Error: 'audio' directory is empty!", delay=0.02)
        type_text("  Please add audio files to process.", delay=0.02)
        sys.exit(1)

    type_text(f"  Found {len(audio_files)} file(s) in audio directory", delay=0.02)
    print()

    # cache metadata
    type_text("  [STEP 1/2] Caching audio metadata...", delay=0.03)
    time.sleep(0.3)
    os.system("python3 scripts/get_mediainfo.py audio")

    # cache created
    if not os.path.exists("audioinfo.json"):
        type_text("  ❌ Error: Cache creation failed!", delay=0.02)
        sys.exit(1)

    # export
    print("\n" + "-" * 80 + "\n")
    type_text("  [STEP 2/2] Validating and exporting...", delay=0.03)
    time.sleep(0.3)
    os.system("python3 scripts/export.py audio")

    print("\n" + "=" * 80)
    type_text("  ✅ QC pipeline complete!", delay=0.04)
    print("=" * 80 + "\n")

elif start == "n":
    print()
    type_text("  👋 Exiting... Have a great day!", delay=0.03)
    print()

else:
    print()
    type_text("  ❌ Invalid input. Exiting...", delay=0.03)
    print()
