# MIDI Karaoke Hybrid KAR File Creator

Creating hybrid KAR files that contain both **SK (Soft Karaoke)** and **ME (MIDI Events)** lyric data in a single file.

## Overview

This project solves the problem of having two separate karaoke formats:
- **SK Files**: Rich metadata, detailed timing, beat markers (`\1 \2 \3 \4`), human-readable lyrics
- **ME Files**: MIDI-compatible, standard lyric meta events, machine-readable

**Goal**: Merge both formats into a single hybrid KAR file so any player can use whichever format it needs.

## How It Works

### SK (Soft Karaoke) System

SK files contain:
- **Metadata headers** (`@L`, `@T`, etc.) - Song information
- **Beat markers** (`\1`, `\2`, `\3`, `\4`) - First pass-through without lyrics, showing song rhythm/beat structure
- **Actual lyrics** - Words synced to timing markers
- **Human-readable format** - Designed for karaoke display systems

**First Pass**: `\1 \2 \3 \4 \5 \6 \7` (instrumental, shows beats)
**Second Pass**: Actual lyrics synced to those beats

### ME (MIDI Events) System

ME files contain:
- **MIDI Header** - Tempo, time signature, PPQN (pulses per quarter note)
- **MIDI Events** - Note On/Off, Control Changes, Program Changes
- **Lyric Meta Events** (0xFF 0x05) - Text events containing lyrics
- **Absolute timing** - Everything tied to MIDI ticks

**Advantage**: Works with any standard MIDI player
**Disadvantage**: Less detailed timing information

## The Hybrid Solution

A hybrid KAR file combines:
1. **SK metadata & lyrics** - For detailed display and editing
2. **MIDI events** - For standard playback compatibility
3. **Both timing systems** - So different players can use whichever suits them

## Files in This Repository

### Python Scripts

#### `analyze_and_merge.py`
Analyzes both SK and ME KAR files to understand their structure:
- Parses MIDI headers and events
- Extracts lyrics and metadata
- Displays hex dumps of binary data
- Shows timing information
- Compares the two formats

```bash
python3 analyze_and_merge.py
```

**Output:**
- Detailed breakdown of both files
- Lyric extraction with timing
- Meta event information
- Comparison summary

#### `create_hybrid_kar.py`
Creates the actual hybrid KAR file:
- Reads SK file (extracts metadata, lyrics, timing)
- Reads ME file (extracts MIDI events, notes)
- Merges both into a single file
- Preserves all timing information
- Generates standard MIDI-compatible output

```bash
python3 create_hybrid_kar.py
```

**Output:**
- `Our_Gods_are_an_awesome_God_En_HYBRID.kar` - The hybrid file

### Shell Scripts

#### `run_pipeline.sh`
Runs the complete analysis and hybrid file creation:

```bash
bash run_pipeline.sh
```

**Executes:**
1. Analysis of SK and ME files
2. Creation of hybrid KAR file
3. Lists all generated files

## Process Workflow

```
SK KAR File                ME KAR File
      |                         |
      v                         v
  [Parse MIDI]            [Parse MIDI]
      |                         |
  - Metadata              - MIDI Notes
  - Lyrics                - Lyric Events
  - Timing                - Tempo/Time Sig
      |                         |
      +----------->+<-----------+
                   |
             [Merge Events]
                   |
             Sort by Time
             Combine Lyrics
             Preserve Metadata
                   |
                   v
          [Write Hybrid KAR]
                   |
          HYBRID.kar File
   (Both SK + ME in one file)
```

## Usage

### Quick Start

1. **Place your KAR files in the repository:**
   ```
   Our_Gods_are_an_awesome_God_En x2SKforAI.kar
   Our_Gods_are_an_awesome_God_En x2MEforAI.kar
   ```

2. **Run the pipeline:**
   ```bash
   bash run_pipeline.sh
   ```

3. **The hybrid file is created:**
   ```
   Our_Gods_are_an_awesome_God_En_HYBRID.kar
   ```

### Manual Execution

**Step 1: Analyze the files**
```bash
python3 analyze_and_merge.py
```

This shows:
- What's in each file
- Lyric content and timing
- Meta event information
- Data comparison

**Step 2: Create the hybrid file**
```bash
python3 create_hybrid_kar.py
```

This produces the hybrid KAR file with both SK and ME data.

## Technical Details

### MIDI Format Structure

```
MThd (Header)
├─ Format Type
├─ Number of Tracks
└─ Division (PPQN - Pulses Per Quarter Note)

MTrk (Track Data)
├─ Delta Time (variable length)
├─ MIDI Event
│  ├─ Meta Event (0xFF)
│  │  ├─ Text (0x01)
│  │  ├─ Lyric (0x05)
│  │  ├─ Tempo (0x51)
│  │  ├─ Time Sig (0x58)
│  │  └─ End of Track (0x2F)
│  ├─ Note On (0x90)
│  ├─ Note Off (0x80)
│  ├─ Control Change (0xB0)
│  ├─ Program Change (0xC0)
│  └─ SysEx (0xF0, 0xF7)
```

### SK vs ME Differences

| Feature | SK | ME |
|---------|----|----|
| Format | Text-based + MIDI | Standard MIDI |
| Lyrics | Text meta events + metadata | Lyric meta events (0xFF 0x05) |
| Timing | Relative + absolute MIDI ticks | Absolute MIDI ticks |
| Metadata | Extensive (@L, @T, etc.) | Minimal |
| Playback | Karaoke-specific players | Any MIDI player |
| Editability | Human-readable | Machine-readable |

### Merging Strategy

1. **Parse both files** into event streams
2. **Extract SK metadata** (text events with metadata headers)
3. **Extract SK lyrics** (lyric/text events)
4. **Extract ME MIDI events** (notes, control changes, tempo)
5. **Sort all events by timestamp**
6. **Write combined events** in MIDI format
7. **Preserve both data types** so any player can read what it needs

## Output Files

After running the pipeline, you'll have:

```
Your_Song_Name_HYBRID.kar
├─ All SK metadata and lyrics
├─ All ME MIDI notes and events
├─ Combined timing information
└─ Compatible with both SK and ME players
```

## Compatibility

**The hybrid file can be opened by:**
- ✅ Karankan (reads SK data)
- ✅ Any MIDI player (reads MIDI events)
- ✅ SK-compatible karaoke players
- ✅ ME-compatible karaoke players

## Troubleshooting

### File Not Found
Make sure both KAR files are in the same directory as the Python scripts:
```bash
ls -la *.kar
```

### Permission Denied
Make the scripts executable:
```bash
chmod +x *.sh *.py
```

### Python Errors
Ensure you have Python 3.6+:
```bash
python3 --version
```

No external dependencies needed - uses only Python standard library!

## Future Enhancements

- [ ] Batch processing multiple song pairs
- [ ] Configuration file for custom mappings
- [ ] Validation and error checking
- [ ] Detailed logging output
- [ ] Support for other karaoke formats
- [ ] GUI for file selection

## Project Structure

```
midi/
├── Our_Gods_are_an_awesome_God_En x2SKforAI.kar    (Input: SK format)
├── Our_Gods_are_an_awesome_God_En x2MEforAI.kar    (Input: ME format)
├── Our_Gods_are_an_awesome_God_En_HYBRID.kar       (Output: Hybrid format)
├── analyze_and_merge.py                             (Analysis tool)
├── create_hybrid_kar.py                             (Creation tool)
├── run_pipeline.sh                                  (Complete pipeline)
└── README.md                                        (This file)
```

## How to Contribute

Found improvements? Have questions? Create an issue or submit a pull request!

## License

This project is open source and available for karaoke enthusiasts everywhere.

---

**Happy karaoke! 🎤🎵**
