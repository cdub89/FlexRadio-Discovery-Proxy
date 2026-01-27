# FlexRadio Discovery Proxy - Release Notes v2.0.0

**Release Date:** January 26, 2026  
**Build:** v2.0.0 Major Architecture Update

---

## 🎉 Major Release: Client/Server Architecture

Version 2.0.0 represents a **complete redesign** of the FlexRadio Discovery Proxy with a fundamentally different approach to enabling remote radio discovery.

---

## Executive Summary

### What Changed

**v1.x Approach:**
- Single script generates synthetic VITA-49 discovery packets
- Uses ping to determine if radio is online
- Requires manual configuration of all radio parameters
- Broadcasts synthetic packets to local network

**v2.0 Approach:**
- **Server script** captures authentic VITA-49 packets from actual radio
- **Client script** rebroadcasts the real packets
- Communication via **shared file** (network share or cloud storage)
- No manual radio configuration needed - uses real data

### Why This Matters

1. **Authenticity**: Broadcasts actual packets with real radio status
2. **Flexibility**: Works across any network topology (VPN, internet, cloud)
3. **Accuracy**: Reflects true radio state (in use, available, offline)
4. **Scalability**: Supports multiple radios easily
5. **Simplicity**: No manual packet construction or radio details needed

---

## New Components

### FRS-Discovery-Server-v2.py

**Purpose:** Runs on remote location where FlexRadio is located

**Features:**
- Listens on UDP port 4992 for FlexRadio discovery broadcasts
- Captures authentic VITA-49 packets from radio
- Parses packet payload to extract radio information
- Writes packet data to JSON file on shared drive
- Rate-limited file updates to prevent excessive I/O
- Detailed console output with radio status
- Comprehensive logging to `discovery-server.log`

**Key Capabilities:**
```python
- Packet capture and validation
- Payload parsing (model, serial, IP, callsign, status, etc.)
- JSON file writing with timestamp and metadata
- Automatic detection of packet absence
- Error handling and recovery
```

### FRS-Discovery-Client-v2.py

**Purpose:** Runs on local PC where SmartSDR client is running

**Features:**
- Monitors shared JSON file for discovery data
- Checks file age to ensure radio is active
- Rebroadcasts authentic packets to local network
- Rate-limited broadcasts to match FlexRadio timing
- Stale file detection with warnings
- Detailed console output with broadcast status
- Comprehensive logging to `discovery-client.log`

**Key Capabilities:**
```python
- File monitoring and age verification
- Packet reconstruction from hex data
- UDP broadcast to local network
- Status change detection and logging
- Periodic status updates
```

### config-v2.ini

**Purpose:** Configuration for both server and client

**Server Settings:**
```ini
[SERVER]
Listen_Address = 0.0.0.0          # Interface to listen on
Discovery_Port = 4992              # FlexRadio discovery port
Shared_File_Path = discovery.json  # Path to shared file
Update_Interval = 2.0              # Seconds between file writes
```

**Client Settings:**
```ini
[CLIENT]
Shared_File_Path = discovery.json      # Same file as server
Broadcast_Address = 255.255.255.255    # Local broadcast
Discovery_Port = 4992                  # FlexRadio discovery port
Check_Interval = 3.0                   # File check frequency
Max_File_Age = 15.0                    # Stale file threshold
```

---

## Technical Implementation

### File Format (discovery.json)

The shared file contains complete discovery packet information:

```json
{
  "timestamp": "2026-01-26 14:23:45",
  "timestamp_unix": 1737904425.123,
  "server_version": "2.0.0",
  "packet_hex": "38520...",
  "packet_size": 748,
  "source_ip": "192.168.0.101",
  "source_port": 4992,
  "radio_info": {
    "model": "FLEX-6600",
    "serial": "3718-0522-6600-0003",
    "ip": "192.168.0.101",
    "nickname": "Lake6600",
    "callsign": "WX7V",
    "version": "4.1.5.39794",
    "status": "Available"
  },
  "parsed_payload": {
    "discovery_protocol_version": "3.1.0.2",
    "model": "FLEX-6600",
    "serial": "3718-0522-6600-0003",
    // ... all discovery fields ...
  }
}
```

### Communication Flow

```
1. FlexRadio broadcasts VITA-49 discovery packet
   ↓
2. Server receives and validates packet
   ↓
3. Server parses payload and extracts radio info
   ↓
4. Server writes complete packet data to JSON file
   ↓
5. File syncs via network share or cloud storage
   ↓
6. Client detects file update
   ↓
7. Client reads and validates packet data
   ↓
8. Client reconstructs packet from hex data
   ↓
9. Client broadcasts packet to local network
   ↓
10. SmartSDR receives broadcast and discovers radio
```

### Timing and Rate Limiting

**Server:**
- Receives packets as fast as radio sends them (typically 2-5 seconds)
- Rate-limits file writes to `Update_Interval` (default 2.0s)
- Prevents excessive disk I/O from rapid broadcasts

**Client:**
- Checks file every `Check_Interval` (default 3.0s)
- Broadcasts immediately when new packet detected
- Warns if file age exceeds `Max_File_Age` (default 15.0s)

**Why These Timings:**
- Balances responsiveness vs. resource usage
- Allows for network/cloud sync delays
- Matches FlexRadio's typical broadcast frequency
- Prevents false "radio offline" warnings

---

## Use Cases

### Scenario 1: Remote Home Radio via VPN

**Setup:**
- FlexRadio at home on 192.168.1.0/24
- Remote laptop via VPN
- VPN provides IP connectivity but different subnet
- SMB share on home NAS

**Configuration:**
- Server at home: `Shared_File_Path = \\nas\flexradio\discovery.json`
- Client on laptop: `Shared_File_Path = Z:\flexradio\discovery.json` (mapped drive)
- Radio appears in SmartSDR instantly

### Scenario 2: Vacation Home Radio via Internet

**Setup:**
- FlexRadio at vacation home
- Primary residence hundreds of miles away
- No VPN, only internet access
- Dropbox on both locations

**Configuration:**
- Server at vacation home: `Shared_File_Path = C:\Dropbox\FlexRadio\discovery.json`
- Client at primary: `Shared_File_Path = C:\Dropbox\FlexRadio\discovery.json`
- Discovery syncs via Dropbox (5-30 second delay)
- SmartSDR shows radio status accurately

### Scenario 3: Multiple Radios at Contest Station

**Setup:**
- Three FlexRadio units at contest site
- Multiple operators on different subnets
- Central file server

**Configuration:**
- Three server instances, each with own file: `discovery-radio1.json`, etc.
- Three client instances on each operator PC
- All radios appear in SmartSDR for each operator

### Scenario 4: Portable Operation with USB Drive

**Setup:**
- FlexRadio in vehicle
- Laptop in different location (hotel room)
- USB drive moved between locations

**Configuration:**
- Server: `Shared_File_Path = discovery.json` (copied to USB before moving)
- Client: `Shared_File_Path = E:\discovery.json` (USB drive)
- Manual file transfer, but still works!

---

## Advantages Over v1.x

| Aspect | v1.x | v2.0 | Winner |
|--------|------|------|--------|
| **Packet Authenticity** | Synthetic | Real | v2.0 ✓ |
| **Radio Status** | Ping guess | Actual status | v2.0 ✓ |
| **Configuration** | Manual all fields | Automatic | v2.0 ✓ |
| **Network Topology** | Direct path only | Any | v2.0 ✓ |
| **Setup Complexity** | Simple | Moderate | v1.x ✓ |
| **Latency** | Instant | File sync delay | v1.x ✓ |
| **Multi-Radio** | Not supported | Easy | v2.0 ✓ |
| **Future-Proof** | Manual updates | Automatic | v2.0 ✓ |
| **Resource Usage** | Low | Moderate | v1.x ✓ |

**Overall Winner:** v2.0 for most use cases

**When to use v1.x:**
- Direct VPN with routed subnet
- Need absolute lowest latency
- Want simplest possible setup
- Single radio only

**When to use v2.0:**
- Internet access (no VPN)
- Multiple radios
- Want authentic radio status
- Flexible network topology
- Future FlexRadio updates

---

## Breaking Changes from v1.x

### ⚠️ Complete Redesign - No Backward Compatibility

**v1.x files:**
- `FRS-Discovery-Proxy.py` - Not used
- `config.ini` - Not compatible
- `broadcast.log` - Different format

**v2.0 files:**
- `FRS-Discovery-Server-v2.py` - New server component
- `FRS-Discovery-Client-v2.py` - New client component
- `config-v2.ini` - Completely different structure
- `discovery-server.log` - Server logging
- `discovery-client.log` - Client logging

**Migration:** There is no automatic migration. v1.x and v2.0 are independent systems.

---

## Installation Requirements

### Server Requirements
- Same subnet as FlexRadio (can receive broadcasts)
- Python 3.6+
- Write access to shared file location
- Firewall allows UDP port 4992 inbound

### Client Requirements
- Same subnet as SmartSDR client
- Python 3.6+
- Read access to shared file location
- Firewall allows UDP port 4992 outbound broadcast

### Shared Storage Requirements
- Network share (SMB/NFS) OR cloud sync (Dropbox/OneDrive/etc.)
- Both server and client must access same file
- Adequate permissions for read/write

### No New Dependencies
Both scripts use only Python standard library:
- `socket` - UDP networking
- `json` - File format
- `configparser` - Configuration
- `logging` - Log files
- `time`, `datetime`, `os`, `sys` - Utilities

---

## Performance Characteristics

### Network Traffic

**Server:**
- Receives: ~1 packet per 2-5 seconds from radio (~750 bytes each)
- Network: Minimal (only UDP receiving)

**Client:**
- Broadcasts: ~1 packet per 3-5 seconds (~750 bytes each)
- Network: Minimal (only UDP broadcasting)

### Disk I/O

**Server:**
- Writes: Every 2 seconds (default)
- File size: ~2-3 KB per write
- Daily I/O: ~43,200 writes, ~130 MB

**Client:**
- Reads: Every 3 seconds (default)
- File size: ~2-3 KB per read
- Daily I/O: ~28,800 reads, ~86 MB

### Cloud Sync Impact

If using cloud storage:
- Dropbox/OneDrive: ~2-3 KB upload/download every 2-5 seconds
- Daily bandwidth: ~200-300 MB total
- Latency: Typically 5-30 seconds depending on service

---

## Known Limitations

1. **File Sync Latency**: Discovery updates limited by file sync speed
   - Network share: <1 second typically
   - Cloud sync: 5-30 seconds typically
   - USB manual: Hours/days potentially

2. **Subnet Requirement**: Server must be on same subnet as FlexRadio
   - Cannot capture broadcasts across routers
   - May not work with radio on separate VLAN

3. **No Bidirectional Status**: Server doesn't know about client connections
   - Radio status reflects radio's view only
   - Client connections not tracked by server

4. **File System Dependency**: Requires reliable shared storage
   - Network outages break communication
   - File permission issues prevent operation
   - Cloud service outages cause delays

5. **Single Packet Storage**: Only most recent packet stored
   - No packet history or playback
   - File corruption loses current state
   - Must wait for next radio broadcast

---

## Testing Recommendations

### Initial Server Testing

1. **Verify Packet Reception:**
```bash
python FRS-Discovery-Server-v2.py
# Should see: "Packet #1 from ..."
```

2. **Check File Creation:**
```bash
# Look for discovery.json in shared location
# File should be ~2-3 KB and update every few seconds
```

3. **Validate JSON Structure:**
```bash
# Open discovery.json and verify all fields present
```

### Initial Client Testing

1. **Verify File Access:**
```bash
python FRS-Discovery-Client-v2.py
# Should see: "Radio discovered: ..."
```

2. **Check Broadcasts:**
```bash
# Use Wireshark: udp.port == 4992
# Should see broadcasts every few seconds
```

3. **Test SmartSDR:**
```bash
# Open SmartSDR
# Radio should appear in chooser
```

### Integration Testing

1. **Stop Server** - Verify client detects stale file
2. **Stop Radio** - Verify server reports no packets
3. **Disconnect Share** - Verify both detect file errors
4. **Simulate Latency** - Add delays to file sync

---

## Troubleshooting Guide

### Server: "Permission denied" on file write

**Cause:** Insufficient write permissions to shared location

**Solution:**
```bash
# Windows: Check share permissions and NTFS permissions
# Linux: Check file ownership and permissions (chmod/chown)
# Cloud: Ensure sync client is running and folder is synced
```

### Client: "File not found"

**Cause:** Shared path not accessible or wrong path

**Solution:**
```bash
# Verify path exists: dir Z:\FlexRadio\discovery.json (Windows)
# Check network share is mounted
# Ensure cloud sync has synced the file
# Try absolute path instead of relative
```

### SmartSDR: "Radio appears then disappears"

**Cause:** File age exceeding Max_File_Age intermittently

**Solution:**
```ini
# Increase Max_File_Age in config-v2.ini
Max_File_Age = 30.0  # Was 15.0
```

### High Disk I/O on cloud sync

**Cause:** Sync service updating index frequently

**Solution:**
```ini
# Increase update intervals
[SERVER]
Update_Interval = 5.0  # Was 2.0
[CLIENT]
Check_Interval = 5.0   # Was 3.0
```

---

## Upgrade Path

### From v1.0.x to v2.0.0

**No direct upgrade - complete redesign**

1. Keep v1.x running initially
2. Set up v2.0 server on remote side
3. Set up v2.0 client on local side
4. Test v2.0 alongside v1.x
5. Once v2.0 verified, stop v1.x
6. Optional: Archive v1.x files for rollback

**Configuration Migration:**
- v1.x `config.ini` is not compatible
- Radio details from v1.x can be ignored (v2.0 captures automatically)
- No other settings carry over

---

## Future Roadmap

### v2.1.0 (Planned)
- Multiple radio support in single server instance
- Radio filtering options
- Packet history and caching
- Web dashboard for monitoring

### v2.2.0 (Planned)
- Direct TCP/UDP tunneling option (bypass file system)
- Encryption for discovery data
- Compression for cloud efficiency
- Automatic server/client discovery

### v3.0.0 (Future)
- Full bidirectional communication
- Client status reporting to server
- Dynamic radio configuration
- SmartSDR integration enhancements

---

## Credits & Acknowledgments

**Original FlexRadio Broadcast Wedge:**
- Mike Hebert, VA3MW (May 2024)
- Initial concept and v1.0 implementation

**v2.0 Client/Server Architecture:**
- Chris L White, WX7V (January 2026)
- Complete redesign with authentic packet capture

**FlexRadio Systems:**
- VITA-49 protocol implementation
- SmartSDR platform and documentation

**Testing & Feedback:**
- Amateur radio community
- FlexRadio user forums

---

## License

MIT License - See LICENSE file

Copyright (c) 2024-2026 VA3MW, WX7V

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## Contact & Support

**Not supported by FlexRadio Systems, Inc.**

For v2.0 specific questions:
- GitHub: [Repository URL]
- Email: [Contact]
- QRZ: WX7V

For general FlexRadio questions:
- FlexRadio Community Forums
- FlexRadio Support

---

**73 de WX7V**

**USE AT YOUR OWN RISK**
