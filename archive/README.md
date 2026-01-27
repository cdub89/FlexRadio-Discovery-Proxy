# FlexRadio Discovery Proxy - Archive

This directory contains deprecated versions of the FlexRadio Discovery Proxy that are no longer actively maintained.

---

## Directory Structure

### `v1.x/` - Version 1.x (Deprecated)

**Status:** ❌ Deprecated as of 2026-01-26  
**Replaced By:** Version 2.1.0+  
**Reason:** v1.x used synthetic packet generation; v2.0+ uses authentic packet capture

---

## Contents: v1.x

### Scripts
- **`FRS-Discovery-Proxy.py`** - v1.0.1 single-script implementation
- **`Original-FRS-Wedge.py`** - VA3MW's original implementation (2024)

### Configuration
- **`config.ini`** - v1.x configuration file (not compatible with v2.x)

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

## Why Deprecated?

### Limitations of v1.x
1. **Synthetic Packets:** Generated packets manually, not from actual radio
2. **Static Configuration:** Required manual configuration of all radio parameters
3. **No Auto-Discovery:** Couldn't detect actual radio status changes
4. **Maintenance Burden:** Had to update packet format manually for new radio features
5. **Limited Flexibility:** Single script couldn't support multiple radios easily

### Advantages of v2.x
1. **Authentic Packets:** Captures and rebroadcasts actual VITA-49 packets from radio
2. **Auto-Configuration:** Automatically extracts radio information from broadcasts
3. **Real Status:** Reflects actual radio status (Available, In Use, etc.)
4. **Future-Proof:** Automatically supports new FlexRadio features and firmware updates
5. **Client-Server Architecture:** Supports multiple deployment scenarios
6. **Health Checks (v2.1+):** Automatic diagnostics and troubleshooting

---

## Migration from v1.x to v2.x

If you're still using v1.x, please see:
- **[MIGRATION_GUIDE_v1_to_v2.md](../MIGRATION_GUIDE_v1_to_v2.md)** - Complete migration guide
- **[README_v2.md](../README_v2.md)** - v2.x documentation
- **[QUICKSTART_v2.md](../QUICKSTART_v2.md)** - Quick setup guide

---

## When to Use v1.x (Rare Cases)

v1.x might still be useful in very specific scenarios:

1. **Direct VPN with routed subnets** where you need the absolute simplest solution
2. **Testing/Development** when you want to simulate a radio without having one
3. **Historical Reference** for understanding how the original implementation worked

**Note:** Even in these cases, v2.x is generally recommended for its authenticity and reliability.

---

## Support Status

| Version | Status | Updates | Support |
|---------|--------|---------|---------|
| v1.0.0 | ❌ Deprecated | None | None |
| v1.0.1 | ❌ Deprecated | None | None |
| v2.0.0 | ✅ Stable | Bug fixes only | Community |
| v2.1.0 | ✅ Active | Active development | Community |

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
Complete redesign to use authentic packet capture instead of synthetic generation, introducing the client-server architecture.

### v2.1.0 Diagnostics Enhancement (January 2026)
Added comprehensive health checks, MIT licensing, and diagnostic capabilities.

---

## Accessing Archived Files

These files are preserved for:
- **Historical Reference:** Understanding the evolution of the project
- **Research:** Comparing approaches (synthetic vs. authentic packets)
- **Emergency Fallback:** In case v2.x doesn't work in your specific environment

To use archived v1.x files:
1. Copy files from `archive/v1.x/` to project root
2. Ensure no v2.x files conflict (rename config-v2.ini temporarily)
3. Run with `python FRS-Discovery-Proxy.py` (v1.x)
4. Refer to v1.x documentation in this directory

**Warning:** v1.x is unsupported and may not work with newer FlexRadio firmware.

---

## Documentation Location

The main project README now focuses on v2.x:
- **[README_v2.md](../README_v2.md)** - Current version documentation
- **[INDEX.md](../INDEX.md)** - Documentation navigation

For v1.x documentation, see the archived release notes in this directory.

---

## License

All archived code retains its original MIT License.

**Copyright © 2026 Chris L White (WX7V)**  
Based on original work by VA3MW (2024)

See [LICENSE](../LICENSE) for complete terms.

---

## Questions?

If you have questions about:
- **Current versions (v2.x):** See main project documentation
- **Migration from v1.x:** See MIGRATION_GUIDE_v1_to_v2.md
- **Historical information:** Review release notes in this directory
- **Why deprecated:** See "Why Deprecated?" section above

---

**Archived:** 2026-01-26  
**Reason:** Superseded by v2.x architecture  
**Maintained By:** Chris L White (WX7V)

---

**73 de WX7V**
