# Hybrid KAR File Creator - Quick Start Guide

## What This Does

Creates a **HYBRID KAR file** that combines:
- **SK (Soft Karaoke) format** - Rich metadata, lyrics, beat markers
- **ME (MIDI Events) format** - Standard MIDI notes and events

Into a **single file** that works with both types of players.

## Quick Start (3 Steps)

### 1. Place Your Files
Put these two KAR files in this directory:
```
Our_Gods_are_an_awesome_God_En x2SKforAI.kar
Our_Gods_are_an_awesome_God_En x2MEforAI.kar
```

### 2. Run the Creator
```bash
python3 hybrid_kar_creator.py
```
OR
```bash
bash create_hybrid.sh
```

### 3. Done!
Your hybrid file will be created:
```
Our_Gods_are_an_awesome_God_En_HYBRID.kar
```

## What You Get

A single KAR file that contains:
✅ All SK lyrics and metadata
✅ All MIDI notes and events
✅ Complete timing information
✅ Works with ANY karaoke player

## Files in This Project

| File | Purpose |
|------|---------|
| `hybrid_kar_creator.py` | Main script - run this! |
| `create_hybrid.sh` | Bash wrapper for main script |
| `create_hybrid_kar.py` | Creates the hybrid KAR file |
| `analyze_and_merge.py` | Analyzes SK and ME files |
| `README.md` | Full documentation |

## Requirements

- Python 3.6+ (that's it!)
- No external dependencies needed

## Troubleshooting

### "File not found" error
Make sure your KAR files are in the same directory as the scripts.

### "Permission denied" error
Make the scripts executable:
```bash
chmod +x hybrid_kar_creator.py create_hybrid.sh
```

### Still not working?
Check that you have Python 3 installed:
```bash
python3 --version
```

## Questions?

See `README.md` for complete documentation.

---

**Ready? Run: `python3 hybrid_kar_creator.py`** 🎤🎵
