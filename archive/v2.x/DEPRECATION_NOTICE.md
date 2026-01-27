# Deprecation Notice - Version 1.x

**Date:** 2026-01-26  
**Affected Versions:** v1.0.0, v1.0.1  
**Status:** ❌ **DEPRECATED**

---

## Summary

**Version 1.x of the FlexRadio Discovery Proxy has been deprecated and is no longer supported.**

All v1.x files have been moved to the `archive/v1.x/` directory for historical reference.

---

## What This Means

### ❌ No Longer Supported
- **No bug fixes** for v1.x
- **No updates** for new FlexRadio firmware
- **No support** via help desk or community

### ✅ Replaced By v2.x
- **v2.0.0+** provides superior functionality
- **v2.1.0** adds health checks and diagnostics
- **Fully supported** with active development

---

## Why Deprecated?

### Critical Limitations of v1.x
1. **Synthetic Packets** - Generated fake discovery packets instead of authentic ones
2. **Manual Configuration** - Required manual entry of all radio parameters
3. **Static Status** - Couldn't reflect actual radio status (Available vs In Use)
4. **Maintenance Burden** - Had to be updated manually for new FlexRadio features
5. **Single Radio Only** - Difficult to support multiple radios

### Superior v2.x Architecture
1. **Authentic Packets** - Captures and rebroadcasts real VITA-49 packets
2. **Auto-Configuration** - Automatically extracts radio information
3. **Real-Time Status** - Shows actual radio availability and usage
4. **Future-Proof** - Automatically supports new FlexRadio features
5. **Multi-Radio Ready** - Easy to run multiple instances

---

## Migration Required

If you're currently using v1.x, **you must migrate to v2.x**.

### Quick Migration Steps
1. **Read Migration Guide:** [MIGRATION_GUIDE_v1_to_v2.md](MIGRATION_GUIDE_v1_to_v2.md)
2. **Install v2.x Scripts:** Already in project root
3. **Configure:** Edit `config-v2.ini` (different from v1.x config.ini)
4. **Deploy Server:** Run `FRS-Discovery-Server-v2.py` at radio location
5. **Deploy Client:** Run `FRS-Discovery-Client-v2.py` at PC location

**Note:** v1.x and v2.x configurations are **NOT compatible**. You must reconfigure.

---

## Archived Files Location

All v1.x files are in: **`archive/v1.x/`**

### Archived Files Include:
- `FRS-Discovery-Proxy.py` (v1.0.1)
- `Original-FRS-Wedge.py` (VA3MW's original)
- `config.ini` (v1.x config)
- `FRS-Discovery-Proxy.bat` (v1.x launcher)
- `RELEASE_NOTES_v1.0.0.md`
- `RELEASE_NOTES_v1.0.1.md`
- `COMPARISON_STABILITY_FIXES.md`
- Log files

See [archive/README.md](archive/README.md) for complete details.

---

## Current Supported Versions

| Version | Status | Documentation |
|---------|--------|---------------|
| **v2.1.0** | ✅ Active Development | [README_v2.md](README_v2.md) |
| **v2.0.0** | ✅ Stable (bug fixes only) | [README_v2.md](README_v2.md) |
| v1.0.1 | ❌ Deprecated | `archive/v1.x/` |
| v1.0.0 | ❌ Deprecated | `archive/v1.x/` |

---

## Features Comparison

| Feature | v1.x | v2.x |
|---------|------|------|
| Packet Type | Synthetic | Authentic |
| Configuration | Manual | Automatic |
| Radio Status | Static | Real-time |
| Multi-Radio | Difficult | Easy |
| Future-Proof | No | Yes |
| Health Checks | No | Yes (v2.1+) |
| Support Status | ❌ None | ✅ Active |

---

## Exception: When v1.x Might Be Used

In **extremely rare** cases, v1.x might be useful for:
1. **Testing without a radio** - Generate fake discovery packets
2. **Research purposes** - Understanding the evolution of the project
3. **Historical reference** - How synthetic packet generation worked

**However,** even for these cases, we recommend using v2.x when possible.

---

## Getting Help with Migration

### Documentation
- **[MIGRATION_GUIDE_v1_to_v2.md](MIGRATION_GUIDE_v1_to_v2.md)** - Complete step-by-step guide
- **[QUICKSTART_v2.md](QUICKSTART_v2.md)** - Fast setup (15 minutes)
- **[README_v2.md](README_v2.md)** - Complete v2.x documentation
- **[VERSION_COMPARISON.md](VERSION_COMPARISON.md)** - Detailed comparison

### Support Channels
- **GitHub Issues:** Report problems or ask questions
- **QRZ:** WX7V
- **Community Forums:** FlexRadio community

**Remember:** This is a community tool, NOT officially supported by FlexRadio Systems.

---

## Timeline

| Date | Event |
|------|-------|
| **2024-05** | VA3MW creates Original-FRS-Wedge.py |
| **2026-01-20** | v1.0.0 released (fork + enhancements) |
| **2026-01-22** | v1.0.1 released (stability fixes) |
| **2026-01-26** | v2.0.0 released (architecture change) |
| **2026-01-26** | v2.1.0 RC released (health checks + license) |
| **2026-01-26** | **v1.x DEPRECATED** |

---

## Frequently Asked Questions

### Q: Can I still use v1.x?
**A:** Technically yes, but it's strongly discouraged. v1.x is unsupported and may not work with newer FlexRadio firmware.

### Q: Will v1.x receive any updates?
**A:** No. All development effort is focused on v2.x.

### Q: Is my v1.x config.ini compatible with v2.x?
**A:** No. v2.x uses `config-v2.ini` with a different structure. You must reconfigure.

### Q: Can I run v1.x and v2.x simultaneously?
**A:** Not recommended. They use the same UDP port (4992) and will conflict.

### Q: What if v2.x doesn't work for me?
**A:** Please report the issue! We want v2.x to work for everyone. Use GitHub issues or contact WX7V.

### Q: Will the migration break my setup?
**A:** v2.x requires a different architecture (server + client), but the migration guide provides step-by-step instructions to minimize disruption.

### Q: How long will archived v1.x files remain available?
**A:** Indefinitely for historical reference, but they are unsupported.

---

## Action Required

### If You're Using v1.x:

1. ✅ **Read this notice carefully**
2. ✅ **Plan your migration** - Review [MIGRATION_GUIDE_v1_to_v2.md](MIGRATION_GUIDE_v1_to_v2.md)
3. ✅ **Test v2.x** - Set up in parallel with v1.x to verify functionality
4. ✅ **Switch to v2.x** - Deploy server and client components
5. ✅ **Remove v1.x** - Stop using deprecated version

### If You're New to This Project:

1. ✅ **Use v2.x** - Start with [QUICKSTART_v2.md](QUICKSTART_v2.md)
2. ✅ **Ignore v1.x** - Focus on current supported versions
3. ✅ **Enjoy health checks** - v2.1.0 includes diagnostic tools

---

## Acknowledgments

**Thank you to all v1.x users** for your feedback and testing. Your input helped shape v2.x into a superior solution.

Special thanks to:
- **VA3MW** - Original concept and implementation
- **Early Adopters** - Testing and feedback on v1.x
- **Community** - Suggestions and bug reports

---

## Final Note

This deprecation is necessary to focus development efforts on the superior v2.x architecture. The move to authentic packet capture provides significant benefits and future-proofs the solution.

**We strongly encourage all users to migrate to v2.x for the best experience.**

---

**Deprecation Date:** 2026-01-26  
**Deprecated By:** Chris L White (WX7V)  
**Superseded By:** Version 2.1.0+

For the current version, see: **[README_v2.md](README_v2.md)**

---

**73 de WX7V**
