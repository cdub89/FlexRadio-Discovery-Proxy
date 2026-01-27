# FlexRadio Discovery Proxy v1.0.0

**Release Date:** January 24, 2026

## Overview

FlexRadio Discovery Proxy enables SmartSDR clients to discover and connect to FlexRadio transceivers that are not on the same local subnet. The proxy acts as a "wedge" by rebroadcasting VITA-49 discovery packets on the local network, making remote radios (e.g., over VPN connections) appear as if they were local.

This is the first stable release, ready for production use.

---

## Key Features

### ✨ Core Functionality
- **VITA-49 Protocol Implementation** - Full support for FlexRadio's discovery protocol with proper packet structure
- **Dynamic Packet Generation** - Automatic timestamp and packet size calculation
- **Health Monitoring** - Continuous ping checks before broadcasting to ensure radio availability
- **Cross-Platform Support** - Works on Windows, Linux, and macOS with automatic OS detection
- **Smart Logging** - State-change-based logging to avoid log file bloat during continuous operation

### 🛠️ Technical Highlights
- **Zero External Dependencies** - Uses only Python 3 standard libraries
- **Proper Error Handling** - Robust exception handling with detailed error logging
- **Configurable** - Easy INI-based configuration for multiple radio setups
- **Production Ready** - Clean code, no linter errors, comprehensive testing

---

## What's New in v1.0.0

This release marks the first production-ready version with:

- ✅ Updated VITA-49 header for SmartSDR 4.1.5 compatibility (up from 3.8.2)
- ✅ Enhanced documentation with detailed troubleshooting guide
- ✅ Comprehensive packet structure documentation for future maintainers
- ✅ Cross-platform ping command support
- ✅ Optimized broadcast timing (10-second intervals for active radios)
- ✅ Clean, maintainable codebase ready for community contributions

---

## System Requirements

### Software
- **Python 3.x** (Python 2.x NOT supported)
- No external packages required - uses only standard library

### Network
- Permission to send UDP broadcast packets
- Permission to execute ping commands  
- Firewall allowing:
  - Outbound UDP to port 4992
  - ICMP ping requests to target radio
  - UDP broadcasts on local network (255.255.255.255)

### Tested Platforms
- ✅ Windows 10/11
- ✅ Linux (various distributions)
- ✅ macOS

---

## Quick Start

### 1. Configure Your Radio

Edit `config.ini` with your radio's parameters:

```ini
[DEFAULT]
IP_Address = 192.168.X.XXX
Callsign = YOUR_CALL
Nickname = Radio-Nickname
Version = 4.1.5.39794
Serial = XXX-XXXX-XXXX-XXXX
Model = FLEX-6600
Radio_License = 00-1C-2D-XX-XX-XX
```

### 2. Run the Proxy

**Windows:**
```cmd
Double-click FRS-Discovery-Proxy.bat
```

**Linux/macOS:**
```bash
python3 FRS-Discovery-Proxy.py
```

### 3. Connect with SmartSDR

Open SmartSDR - your remote radio should now appear in the radio chooser!

---

## Documentation

📖 **[Complete Documentation in README.md](README.md)**

The comprehensive README includes:
- Detailed setup instructions
- VITA-49 packet structure documentation
- How to capture and update discovery packets
- Troubleshooting guide
- Future maintenance instructions

---

## Credits

**Original Author:** VA3MW (Michael Walker) - May 2024  
**Enhanced & Updated:** WX7V (Chris L White) - January 2026

Special thanks to ChatGPT-4 for development assistance.

---

## License

MIT License - See [LICENSE](LICENSE) file for full terms.

**Important:** This software is provided "AS IS", WITHOUT WARRANTY OF ANY KIND. This script is not officially supported by FlexRadio Inc.

---

## Support & Contributing

### Found a Bug?
Please open an issue with:
- Your Python version (`python --version`)
- Operating system
- Contents of `broadcast.log`
- Steps to reproduce

### Want to Contribute?
Pull requests are welcome! Please ensure:
- Code follows existing style
- No new external dependencies
- Documentation is updated
- Changes are tested on Windows and Linux

---

## Acknowledgments

This project enables amateur radio operators to access their FlexRadio transceivers remotely while maintaining the native SmartSDR discovery experience. Thank you to the ham radio community for continued support and testing.

---

## What's Next?

Planned for future releases:
- Enhanced configuration validation
- Graceful shutdown handling (Ctrl+C)
- Command-line argument support
- Multiple radio support from single proxy instance

---

**73 de WX7V**

*FlexRadio Discovery Proxy - Bringing your radio closer, no matter how far.*
