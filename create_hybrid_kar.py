#!/usr/bin/env python3
"""
Create hybrid KAR files that contain both SK (Soft Karaoke) and ME (MIDI Events) data.
This script merges SK metadata/lyrics with MIDI event data into a single file.
"""

import struct
import sys
from pathlib import Path
from io import BytesIO

class KARMerger:
    def __init__(self, sk_file, me_file, output_file):
        self.sk_file = sk_file
        self.me_file = me_file
        self.output_file = output_file
        self.sk_data = None
        self.me_data = None
        self.sk_events = []
        self.me_events = []
    
    def read_file(self, filename):
        """Read a KAR file"""
        with open(filename, 'rb') as f:
            return f.read()
    
    def parse_midi_events(self, data, label=""):
        """Extract all events from MIDI data"""
        events = []
        
        if data[:4] != b'MThd':
            print(f"{label}ERROR: Not valid MIDI")
            return events
        
        # Parse header
        header_len = struct.unpack('>I', data[4:8])[0]
        format_type = struct.unpack('>H', data[8:10])[0]
        num_tracks = struct.unpack('>H', data[10:12])[0]
        division = struct.unpack('>H', data[12:14])[0]
        
        print(f"{label}Format: {format_type}, Tracks: {num_tracks}, Division: {division}")
        
        pos = 14
        track_num = 0
        
        while pos < len(data):
            if pos + 8 > len(data):
                break
            
            if data[pos:pos+4] == b'MTrk':
                track_num += 1
                track_len = struct.unpack('>I', data[pos+4:pos+8])[0]
                pos += 8
                track_end = pos + track_len
                
                current_time = 0
                while pos < track_end:
                    delta, pos = self._read_varint(data, pos)
                    current_time += delta
                    
                    if pos >= track_end:
                        break
                    
                    status = data[pos]
                    pos += 1
                    
                    # Meta event
                    if status == 0xFF:
                        if pos >= track_end:
                            break
                        meta_type = data[pos]
                        pos += 1
                        
                        if pos >= track_end:
                            break
                        length, pos = self._read_varint(data, pos)
                        
                        if pos + length > track_end:
                            break
                        
                        event_data = data[pos:pos+length]
                        pos += length
                        
                        events.append({
                            'type': 'meta',
                            'meta_type': meta_type,
                            'time': current_time,
                            'data': event_data
                        })
                    
                    # MIDI Note On
                    elif status & 0xF0 == 0x90:
                        if pos + 2 > track_end:
                            break
                        note = data[pos]
                        velocity = data[pos+1]
                        pos += 2
                        
                        events.append({
                            'type': 'note_on',
                            'time': current_time,
                            'note': note,
                            'velocity': velocity
                        })
                    
                    # MIDI Note Off
                    elif status & 0xF0 == 0x80:
                        if pos + 2 > track_end:
                            break
                        note = data[pos]
                        velocity = data[pos+1]
                        pos += 2
                        
                        events.append({
                            'type': 'note_off',
                            'time': current_time,
                            'note': note
                        })
                    
                    # Control Change
                    elif status & 0xF0 == 0xB0:
                        if pos + 2 > track_end:
                            break
                        controller = data[pos]
                        value = data[pos+1]
                        pos += 2
                        
                        events.append({
                            'type': 'control_change',
                            'time': current_time,
                            'controller': controller,
                            'value': value
                        })
                    
                    # Program Change
                    elif status & 0xF0 == 0xC0:
                        if pos + 1 > track_end:
                            break
                        program = data[pos]
                        pos += 1
                        
                        events.append({
                            'type': 'program_change',
                            'time': current_time,
                            'program': program
                        })
                    
                    # SysEx
                    elif status == 0xF0 or status == 0xF7:
                        if pos >= track_end:
                            break
                        length, pos = self._read_varint(data, pos)
                        if pos + length > track_end:
                            break
                        sysex_data = data[pos:pos+length]
                        pos += length
                        
                        events.append({
                            'type': 'sysex',
                            'time': current_time,
                            'data': sysex_data
                        })
                
                pos = track_end
            else:
                pos += 1
        
        return events
    
    def _read_varint(self, data, pos):
        """Read variable length integer"""
        value = 0
        while pos < len(data):
            byte = data[pos]
            pos += 1
            value = (value << 7) | (byte & 0x7F)
            if not (byte & 0x80):
                break
        return value, pos
    
    def _write_varint(self, value):
        """Write variable length integer"""
        buffer = bytearray()
        buffer.append(value & 0x7F)
        value >>= 7
        
        while value:
            buffer.insert(0, (value & 0x7F) | 0x80)
            value >>= 7
        
        return bytes(buffer)
    
    def create_hybrid_file(self):
        """Create hybrid KAR file with both SK and ME data"""
        print("\n" + "="*100)
        print("CREATING HYBRID KAR FILE")
        print("="*100 + "\n")
        
        # Read files
        self.sk_data = self.read_file(self.sk_file)
        self.me_data = self.read_file(self.me_file)
        
        print(f"SK file size: {len(self.sk_data)} bytes")
        print(f"ME file size: {len(self.me_data)} bytes\n")
        
        # Parse events
        print("Parsing SK file...")
        self.sk_events = self.parse_midi_events(self.sk_data, "  SK: ")
        
        print(f"Found {len(self.sk_events)} events in SK file\n")
        
        print("Parsing ME file...")
        self.me_events = self.parse_midi_events(self.me_data, "  ME: ")
        
        print(f"Found {len(self.me_events)} events in ME file\n")
        
        # Extract SK lyrics/metadata
        sk_lyrics = []
        sk_metadata = []
        
        for evt in self.sk_events:
            if evt['type'] == 'meta':
                meta_type = evt['meta_type']
                data = evt['data']
                
                # Lyric event (0x05)
                if meta_type == 0x05:
                    text = data.decode('utf-8', errors='replace')
                    sk_lyrics.append((evt['time'], text))
                    print(f"  SK Lyric @ {evt['time']:6d}: {text}")
                
                # Text event (0x01)
                elif meta_type == 0x01:
                    text = data.decode('utf-8', errors='replace')
                    sk_metadata.append((evt['time'], text))
                    print(f"  SK Text @ {evt['time']:6d}: {text}")
        
        print(f"\nExtracted {len(sk_lyrics)} lyrics and {len(sk_metadata)} metadata from SK file")
        
        # Create hybrid file by merging SK metadata into ME structure
        hybrid_data = self._merge_events()
        
        # Write output
        with open(self.output_file, 'wb') as f:
            f.write(hybrid_data)
        
        print(f"\nHybrid KAR file created: {self.output_file} ({len(hybrid_data)} bytes)")
        print("="*100 + "\n")
    
    def _merge_events(self):
        """Merge SK and ME events into a single MIDI file"""
        output = BytesIO()
        
        # Write MIDI header (copy from ME file)
        if self.me_data[:4] == b'MThd':
            header_len = struct.unpack('>I', self.me_data[4:8])[0]
            output.write(self.me_data[:8+header_len])
        
        # Create merged track
        track_data = BytesIO()
        
        # Combine all events sorted by time
        all_events = []
        
        # Add ME events
        for evt in self.me_events:
            all_events.append(('ME', evt['time'], evt))
        
        # Add SK events
        for evt in self.sk_events:
            all_events.append(('SK', evt['time'], evt))
        
        # Sort by time
        all_events.sort(key=lambda x: x[1])
        
        # Write events
        current_time = 0
        for source, time, evt in all_events:
            delta = time - current_time
            current_time = time
            
            # Write delta time
            track_data.write(self._write_varint(delta))
            
            # Write event
            if evt['type'] == 'meta':
                track_data.write(b'\xFF')
                track_data.write(bytes([evt['meta_type']]))
                track_data.write(self._write_varint(len(evt['data'])))
                track_data.write(evt['data'])
            
            elif evt['type'] == 'note_on':
                track_data.write(bytes([0x90]))
                track_data.write(bytes([evt['note']]))
                track_data.write(bytes([evt['velocity']]))
            
            elif evt['type'] == 'note_off':
                track_data.write(bytes([0x80]))
                track_data.write(bytes([evt['note']]))
                track_data.write(bytes([0x40]))
            
            elif evt['type'] == 'control_change':
                track_data.write(bytes([0xB0]))
                track_data.write(bytes([evt['controller']]))
                track_data.write(bytes([evt['value']]))
            
            elif evt['type'] == 'program_change':
                track_data.write(bytes([0xC0]))
                track_data.write(bytes([evt['program']]))
            
            elif evt['type'] == 'sysex':
                track_data.write(b'\xF0')
                track_data.write(self._write_varint(len(evt['data'])))
                track_data.write(evt['data'])
        
        # Write end of track
        track_data.write(b'\x00\xFF\x2F\x00')
        
        # Write track header
        track_bytes = track_data.getvalue()
        output.write(b'MTrk')
        output.write(struct.pack('>I', len(track_bytes)))
        output.write(track_bytes)
        
        return output.getvalue()

def main():
    sk_file = 'Our_Gods_are_an_awesome_God_En x2SKforAI.kar'
    me_file = 'Our_Gods_are_an_awesome_God_En x2MEforAI.kar'
    output_file = 'Our_Gods_are_an_awesome_God_En_HYBRID.kar'
    
    if not Path(sk_file).exists():
        print(f"ERROR: {sk_file} not found")
        return
    
    if not Path(me_file).exists():
        print(f"ERROR: {me_file} not found")
        return
    
    merger = KARMerger(sk_file, me_file, output_file)
    merger.create_hybrid_file()

if __name__ == '__main__':
    main()
