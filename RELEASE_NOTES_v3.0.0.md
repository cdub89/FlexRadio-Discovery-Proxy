# Release Notes - Version 3.0.0

**Release Date:** January 27, 2026  
**Release Type:** Major Version - Breaking Changes  
**Status:** Production Ready

---

## 🚀 Major Changes

### **Socket-Only Architecture**

Version 3.0.0 removes file-based communication mode and focuses exclusively on TCP socket streaming for optimal performance and simplicity.

---

## ✨ What's New

### Removed Features (Simplification)
- ❌ **File mode removed** - No more shared file dependencies
- ❌ **Cloud sync removed** - No more OneDrive/Dropbox requirements
- ❌ **File monitoring removed** - No more file age checks
- ❌ **Shared storage removed** - No more network share configuration

### Architecture Improvements
- ✅ **Socket-only mode** - Direct TCP streaming between server and client
- ✅ **Real-time communication** - Sub-second latency
- ✅ **Simplified configuration** - Fewer settings to manage
- ✅ **Cleaner codebase** - Removed ~150 lines of file handling code

### Performance Enhancements
- ✅ **Minimal logging** - Log files only written at startup/shutdown
- ✅ **Reduced disk I/O** - No continuous file writes
- ✅ **Better reliability** - No file system dependencies
- ✅ **Lower latency** - <1 second vs 5-30 seconds with file mode

---

## 🔧 Breaking Changes

### Configuration Changes

**REMOVED from config.ini (formerly config-v2.ini):**
```ini
# Server settings removed:
Stream_Mode = socket|file        # No longer needed
Shared_File_Path = ...           # File mode removed
Update_Interval = ...            # File mode removed

# Client settings removed:
Connection_Mode = socket|file    # No longer needed
Shared_File_Path = ...           # File mode removed
Check_Interval = ...             # File mode removed
Max_File_Age = ...               # File mode removed
```

**REQUIRED in config.ini:**
```ini
[SERVER]
Listen_Address = 0.0.0.0
Discovery_Port = 4992
Stream_Port = 5992              # TCP port for clients
Max_Clients = 5                 # Max simultaneous connections

[CLIENT]
Server_Address = 192.168.0.100  # Server IP (required)
Stream_Port = 5992              # Must match server
Reconnect_Interval = 5.0
Broadcast_Address = 255.255.255.255
Discovery_Port = 4992
```

### Code Changes

**Server (FRS-Discovery-Server.py):**
- Removed `Stream_Mode` parameter
- Removed `write_to_file()` method
- Removed `touch_file()` method
- Removed file mode logic from main loop
- Removed `Shared_File_Path`, `Update_Interval` settings
- Always runs in socket mode

**Client (FRS-Discovery-Client.py):**
- Removed `Connection_Mode` parameter
- Removed `run_file_mode()` method
- Removed `read_discovery_file()` method
- Renamed `run_socket_mode()` to `run()`
- Removed file monitoring logic
- Always runs in socket mode

---

## 📊 Performance Comparison

### v2.x File Mode vs v3.0 Socket Mode

| Metric | v2.x File Mode | v3.0 Socket |
|--------|---------------|-------------|
| **Latency** | 5-30 seconds | <1 second |
| **File I/O** | Continuous | Startup/shutdown only |
| **Dependencies** | File system, cloud sync | Network only |
| **Complexity** | High | Low |
| **Configuration** | 15+ settings | 10 settings |
| **Reliability** | Medium (file system) | High (TCP) |

### v2.x Socket Mode vs v3.0 Socket Mode

| Metric | v2.x Socket | v3.0 Socket |
|--------|-------------|-------------|
| **Functionality** | Same | Same |
| **Performance** | Same | Slightly better (less logging) |
| **Code Size** | Larger | Smaller (-150 lines) |
| **Configuration** | More options | Simpler |

---

## 🔄 Migration Guide

### From v2.x File Mode

1. **Stop both server and client**
   ```bash
   # Stop current v2.x processes
   ```

2. **Update configuration file**
   ```bash
   # Rename config-v2.ini to config.ini
   # Remove all file mode settings
   # Add Server_Address to [CLIENT] section
   # Remove Stream_Mode and Connection_Mode
   ```

3. **Verify network connectivity**
   ```bash
   # Ensure TCP port 5992 is accessible between locations
   ping <server-ip>
   telnet <server-ip> 5992
   ```

4. **Update scripts**
   ```bash
   # Download new v3.0.0 scripts
   # Replace FRS-Discovery-Server.py
   # Replace FRS-Discovery-Client.py
   ```

5. **Test connection**
   ```bash
   # Start server first
   python FRS-Discovery-Server.py
   
   # Start client (should connect immediately)
   python FRS-Discovery-Client.py
   ```

6. **Remove old files**
   ```bash
   # Optional: Remove discovery.json and related files
   # No longer needed
   ```

### From v2.x Socket Mode

✅ **No changes needed!**

If you were already using socket mode in v2.x, v3.0 will work with minimal changes:
- Update scripts to v3.0.0
- Remove unused settings from config (they're ignored anyway)
- Restart server and client

### From v1.x

Not supported directly. See `MIGRATION_GUIDE_v1_to_v2.md` for v1.x → v2.x migration, then follow v2.x → v3.0 migration above.

---

## 📝 Detailed Changes

### Server Changes

**Removed Methods:**
- `write_to_file(packet_data)` - No longer needed
- `touch_file()` - No longer needed

**Removed Instance Variables:**
- `self.stream_mode` - Always socket mode now
- `self.shared_file_path` - File mode removed
- `self.update_interval` - File mode removed
- `self.last_write_time` - File mode removed
- `self.last_payload_data` - File mode removed
- `self.last_touch_time` - File mode removed

**Simplified Configuration:**
- No `Stream_Mode` validation
- No conditional initialization based on mode
- Cleaner `__init__()` method

**Improved Logging:**
- Removed operational logging
- Only logs startup, shutdown, and fatal errors
- Minimal disk I/O

### Client Changes

**Removed Methods:**
- `run_file_mode()` - File mode removed
- `read_discovery_file()` - File mode removed

**Removed Instance Variables:**
- `self.connection_mode` - Always socket mode now
- `self.shared_file_path` - File mode removed
- `self.check_interval` - File mode removed
- `self.max_file_age` - File mode removed

**Renamed Methods:**
- `run_socket_mode()` → `run()` - Now the only run method

**Simplified Configuration:**
- No `Connection_Mode` validation
- No conditional initialization based on mode
- Cleaner `__init__()` method

**Improved Logging:**
- Removed operational logging
- Only logs startup, shutdown, and fatal errors
- Minimal disk I/O

---

## 🐛 Bug Fixes

- Fixed: File timestamp update logic (removed, no longer applicable)
- Fixed: File stale detection false positives (removed, no longer applicable)
- Fixed: Cloud sync timing issues (removed, no longer applicable)
- Fixed: File permission errors (removed, no longer applicable)

---

## 📚 Documentation Updates

### Updated Files:
- `README.md` - Reflects v3.0 socket-only architecture
- `.cursorrules` - Updated to v3.0 specifications
- `config-v2.ini` - Simplified configuration

### New Files:
- `RELEASE_NOTES_v3.0.0.md` - This file

### To Be Updated:
- `README_v2.md` - Should be updated to reflect v3.0 changes
- `QUICKSTART_v2.md` - Should be updated to remove file mode instructions
- Other documentation files as needed

---

## ⚠️ Known Issues

None at this time.

---

## 🔮 Future Plans

With the simplified v3.0 codebase, future enhancements may include:

- **Multi-radio support** - Single server monitoring multiple radios
- **Web dashboard** - Browser-based monitoring interface
- **Metrics/statistics** - Track usage patterns
- **Enhanced health checks** - More comprehensive diagnostics
- **IPv6 support** - Modern network compatibility

See [ENHANCEMENTS_ROADMAP.md](ENHANCEMENTS_ROADMAP.md) for details.

---

## 📞 Support

### ⚠️ Important Notice

This software is **NOT officially supported** by FlexRadio Systems, Inc., its employees, or its help desk. This is an independent community tool.

**For official FlexRadio support:** https://www.flexradio.com

### Community Support

- **GitHub Issues:** Report bugs or request features
- **Discussions:** Share experiences and solutions
- **Pull Requests:** Contributions welcome!

---

## 🙏 Credits

- **v3.0 Development:** WX7V
- **v2.x Development:** WX7V
- **Original Concept:** VA3MW (v1.x)
- **FlexRadio VITA-49 Protocol:** FlexRadio Systems, Inc.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

Copyright (c) 2026 Chris L White (WX7V)  
Based on original work by VA3MW (2024)

---

**Version 3.0.0** - Socket-Only Edition  
*Simpler. Faster. Better.*
