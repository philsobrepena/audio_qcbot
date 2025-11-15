# Quick Start Guide

Get started with Audio QC Bot in 3 minutes.

## Prerequisites

### Check FFmpeg Installation

FFmpeg is required for audio processing. Verify it's installed:

```bash
# Check FFmpeg is available
ffmpeg -version
```

**If not installed:**

- **OnDemand**: `ffmpeg`

- **Mac**: `brew install ffmpeg`

- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

- **Linux**: `sudo apt-get install ffmpeg` or `sudo yum install ffmpeg`

### Check Python Version

```bash
python3 --version  # Should be 3.8 or higher
```

## Project Structure

```
qcbot/
├── __main__.py              # Main entry point
├── audio/                   # INPUT: Drop your audio files here
├── audio_reformatted/       # OUTPUT: Processed files appear here
├── .audioinfo.json          # CACHE: Metadata cache (auto-generated)
├── export_report.json       # REPORT: Export report (optional)
├── scripts/                 # Internal processing scripts
├── pydub/                   # Vendored PyDub library
└── config/                  # Quality standards configuration
```

### Key Files & Directories

#### `audio/` (Input Directory)
- **Purpose**: Place your source audio files here
- **Supported formats**: WAV, MP3, FLAC, OGG, M4A, AAC
- **User action**: Drop files before running the bot

#### `audio_reformatted/` (Output Directory)
- **Purpose**: Processed audio files are exported here
- **Format**: 48kHz, 32-bit WAV files
- **Target Loudness**: -30dBFS RMS

#### `.audioinfo.json` (Metadata Cache)
- **Purpose**: Caches audio metadata to avoid expensive re-scans
- **Contents**: Sample rate, bit depth, format, size, duration, loudness for each file
- **User action**: Auto-generated file
- **When to delete**: Remove to force full rescan of audio files

#### `export_report.json` (Export Report - Optional)
- **Purpose**: Detailed report of processing operations
- **Contents**:
  - Total files processed
  - Files with gain applied vs. reformat only
  - Individual file details (sample rate, bit depth, loudness, duration)
- **User action**: Generated when you choose "Y" to save report after export

## How to Run

### Option 1: From Inside the `qcbot/` Directory

```bash
# Navigate to project directory
cd qcbot

# Run the main workflow (automated)
python3 __main__.py

# Or run individual steps manually:

# Step 1: Cache metadata
python3 scripts/get_mediainfo.py audio

# Step 2: Validate and export
python3 scripts/export.py audio
```

### Python Command Alternatives

**OnDemand (Mac/Linux):** Use `python3`
```bash
python3 __main__.py
```

**Windows or systems with Python 3 as default:** Use `python`
```bash
python __main__.py
```

**Check which one works for you:**
```bash
python3 --version  # Try this first (OnDemand standard)
python --version   # Fallback if python3 not found
```

## Workflow Steps

### Step 1: Prepare Your Audio

1. Place audio files in the `audio/` directory
2. Supported formats: WAV, MP3, FLAC, OGG, M4A, AAC

### Step 2: Run the QC Bot

```bash
cd qcbot
python3 __main__.py
```

The bot will:
1. Show a welcome screen with capabilities
2. Ask if you're ready to begin
3. Scan and cache metadata for all audio files
4. Validate files against quality standards
5. Export corrected files to `audio_reformatted/`
6. Optionally generate a detailed report

### Step 3: Retrieve Processed Audio

Find your processed files in `audio_reformatted/`:
- All files are converted to **48kHz, 32-bit WAV**
- Files below -32dB loudness are boosted to **-30dB target**

## Quality Standards

Files are validated against these standards (configured in `config/acceptable_formats.py`):

- **Sample Rate**: 48000 Hz
- **Bit Depth**: 32-bit
- **Bit Depth Minimum**: 24-bit (files below this are skipped - upconversion artifacts)
- **Loudness Target**: -30.0 dBFS
- **Loudness Min**: -32.0 dBFS (files below are boosted)
- **Loudness Max**: -24.0 dBFS (files above are skipped - cannot auto-fix)

## Troubleshooting

### "FFmpeg not found"
```bash
# Install FFmpeg first
ffmpeg # On Demand
brew install ffmpeg  # Mac
# Then retry
```

### "Error: 'audio' directory not found"
```bash
# Create the audio directory
mkdir audio
# Add your audio files
cp /path/to/files/*.wav audio/
```

### "Error processing [file]: ..."
- File may not be a valid audio file
- File may be corrupted
- Check the error message for details
- Processing continues for other files

### Want to Reprocess Everything?
```bash
# Delete the cache to force full rescan
rm .audioinfo.json

# Clear output directory
rm -rf audio_reformatted/*

# Run again
python3 __main__.py
```

### Files Processing Out of Order?
- This is normal with parallel processing (8 workers)
- Files complete based on size and complexity, not alphabetical order
- Final output includes all files regardless of order

## Performance

**Sequential Processing (old):**
- 100 files × 2 seconds = ~200 seconds (3.3 minutes)

**Parallel Processing (current):**
- 100 files ÷ 8 workers × 2 seconds = ~25-30 seconds
- **7-8x faster** on multi-core machines

## Advanced Usage

### Manual Step-by-Step Execution

```bash
# Step 1: Cache metadata only
python3 scripts/get_mediainfo.py audio

# Step 2: Validate and export
python3 scripts/export.py audio

# Optional: Generate report for reformatted files
python3 scripts/get_mediainfo.py audio_reformatted
```

### Change Quality Standards
## ( NOT YET READY - STANDARDS CAN CHANGE, BUT CONVERSIONS ARE NOT AUTO UPDATED )

Edit `config/acceptable_formats.py`:

```python
VALID_SAMPLE_RATE = '48000'     # Change target sample rate
VALID_BITS_PER_SAMPLE = '32'     # Change target bit depth
LOUDNESS_TARGET = -30.0            # Change target loudness
LOUDNESS_THRESHOLD_MIN = -32.0     # Change minimum threshold
```

## Next Steps

- See [README.md](README.md) for full documentation
- Check planned features and roadmap
- Report issues or suggest improvements

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python3 __main__.py` | Run full automated workflow |
| `python3 scripts/get_mediainfo.py audio` | Cache metadata only |
| `python3 scripts/export.py audio` | Validate and export only |
| `ffmpeg -version` | Check FFmpeg installation |
| `rm .audioinfo.json` | Clear cache and force rescan |

---

**Ready to process audio?**

Drop files in `audio/` and run `python3 __main__.py`! 🎵🤖
