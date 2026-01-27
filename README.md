# FlexRadio Discovery Proxy

**Current Version:** v3.0.0  
**Status:** ✅ Production Ready

---

## Quick Start

### 1. Download or Clone
```bash
git clone https://github.com/yourusername/FlexRadio-Discovery-Proxy.git
cd FlexRadio-Discovery-Proxy
```

### 2. Configure
Edit `config.ini`:
- **Server:** No changes needed (defaults work)
- **Client:** Set `Server_Address` to your server's IP address

### 3. Run Server (at radio location)
```bash
python FRS-Discovery-Server.py
```
or double-click `FRS-Discovery-Server.bat` (Windows)

### 4. Run Client (at SmartSDR location)
```bash
python FRS-Discovery-Client.py
```
or double-click `FRS-Discovery-Client.bat` (Windows)

### 5. Start SmartSDR
Your radio should appear in the chooser!

**For detailed setup:** See [HEALTH_CHECK_GUIDE.md](HEALTH_CHECK_GUIDE.md) and [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## What's New in v3.0.0

### 🚀 **Major Simplification - Socket Mode Only**
- **Removed:** File-based mode (cumbersome and slower)
- **Focus:** TCP socket streaming only
- **Result:** Simpler, faster, more reliable
- **Latency:** Sub-second real-time communication

### ✅ **Streamlined Architecture**
- Direct TCP connection between server and client
- No file system dependencies
- No cloud sync required
- Cleaner codebase

### ✅ **Minimal Logging**
- Log files only written at startup and shutdown
- Reduced disk I/O for better performance
- All operational info still shown on console

---

## Previous Versions

### v2.x (Deprecated - File Mode)
- Supported both socket and file modes
- File mode required shared storage (OneDrive, Dropbox, network shares)
- More complex configuration
- Higher latency with file mode

### v1.x (Archived)
- Generated synthetic packets
- Single-location deployment
- See `archive/v1.x/` for historical reference

---

## Architecture

**v3.x uses a streamlined client-server model:**

### Server Component
- Runs at remote location where FlexRadio is located
- Captures real VITA-49 discovery packets from radio
- Streams packets to connected clients via TCP
- File: `FRS-Discovery-Server.py`

### Client Component  
- Runs at local PC where SmartSDR is running
- Connects to server via TCP socket
- Receives packets in real-time
- Rebroadcasts packets locally for SmartSDR
- File: `FRS-Discovery-Client.py`

### Network Requirements
- VPN or direct network connection between locations
- TCP port 5992 accessible (configurable)
- UDP port 4992 for FlexRadio discovery (standard)

---

## Use Cases

### Perfect For:
✅ **VPN Access** - Access your FlexRadio over VPN from anywhere  
✅ **Remote Operation** - Operate from home, work, mobile  
✅ **Multiple Locations** - Multiple clients can connect to one server  
✅ **Real-Time** - Sub-second latency for discovery packets  

### Not Needed For:
❌ **Same Subnet** - If SmartSDR and radio are on same network  
❌ **Direct Network** - If discovery packets already broadcast across your network  

---

## Why v3.x?

### Advantages Over v2.x

| Feature | v2.x | v3.x |
|---------|------|------|
| **Socket Mode** | Optional | Standard |
| **File Mode** | Supported | Removed |
| **Latency** | 1-30s (file) | <1s (socket) |
| **Configuration** | Complex | Simple |
| **Dependencies** | File system | Network only |
| **Setup Time** | 30 min | 15 min |
| **Reliability** | Good | Excellent |

### Advantages Over v1.x

| Feature | v1.x | v3.x |
|---------|------|------|
| **Packet Type** | Synthetic (fake) | Authentic (real) |
| **Configuration** | Manual setup | Auto-detects radio |
| **Radio Status** | Static | Real-time |
| **Multi-Radio** | Difficult | Easy |
| **Health Checks** | No | Yes |
| **Support** | ❌ Deprecated | ✅ Active |

---

## Installation

### Requirements
- **Python 3.7+** on both server and client machines
- **Network connectivity** between server and client (VPN or direct)
- **FlexRadio** on same subnet as server

### Quick Setup

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/yourusername/FlexRadio-Discovery-Proxy.git
   cd FlexRadio-Discovery-Proxy
   ```

2. **Configure `config.ini`**
   - Set `Server_Address` on client to your server's IP
   - Adjust ports if needed (default 5992)

3. **Run server at radio location**
   ```bash
   python FRS-Discovery-Server.py
   ```

4. **Run client at SmartSDR location**
   ```bash
   python FRS-Discovery-Client.py
   ```

5. **Start SmartSDR** - Your radio should appear!

---

## Documentation

### Essential Reading
- **[HEALTH_CHECK_GUIDE.md](HEALTH_CHECK_GUIDE.md)** - Diagnostics and troubleshooting
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[INDEX.md](INDEX.md)** - Complete documentation index

### Reference
- **[RELEASE_NOTES_v3.0.0.md](RELEASE_NOTES_v3.0.0.md)** - Current release notes
- **[ENHANCEMENTS_ROADMAP.md](ENHANCEMENTS_ROADMAP.md)** - Future plans
- **[L3VPN_SOLUTION_GUIDE.md](L3VPN_SOLUTION_GUIDE.md)** - VPN setup guide

### Archive
- **[archive/](archive/)** - Previous versions (v1.x, v2.x)

---

## Support

### ⚠️ Important Notice

This software is **NOT officially supported** by FlexRadio Systems, Inc., its employees, or its help desk. This is an independent community tool.

**For official FlexRadio support:** https://www.flexradio.com

### Community Support

- GitHub Issues: Report bugs or request features
- Discussions: Share experiences and solutions
- Pull Requests: Contributions welcome!

---

## License

MIT License - See [LICENSE](LICENSE) file for details

Copyright (c) 2026 Chris L White (WX7V)  
Based on original work by VA3MW (2024)

---

## Credits

- **Original Concept:** VA3MW (v1.x)
- **v2.x/v3.x Development:** WX7V
- **FlexRadio VITA-49 Protocol:** FlexRadio Systems, Inc.

---

## Quick Links

| Document | Purpose |
|----------|---------|
| [HEALTH_CHECK_GUIDE.md](HEALTH_CHECK_GUIDE.md) | Diagnostic tools and health checks |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Fix common problems |
| [RELEASE_NOTES_v3.0.0.md](RELEASE_NOTES_v3.0.0.md) | What's new in v3.0 |
| [L3VPN_SOLUTION_GUIDE.md](L3VPN_SOLUTION_GUIDE.md) | VPN setup guide |
| [INDEX.md](INDEX.md) | Complete documentation index |

---

**Version 3.0.0** - Socket-Only Edition  
*Simpler. Faster. Better.*
