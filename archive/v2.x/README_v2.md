# FlexRadio Discovery Proxy v2.2 - Client/Server Architecture

**Version:** 2.2.0  
**Author:** Chris L White, WX7V (2026)  
**Based on:** Original work by VA3MW (2024)  
**License:** MIT

---

## ⚠️ WARNING: USE AT YOUR OWN RISK

This script is provided "as is," without warranty of any kind, express or implied. The authors and copyright holders are not liable for any damages arising from the use of this software.

**This script is not supported in any way by FlexRadio Inc.**

---

## 🚀 What's New in v2.2

Version 2.2 introduces **socket-based communication** for real-time discovery packet streaming:

### NEW: Socket Mode (v2.2.0)
- **Direct TCP Connection**: Real-time packet streaming over L3VPN
- **Sub-Second Latency**: Eliminates 5-30 second cloud sync delays
- **Multi-Client Support**: Single server streams to multiple clients
- **Automatic Reconnection**: Client recovers from connection failures
- **Dual Mode**: Choose between socket (real-time) or file (cloud sync) modes

### v2.1.0 Features
- **Health Checks**: Startup diagnostics and periodic monitoring
- **Better Troubleshooting**: Clear pass/fail/warn indicators
- **Network Validation**: Automatic connectivity testing

### v2.0 Architecture (Client/Server)
- **Server**: Captures **actual** VITA-49 discovery packets from FlexRadio
- **Client**: Rebroadcasts the real packets to local network
- **Communication**: Socket-based (new) or file-based via shared drive
- **Advantages**:
  - Always broadcasts authentic packets with current radio status
  - Automatically tracks radio state changes (in use, available, etc.)
  - Works across any network topology (VPN, internet, etc.)
  - No manual radio configuration needed - uses real data

---

## Architecture Overview

```
┌─────────────────────────────────────┐         ┌──────────────────────────────────┐
│  Remote Location (Server)           │         │  Local PC (Client)               │
│                                      │         │                                  │
│  ┌──────────────┐                   │         │                                  │
│  │  FlexRadio   │                   │         │  ┌────────────────────┐          │
│  │  (on subnet) │                   │         │  │  SmartSDR Client   │          │
│  └──────┬───────┘                   │         │  └─────────▲──────────┘          │
│         │ UDP 4992                  │         │            │                     │
│         │ Discovery Broadcasts      │         │            │ Discovers           │
│         ▼                            │         │            │ Radio               │
│  ┌──────────────────────┐           │         │  ┌─────────┴──────────┐          │
│  │ FRS-Discovery-       │           │         │  │ FRS-Discovery-     │          │
│  │ Server-v2.py         │           │         │  │ Client-v2.py       │          │
│  │                      │           │         │  │                    │          │
│  │ • Listens on 4992    │           │         │  │ • Reads file       │          │
│  │ • Captures packets   │◄──────────┼─────────┤  │ • Broadcasts 4992  │          │
│  │ • Writes to file     │  Shared   │ Network │  │ • Rate limited     │          │
│  └──────────────────────┘  Drive/   │  Share  │  └────────────────────┘          │
│                            Cloud     │   or    │                                  │
│                            Storage   │  Cloud  │                                  │
└─────────────────────────────────────┘  Sync   └──────────────────────────────────┘
                                       (discovery.json)
```

---

## How It Works

### Server Side (Remote Location)
1. Binds to UDP port 4992 and listens for FlexRadio discovery broadcasts
2. Receives authentic VITA-49 packets from the radio
3. Parses packet contents (model, serial, IP, status, etc.)
4. Writes packet data to JSON file on shared drive
5. Rate-limits file writes to prevent excessive I/O

### Client Side (Local PC)
1. Monitors the shared JSON file for updates
2. Checks file age to ensure radio is still active
3. Reads the captured packet data
4. Rebroadcasts the authentic packet on local network
5. SmartSDR clients receive broadcasts and discover the radio

### File Communication
The shared file (`discovery.json`) contains:
- Complete packet hex dump
- Parsed radio information (model, serial, IP, callsign, etc.)
- Timestamp and age information
- Server version for compatibility checking

---

## System Requirements

### Server Requirements
- **Location**: Must be on same subnet as FlexRadio
- **OS**: Windows, Linux, or macOS
- **Python**: 3.6 or higher
- **Network**: Ability to receive UDP broadcasts on port 4992
- **Storage**: Access to shared drive/folder (network share or cloud sync)

### Client Requirements
- **Location**: Same network as SmartSDR client
- **OS**: Windows, Linux, or macOS
- **Python**: 3.6 or higher
- **Network**: Ability to send UDP broadcasts on port 4992
- **Storage**: Access to same shared drive/folder as server

### Shared Storage Options
- **Network Share**: SMB/CIFS (Windows file sharing), NFS (Linux)
- **Cloud Sync**: Dropbox, Google Drive, OneDrive, iCloud Drive, etc.
- **USB Drive**: If moving between networks physically
- **WebDAV**: Network-based file access protocol

---

## Installation & Configuration

### Step 1: Install Python

Both server and client need Python 3.6+:

**Windows:**
```powershell
# Download from python.org or use Microsoft Store
python --version
```

**Linux/macOS:**
```bash
python3 --version
# If not installed: sudo apt install python3 (Linux) or use Homebrew (macOS)
```

### Step 2: Set Up Shared Storage

Choose one of these options:

#### Option A: Network Share (Recommended for VPN scenarios)

**Windows Server Share:**
```powershell
# Create shared folder
New-SmbShare -Name "FlexRadio" -Path "C:\FlexRadio" -FullAccess "Everyone"
```

**Client Access:**
```powershell
# Map network drive (optional)
net use Z: \\server\FlexRadio
```

#### Option B: Cloud Sync (Recommended for Internet scenarios)

1. Install Dropbox/Google Drive/OneDrive on both machines
2. Create a shared folder: `FlexRadio`
3. Ensure sync is active on both machines

#### Option C: Local Testing
For testing on same machine, use local path like `C:\FlexRadio\discovery.json`

### Step 3: Configure config-v2.ini

Edit `config-v2.ini` on both server and client:

**Server Configuration:**
```ini
[SERVER]
Listen_Address = 0.0.0.0
Discovery_Port = 4992
Shared_File_Path = Z:\FlexRadio\discovery.json  # Or cloud path
Update_Interval = 2.0
```

**Client Configuration:**
```ini
[CLIENT]
Shared_File_Path = Z:\FlexRadio\discovery.json  # Same as server!
Broadcast_Address = 255.255.255.255
Discovery_Port = 4992
Check_Interval = 3.0
Max_File_Age = 15.0
```

**Important:** `Shared_File_Path` must point to the same file on both machines!

---

## Usage

### Starting the Server (Remote Location)

**Windows:**
```powershell
python FRS-Discovery-Server-v2.py
```

**Linux/macOS:**
```bash
python3 FRS-Discovery-Server-v2.py
```

**Expected Output:**
```
======================================================================
FlexRadio Discovery Server v2.0.0
======================================================================

Server Configuration:
  Listen Address: 0.0.0.0
  Discovery Port: 4992
  Shared File: Z:\FlexRadio\discovery.json
  Update Interval: 2.0s

======================================================================

Listening for FlexRadio discovery packets...

14:23:45 - Packet #1 from 192.168.0.101
  Radio: FLEX-6600 (Lake6600)
  Callsign: WX7V | IP: 192.168.0.101
  Status: Available | Version: 4.1.5.39794
  → Packet written to: Z:\FlexRadio\discovery.json
```

### Starting the Client (Local PC)

**Windows:**
```powershell
python FRS-Discovery-Client-v2.py
```

**Linux/macOS:**
```bash
python3 FRS-Discovery-Client-v2.py
```

**Expected Output:**
```
======================================================================
FlexRadio Discovery Client v2.0.0
======================================================================

Client Configuration:
  Shared File: Z:\FlexRadio\discovery.json
  Broadcast Address: 255.255.255.255
  Discovery Port: 4992
  Check Interval: 3.0s
  Max File Age: 15.0s

======================================================================

Monitoring for discovery packets...

14:23:50 - Radio discovered:
  FLEX-6600 (Lake6600)
  Callsign: WX7V | IP: 192.168.0.101
  Status: Available | Version: 4.1.5.39794
  File age: 2.3s | Server: v2.0.0
14:23:50 - ✓ Started broadcasting discovery packets
14:24:20 - ✓ Broadcasting... (packet #10, file age: 4.1s)
```

### Opening SmartSDR

1. Start SmartSDR client on same PC as client script
2. Radio should appear in the radio chooser
3. Click to connect (network route to radio IP must exist)

---

## Monitoring & Troubleshooting

### Health Checks (v2.1.0+)

**Automatic diagnostics** help identify configuration issues and connectivity problems:

#### Startup Health Checks
Every time you start the server or client, automatic health checks validate:
- ✅ Network interfaces and IP addresses
- ✅ UDP port 4992 availability
- ✅ Broadcast capability (client)
- ✅ File read/write permissions
- ✅ VPN/Server connectivity (optional)
- ✅ FlexRadio connectivity (optional)

**Example Output:**
```
======================================================================
Startup Health Check
======================================================================
[+] [PASS]   Network Interfaces             Found 1 network interface(s)
[+] [PASS]   UDP Port 4992                  Port 4992 is available
[+] [PASS]   VPN/Server Connectivity        192.168.1.100 is reachable
                                          Latency: 45ms
[+] [PASS]   File Read Permission           Can read discovery file

----------------------------------------------------------------------
Status: 4 passed (Total: 4)
Overall: OPERATIONAL
======================================================================
```

#### Periodic Health Monitoring
During operation, health checks run every 60 seconds (configurable) to detect:
- Network connectivity changes
- VPN disconnections
- Port conflicts
- File system issues

**For complete health check documentation, see:** [HEALTH_CHECK_GUIDE.md](HEALTH_CHECK_GUIDE.md)

### Log Files

**Server:** `discovery-server.log`
- Tracks packets received from radio
- Records file write operations
- Logs errors and warnings
- Health check results

**Client:** `discovery-client.log`
- Tracks broadcasts sent
- Records file read operations
- Logs stale file warnings
- Health check results

### Common Issues

#### Server: No Packets Received

**Symptoms:**
```
15:30:00 - No packets received for 30+ seconds
```

**Solutions:**
1. Verify radio is powered on and connected to network
2. Check server is on same subnet as radio
3. Confirm port 4992 is not blocked by firewall
4. Try binding to specific interface IP instead of 0.0.0.0

#### Client: File Not Found

**Symptoms:**
```
15:30:00 - ⚠ Cannot read discovery file: File not found
```

**Solutions:**
1. Verify `Shared_File_Path` is correct in config
2. Check network share is mounted/accessible
3. Ensure server has written at least one packet
4. Verify cloud sync is active and file has synced

#### Client: Stale File Warning

**Symptoms:**
```
15:30:00 - ⚠ Discovery file is stale (45.2s old) - Radio may be offline
```

**Solutions:**
1. Check if server script is still running
2. Verify radio is still broadcasting
3. Check network share connectivity
4. Review `discovery-server.log` for errors

#### SmartSDR: Radio Not Appearing

**Solutions:**
1. Verify client script is running and broadcasting
2. Check Windows Firewall allows Python UDP broadcasts
3. Ensure SmartSDR and client are on same subnet
4. Try running client script as Administrator (Windows)

---

## Performance Tuning

### Update Interval (Server)

```ini
Update_Interval = 2.0  # Seconds between file writes
```

- **Lower (1.0s)**: Faster client response, more disk I/O
- **Higher (5.0s)**: Less disk I/O, slower client updates
- **Recommended**: 2.0-3.0 seconds

### Check Interval (Client)

```ini
Check_Interval = 3.0  # Seconds between file reads
```

- **Lower (1.0s)**: Faster discovery, more disk I/O
- **Higher (5.0s)**: Less disk I/O, slower discovery
- **Recommended**: 2.0-4.0 seconds

### Max File Age (Client)

```ini
Max_File_Age = 15.0  # Seconds before file considered stale
```

- **Calculation**: Should be at least `Update_Interval + Check_Interval + network_delay`
- **Recommended**: 15-30 seconds

---

## Advanced Scenarios

### Multiple Radios

To support multiple radios:

1. Run multiple server instances with different shared files:
   ```ini
   # Server 1: config-v2-radio1.ini
   Shared_File_Path = discovery-radio1.json
   
   # Server 2: config-v2-radio2.ini
   Shared_File_Path = discovery-radio2.json
   ```

2. Run multiple client instances reading different files

### Internet Access (Cloud Sync)

Perfect for accessing your home radio from a remote location:

1. **At Home**: Run server with Dropbox/OneDrive sync folder
2. **Remote**: Run client with same sync folder
3. **Latency**: Depends on cloud sync speed (typically 5-30 seconds)

### VPN Access (Network Share)

For VPN scenarios with file sharing:

1. Set up SMB share on server side
2. Mount share on client side via VPN
3. Configure both scripts to use share path

---

## Security Considerations

### Network Shares
- Use authentication on network shares
- Limit access to specific users
- Consider using VPN for share access over internet

### Cloud Storage
- Enable two-factor authentication
- Use encrypted folders (VeraCrypt, Cryptomator)
- Review cloud provider's security policies

### Firewall Rules
- Allow Python through firewall on both machines
- Restrict port 4992 to local network only
- Use Windows Defender or third-party AV exceptions if needed

---

## Comparison: v1.x vs v2.0

| Feature | v1.x | v2.0 |
|---------|------|------|
| **Architecture** | Single script | Client + Server |
| **Packet Source** | Synthetic (generated) | Authentic (captured) |
| **Configuration** | Manual radio details | Automatic from packets |
| **Radio Status** | Ping-based guess | Actual radio status |
| **Network Topology** | Direct network path required | Any topology (file-based) |
| **Multi-Radio** | Not supported | Supported (multiple instances) |
| **Complexity** | Simple | Moderate |
| **Use Case** | Direct VPN connections | Any network scenario |

---

## Migration from v1.x

If you're currently using v1.x and want to migrate:

1. **Keep v1.x running** during transition
2. **Set up v2 server** at radio location
3. **Verify server** is capturing packets
4. **Set up v2 client** at PC location
5. **Test with SmartSDR** while v1.x still running
6. **Stop v1.x** once v2 is confirmed working

v1.x and v2.0 are **completely independent** - no configuration carries over.

---

## Limitations

1. **File-Based Latency**: Discovery updates are limited by file sync speed
2. **Single Direction**: Server doesn't receive client status
3. **No Encryption**: Discovery packets are not encrypted by FlexRadio
4. **Subnet Dependency**: Server must be on same subnet as radio
5. **File Locking**: Some sync services may cause brief file locks

---

## Future Enhancements

Potential improvements for future releases:

- Direct TCP/UDP tunneling option
- Web dashboard for monitoring
- Automatic server/client pairing
- Docker containers for easy deployment
- systemd/Windows Service integration
- Packet filtering and modification options

---

## Credits

**Original Concept:** VA3MW - FlexRadio Broadcast Wedge (2024)  
**v2.0 Architecture:** Chris L White, WX7V (2026)  
**Protocol Documentation:** FlexRadio Systems VITA-49 Implementation

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for complete details.

**Copyright © 2026 Chris L White (WX7V)**  
Based on original work by VA3MW (2024)

### Disclaimer

**⚠️ IMPORTANT: This software is NOT officially supported by FlexRadio Systems, Inc., its employees, or its help desk.**

This is an independent, community-developed tool created to solve specific networking challenges when accessing FlexRadio transceivers over VPN or remote connections. While it follows the FlexRadio Discovery Protocol specifications, it is not endorsed, maintained, or supported by FlexRadio Systems.

For official FlexRadio support and products, please visit:
- **Website:** https://www.flexradio.com
- **Help Desk:** https://helpdesk.flexradio.com
- **Community:** https://community.flexradio.com

### Warranty Disclaimer

This software is provided "AS IS", WITHOUT WARRANTY OF ANY KIND, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. See the LICENSE file for complete terms.

---

## Support

For issues or questions about this community tool:
- **GitHub Issues:** [Repository URL]
- **QRZ:** WX7V
- **Email:** [Your Contact]

For official FlexRadio product support, use the links above in the Disclaimer section.

---

**73 de WX7V**
