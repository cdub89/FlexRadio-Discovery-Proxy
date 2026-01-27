# FlexRadio Discovery Proxy - Documentation Index

## Welcome!

**Current Version:** v2.2.0 (Socket Mode Release)

This repository contains the FlexRadio Discovery Proxy for accessing FlexRadio transceivers over VPN or remote connections.

---

## ⚠️ Important: Version 1.x Deprecated

**Version 1.x has been deprecated as of 2026-01-26.**
- ❌ All v1.x files moved to `archive/v1.x/`
- ✅ Please use v2.x (current version)
- See **[DEPRECATION_NOTICE.md](DEPRECATION_NOTICE.md)** for details

---

## Quick Links

### For New Users
- **[QUICKSTART_v2.md](QUICKSTART_v2.md)** - Get started with v2.2 in 15 minutes
- **[README_v2.md](README_v2.md)** - Complete v2.x documentation
- **[RELEASE_NOTES_v2.2.0.md](RELEASE_NOTES_v2.2.0.md)** - 🚀 NEW: Socket mode features

### For Current Users
- **[README_v2.md](README_v2.md)** - v2.x documentation (client-server)
- **[HEALTH_CHECK_GUIDE.md](HEALTH_CHECK_GUIDE.md)** - v2.1+ diagnostics guide
- **[RELEASE_NOTES_v2.2.0.md](RELEASE_NOTES_v2.2.0.md)** - 🚀 NEW: v2.2.0 socket mode
- **[RELEASE_NOTES_v2.1.0.md](RELEASE_NOTES_v2.1.0.md)** - v2.1.0 health checks
- **[L3VPN_SOLUTION_GUIDE.md](L3VPN_SOLUTION_GUIDE.md)** - L3 VPN (WireGuard) solution guide

### For v1.x Users (Migration Required)
- **[DEPRECATION_NOTICE.md](DEPRECATION_NOTICE.md)** - ⚠️ v1.x deprecation notice
- **[MIGRATION_GUIDE_v1_to_v2.md](MIGRATION_GUIDE_v1_to_v2.md)** - Complete migration guide
- **[archive/](archive/)** - Archived v1.x files

### Planning & Future Development
- **[ENHANCEMENTS_ROADMAP.md](ENHANCEMENTS_ROADMAP.md)** - Planned features for v3.0
- **[PROGRESS_TRACKER.md](PROGRESS_TRACKER.md)** - ✅ Track implementation progress
- **[PRIORITY_1_COMPLETION_SUMMARY.md](PRIORITY_1_COMPLETION_SUMMARY.md)** - ✅ Priority 1 completion report
- **[PRIORITY_2_COMPLETION_SUMMARY.md](PRIORITY_2_COMPLETION_SUMMARY.md)** - ✅ Priority 2 completion report
- **[PRIORITY_4_COMPLETION_SUMMARY.md](PRIORITY_4_COMPLETION_SUMMARY.md)** - ✅ Priority 4 completion report

---

## Version Overview

### v2.x - Client-Server Architecture (Current)

**Status:** ✅ Active Development

**Best for:**
- All use cases (replaces v1.x completely)
- Cloud-based access (Dropbox, OneDrive, etc.)
- Direct VPN connections
- Multiple radios
- Complex network topologies
- Authentic radio status
- Health checks and diagnostics (v2.1+)

**Files:**
- `FRS-Discovery-Server.py` - Server (captures packets)
- `FRS-Discovery-Client.py` - Client (rebroadcasts)
- `config.ini` - Configuration
- `health_checks.py` - Health check framework (v2.1+)
- `FRS-Discovery-Server-v2.bat` - Windows server launcher
- `FRS-Discovery-Client-v2.bat` - Windows client launcher

**Documentation:**
- [README_v2.md](README_v2.md)
- [QUICKSTART_v2.md](QUICKSTART_v2.md)
- [HEALTH_CHECK_GUIDE.md](HEALTH_CHECK_GUIDE.md) - v2.1+ diagnostics
- [RELEASE_NOTES_v2.2.0.md](RELEASE_NOTES_v2.2.0.md) - 🚀 Socket mode (latest)
- [RELEASE_NOTES_v2.1.0.md](RELEASE_NOTES_v2.1.0.md) - Health checks
- [RELEASE_NOTES_v2.0.0.md](RELEASE_NOTES_v2.0.0.md) - Client-server architecture
- [MIGRATION_GUIDE_v1_to_v2.md](MIGRATION_GUIDE_v1_to_v2.md)

### v1.x - Single Script Architecture (Deprecated)

**Status:** ❌ DEPRECATED as of 2026-01-26

**Location:** `archive/v1.x/` (archived)

**Why Deprecated:**
- Synthetic packets (not authentic)
- Manual configuration required
- No health checks
- Static radio status
- Superseded by superior v2.x architecture

**Documentation:**
- [DEPRECATION_NOTICE.md](DEPRECATION_NOTICE.md) - Deprecation details
- [archive/README.md](archive/README.md) - Archived files info
- v1.x release notes in `archive/v1.x/`

---

## Documentation by Topic

### Installation & Setup
- **v2.x (Current):** See [QUICKSTART_v2.md](QUICKSTART_v2.md) - 15 minute setup guide
- **v1.x (Deprecated):** See `archive/v1.x/` - No longer supported

### Configuration
- **v2.x (Current):** See [README_v2.md](README_v2.md#configuration) - config.ini setup
- **Health Checks:** See [HEALTH_CHECK_GUIDE.md](HEALTH_CHECK_GUIDE.md) - Diagnostics configuration
- **v1.x (Deprecated):** See `archive/v1.x/` - Not compatible with v2.x

### Usage Instructions
- **v2.x (Current):** See [README_v2.md](README_v2.md#usage)
- **v1.x (Deprecated):** See `archive/v1.x/` - No longer maintained

### Troubleshooting
- **Health Checks:** See [HEALTH_CHECK_GUIDE.md](HEALTH_CHECK_GUIDE.md) - Diagnostic tools (v2.1+)
- **v2.x Issues:** See [README_v2.md](README_v2.md#monitoring--troubleshooting)
- **Migration Issues:** See [MIGRATION_GUIDE_v1_to_v2.md](MIGRATION_GUIDE_v1_to_v2.md#troubleshooting-migration-issues)
- **v1.x (Deprecated):** See `archive/v1.x/` - Unsupported

### Protocol Documentation
- **VITA-49 Format:** See [.cursorrules](.cursorrules) - Technical protocol details
- **Packet Analysis:** Included in `.cursorrules`
- **L3 VPN Setup:** See [L3VPN_SOLUTION_GUIDE.md](L3VPN_SOLUTION_GUIDE.md) - WireGuard/L3 VPN guide

### Version History
- **v2.1.0:** [RELEASE_NOTES_v2.1.0.md](RELEASE_NOTES_v2.1.0.md) (in progress)
- **v2.0.0:** [RELEASE_NOTES_v2.0.0.md](RELEASE_NOTES_v2.0.0.md)
- **v1.0.1:** `archive/v1.x/RELEASE_NOTES_v1.0.1.md` (deprecated)
- **v1.0.0:** `archive/v1.x/RELEASE_NOTES_v1.0.0.md` (deprecated)
- **v2.1.0:** [RELEASE_NOTES_v2.1.0.md](RELEASE_NOTES_v2.1.0.md) (in progress)

---

## Architecture Diagrams

### v2.x Architecture (Client-Server)

```
┌────────────────────────────┐         ┌──────────────────┐         ┌────────────────────────────┐
│  Remote Location           │         │  Shared Storage  │         │  Local PC                  │
│                            │         │                  │         │                            │
│  ┌──────────────────┐      │         │                  │         │                            │
│  │  FlexRadio       │      │         │                  │         │                            │
│  │                  │      │         │                  │         │                            │
│  │  Broadcasts      │      │         │                  │         │  ┌──────────────────┐     │
│  │  VITA-49 packets │      │         │                  │         │  │  SmartSDR Client │     │
│  └────────┬─────────┘      │         │                  │         │  └────────▲─────────┘     │
│           │                │         │                  │         │           │               │
│           │ UDP 4992       │         │                  │         │           │ Discovers     │
│           ▼                │         │                  │         │           │               │
│  ┌──────────────────┐      │         │  ┌────────────┐  │         │  ┌────────┴─────────┐     │
│  │  FRS-Discovery-  │      │         │  │ discovery. │  │         │  │  FRS-Discovery-  │     │
│  │  Server-v2.py    │      │         │  │ json       │  │         │  │  Client-v2.py    │     │
│  │                  │      │         │  │            │  │         │  │                  │     │
│  │  Captures real   ├──────┼────────►│  │  Packet    ├──┼────────►│  │  Reads file      │     │
│  │  packets         │      │ Writes │  │  data      │  │  Reads  │  │  Rebroadcasts    │     │
│  └──────────────────┘      │         │  │            │  │         │  │  locally         │     │
│                            │         │  │            │  │         │  └──────────────────┘     │
└────────────────────────────┘         │  └────────────┘  │         │           │               │
                                       │                  │         │           │ UDP 4992      │
                                       │  Network Share   │         │           │ Broadcast     │
                                       │  or Cloud Sync   │         │           ▼               │
                                       │  (Dropbox, etc.) │         │  ┌──────────────────┐     │
                                       │                  │         │  │  Receives        │     │
                                       └──────────────────┘         │  │  broadcasts      │     │
                                                                    │  └──────────────────┘     │
                                                                    └────────────────────────────┘
```

---

## File Reference

### Active Scripts (v2.x)

| File | Purpose |
|------|---------|
| `FRS-Discovery-Server.py` | Server component (captures packets) |
| `FRS-Discovery-Client.py` | Client component (rebroadcasts packets) |
| `health_checks.py` | Health check framework (v2.1+) |
| `test_health_checks.py` | Test suite for health checks |

### Configuration (v2.x)

| File | Purpose |
|------|---------|
| `config.ini` | v2.x configuration with [DIAGNOSTICS] section |

### Launchers (Windows)

| File | Purpose |
|------|---------|
| `FRS-Discovery-Server-v2.bat` | Launch v2.x server |
| `FRS-Discovery-Client-v2.bat` | Launch v2.x client |

### Deprecated/Archived (v1.x)

| File | Purpose | Location |
|------|---------|----------|
| `FRS-Discovery-Proxy.py` | v1.x single script | `archive/v1.x/` |
| `Original-FRS-Wedge.py` | VA3MW's original | `archive/v1.x/` |
| `config.ini` | v1.x configuration | `archive/v1.x/` |
| `FRS-Discovery-Proxy.bat` | v1.x launcher | `archive/v1.x/` |
| v1.x logs | Old log files | `archive/v1.x/` |

### Documentation

| File | Purpose |
|------|---------|
| `INDEX.md` | This file - navigation hub |
| `README.md` | Project overview (redirects to README_v2.md) |
| `README_v2.md` | **v2.x complete documentation** |
| `QUICKSTART_v2.md` | **v2.x quick setup guide (15 minutes)** |
| `HEALTH_CHECK_GUIDE.md` | **v2.1+ health checks and diagnostics** |
| `DEPRECATION_NOTICE.md` | **v1.x deprecation notice** |
| `V1_DEPRECATION_SUMMARY.md` | **v1.x deprecation implementation summary** |
| `MIGRATION_GUIDE_v1_to_v2.md` | Migrate from v1.x to v2.x |
| `VERSION_COMPARISON.md` | Compare v1.x vs v2.x (historical) |
| `L3VPN_SOLUTION_GUIDE.md` | L3 VPN (WireGuard) solution guide |
| `ENHANCEMENTS_ROADMAP.md` | Future enhancements planning |
| `PROGRESS_TRACKER.md` | Enhancement implementation tracking |
| `RELEASE_NOTES_v2.1.0.md` | v2.1.0 release notes (RC) |
| `RELEASE_NOTES_v2.0.0.md` | v2.0.0 release notes |
| `PRIORITY_4_COMPLETION_SUMMARY.md` | Priority 4 implementation report |
| `PRIORITY_2_COMPLETION_SUMMARY.md` | Priority 2 implementation report |
| `SESSION_SUMMARY_2026-01-26.md` | Development session summary |
| `.cursorrules` | Technical VITA-49 protocol documentation |
| `LICENSE` | MIT License |

### Archived Documentation (v1.x)

| File | Location |
|------|----------|
| v1.x release notes | `archive/v1.x/` |
| v1.x comparisons | `archive/v1.x/` |
| `archive/README.md` | Archive directory guide |

### Logs (Active)

| File | Purpose |
|------|---------|
| `discovery-server.log` | v2.x server activity log |
| `discovery-client.log` | v2.x client activity log |

### Communication File (v2.x)

| File | Purpose |
|------|---------|
| `discovery.json` | Packet data transfer between server and client |

### Archived Logs

| File | Location |
|------|----------|
| `broadcast.log` | `archive/v1.x/` |
| `broadcast-dragon.log` | `archive/v1.x/` |

---

## Getting Started Flowchart

```
START: New to FlexRadio Discovery Proxy?
│
└─ Use v2.x (Current Version)
   │
   ├─ Read: QUICKSTART_v2.md (15 minute setup)
   │  OR
   │  Read: README_v2.md (complete docs)
   │
   ├─ Setup: config.ini
   │  Configure shared storage path
   │
   ├─ Run at Radio Location:
   │  FRS-Discovery-Server.py
   │
   ├─ Run at PC Location:
   │  FRS-Discovery-Client.py
   │
   └─ Open SmartSDR → Radio appears!

ALREADY USING v1.x?
│
├─ ⚠️ v1.x is DEPRECATED
│
└─ Migration Required:
   │
   ├─ Read: DEPRECATION_NOTICE.md
   │
   ├─ Read: MIGRATION_GUIDE_v1_to_v2.md
   │
   ├─ Note: v1.x and v2.x configs NOT compatible
   │
   └─ Follow migration steps to v2.x
```

---

## Support & Contact

### This Project
- **Author:** Chris L White, WX7V
- **Based on:** Original work by VA3MW
- **GitHub:** [Repository URL]
- **QRZ:** WX7V

### FlexRadio Systems
- **Website:** https://www.flexradio.com
- **Community:** https://community.flexradio.com
- **Support:** https://helpdesk.flexradio.com

**Important:** This project is **NOT supported by FlexRadio Systems, Inc.** It is a third-party tool created by amateur radio operators.

---

## License

MIT License - See [LICENSE](LICENSE) file

This software is provided "AS IS", WITHOUT WARRANTY OF ANY KIND.

---

## Contributing

Contributions welcome! Please:
1. Test thoroughly before submitting
2. Update documentation as needed
3. Follow existing code style
4. Include examples for new features

---

## Changelog Summary

| Version | Date | Status | Major Changes |
|---------|------|--------|---------------|
| **v2.1.0** | 2026-01-26 | ✅ RC | **MIT License, health checks, diagnostics** |
| **v2.0.0** | 2026-01-26 | ✅ Stable | **Client-server architecture, authentic packets** |
| v1.0.1 | 2026-01-22 | ❌ Deprecated | Timing fixes, stability improvements |
| v1.0.0 | 2026-01-20 | ❌ Deprecated | Fork of VA3MW's work, VITA-49 improvements |

**Note:** v1.x versions moved to `archive/v1.x/` as of 2026-01-26

---

**73 de WX7V**

**Happy DXing!**
