# FlexRadio Discovery Proxy v3.0.1 - Changelog

## Version 3.0.1 (January 28, 2026)

### Enhanced Logging Features

Version 3.0.1 introduces intelligent logging enhancements for both server and client components.

### Bug Fixes

**Fixed: Health Check Configuration Error**
- Fixed `KeyError: 'Shared_File_Path'` when running health checks in v3.0
- Health checks now correctly default to socket mode (v3.0+) instead of legacy file mode (v2.x)
- Added proper fallback handling for missing legacy configuration options
- File: `health_checks.py`

**Improved: Log Flushing**
- Added explicit log flushing for initial packet and payload change events
- Console confirmation message when logging occurs
- Ensures logs are immediately written to disk for troubleshooting
- Files: `FRS-Discovery-Server.py`, `FRS-Discovery-Client.py`

#### New Features

1. **Cached Packet Mode for Offline Operation (Client)**
   - **Automatic packet caching:** Client saves last received discovery packet to disk
   - **Offline fallback:** When server is unreachable, client uses cached packet
   - **Continuous broadcasting:** Cached packet broadcasts at configurable interval
   - **Background reconnection:** Client continues trying to reconnect while in cached mode
   - **Automatic mode switching:** Seamlessly switches between LIVE and CACHED modes
   - **Cache age validation:** Configurable maximum age for cached packets
   - **Visual indicators:** Console shows current mode [LIVE] or [CACHED]
   - **Resilient operation:** Maintains radio visibility even when server is down
   - **Perfect for:** VPN disruptions, server maintenance, network issues

2. **Log Rotation at Startup with Automatic Cleanup**
   - Automatically archives existing log files on startup
   - Archived files are timestamped with the original file's modification time
   - Format: `discovery-server_YYYYMMDD_HHMMSS.log`
   - Example: `discovery-server_20260128_143052.log`
   - **Configurable retention:** Set maximum number of archived logs to keep
   - **Automatic cleanup:** Oldest logs deleted when limit exceeded
   - **Default:** Keeps 2 most recent archived logs
   - **Configuration:** `Max_Log_Files` in `[DIAGNOSTICS]` section
   - Set to 0 to keep all archived logs indefinitely
   - Prevents log files from growing indefinitely
   - Maintains historical logs for troubleshooting

2. **Initial Discovery Packet Logging with Full Hex Dump**
   - The first discovery packet received is always logged with complete details
   - **Full hex dump** in standard format (16 bytes per line with ASCII representation)
   - **All parsed fields** displayed in readable format
   - Captures critical radio information at startup:
     - Model and nickname
     - Callsign and IP address
     - Status and version
     - Serial number
     - Packet size and source information
   - Server logs when first packet is received from radio
   - Client logs when first packet is received from server

3. **Payload Change Detection with Full Packet Logging**
   - Intelligently logs only when payload content changes
   - **Full hex dump** of changed packet for analysis
   - **All parsed fields** with current values
   - Tracks and compares discovery packet payloads
   - Logs specific fields that have changed
   - Shows old value → new value for changed fields
   - Identifies newly added and removed fields
   - Reduces log noise while capturing important state changes
   - Perfect for troubleshooting radio state transitions

#### Configuration

**New Settings in `config.ini`:**

**Client Cache Settings:**
```ini
[CLIENT]
# Cache settings for offline operation
# File to store last received discovery packet
Cached_Packet_File = last_discovery_packet.json

# Use cached packet when server is unreachable (true/false)
Use_Cached_Packet = true

# Maximum age of cached packet in seconds (0 = no limit)
# If cached packet is older than this, it won't be used
Max_Cache_Age = 3600

# Broadcast interval when using cached packet (seconds)
# How often to rebroadcast the cached packet when server is offline
Cached_Broadcast_Interval = 3.0
```

**Cache Configuration Examples:**
- `Use_Cached_Packet = true`: Enable cached packet fallback (default, recommended)
- `Use_Cached_Packet = false`: Disable cached mode (stop broadcasting when server is down)
- `Max_Cache_Age = 3600`: Use cached packet if less than 1 hour old
- `Max_Cache_Age = 0`: Use cached packet regardless of age
- `Cached_Broadcast_Interval = 3.0`: Broadcast every 3 seconds in cached mode

**Log Rotation Settings:**
```ini
[DIAGNOSTICS]
# Maximum number of rotated log files to keep
# Older log files beyond this limit will be automatically deleted
# Set to 0 to keep all archived logs indefinitely
Max_Log_Files = 2
```

**Log Rotation Examples:**
- `Max_Log_Files = 2` (default): Keeps 2 most recent archived logs
- `Max_Log_Files = 5`: Keeps 5 most recent archived logs
- `Max_Log_Files = 0`: Keeps all archived logs (no automatic deletion)

#### Technical Details

**Server Changes (`FRS-Discovery-Server.py`):**
- Added `rotate_log_file()` function with max_log_files parameter
- Added `cleanup_old_logs()` function for automatic log cleanup
- Added payload tracking: `last_payload` and `first_packet_received`
- Enhanced packet processing to detect payload changes
- Logs detailed field-level changes with before/after values
- Reads `Max_Log_Files` from config with fallback to 2
- Version updated to 3.0.1

**Client Changes (`FRS-Discovery-Client.py`):**
- Added `rotate_log_file()` function with max_log_files parameter
- Added `cleanup_old_logs()` function for automatic log cleanup
- Added payload tracking: `last_payload` and `first_packet_received`
- Enhanced packet processing to detect payload changes
- Compares parsed payload as JSON to avoid false positives from timestamp variations
- Logs detailed field-level changes with before/after values
- Reads `Max_Log_Files` from config with fallback to 2
- Version updated to 3.0.1

**Configuration Changes (`config.ini`):**
- Added `Max_Log_Files` setting to `[DIAGNOSTICS]` section
- Default value: 2
- Controls automatic cleanup of old archived log files

#### Example Startup Output

**Client in Cached Mode (Server Unreachable):**
```
Connecting to server 192.168.0.100:5992...
⚠ Connection timeout to 192.168.0.100:5992

14:30:52 - ⚠ Server unreachable after 1 attempts
  Switching to CACHED PACKET MODE
  Broadcasting cached discovery packet every 3.0s
  Will continue trying to reconnect to server...

14:30:52 - [CACHED MODE] Broadcasting FLEX-6600 (packet #1)
  Reconnect attempts: 5 | Next attempt in 5s

✓ Loaded cached packet from 2026-01-28 13:45:30
  Cache age: 2722 seconds

14:31:12 - [CACHED MODE] Broadcasting FLEX-6600 (packet #20)
  Reconnect attempts: 10 | Next attempt in 5s

14:31:42 - ✓ Reconnected to server - switching to LIVE MODE

14:31:45 - Radio discovered:
  FLEX-6600 (Lake6600)
  Callsign: WX7V | IP: 192.168.0.101
  Status: Available | Version: 4.1.5.39794
  Server: v3.0.1
14:31:45 - ✓ Started broadcasting discovery packets [LIVE MODE]
```

**Log Rotation and Cleanup:**
```
Rotated log file: discovery-server.log → discovery-server_20260128_143052.log
Deleted old log file: discovery-server_20260128_120301.log
Deleted old log file: discovery-server_20260128_095423.log
```
*(Keeps only the 2 most recent archived logs based on Max_Log_Files setting)*

#### Example Log Output

**Initial Packet (Server):**
```
2026-01-28 14:30:52 - INFO - ================================================================================
2026-01-28 14:30:52 - INFO - INITIAL DISCOVERY PACKET - 2026-01-28 14:30:52
2026-01-28 14:30:52 - INFO - ================================================================================
2026-01-28 14:30:52 - INFO - Radio: FLEX-6600 (Lake6600)
2026-01-28 14:30:52 - INFO - Callsign: WX7V | IP: 192.168.0.101
2026-01-28 14:30:52 - INFO - Status: Available | Version: 4.1.5.39794
2026-01-28 14:30:52 - INFO - Serial: 3718-0522-6600-0003
2026-01-28 14:30:52 - INFO - Source: 192.168.0.101:4992 | Packet Size: 748 bytes
2026-01-28 14:30:52 - INFO - 
2026-01-28 14:30:52 - INFO - Full Packet Hex Dump:
2026-01-28 14:30:52 - INFO - --------------------------------------------------------------------------------
2026-01-28 14:30:52 - INFO - 0000  38 52 00 b4 00 00 08 00 00 00 1c 2d 53 4c ff ff  8R.........-SL..
2026-01-28 14:30:52 - INFO - 0010  69 75 47 d1 00 00 00 00 00 00 00 00 64 69 73 63  iuG.........disc
2026-01-28 14:30:52 - INFO - 0020  6f 76 65 72 79 5f 70 72 6f 74 6f 63 6f 6c 5f 76  overy_protocol_v
2026-01-28 14:30:52 - INFO - 0030  65 72 73 69 6f 6e 3d 33 2e 31 2e 30 2e 32 20 6d  ersion=3.1.0.2 m
2026-01-28 14:30:52 - INFO - 0040  6f 64 65 6c 3d 46 4c 45 58 2d 36 36 30 30 20 73  odel=FLEX-6600 s
2026-01-28 14:30:52 - INFO - [... continues with full hex dump ...]
2026-01-28 14:30:52 - INFO - --------------------------------------------------------------------------------
2026-01-28 14:30:52 - INFO - 
2026-01-28 14:30:52 - INFO - Parsed Discovery Fields:
2026-01-28 14:30:52 - INFO - --------------------------------------------------------------------------------
2026-01-28 14:30:52 - INFO -   available_clients              = 2
2026-01-28 14:30:52 - INFO -   available_panadapters          = 4
2026-01-28 14:30:52 - INFO -   available_slices               = 4
2026-01-28 14:30:52 - INFO -   callsign                       = WX7V
2026-01-28 14:30:52 - INFO -   discovery_protocol_version     = 3.1.0.2
2026-01-28 14:30:52 - INFO -   ip                             = 192.168.0.101
2026-01-28 14:30:52 - INFO -   licensed_clients               = 2
2026-01-28 14:30:52 - INFO -   max_licensed_version           = v4
2026-01-28 14:30:52 - INFO -   max_panadapters                = 4
2026-01-28 14:30:52 - INFO -   max_slices                     = 4
2026-01-28 14:30:52 - INFO -   model                          = FLEX-6600
2026-01-28 14:30:52 - INFO -   nickname                       = Lake6600
2026-01-28 14:30:52 - INFO -   port                           = 4992
2026-01-28 14:30:52 - INFO -   serial                         = 3718-0522-6600-0003
2026-01-28 14:30:52 - INFO -   status                         = Available
2026-01-28 14:30:52 - INFO -   version                        = 4.1.5.39794
2026-01-28 14:30:52 - INFO -   [... all other fields ...]
2026-01-28 14:30:52 - INFO - ================================================================================
```

**Payload Change:**
```
2026-01-28 15:15:23 - INFO - ================================================================================
2026-01-28 15:15:23 - INFO - DISCOVERY PAYLOAD CHANGED - 2026-01-28 15:15:23
2026-01-28 15:15:23 - INFO - ================================================================================
2026-01-28 15:15:23 - INFO - Radio: FLEX-6600 (Lake6600)
2026-01-28 15:15:23 - INFO - Callsign: WX7V | IP: 192.168.0.101
2026-01-28 15:15:23 - INFO - Status: In Use | Version: 4.1.5.39794
2026-01-28 15:15:23 - INFO - Source: 192.168.0.101:4992 | Packet Size: 748 bytes
2026-01-28 15:15:23 - INFO - 
2026-01-28 15:15:23 - INFO - Changed Fields:
2026-01-28 15:15:23 - INFO - --------------------------------------------------------------------------------
2026-01-28 15:15:23 - INFO -   status                         = 'Available' → 'In Use'
2026-01-28 15:15:23 - INFO -   available_clients              = '2' → '1'
2026-01-28 15:15:23 - INFO -   inuse_ip                       = '' → '192.168.1.50'
2026-01-28 15:15:23 - INFO -   inuse_host                     = '' → 'station1.local'
2026-01-28 15:15:23 - INFO -   gui_client_ips                 = (new) '192.168.1.50'
2026-01-28 15:15:23 - INFO -   gui_client_handles             = (new) '0x12345678'
2026-01-28 15:15:23 - INFO - 
2026-01-28 15:15:23 - INFO - Full Packet Hex Dump:
2026-01-28 15:15:23 - INFO - --------------------------------------------------------------------------------
2026-01-28 15:15:23 - INFO - 0000  38 52 00 b4 00 00 08 00 00 00 1c 2d 53 4c ff ff  8R.........-SL..
2026-01-28 15:15:23 - INFO - [... full hex dump of changed packet ...]
2026-01-28 15:15:23 - INFO - --------------------------------------------------------------------------------
2026-01-28 15:15:23 - INFO - 
2026-01-28 15:15:23 - INFO - All Current Discovery Fields:
2026-01-28 15:15:23 - INFO - --------------------------------------------------------------------------------
2026-01-28 15:15:23 - INFO -   [... all current field values ...]
2026-01-28 15:15:23 - INFO - ================================================================================
```

#### Benefits

- **Resilient Operation:** Client continues working even when server is unreachable
- **Seamless Fallback:** Automatic switch to cached mode with no user intervention
- **Continuous Visibility:** SmartSDR can always discover the radio
- **VPN-Friendly:** Handles temporary VPN disconnections gracefully
- **Background Recovery:** Automatically reconnects when server becomes available
- **Complete Packet Analysis:** Full hex dump enables deep troubleshooting
- **Readable Field Values:** All discovery fields displayed in human-readable format
- **Protocol Analysis:** Hex dump shows VITA-49 header structure
- **Reduced Log Noise:** Only meaningful changes are logged, not every packet
- **Better Diagnostics:** Archived logs preserve history for troubleshooting
- **State Tracking:** Easily see when radio status changes (Available ↔ In Use)
- **Change Visibility:** Clear view of what fields changed and their values
- **Historical Data:** Timestamped archives maintain long-term history
- **Network Analysis:** Can analyze packet contents for debugging network issues

#### Backward Compatibility

- Fully compatible with v3.0.0
- No configuration changes required
- Existing `config.ini` works without modification
- Log rotation happens automatically on startup

#### Files Modified

- `FRS-Discovery-Server.py` → v3.0.1
  - Enhanced logging with full hex dumps
  - Payload change detection
  - Log flushing
- `FRS-Discovery-Client.py` → v3.0.1
  - **Cached packet mode for offline operation**
  - Enhanced logging with full hex dumps
  - Payload change detection
  - Log flushing
  - Automatic mode switching (LIVE ↔ CACHED)
- `health_checks.py` → Bug fix for v3.0 compatibility
- `config.ini` → Added cache settings and log rotation setting
  - `Cached_Packet_File`
  - `Use_Cached_Packet`
  - `Max_Cache_Age`
  - `Cached_Broadcast_Interval`
  - `Max_Log_Files`

#### Upgrade Instructions

**Step 1: Update Files**
Replace the following files:
1. `FRS-Discovery-Server.py`
2. `FRS-Discovery-Client.py`
3. `health_checks.py`

**Step 2: Update Configuration (Optional)**
Add the following line to your `config.ini` under the `[DIAGNOSTICS]` section:
```ini
Max_Log_Files = 2
```

If you don't add this setting, the default value of 2 will be used automatically.

**Step 3: Start Application**
Existing log files will be automatically archived on next startup, and old archives will be cleaned up based on your `Max_Log_Files` setting.

---

**Copyright (c) 2026 Chris L White (WX7V)**  
Licensed under the MIT License
