# FlexRadio Discovery Proxy - Release Notes v2.2.1

**Release Date:** January 27, 2026  
**Release Type:** CRITICAL BUG FIX  
**Severity:** HIGH - Socket mode was completely non-functional in v2.2.0

---

## 🚨 Critical Bug Fix

### Socket Mode Accept Thread Race Condition (CRITICAL)

**Issue:** In v2.2.0, socket mode was completely broken - the server could not accept client connections.

**Root Cause:** Race condition in server initialization:
- Accept thread was started at line 131 of `start()` method
- `self.running = True` was set at line 167 (36 lines later)
- Accept thread's `while self.running:` loop never executed because flag was False
- No client connections could be accepted

**Symptoms:**
- Server showed "⚠ No clients connected" continuously
- Client reported "✓ Connected to server" but received no packets
- Health checks passed (TCP port was listening)
- But actual client connections were never processed

**Fix:** Set `self.running = True` immediately before starting accept thread (line 129)

**Impact:** 
- **v2.2.0 socket mode:** Completely non-functional
- **v2.2.0 file mode:** Unaffected
- **v2.2.1:** Fully functional in both modes

---

## Changes

### Server (FRS-Discovery-Server-v2.py)

**Bug Fixes:**
- Fixed critical race condition in accept thread initialization
- Accept thread now properly enters main loop and accepts connections
- Removed excessive debug output (cleanup)

**Code Changes:**
```python
# Before (v2.2.0):
if self.stream_mode == 'socket':
    self.setup_tcp_socket()
    accept_thread = threading.Thread(target=self.accept_clients, daemon=True)
    accept_thread.start()
    # ... 36 lines of health checks ...
    self.running = True  # TOO LATE!

# After (v2.2.1):
if self.stream_mode == 'socket':
    self.setup_tcp_socket()
    self.running = True  # Set BEFORE starting thread
    accept_thread = threading.Thread(target=self.accept_clients, daemon=True)
    accept_thread.start()
```

### Client (FRS-Discovery-Client-v2.py)

**Changes:**
- Version updated to 2.2.1 for consistency
- No functional changes (client code was working correctly)

---

## Testing Results

**Test Environment:**
- Windows 10 (Build 26200)
- Python 3.x
- FlexRadio FLEX-6400M running firmware 4.1.5.39794
- Server and client on same machine (192.168.1.22) for testing

**Test Results:**
- ✅ Server accepts client connections immediately
- ✅ Packets stream reliably from server to client
- ✅ Client successfully rebroadcasts discovery packets
- ✅ 5,000+ packets transmitted without errors
- ✅ Clean, professional console output
- ✅ Health checks pass correctly

---

## Upgrade Instructions

### From v2.2.0 (RECOMMENDED - CRITICAL FIX)

**If you're running v2.2.0 in socket mode, upgrade immediately.**

1. Stop both server and client processes
2. Replace files:
   - `FRS-Discovery-Server-v2.py`
   - `FRS-Discovery-Client-v2.py`
3. No configuration changes needed
4. Restart server first, then client

**Breaking Changes:** None  
**Configuration Changes:** None  
**Database/File Changes:** None

### From v2.1.x or earlier

Socket mode was introduced in v2.2.0. If upgrading from v2.1.x:
1. Update `config-v2.ini` to include socket mode settings
2. See `MIGRATION_GUIDE_v1_to_v2.md` for details

---

## Known Issues

None. This release fixes the critical v2.2.0 bug with no new issues introduced.

---

## Version Compatibility

| Component | v2.2.1 | v2.2.0 | v2.1.0 |
|-----------|--------|--------|--------|
| Socket Mode (Server) | ✅ Works | ❌ Broken | ❌ N/A |
| Socket Mode (Client) | ✅ Works | ❌ Broken | ❌ N/A |
| File Mode (Server) | ✅ Works | ✅ Works | ✅ Works |
| File Mode (Client) | ✅ Works | ✅ Works | ✅ Works |

---

## Files Changed

### Modified Files
- `FRS-Discovery-Server-v2.py` (v2.2.0 → v2.2.1)
  - Line 129: Added `self.running = True` before accept thread start
  - Removed debug print statements (cleanup)
- `FRS-Discovery-Client-v2.py` (v2.2.0 → v2.2.1)
  - Version number update only
- `config-v2.ini`
  - Set `Debug_Logging = false` (was enabled for troubleshooting)

### New Files
- `RELEASE_NOTES_v2.2.1.md` (this file)

### Unchanged Files
- `health_checks.py`
- `diagnose_connection.py`
- All documentation files
- All batch files

---

## Credits

**Bug Discovered By:** Chris L White (WX7V)  
**Fixed By:** AI Assistant with systematic debugging  
**Testing:** Chris L White (WX7V)

**Debugging Process:**
1. Identified client couldn't receive packets despite successful connection
2. Added debug output to trace packet flow
3. Discovered accept thread was not entering main loop
4. Added debug output to accept thread
5. Found `self.running = False` at thread start
6. Identified race condition in initialization order
7. Fixed by moving `self.running = True` before thread start
8. Verified fix with 5,000+ successful packet transmissions

---

## Support

This is an independent community tool and is NOT officially supported by FlexRadio Systems, Inc.

For questions or issues:
- GitHub Issues: https://github.com/[your-repo]/FlexRadio-Discovery-Proxy
- Email: [your contact info]

For official FlexRadio support:
- Website: https://www.flexradio.com
- Support: https://helpdesk.flexradio.com

---

## License

MIT License - Copyright (c) 2026 Chris L White (WX7V)

Based on original work by VA3MW (2024)

See LICENSE file for details.
