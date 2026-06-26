#!/usr/bin/env python3
"""
Script to analyze and compare SK (Soft Karaoke) vs ME (MIDI Events) KAR files.
Decodes MIDI structure and extracts lyrics/metadata from both formats.
"""

import struct
import sys
from pathlib import Path

def read_variable_length(data, pos):
    """Read MIDI variable length value"""
    value = 0
    while True:
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            break
    return value, pos

def parse_midi_file(filename):
    """Parse a MIDI/KAR file and extract all events"""
    with open(filename, 'rb') as f:
        data = f.read()
    
    print(f"\n{'='*80}")
    print(f"FILE: {Path(filename).name}")
    print(f"SIZE: {len(data)} bytes")
    print(f"{'='*80}\n")
    
    # Check header
    if data[:4] != b'MThd':
        print("ERROR: Not a valid MIDI file")
        return
    
    # Parse header
    header_len = struct.unpack('>I', data[4:8])[0]
    format_type = struct.unpack('>H', data[8:10])[0]
    num_tracks = struct.unpack('>H', data[10:12])[0]
    division = struct.unpack('>H', data[12:14])[0]
    
    print(f"MIDI Header:")
    print(f"  Format: {format_type}")
    print(f"  Tracks: {num_tracks}")
    print(f"  Division (PPQN): {division}")
    print()
    
    pos = 14
    track_num = 0
    
    while pos < len(data):
        if data[pos:pos+4] == b'MTrk':
            track_num += 1
            track_start = pos
            track_len = struct.unpack('>I', data[pos+4:pos+8])[0]
            pos += 8
            track_end = pos + track_len
            
            print(f"TRACK {track_num} (bytes {track_start}-{track_end}):")
            print(f"  Length: {track_len} bytes")
            print()
            
            # Parse track events
            current_time = 0
            event_count = 0
            
            while pos < track_end:
                # Read delta time
                delta, pos = read_variable_length(data, pos)
                current_time += delta
                
                event_count += 1
                status = data[pos]
                pos += 1
                
                # Meta event
                if status == 0xFF:
                    meta_type = data[pos]
                    pos += 1
                    length, pos = read_variable_length(data, pos)
                    event_data = data[pos:pos+length]
                    pos += length
                    
                    # Decode meta event
                    if meta_type == 0x01:  # Text Event
                        text = event_data.decode('utf-8', errors='replace')
                        print(f"  [{current_time:6d}] Text Event: {text}")
                    elif meta_type == 0x05:  # Lyric Event
                        text = event_data.decode('utf-8', errors='replace')
                        print(f"  [{current_time:6d}] Lyric Event: {text}")
                    elif meta_type == 0x03:  # Sequence/Track Name
                        text = event_data.decode('utf-8', errors='replace')
                        print(f"  [{current_time:6d}] Track Name: {text}")
                    elif meta_type == 0x51:  # Set Tempo
                        tempo = struct.unpack('>I', b'\x00' + event_data)[0]
                        bpm = 60000000 / tempo
                        print(f"  [{current_time:6d}] Set Tempo: {bpm:.2f} BPM ({tempo} µs/beat)")
                    elif meta_type == 0x58:  # Time Signature
                        num, denom, cc, bb = struct.unpack('BBBB', event_data)
                        print(f"  [{current_time:6d}] Time Sig: {num}/{2**denom}")
                    elif meta_type == 0x00:  # Sequence Number
                        print(f"  [{current_time:6d}] Sequence Number: {struct.unpack('>H', event_data)[0]}")
                    elif meta_type == 0x2F:  # End of Track
                        print(f"  [{current_time:6d}] End of Track")
                    else:
                        # Print raw hex for unknown meta events
                        hex_data = ' '.join(f'{b:02x}' for b in event_data[:20])
                        if len(event_data) > 20:
                            hex_data += "..."
                        print(f"  [{current_time:6d}] Meta Event 0x{meta_type:02x}: {hex_data}")
                
                # SysEx event
                elif status == 0xF0 or status == 0xF7:
                    length, pos = read_variable_length(data, pos)
                    event_data = data[pos:pos+length]
                    pos += length
                    hex_data = ' '.join(f'{b:02x}' for b in event_data[:20])
                    if len(event_data) > 20:
                        hex_data += "..."
                    print(f"  [{current_time:6d}] SysEx Event: {hex_data}")
                
                # MIDI channel event
                else:
                    if status & 0xF0 == 0x90:  # Note On
                        note = data[pos]
                        velocity = data[pos+1]
                        pos += 2
                        print(f"  [{current_time:6d}] Note On: Note={note}, Velocity={velocity}")
                    elif status & 0xF0 == 0x80:  # Note Off
                        note = data[pos]
                        velocity = data[pos+1]
                        pos += 2
                        print(f"  [{current_time:6d}] Note Off: Note={note}")
                    elif status & 0xF0 == 0xB0:  # Control Change
                        controller = data[pos]
                        value = data[pos+1]
                        pos += 2
                        print(f"  [{current_time:6d}] CC: Controller={controller}, Value={value}")
                    elif status & 0xF0 == 0xC0:  # Program Change
                        program = data[pos]
                        pos += 1
                        print(f"  [{current_time:6d}] Program Change: Program={program}")
                    else:
                        print(f"  [{current_time:6d}] Unknown MIDI event: 0x{status:02x}")
            
            print(f"  Total events: {event_count}")
            print()
            pos = track_end
        else:
            pos += 1
    
    print(f"{'='*80}\n")

if __name__ == '__main__':
    # Parse both files
    parse_midi_file('Our_Gods_are_an_awesome_God_En x2MEforAI.kar')
    parse_midi_file('Our_Gods_are_an_awesome_God_En x2SKforAI.kar')
