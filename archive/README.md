# FlexRadio Discovery Proxy - Archive

This directory contains deprecated versions of the FlexRadio Discovery Proxy that are no longer actively maintained.

---

## Directory Structure

### `v1.x/` - Version 1.x (Deprecated)

**Status:** ❌ Deprecated as of 2026-01-26  
**Replaced By:** Version 2.0+  
**Reason:** v1.x used synthetic packet generation; v2.0+ uses authentic packet capture

### `v2.x/` - Version 2.x (Archived)

**Status:** 📦 Archived as of 2026-01-27  
**Replaced By:** Version 3.0.0  
**Reason:** v2.x supported both file and socket modes; v3.0 simplified to socket-only

---

## Contents: v1.x

### Scripts
- **`FRS-Discovery-Proxy.py`** - v1.0.1 single-script implementation
- **`Original-FRS-Wedge.py`** - VA3MW's original implementation (2024)

### Configuration
- **`config.ini`** - v1.x configuration file (not compatible with v2.x+)

### Launchers
- **`FRS-Discovery-Proxy.bat`** - Windows launcher for v1.x

### Documentation
- **`RELEASE_NOTES_v1.0.0.md`** - Initial v1.0.0 release notes
- **`RELEASE_NOTES_v1.0.1.md`** - v1.0.1 stability improvements
- **`COMPARISON_STABILITY_FIXES.md`** - Comparison between v1.0.0 and v1.0.1

### Logs
- **`broadcast.log`** - v1.x log file (archived state)
- **`broadcast-dragon.log`** - v1.x log file (archived state)

---

## Contents: v2.x

### Release Notes (5 files)
- **`RELEASE_NOTES_v2.0.0.md`** - Initial v2.0 release (file-based mode)
- **`RELEASE_NOTES_v2.1.0.md`** - Health checks and diagnostics
- **`RELEASE_NOTES_v2.2.0.md`** - Socket mode added (dual-mode support)
- **`RELEASE_NOTES_v2.2.1.md`** - Bug fixes
- **`BUGFIX_SUMMARY_v2.2.1.md`** - Detailed bug fix documentation

### User Documentation (4 files)
- **`README_v2.md`** - Complete v2.x documentation
- **`QUICKSTART_v2.md`** - Quick setup guide for v2.x
- **`WHATS_NEW_v2.md`** - Feature highlights
- **`TESTING_GUIDE_v2.2.md`** - Testing procedures

### Migration and Comparison (4 files)
- **`MIGRATION_GUIDE_v1_to_v2.md`** - v1.x to v2.x migration guide
- **`VERSION_COMPARISON.md`** - Comparison of v1.x vs v2.x
- **`V1_DEPRECATION_SUMMARY.md`** - v1.x deprecation details
- **`DEPRECATION_NOTICE.md`** - Formal deprecation notice

### Development Documentation (9 files)
- **`SESSION_SUMMARY_2026-01-26.md`** - Development session notes
- **`SESSION_SUMMARY_2026-01-27.md`** - Development session notes
- **`SESSION_SUMMARY_2026-01-27_FINAL.md`** - Final session summary
- **`CLEANUP_SUMMARY_2026-01-27.md`** - Code cleanup documentation
- **`PROGRESS_TRACKER.md`** - v2.x development progress
- **`PRIORITY_1_COMPLETION_SUMMARY.md`** - Priority 1 tasks
- **`PRIORITY_2_COMPLETION_SUMMARY.md`** - Priority 2 tasks
- **`PRIORITY_4_COMPLETION_SUMMARY.md`** - Priority 4 tasks

See [v2.x/README.md](v2.x/README.md) for complete v2.x archive documentation.

---

## Why Deprecated/Archived?

### Limitations of v1.x
1. **Synthetic Packets:** Generated packets manually, not from actual radio
2. **Static Configuration:** Required manual configuration of all radio parameters
3. **No Auto-Discovery:** Couldn't detect actual radio status changes
4. **Maintenance Burden:** Had to update packet format manually for new radio features
5. **Limited Flexibility:** Single script couldn't support multiple radios easily

### Advantages of v2.x Over v1.x
1. **Authentic Packets:** Captures and rebroadcasts actual VITA-49 packets from radio
2. **Auto-Configuration:** Automatically extracts radio information from broadcasts
3. **Real Status:** Reflects actual radio status (Available, In Use, etc.)
4. **Future-Proof:** Automatically supports new FlexRadio features and firmware updates
5. **Client-Server Architecture:** Supports multiple deployment scenarios
6. **Health Checks (v2.1+):** Automatic diagnostics and troubleshooting

### Why v2.x Was Archived (v3.0 Changes)
1. **File Mode Complexity:** Required file systems, cloud sync, network shares
2. **Higher Latency:** File mode had 5-30 second delays
3. **Reliability Issues:** Dependent on file systems and sync services
4. **Maintenance Overhead:** Extra code for dual-mode support
5. **Socket Mode Superior:** Direct TCP proved simpler, faster, more reliable

---

## Version Timeline

| Version | Release Date | Status | Notes |
|---------|--------------|--------|-------|
| v1.0.0 | Jan 2026 | ❌ Deprecated | Synthetic packets |
| v1.0.1 | Jan 2026 | ❌ Deprecated | Stability fixes |
| v2.0.0 | Jan 2026 | 📦 Archived | File-based mode introduced |
| v2.1.0 | Jan 2026 | 📦 Archived | Health checks added |
| v2.2.0 | Jan 2026 | 📦 Archived | Socket mode added (dual-mode) |
| v2.2.1 | Jan 2026 | 📦 Archived | Final v2.x release |
| **v3.0.0** | Jan 27, 2026 | ✅ **Current** | Socket-only, simplified |

---

## Migration Guides

### From v1.x to Current (v3.0)
1. Review v2.x migration guide: `archive/v2.x/MIGRATION_GUIDE_v1_to_v2.md`
2. Then follow v3.0 setup in main directory

### From v2.x to v3.0
See main directory `RELEASE_NOTES_v3.0.0.md` for:
- Configuration changes
- Removed features (file mode)
- Migration steps

---

## Support Status

| Version | Status | Updates | Support |
|---------|--------|---------|---------|
| v1.0.x | ❌ Deprecated | None | None |
| v2.0.x-v2.2.x | 📦 Archived | None | None |
| **v3.0.0** | ✅ **Active** | Active | Community |

---

## Current Version

**Version 3.0.0** is the current production version.

Key features:
- ✅ Socket-only (TCP streaming)
- ✅ Real-time communication (<1 second latency)
- ✅ Simplified configuration
- ✅ Multiple client support
- ✅ Automatic reconnection
- ✅ Minimal logging

See main directory for current documentation:
- **[README.md](../README.md)** - Current overview
- **[RELEASE_NOTES_v3.0.0.md](../RELEASE_NOTES_v3.0.0.md)** - v3.0 changes

---

## Historical Context

### Original Work by VA3MW (2024)
The Original-FRS-Wedge.py was created by VA3MW to solve the problem of accessing FlexRadio transceivers over VPN connections where discovery broadcasts don't cross network boundaries.

### v1.0.0 Fork (January 2026)
Chris L White (WX7V) forked VA3MW's work and enhanced it with:
- Proper VITA-49 packet structure
- Dynamic timestamp generation
- Improved configuration
- Better error handling

### v1.0.1 Stability Release (January 2026)
Added timing improvements and stability fixes to address edge cases in ping handling.

### v2.0.0 Architecture Shift (January 2026)
Complete redesign to use authentic packet capture instead of synthetic generation, introducing the client-server architecture with file-based communication.

### v2.1.0 Diagnostics Enhancement (January 2026)
Added comprehensive health checks, MIT licensing, and diagnostic capabilities.

### v2.2.0 Dual-Mode Support (January 2026)
Added socket mode (TCP streaming) alongside existing file mode, giving users choice based on their network setup.

### v2.2.1 Final v2.x Release (January 2026)
Bug fixes and stability improvements for socket mode.

### v3.0.0 Simplification (January 27, 2026)
Removed file mode, focused exclusively on socket mode for optimal performance and simplicity. v2.x documentation archived.

---

## Accessing Archived Files

These files are preserved for:
- **Historical Reference:** Understanding the evolution of the project
- **Research:** Comparing approaches across versions
- **Migration Support:** Helping users understand changes

**Note:** Archived versions are unsupported and may not work with newer FlexRadio firmware.

---

## Documentation Location

The main project README focuses on v3.0:
- **[README.md](../README.md)** - Current version documentation
- **[INDEX.md](../INDEX.md)** - Documentation navigation
- **[TROUBLESHOOTING.md](../TROUBLESHOOTING.md)** - Current troubleshooting

For archived documentation:
- **v1.x:** See release notes in `v1.x/` directory
- **v2.x:** See [v2.x/README.md](v2.x/README.md) and documentation files

---

## License

All archived code retains its original MIT License.

**Copyright © 2026 Chris L White (WX7V)**  
Based on original work by VA3MW (2024)

See [LICENSE](../LICENSE) for complete terms.

---

## Questions?

If you have questions about:
- **Current version (v3.0):** See main project documentation
- **Migration from v1.x:** See `archive/v2.x/MIGRATION_GUIDE_v1_to_v2.md`
- **Migration from v2.x:** See `RELEASE_NOTES_v3.0.0.md` in main directory
- **Historical information:** Review release notes in archive directories
- **Why versions changed:** See "Why Deprecated/Archived?" section above

---

## Archive Structure

```
archive/
├── README.md         # This file
├── v1.x/            # Version 1.x (synthetic packets)
│   ├── Scripts (2 files)
│   ├── Configuration (1 file)
│   ├── Documentation (3 files)
│   └── Logs (2 files)
└── v2.x/            # Version 2.x (dual-mode)
    ├── README.md    # v2.x archive overview
    ├── Release Notes (5 files)
    ├── User Documentation (4 files)
    ├── Migration Guides (4 files)
    └── Development Documentation (9 files)
```

---

**v1.x Deprecated:** 2026-01-26  
**v2.x Archived:** 2026-01-27  
**Maintained By:** Chris L White (WX7V)

---

**73 de WX7V**
