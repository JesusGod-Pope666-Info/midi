#!/usr/bin/env python3
"""
Analyze SK vs ME KAR files and create a hybrid file combining both formats.
"""

import struct
import sys
from pathlib import Path
from collections import defaultdict

class MIDIParser:
    def __init__(self, filename):
        self.filename = filename
        self.data = None
        self.events = []
        self.metadata = {}
        self.lyrics = []
        self.notes = []
        self.parse()
    
    def parse(self):
        """Parse MIDI file"""
        with open(self.filename, 'rb') as f:
            self.data = f.read()
        
        print(f"\n{'='*100}")
        print(f"ANALYZING: {Path(self.filename).name} ({len(self.data)} bytes)")
        print(f"{'='*100}\n")
        
        # Print hex dump of first 500 bytes
        print("HEX DUMP (first 500 bytes):")
        for i in range(0, min(500, len(self.data)), 16):
            hex_part = ' '.join(f'{b:02x}' for b in self.data[i:i+16])
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in self.data[i:i+16])
            print(f"{i:04x}: {hex_part:<48} {ascii_part}")
        print()
        
        # Check header
        if self.data[:4] != b'MThd':
            print("ERROR: Not a valid MIDI file")
            return
        
        # Parse header
        header_len = struct.unpack('>I', self.data[4:8])[0]
        format_type = struct.unpack('>H', self.data[8:10])[0]
        num_tracks = struct.unpack('>H', self.data[10:12])[0]
        division = struct.unpack('>H', self.data[12:14])[0]
        
        print(f"MIDI HEADER:")
        print(f"  Format Type: {format_type}")
        print(f"  Number of Tracks: {num_tracks}")
        print(f"  Division (PPQN): {division}")
        print()
        
        pos = 14
        track_num = 0
        
        while pos < len(self.data):
            if pos + 8 > len(self.data):
                break
            
            if self.data[pos:pos+4] == b'MTrk':
                track_num += 1
                track_len = struct.unpack('>I', self.data[pos+4:pos+8])[0]
                pos += 8
                track_end = pos + track_len
                
                print(f"TRACK {track_num} ({track_len} bytes):")
                self._parse_track(pos, track_end)
                print()
                
                pos = track_end
            else:
                pos += 1
    
    def _read_varint(self, pos):
        """Read variable length integer"""
        value = 0
        while pos < len(self.data):
            byte = self.data[pos]
            pos += 1
            value = (value << 7) | (byte & 0x7F)
            if not (byte & 0x80):
                break
        return value, pos
    
    def _parse_track(self, start, end):
        """Parse a single track"""
        pos = start
        current_time = 0
        event_num = 0
        
        while pos < end:
            # Read delta time
            delta, pos = self._read_varint(pos)
            current_time += delta
            
            if pos >= end:
                break
            
            status = self.data[pos]
            pos += 1
            event_num += 1
            
            # Meta event (0xFF)
            if status == 0xFF:
                if pos >= end:
                    break
                meta_type = self.data[pos]
                pos += 1
                
                if pos >= end:
                    break
                length, pos = self._read_varint(pos)
                
                if pos + length > end:
                    break
                
                event_data = self.data[pos:pos+length]
                pos += length
                
                # Parse specific meta events
                if meta_type == 0x01:  # Text Event
                    text = event_data.decode('utf-8', errors='replace')
                    print(f"  [{current_time:6d}] Text: {text}")
                    self.events.append(('text', current_time, text))
                
                elif meta_type == 0x05:  # Lyric Event
                    text = event_data.decode('utf-8', errors='replace')
                    print(f"  [{current_time:6d}] Lyric: {text}")
                    self.lyrics.append((current_time, text))
                    self.events.append(('lyric', current_time, text))
                
                elif meta_type == 0x03:  # Sequence/Track Name
                    text = event_data.decode('utf-8', errors='replace')
                    print(f"  [{current_time:6d}] Track Name: {text}")
                
                elif meta_type == 0x51:  # Set Tempo
                    if len(event_data) >= 3:
                        tempo = struct.unpack('>I', b'\x00' + event_data[:3])[0]
                        bpm = 60000000 / tempo if tempo > 0 else 0
                        print(f"  [{current_time:6d}] Set Tempo: {bpm:.1f} BPM")
                        self.metadata['tempo'] = tempo
                
                elif meta_type == 0x58:  # Time Signature
                    if len(event_data) >= 4:
                        num, denom, cc, bb = struct.unpack('BBBB', event_data)
                        print(f"  [{current_time:6d}] Time Sig: {num}/{2**denom}")
                
                elif meta_type == 0x2F:  # End of Track
                    print(f"  [{current_time:6d}] End of Track")
                
                else:
                    # Unknown meta event - print hex
                    hex_str = ' '.join(f'{b:02x}' for b in event_data[:30])
                    if len(event_data) > 30:
                        hex_str += "..."
                    text_str = event_data.decode('utf-8', errors='replace')[:50]
                    print(f"  [{current_time:6d}] Meta 0x{meta_type:02x} (len={length}): {hex_str}")
                    if text_str:
                        print(f"                      Text: {text_str}")
                    self.events.append(('meta', current_time, meta_type, hex_str))
            
            # MIDI Note On (0x90)
            elif status & 0xF0 == 0x90:
                if pos + 2 > end:
                    break
                note = self.data[pos]
                velocity = self.data[pos+1]
                pos += 2
                if velocity > 0:
                    print(f"  [{current_time:6d}] Note On: {note} vel={velocity}")
                    self.notes.append((current_time, 'on', note, velocity))
            
            # MIDI Note Off (0x80)
            elif status & 0xF0 == 0x80:
                if pos + 2 > end:
                    break
                note = self.data[pos]
                velocity = self.data[pos+1]
                pos += 2
                print(f"  [{current_time:6d}] Note Off: {note}")
                self.notes.append((current_time, 'off', note, velocity))
            
            # Control Change (0xB0)
            elif status & 0xF0 == 0xB0:
                if pos + 2 > end:
                    break
                controller = self.data[pos]
                value = self.data[pos+1]
                pos += 2
                # print(f"  [{current_time:6d}] CC: {controller} = {value}")
            
            # Program Change (0xC0)
            elif status & 0xF0 == 0xC0:
                if pos + 1 > end:
                    break
                program = self.data[pos]
                pos += 1
                # print(f"  [{current_time:6d}] Program: {program}")
            
            # SysEx (0xF0, 0xF7)
            elif status == 0xF0 or status == 0xF7:
                if pos >= end:
                    break
                length, pos = self._read_varint(pos)
                if pos + length > end:
                    break
                sysex_data = self.data[pos:pos+length]
                pos += length
                hex_str = ' '.join(f'{b:02x}' for b in sysex_data[:30])
                if len(sysex_data) > 30:
                    hex_str += "..."
                print(f"  [{current_time:6d}] SysEx: {hex_str}")
            
            else:
                # Unknown status
                pass
        
        print(f"  Total events in track: {event_num}")

def main():
    me_file = 'Our_Gods_are_an_awesome_God_En x2MEforAI.kar'
    sk_file = 'Our_Gods_are_an_awesome_God_En x2SKforAI.kar'
    
    print("\n" + "="*100)
    print("MIDI/KAR FILE ANALYSIS - Comparing SK vs ME Formats")
    print("="*100)
    
    # Parse both files
    me_parser = MIDIParser(me_file)
    sk_parser = MIDIParser(sk_file)
    
    # Compare
    print("\n" + "="*100)
    print("COMPARISON")
    print("="*100)
    print(f"\nME File Lyrics ({len(me_parser.lyrics)} total):")
    for time, text in me_parser.lyrics[:20]:  # First 20
        print(f"  [{time:6d}] {text}")
    
    print(f"\nSK File Lyrics ({len(sk_parser.lyrics)} total):")
    for time, text in sk_parser.lyrics[:20]:  # First 20
        print(f"  [{time:6d}] {text}")
    
    print(f"\nME File Events: {len(me_parser.events)}")
    print(f"SK File Events: {len(sk_parser.events)}")
    
    print(f"\nME File Notes: {len(me_parser.notes)}")
    print(f"SK File Notes: {len(sk_parser.notes)}")

if __name__ == '__main__':
    main()
