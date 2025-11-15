# Audio QC Bot

Audio quality control automation for Manifold storage - runs on OnDemand.

## Purpose

Automated QC for audio files:
- **Cache Metadata**: Extract sample rate, bit depth, loudness (avoids expensive re-scans)
- **Validate**: Check files against standards (48kHz, 32-bit, -30dB target)
- **Smart Skipping**:
  - Low sample rate (<48kHz) - prevents upsampling artifacts
  - Low bit depth (<24-bit) - prevents upconversion artifacts
  - Excessive loudness (>-24dB) - cannot auto-fix
- **Reformat**: Convert to 48kHz/32-bit WAV
- **Loudness Correction**: Apply gain to -30dB target
- **Report**: Duration tracking and processing summary

## Current Workflow

### 1. Cache Audio Metadata
Extracts media info and calculates loudness for all audio files. Results are cached to JSON to avoid redundant FFmpeg operations.

```bash
python scripts\get_mediainfo.py audio
```

**Output**: `audioinfo.json` containing sample rate, bit depth, format, size, duration, and loudness for each file.

### 2. Validate & Export
Validates cached metadata against quality standards and exports corrected audio files.

```bash
python scripts\export.py audio
```

**Process**:
- Detects files with sample rates below 48kHz and prompts user for conversion decision
- Validates audio format (sample rate, bit depth) and loudness
- Identifies files needing:
  - Loudness correction + reformatting
  - Format correction only
- Exports corrected files to `audio_reformatted/` directory (preserving original filenames)
- Generates detailed export report with:
  - Total duration of all files vs. fixed files
  - Coverage percentage
  - Files skipped due to low sample rate (if any)
- Optionally saves report to JSON
- Optionally clears directories and cached data

**Output**: Corrected audio files in `audio_reformatted/` directory

### 3. Export Report
The export process automatically generates a detailed report showing:
- **Summary Statistics**:
  - Total files in project vs. files exported
  - Files with gain applied vs. reformat only
  - Files skipped due to low sample rate
  - Total duration (all files vs. fixed files)
  - Coverage percentage
- **Individual File Details**: Sample rate, bit depth, loudness, duration
- **Skipped Files**: Files with low sample rates that were not converted

Reports are displayed on-screen and can optionally be saved to `export_report.json` with structured data:

```json
{
  "summary": {
    "total_files_original": 10,
    "total_files_exported": 8,
    "files_with_gain": 3,
    "files_reformat_only": 5,
    "files_skipped_low_sample_rate": 2,
    "duration_original_seconds": 450.5,
    "duration_original_minutes": 7.51,
    "duration_fixed_seconds": 380.2,
    "duration_fixed_minutes": 6.34,
    "coverage_percentage": 84.4
  },
  "exported_files": { ... },
  "skipped_files": {
    "low_sample_rate": { ... }
  }
}
```

## Project Structure

```
qcbot/
├── scripts/
│   ├── get_mediainfo.py   # Cache audio metadata to JSON
│   ├── validate.py         # Validate cached metadata against standards
│   ├── export.py           # Export corrected audio files
│   ├── reset.py            # Audio transformation functions
│   ├── io.py               # (WIP) Manifold I/O operations
│   └── augment.py          # (WIP) Silence stripping & fadeouts
├── config/
│   └── acceptable_formats.py  # Quality standards & thresholds
├── pydub/
│   └── pydub-master/      # Vendored PyDub library
├── audio/                  # Source audio files
├── audio_reformatted/      # Exported corrected files
└── audioinfo.json          # Cached metadata
```

## Configuration

All configuration is in Python constants for simplicity. Edit `config/acceptable_formats.py`:

```python
VALID_SAMPLE_RATE = '48000'
VALID_BITS_PER_SAMPLE = '32'
LOUDNESS_TARGET = -30.0        # Target loudness in dBFS
LOUDNESS_THRESHOLD_MIN = -32.0 # Minimum acceptable loudness
```

## Setup

### Requirements
- **Python 3.8+**
- **ffmpeg** (must be installed and available in system PATH)

### Installation
No dependencies to install! PyDub is vendored in the `pydub/` directory.

```bash
# Clone the repository
cd qcbot

# Verify ffmpeg is installed
ffmpeg -version

# Ready to run!
python scripts\get_mediainfo.py audio
```

## Dependencies

- **PyDub** (vendored locally in `pydub/pydub-master/` due to OnDemand pip restrictions)
- **ffmpeg** (system dependency - must be installed separately)

## Known Limitations & Planned Features

### Current Limitations
- **Non-media file handling**: Scripts will crash if the audio directory contains non-media files (e.g., `.txt`, `.md`). Currently no file type filtering or error handling.
- **Format name validation**: Most media files are converted regardless of their `format_name` field. Edge cases with incorrect or non-standard format names are not yet handled.
- **No concurrency**: Files are processed sequentially despite configuration supporting batch processing. For larger batches, we may need to Implement chunking.
- **Manual workflow**: Requires manual execution of each script step.

### Planned Improvements
- **File type filtering**: Add validation to skip or handle non-audio files gracefully
- **Format name edge cases**: Implement robust handling for incorrectly named or non-standard audio formats
- **Parallel processing**: Implement multiprocessing using configured worker count for faster batch operations
- **Manifold integration**: Complete `io.py` for automated pull/push operations
- **Audio augmentation**: Complete `augment.py` for fadeouts and silence handling
- **Error handling**: Add comprehensive try/catch blocks and recovery mechanisms
- **CLI interface**: Unified command-line interface via `__main__.py`
- **Logging framework**: Replace print statements with proper logging
- **UI layer**: Non-developer interface for configuration and operation

## Performance Updates

### Multiprocessing for Metadata Caching (Planned)

The metadata caching layer (`get_mediainfo.py`) is being upgraded to use parallel processing for significant performance improvements.

#### Sequential (Current Implementation)
- **Processing Model**: Files processed one at a time
- **Worker Count**: 1 (single-threaded)
- **Performance**: ~2 seconds per file for FFmpeg operations + loudness calculation
- **Example**: 100 files = **200 seconds** (~3.3 minutes)

**Bottlenecks:**
- Each file waits for previous file to complete
- CPU cores underutilized (typically only 12-15% usage on 8-core machines)
- FFmpeg and AudioSegment operations are CPU-bound but run sequentially

#### Parallel with Multiprocessing (Planned)
- **Processing Model**: 8 worker processes processing files simultaneously
- **Worker Count**: 8 (configurable based on CPU cores)
- **Performance**: ~2 seconds per file, but 8 files processed at once
- **Example**: 100 files = **25-30 seconds** (~7-8x speedup)

**Improvements:**
- ✅ **7-8x faster** on 8-core machines for large batches
- ✅ **Better error handling** - one failed file doesn't crash entire batch
- ✅ **Real-time progress** - see files complete as they finish processing
- ✅ **CPU utilization** - 80-90% usage across all cores
- ✅ **Scalable** - worker count adjusts based on system capabilities

**Technical Approach:**
```python
# Uses Python multiprocessing.Pool with imap()
with Pool(processes=8) as pool:
    for i, (filename, info) in enumerate(pool.imap(process_single_file, file_args), 1):
        audioinfo[filename] = info
        print(f"[{i}/{len(content)}] ✓ {filename}")
```

**Memory Considerations:**
- 8 workers can load 8 AudioSegments simultaneously
- For 50MB files: 8 × 50MB = 400MB peak memory usage
- Acceptable on modern machines with 8GB+ RAM

**Performance Scaling:**

| Files | Sequential | 8 Workers | Speedup |
|-------|-----------|-----------|---------|
| 10    | 20s       | 5s        | 4x      |
| 50    | 100s      | 15s       | 6.6x    |
| 100   | 200s      | 28s       | 7.1x    |
| 500   | 1000s     | 140s      | 7.1x    |

*Note: Speedup is not perfect 8x due to Python process overhead, result aggregation, and variable file processing times.*

## Notes

- This is a **prototype** focused on core functionality
- PyDub is vendored locally due to pip security restrictions on OnDemand servers
- User input prompts will be removed once concurrency is implemented
- Error handling and module structure will be refactored post-prototype


## Author

- QCBot - Audio Quality Control Client -

Phil Sobrepena
https://github.com/philsobrepena

- PyDub - Audio Augmentation Library -

James Robert
https://github.com/jiaaro
