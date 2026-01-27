# FlexRadio Discovery Proxy - Version Comparison

## ⚠️ Important: Version 1.x Deprecated

**As of 2026-01-26, Version 1.x has been deprecated.**

- ❌ v1.x files moved to `archive/v1.x/`
- ❌ No longer supported or maintained
- ✅ Use v2.x (current version)
- See [DEPRECATION_NOTICE.md](DEPRECATION_NOTICE.md) for details

**This document is maintained for historical reference only.**

---

## Quick Reference

| Aspect | v1.x | v2.0 |
|--------|------|------|
| **Architecture** | Single script | Client + Server |
| **Packet Source** | Synthetic (generated) | Authentic (captured) |
| **Configuration** | Manual radio details | Automatic from packets |
| **Communication** | Direct broadcast | File-based |
| **Network Requirements** | Direct VPN/route | Any topology |
| **Setup Complexity** | Simple | Moderate |
| **Use Cases** | Direct VPN | VPN, Internet, Cloud |

---

## File Structure Comparison

### v1.x Files

| File | Purpose |
|------|---------|
| `FRS-Discovery-Proxy.py` | Main script (generates packets) |
| `config.ini` | Configuration (radio details) |
| `broadcast.log` | Activity logging |
| `FRS-Discovery-Proxy.bat` | Windows launcher |
| `README.md` | Documentation |
| `RELEASE_NOTES_v1.0.0.md` | v1.0.0 release notes |
| `RELEASE_NOTES_v1.0.1.md` | v1.0.1 release notes |

### v2.0 Files (New)

| File | Purpose |
|------|---------|
| `FRS-Discovery-Server-v2.py` | **Server component** (captures packets) |
| `FRS-Discovery-Client-v2.py` | **Client component** (rebroadcasts packets) |
| `config-v2.ini` | **Configuration** (server + client settings) |
| `discovery.json` | **Communication file** (packet data) |
| `discovery-server.log` | Server activity log |
| `discovery-client.log` | Client activity log |
| `FRS-Discovery-Server-v2.bat` | Windows server launcher |
| `FRS-Discovery-Client-v2.bat` | Windows client launcher |
| `README_v2.md` | **v2 documentation** |
| `RELEASE_NOTES_v2.0.0.md` | **v2.0.0 release notes** |
| `MIGRATION_GUIDE_v1_to_v2.md` | **Migration instructions** |
| `QUICKSTART_v2.md` | **Quick setup guide** |
| `VERSION_COMPARISON.md` | This file |

---

## Configuration Comparison

### v1.x config.ini

```ini
[DEFAULT]
IP_Address = 192.168.0.101
Callsign = WX7V
Nickname = Lake6600
Version = 4.1.5.39794
Serial = 3718-0522-6600-0003
Model = FLEX-6600
Radio_License = 00-1C-2D-05-0A-5A
```

**All fields must be manually configured.**

### v2.0 config-v2.ini

```ini
[SERVER]
Listen_Address = 0.0.0.0
Discovery_Port = 4992
Shared_File_Path = discovery.json
Update_Interval = 2.0

[CLIENT]
Shared_File_Path = discovery.json
Broadcast_Address = 255.255.255.255
Discovery_Port = 4992
Check_Interval = 3.0
Max_File_Age = 15.0
```

**Radio details are captured automatically from real packets.**

---

## Feature Comparison

### Discovery Method

**v1.x:**
- Pings radio IP to check availability
- Generates synthetic VITA-49 packet
- Uses manually configured radio information
- Assumes radio is "Available" if ping succeeds

**v2.0:**
- Listens for actual VITA-49 broadcasts
- Captures authentic packets from radio
- Extracts real radio information automatically
- Reports actual radio status (Available, In Use, etc.)

### Network Topology Support

**v1.x:**
- ✓ Direct VPN with routed subnets
- ✗ Non-routed networks
- ✗ Cloud-based scenarios
- ✗ Complex network topologies

**v2.0:**
- ✓ Direct VPN with routed subnets
- ✓ Non-routed networks (via file sharing)
- ✓ Cloud-based scenarios (Dropbox, OneDrive, etc.)
- ✓ Any network topology with file access

### Configuration Maintenance

**v1.x:**
- Manual configuration required
- Must update when radio firmware changes
- Must update when radio settings change
- Risk of outdated version strings

**v2.0:**
- Zero manual configuration
- Automatically tracks firmware updates
- Automatically tracks radio settings
- Always current with radio state

### Multi-Radio Support

**v1.x:**
- Not supported (single radio only)
- Would require multiple script instances with separate configs

**v2.0:**
- Easy multi-radio support
- Run multiple server instances with different output files
- Run multiple client instances reading different files

---

## Performance Comparison

### Latency

**v1.x:**
- Discovery broadcast: Immediate (11 seconds between broadcasts)
- Response to radio changes: 11-21 seconds (depends on ping + broadcast cycle)

**v2.0:**
- Discovery broadcast: Depends on file sync
  - Network share: < 1 second typically
  - Cloud sync: 5-30 seconds typically
- Response to radio changes: File sync delay + check interval

**Winner for latency:** v1.x (if direct network path exists)

### Resource Usage

**v1.x:**
- CPU: Very low (ping + packet generation)
- Network: Minimal (ICMP ping + UDP broadcast)
- Disk: Minimal (logging only)

**v2.0:**
- CPU: Low (packet capture + file I/O)
- Network: Minimal (UDP receive/broadcast)
- Disk: Moderate (periodic file writes/reads)

**Winner for resources:** v1.x (slightly lower overhead)

### Accuracy

**v1.x:**
- Radio status: Ping-based guess (not accurate)
- Firmware version: Manual update required
- Radio state: Always shows "Available"

**v2.0:**
- Radio status: Actual status from radio
- Firmware version: Always current
- Radio state: Reflects real state (Available/In Use/Update)

**Winner for accuracy:** v2.0 (significantly better)

---

## Use Case Recommendations

### Use v1.x When:

1. ✓ You have **direct VPN with routed subnets**
2. ✓ You need **absolute lowest latency**
3. ✓ You want **simplest possible setup**
4. ✓ You have **single radio only**
5. ✓ You have **stable radio configuration**
6. ✓ File-based communication is not viable

### Use v2.0 When:

1. ✓ You need **authentic radio status**
2. ✓ You have **complex network topology**
3. ✓ You want **zero configuration maintenance**
4. ✓ You need **cloud-based access** (no VPN)
5. ✓ You have **multiple radios**
6. ✓ Your network is **non-routed or blocked**
7. ✓ You want **future-proof automatic updates**

---

## Migration Decision Tree

```
Do you have a working v1.x setup?
│
├─ No → Start with v2.0 (better long-term)
│
└─ Yes → Is it working well?
    │
    ├─ No → Try v2.0 (might solve issues)
    │
    └─ Yes → Do you need any of these?
        │
        ├─ Authentic radio status
        ├─ Multiple radios
        ├─ Cloud access (no VPN)
        ├─ Auto-update radio info
        │
        ├─ Yes to any → Migrate to v2.0
        │
        └─ No to all → Stay with v1.x (it works!)
```

---

## Technical Differences

### Packet Handling

**v1.x:**
```python
# Generate synthetic packet
message_text = f'discovery_protocol_version=3.1.0.2 model={model} ...'
payload_bytes = message_text.encode('utf-8')
vita_header = construct_vita_header(...)
message = vita_header + payload_bytes
sock.sendto(message, (broadcast_address, port))
```

**v2.0 Server:**
```python
# Capture real packet
data, addr = sock.recvfrom(4096)
packet_hex = data.hex()
payload = data[28:]
parsed_info = parse_discovery_payload(payload)
packet_data = {'packet_hex': packet_hex, 'radio_info': parsed_info, ...}
with open(shared_file_path, 'w') as f:
    json.dump(packet_data, f)
```

**v2.0 Client:**
```python
# Rebroadcast real packet
with open(shared_file_path, 'r') as f:
    packet_data = json.load(f)
packet_bytes = bytes.fromhex(packet_data['packet_hex'])
sock.sendto(packet_bytes, (broadcast_address, port))
```

### Status Detection

**v1.x:**
```python
# Ping-based status
response = subprocess.run(['ping', '-n', '1', ip_address])
if response.returncode == 0:
    status = 'Available'  # Always "Available"
```

**v2.0:**
```python
# Actual status from radio
parsed_info = parse_discovery_payload(payload)
status = parsed_info.get('status', 'Unknown')  # Real status: Available, In Use, etc.
```

### Configuration Updates

**v1.x:**
```python
# Manual configuration
config = configparser.ConfigParser()
config.read('config.ini')
version = config['DEFAULT']['Version']  # Must update manually
```

**v2.0:**
```python
# Automatic from packets
parsed_info = parse_discovery_payload(payload)
version = parsed_info.get('version', 'Unknown')  # Always current
```

---

## Compatibility

### Operating Systems

| OS | v1.x | v2.0 |
|----|------|------|
| Windows 10/11 | ✓ | ✓ |
| Linux | ✓ | ✓ |
| macOS | ✓ | ✓ |

### Python Versions

| Version | v1.x | v2.0 |
|---------|------|------|
| Python 2.x | ✗ | ✗ |
| Python 3.6+ | ✓ | ✓ |
| Python 3.10+ | ✓ | ✓ |

### FlexRadio Models

| Model | v1.x | v2.0 |
|-------|------|------|
| FLEX-6300 | ✓ | ✓ |
| FLEX-6400 | ✓ | ✓ |
| FLEX-6600 | ✓ | ✓ |
| FLEX-6700 | ✓ | ✓ |
| FLEX-8600 | ✓ | ✓ |

### SmartSDR Versions

| Version | v1.x | v2.0 |
|---------|------|------|
| SmartSDR 3.x | ✓ | ✓ |
| SmartSDR 4.x | ✓ | ✓ |
| SmartSDR 5.x | ? | ✓ (auto-adapts) |

---

## Summary

### v1.x Strengths
- Simplest setup
- Lowest latency
- Minimal resource usage
- Single file deployment

### v2.0 Strengths
- Authentic radio status
- Automatic configuration
- Flexible network topology
- Multi-radio support
- Future-proof

### Bottom Line

**v1.x** is perfect if you have a working VPN and want simple, fast discovery.

**v2.0** is better for complex scenarios, multiple radios, or cloud-based access.

**Both versions** are fully functional and supported. Choose based on your needs.

---

## Version History

| Version | Date | Key Features |
|---------|------|--------------|
| v1.0.0 | January 2026 | Initial release (fork of VA3MW's work) |
| v1.0.1 | January 2026 | Stability fixes, timing improvements |
| v2.0.0 | January 2026 | **Client-server architecture, authentic packets** |

---

**Author:** Chris L White, WX7V  
**Based on:** Original work by VA3MW  
**License:** MIT  
**Not supported by FlexRadio Systems, Inc.**

**73 de WX7V**
