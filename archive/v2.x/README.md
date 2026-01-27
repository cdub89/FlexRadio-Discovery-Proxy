# FlexRadio Discovery Proxy - Version 2.x Archive

This directory contains archived documentation and files from Version 2.x of the FlexRadio Discovery Proxy.

**Archive Date:** January 27, 2026  
**Reason:** Version 3.0.0 removed file-based mode, simplifying to socket-only architecture

---

## What Was Version 2.x?

Version 2.x introduced a client-server architecture with **two communication modes**:

1. **Socket Mode** (TCP streaming) - Real-time, low latency
2. **File Mode** (Shared file) - Cloud sync compatible, higher latency

Version 2.x supported both modes simultaneously, allowing users to choose based on their network setup.

---

## Why Was It Archived?

Version 3.0.0 removed file mode because:
- **Complexity:** Required file system, cloud sync, and network shares
- **Latency:** 5-30 second delays with cloud sync
- **Reliability:** Dependent on file system and sync services
- **Maintenance:** Extra code to maintain and test

Socket mode proved to be:
- ✅ Simpler to configure
- ✅ More reliable (TCP)
- ✅ Faster (<1 second latency)
- ✅ Easier to troubleshoot

---

## Archived Files

### Release Notes
- `RELEASE_NOTES_v2.0.0.md` - Initial v2.0 release (file-based mode)
- `RELEASE_NOTES_v2.1.0.md` - Health checks and diagnostics
- `RELEASE_NOTES_v2.2.0.md` - Socket mode added
- `RELEASE_NOTES_v2.2.1.md` - Bug fixes
- `BUGFIX_SUMMARY_v2.2.1.md` - Detailed bug fix documentation

### User Documentation
- `README_v2.md` - Complete v2.x documentation
- `QUICKSTART_v2.md` - Quick setup guide for v2.x
- `WHATS_NEW_v2.md` - Feature highlights
- `TESTING_GUIDE_v2.2.md` - Testing procedures

### Migration and Comparison
- `MIGRATION_GUIDE_v1_to_v2.md` - v1.x to v2.x migration guide
- `VERSION_COMPARISON.md` - Comparison of v1.x vs v2.x
- `V1_DEPRECATION_SUMMARY.md` - v1.x deprecation details
- `DEPRECATION_NOTICE.md` - Formal deprecation notice

### Development Documentation
- `SESSION_SUMMARY_2026-01-26.md` - Development session notes
- `SESSION_SUMMARY_2026-01-27.md` - Development session notes
- `SESSION_SUMMARY_2026-01-27_FINAL.md` - Final session summary
- `CLEANUP_SUMMARY_2026-01-27.md` - Code cleanup documentation
- `PROGRESS_TRACKER.md` - v2.x development progress
- `PRIORITY_1_COMPLETION_SUMMARY.md` - Priority 1 tasks
- `PRIORITY_2_COMPLETION_SUMMARY.md` - Priority 2 tasks
- `PRIORITY_4_COMPLETION_SUMMARY.md` - Priority 4 tasks

---

## Version 2.x Timeline

**v2.0.0** (January 2026)
- Initial release with file-based communication
- Client-server architecture
- Authentic VITA-49 packet capture
- Cloud sync support (OneDrive, Dropbox)

**v2.1.0** (January 2026)
- Health check system
- Startup diagnostics
- Network connectivity testing
- MIT License

**v2.2.0** (January 2026)
- Socket mode added (TCP streaming)
- Dual-mode support (file + socket)
- Configurable communication mode
- Improved performance

**v2.2.1** (January 2026)
- Bug fixes for socket mode
- Connection stability improvements
- Final v2.x release

**v3.0.0** (January 27, 2026)
- File mode removed
- Socket-only architecture
- Simplified configuration
- v2.x documentation archived

---

## Key Features of v2.x

### File Mode (Archived)
- ✅ Worked across any network topology
- ✅ Cloud sync compatible (OneDrive, Dropbox, Google Drive)
- ✅ No direct network connection required
- ❌ Higher latency (5-30 seconds)
- ❌ File system dependencies
- ❌ Complex setup

### Socket Mode (Continued in v3.0)
- ✅ Real-time streaming (<1 second)
- ✅ Direct TCP connection
- ✅ Multiple clients supported
- ✅ Simple configuration
- ✅ High reliability

---

## Migration from v2.x to v3.0

### If You Were Using File Mode

1. **Switch to socket mode:**
   - Update config-v2.ini
   - Remove file mode settings
   - Add Server_Address setting
   - Ensure TCP connectivity

2. **Update scripts:**
   - Download v3.0.0 scripts
   - Replace server and client scripts

3. **Test:**
   - Start server at radio location
   - Start client at SmartSDR location
   - Verify connection

### If You Were Using Socket Mode

✅ **Minimal changes needed!**
- Update scripts to v3.0.0
- Remove unused config settings (optional)
- Everything else stays the same

---

## Historical Reference

This archive serves as:
- Documentation of file mode implementation
- Reference for dual-mode architecture
- Historical record of v2.x development
- Migration guide for users

---

## Current Version

**Version 3.0.0** is the current production version.

See the main directory for:
- Current documentation
- Active scripts
- Configuration files
- Support information

---

## Support

Version 2.x is **no longer supported or maintained**.

For current support:
- Use Version 3.0.0
- See main directory README.md
- Report issues on GitHub

---

## Archive Structure

```
archive/
├── v1.x/           # Version 1.x (synthetic packets)
└── v2.x/           # Version 2.x (dual-mode)
    ├── README.md   # This file
    ├── Release Notes (5 files)
    ├── User Documentation (4 files)
    ├── Migration Guides (4 files)
    └── Development Documentation (9 files)
```

---

**Archived:** January 27, 2026  
**Superseded By:** Version 3.0.0  
**Archive Purpose:** Historical reference and migration support
