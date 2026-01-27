# FlexRadio Discovery Proxy

**Current Version:** v2.1.0 (Release Candidate)  
**Status:** ✅ Active Development

---

## ⚠️ Important: Version 1.x Deprecated

**Version 1.x has been deprecated as of 2026-01-26.**

- ❌ v1.x files moved to `archive/v1.x/`
- ❌ v1.x no longer supported or maintained
- ✅ Please use v2.x (current version)

See [DEPRECATION_NOTICE.md](DEPRECATION_NOTICE.md) for details.

---

## Quick Start

**For the current version (v2.x), please see:**

### 📚 **[README_v2.md](README_v2.md)** - Complete Documentation

### 🚀 **[QUICKSTART_v2.md](QUICKSTART_v2.md)** - 15-Minute Setup Guide

### 📋 **[INDEX.md](INDEX.md)** - Documentation Navigation

---

## What's New in v2.1.0

### ✅ MIT License and Attribution
- Professional open-source licensing
- Clear copyright and disclaimers
- FlexRadio support distinction

### ✅ Network Health Checks
- Automatic startup diagnostics
- Continuous health monitoring
- VPN/connectivity testing
- Port availability checks
- File permission validation

### ✅ Comprehensive Documentation
- [HEALTH_CHECK_GUIDE.md](HEALTH_CHECK_GUIDE.md) - Diagnostic guide
- [ENHANCEMENTS_ROADMAP.md](ENHANCEMENTS_ROADMAP.md) - Future plans
- [PROGRESS_TRACKER.md](PROGRESS_TRACKER.md) - Development tracking

---

## Why v2.x?

### Advantages Over v1.x

| Feature | v1.x | v2.x |
|---------|------|------|
| **Packet Type** | Synthetic (fake) | Authentic (real) |
| **Configuration** | Manual setup | Auto-detects radio info |
| **Radio Status** | Static | Real-time |
| **Multi-Radio** | Difficult | Easy |
| **Health Checks** | No | Yes (v2.1+) |
| **Support** | ❌ Deprecated | ✅ Active |

---

## Architecture

**v2.x uses a client-server model:**

### Server Component
- Runs at radio location
- Captures real VITA-49 packets
- Writes to shared file
- File: `FRS-Discovery-Server-v2.py`

### Client Component  
- Runs at PC location (SmartSDR)
- Reads from shared file
- Rebroadcasts locally
- File: `FRS-Discovery-Client-v2.py`

### Shared Storage
- Network share or cloud sync
- OneDrive, Dropbox, Google Drive
- Or direct network file share

---

## Migration from v1.x

If you're currently using v1.x:

1. **Read:** [MIGRATION_GUIDE_v1_to_v2.md](MIGRATION_GUIDE_v1_to_v2.md)
2. **Understand:** Architecture is completely different
3. **Configure:** Use `config-v2.ini` (not config.ini)
4. **Deploy:** Server at radio, client at PC
5. **Test:** Run in parallel with v1.x before switching

**Note:** v1.x and v2.x configs are **NOT compatible**.

---

## Installation

### Requirements
- Python 3.6+
- Shared storage (network share or cloud)
- FlexRadio on network

### Quick Setup

**1. Configure shared storage:**
```ini
# config-v2.ini
[SERVER]
Shared_File_Path = path/to/shared/discovery.json

[CLIENT]
Shared_File_Path = path/to/shared/discovery.json
```

**2. Start server (at radio location):**
```bash
python FRS-Discovery-Server-v2.py
```

**3. Start client (at PC):**
```bash
python FRS-Discovery-Client-v2.py
```

**4. Open SmartSDR:**
Radio should appear in chooser!

For detailed instructions: [QUICKSTART_v2.md](QUICKSTART_v2.md)

---

## System Requirements

- **Python:** 3.6 or later
- **OS:** Windows, macOS, Linux
- **Network:** Shared storage or cloud sync
- **FlexRadio:** Any FLEX-6000 or FLEX-8000 series

---

## Key Features

### v2.0.0+
- ✅ Authentic VITA-49 packet capture
- ✅ Client-server architecture
- ✅ Real-time radio status
- ✅ Auto-configuration
- ✅ Multi-radio support

### v2.1.0+ (Current)
- ✅ Network health checks
- ✅ Startup diagnostics
- ✅ Periodic monitoring
- ✅ MIT License
- ✅ Comprehensive documentation

---

## Documentation

### Current Version (v2.x)
- **[README_v2.md](README_v2.md)** - Complete documentation
- **[QUICKSTART_v2.md](QUICKSTART_v2.md)** - Fast setup guide
- **[HEALTH_CHECK_GUIDE.md](HEALTH_CHECK_GUIDE.md)** - Diagnostics guide
- **[MIGRATION_GUIDE_v1_to_v2.md](MIGRATION_GUIDE_v1_to_v2.md)** - Upgrade guide
- **[INDEX.md](INDEX.md)** - Full documentation index

### Planning & Roadmap
- **[ENHANCEMENTS_ROADMAP.md](ENHANCEMENTS_ROADMAP.md)** - Future features
- **[PROGRESS_TRACKER.md](PROGRESS_TRACKER.md)** - Development progress
- **[RELEASE_NOTES_v2.1.0.md](RELEASE_NOTES_v2.1.0.md)** - Latest changes

### Deprecated (v1.x)
- **[archive/](archive/)** - Archived v1.x files
- **[DEPRECATION_NOTICE.md](DEPRECATION_NOTICE.md)** - Deprecation details

---

## License

**Copyright © 2026 Chris L White (WX7V)**  
Based on original work by VA3MW (2024)

Licensed under the **MIT License** - see [LICENSE](LICENSE) file.

### Important Disclaimer

**⚠️ This software is NOT officially supported by FlexRadio Systems, Inc., its employees, or its help desk.**

This is an independent, community-developed tool. For official FlexRadio support:
- **Website:** https://www.flexradio.com
- **Help Desk:** https://helpdesk.flexradio.com
- **Community:** https://community.flexradio.com

---

## Support

### For This Community Tool:
- **GitHub Issues:** Report bugs or ask questions
- **QRZ:** WX7V
- **Documentation:** See INDEX.md for complete guide

### For Official FlexRadio Products:
- Use the links in the Disclaimer section above

---

## Quick Links

| Link | Purpose |
|------|---------|
| [README_v2.md](README_v2.md) | **Start here** for v2.x documentation |
| [QUICKSTART_v2.md](QUICKSTART_v2.md) | 15-minute setup guide |
| [HEALTH_CHECK_GUIDE.md](HEALTH_CHECK_GUIDE.md) | Troubleshooting diagnostics |
| [INDEX.md](INDEX.md) | Complete documentation index |
| [DEPRECATION_NOTICE.md](DEPRECATION_NOTICE.md) | v1.x deprecation notice |
| [archive/](archive/) | Archived v1.x files |

---

## Version History

| Version | Date | Status | Notes |
|---------|------|--------|-------|
| **v2.1.0** | 2026-01-26 | ✅ Release Candidate | Health checks + license |
| **v2.0.0** | 2026-01-26 | ✅ Stable | Client-server architecture |
| v1.0.1 | 2026-01-22 | ❌ Deprecated | Moved to archive/ |
| v1.0.0 | 2026-01-20 | ❌ Deprecated | Moved to archive/ |

---

## Contributing

Contributions welcome! Please:
1. Test thoroughly before submitting
2. Update documentation as needed
3. Follow existing code style
4. Include examples for new features

All contributions under MIT License terms.

---

## Credits

- **Original Concept:** VA3MW - FlexRadio Broadcast Wedge (2024)
- **v1.x Fork:** Chris L White, WX7V (2026)
- **v2.x Architecture:** Chris L White, WX7V (2026)
- **Protocol Documentation:** FlexRadio Systems VITA-49 implementation

---

**For current version documentation, see: [README_v2.md](README_v2.md)**

**73 de WX7V**
