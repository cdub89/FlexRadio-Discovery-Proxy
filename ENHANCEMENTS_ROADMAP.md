# FlexRadio Discovery Proxy - Enhancement Roadmap

This document outlines planned enhancements to improve performance, reliability, and usability of the FlexRadio Discovery Proxy system.

---

## Priority 1: Direct Network Communication over L3VPN

### Problem Statement
The current v2.0 file-based communication via OneDrive (or other cloud sync services) has inherent limitations:
- **Sync Delays:** OneDrive caching and publishing delays can cause 5-30 second latencies
- **Stale File Detection:** Client detects stale connections even when server is actively writing packets
- **Unnecessary Overhead:** File I/O and cloud sync overhead for what is essentially a network data stream
- **Reliability Issues:** Dependent on third-party sync service availability and performance

### Proposed Solution
Leverage the existing L3VPN connection for direct socket-based communication:

#### Architecture Changes
1. **Server Component:**
   - Continue listening on UDP port 4992 for FlexRadio broadcasts
   - Add TCP server socket listening on configurable port (e.g., 5992)
   - Stream captured VITA-49 packets directly to connected clients
   - Maintain JSON format for compatibility but send over socket instead of file

2. **Client Component:**
   - Add TCP client socket to connect to remote server
   - Receive discovery packets in real-time over VPN connection
   - Rebroadcast to local network on UDP port 4992
   - Implement reconnection logic for connection failures

#### Configuration Changes
```ini
[SERVER]
Listen_Address = 0.0.0.0
Discovery_Port = 4992
Stream_Port = 5992              # NEW: Port for client connections
Max_Clients = 5                 # NEW: Maximum simultaneous clients
Stream_Mode = socket            # NEW: 'socket' or 'file'
Shared_File_Path = discovery.json  # Fallback mode

[CLIENT]
Server_Address = 192.168.1.100  # NEW: Server IP over VPN
Stream_Port = 5992              # NEW: Port to connect to
Connection_Mode = socket        # NEW: 'socket' or 'file'
Reconnect_Interval = 5.0        # NEW: Seconds between reconnection attempts
Shared_File_Path = discovery.json  # Fallback mode
```

#### Benefits
- **Real-time:** Sub-second latency instead of 5-30 seconds
- **Reliable:** Direct connection with immediate failure detection
- **Efficient:** No file I/O or cloud sync overhead
- **Scalable:** Support multiple clients from single server
- **Simpler:** No dependency on cloud storage services

#### Implementation Notes
- Use persistent TCP connection with keepalive
- Implement heartbeat mechanism for connection health monitoring
- Maintain file-based mode as fallback option
- Consider TLS/SSL for secure transmission over internet

---

## Priority 2: Network Health Checks and Diagnostics

### Problem Statement
Users struggle to troubleshoot connectivity issues without diagnostic tools. Common issues include:
- VPN not established or misconfigured
- Firewall blocking UDP port 4992
- FlexRadio unreachable from server location
- Incorrect network configuration

### Proposed Solution
Implement comprehensive startup health checks and ongoing monitoring:

#### Startup Diagnostics (Server)
1. **Network Interface Check:**
   - Verify binding to correct interface
   - Display all available network interfaces
   - Confirm UDP port 4992 can be bound

2. **FlexRadio Connectivity:**
   - Ping test to configured FlexRadio IP (if specified)
   - Listen for discovery broadcasts
   - Timeout warning if no packets received in 30 seconds

3. **Firewall Status:**
   - Verify UDP port 4992 is accessible
   - Test outbound connectivity to client (if in socket mode)

#### Startup Diagnostics (Client)
1. **VPN Connectivity Check:**
   - Ping test to server IP address
   - Verify VPN routes are active
   - Display local network configuration

2. **Server Reachability:**
   - TCP connection test to server stream port
   - File access test (if in file mode)
   - Latency measurement

3. **Port 4992 Accessibility:**
   - Verify UDP port 4992 can be bound locally
   - Test broadcast capability on local network
   - Check for port conflicts

4. **Firewall Validation:**
   - Request test packets from server (TCP and UDP)
   - Verify packets can be received
   - Display firewall recommendations if tests fail

#### Health Check Output Format
```
=== FlexRadio Discovery Proxy - Health Check ===
Mode: CLIENT
Time: 2026-01-26 14:30:00

[PASS] VPN Connection: 192.168.1.100 reachable (latency: 45ms)
[PASS] Server Connection: TCP port 5992 accessible
[PASS] Local Port 4992: Successfully bound
[PASS] Broadcast Capability: Enabled
[WARN] Firewall: UDP port 4992 may be filtered (no test packet received)
[PASS] Recent Discovery Packet: Received 2 seconds ago

Status: OPERATIONAL (1 warning)
```

#### Continuous Monitoring
- Periodic connection health checks (every 60 seconds)
- Log warnings when connectivity degrades
- Automatic recovery attempts
- Statistics tracking (packets received, latency, errors)

#### Configuration Changes
```ini
[DIAGNOSTICS]
Enable_Health_Checks = true
Startup_Tests = true
Periodic_Check_Interval = 60.0
Ping_Timeout = 5.0
Test_Server_IP = 192.168.1.100  # Server to test connectivity
Display_Interface_Info = true
```

#### Benefits
- **Faster Troubleshooting:** Immediate identification of configuration issues
- **User-Friendly:** Clear pass/fail/warn messages with recommendations
- **Proactive:** Detect problems before they impact operation
- **Educational:** Helps users understand network requirements

---

## Priority 3: Avalonia UI Application

### Problem Statement
Current command-line interface requires:
- Manual editing of configuration files
- Separate terminal windows for client and server
- External tools to view logs
- Technical knowledge to interpret packet data

### Proposed Solution
Create a modern cross-platform GUI application using Avalonia UI framework:

#### Features

##### 1. Configuration Management
- **Config Editor Tab:**
  - Form-based editor for all configuration parameters
  - Validation of IP addresses, ports, and file paths
  - Separate views for SERVER and CLIENT sections
  - Save/Load/Reset configuration options
  - Import settings from existing config.ini

##### 2. Mode Selection and Control
- **Mode Selector:**
  - Radio buttons: "Server Mode" / "Client Mode"
  - Auto-detection based on current config
  - Visual indication of active mode
  
- **Process Control:**
  - Start/Stop/Restart buttons
  - Process status indicator (Running/Stopped/Error)
  - Resource usage display (CPU, memory, network)
  - Auto-start option

##### 3. Health Check Dashboard
- **Network Status Panel:**
  - Visual indicators (green/yellow/red) for each health check
  - Real-time connectivity status
  - Latency graphs
  - Packet statistics
  
- **Manual Test Button:**
  - Run health checks on demand
  - Display detailed results in expandable panel
  - Export test results to file

##### 4. Log Viewer
- **Real-Time Log Tailing:**
  - Tabbed interface: Server Log / Client Log
  - Color-coded log levels (INFO/WARN/ERROR)
  - Auto-scroll option
  - Search/filter capability
  - Export logs to file
  - Log rotation display

##### 5. Packet Inspector
- **Discovery Packet Display:**
  - Real-time packet arrival indicator
  - Parsed payload display (key-value pairs)
  - Radio information card:
    - Model, Serial, Version
    - Nickname, Callsign
    - IP Address, Status
    - Available Clients/Panadapters/Slices
  - Raw packet hex viewer (collapsible)
  - Packet history (last 10 packets)
  - Timestamp for each packet

#### UI Layout (Mockup)
```
┌─────────────────────────────────────────────────────────────┐
│ FlexRadio Discovery Proxy v2.1                         [_][□][X] │
├─────────────────────────────────────────────────────────────┤
│ [Dashboard] [Configuration] [Logs] [Packets] [About]       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Mode: ○ Server  ● Client                                  │
│  Status: ● Running                                          │
│  [Start] [Stop] [Restart]                                   │
│                                                             │
│  ┌─ Health Check ────────────────────────────────────────┐ │
│  │ ✓ VPN Connection          Latency: 45ms               │ │
│  │ ✓ Server Reachable        Port 5992: Open             │ │
│  │ ✓ Local Port 4992         Bound successfully          │ │
│  │ ⚠ Firewall                UDP may be filtered         │ │
│  │                                                        │ │
│  │ [Run Tests]                                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─ Discovery Packet (2s ago) ───────────────────────────┐ │
│  │ Model: FLEX-6600          Serial: 3718-0522-6600-0003 │ │
│  │ Nickname: Lake6600        Callsign: WX7V              │ │
│  │ IP: 192.168.0.101         Version: 4.1.5.39794        │ │
│  │ Status: Available         Clients: 1/2                │ │
│  │ Panadapters: 3/4          Slices: 3/4                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─ Statistics ───────────────────────────────────────────┐ │
│  │ Packets Received: 1,247   Broadcast: 1,247            │ │
│  │ Errors: 0                 Uptime: 2h 15m              │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Technical Implementation
- **Framework:** Avalonia UI 11.x (cross-platform: Windows, macOS, Linux)
- **Language:** C# with .NET 8
- **Architecture:** MVVM pattern
- **Process Management:** Launch Python scripts as subprocesses
- **Log Parsing:** Tail log files using FileSystemWatcher
- **Packet Parsing:** Parse JSON discovery data
- **Configuration:** Read/write INI files using IniParser library

#### Project Structure
```
FlexRadio-Discovery-Proxy-UI/
├── FRSDiscoveryProxy.Desktop/
│   ├── ViewModels/
│   │   ├── MainViewModel.cs
│   │   ├── DashboardViewModel.cs
│   │   ├── ConfigViewModel.cs
│   │   ├── LogsViewModel.cs
│   │   └── PacketsViewModel.cs
│   ├── Views/
│   │   ├── MainWindow.axaml
│   │   ├── DashboardView.axaml
│   │   ├── ConfigView.axaml
│   │   ├── LogsView.axaml
│   │   └── PacketsView.axaml
│   ├── Models/
│   │   ├── DiscoveryPacket.cs
│   │   ├── HealthCheck.cs
│   │   └── Configuration.cs
│   ├── Services/
│   │   ├── ProcessManager.cs
│   │   ├── LogTailer.cs
│   │   ├── PacketParser.cs
│   │   └── HealthChecker.cs
│   └── Program.cs
├── Assets/
│   └── Icons/
└── README_UI.md
```

#### Benefits
- **User-Friendly:** No command-line knowledge required
- **Visual Feedback:** Clear indication of status and problems
- **Integrated:** All tools in one application
- **Professional:** Modern, polished user experience
- **Cross-Platform:** Works on Windows, macOS, and Linux

---

## Priority 4: MIT License and Attribution

### Problem Statement
Current project lacks formal licensing and attribution, which can cause:
- Uncertainty about usage rights
- Unclear support boundaries
- Missing recognition for author
- Potential confusion about official FlexRadio support

### Proposed Solution
Add MIT License with proper attribution and disclaimers:

#### LICENSE File
Create standard MIT License with:
- Copyright © 2026 Chris L White (WX7V)
- Permission grants for use, modification, distribution
- Warranty disclaimer
- Liability limitations

#### README Additions
Add prominent section in all README files:

```markdown
## License and Attribution

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Copyright © 2026 Chris L White (WX7V)**

### Disclaimer

**This software is NOT officially supported by FlexRadio Systems, its employees, or its help desk.**

This is an independent, community-developed tool created to solve specific networking challenges when accessing FlexRadio transceivers over VPN or remote connections. While it follows the FlexRadio Discovery Protocol specifications, it is not endorsed, maintained, or supported by FlexRadio Systems.

For official FlexRadio support and products, please visit:
- Website: https://www.flexradio.com
- Help Desk: https://helpdesk.flexradio.com

### Acknowledgments

Thanks to the FlexRadio community and the VITA-49 standards organization for their excellent documentation.
```

#### Source File Headers
Add header to all Python source files:

```python
#!/usr/bin/env python3
"""
FlexRadio Discovery Proxy - [Component Name]
Copyright (c) 2026 Chris L White (WX7V)

Licensed under the MIT License - see LICENSE file for details

This software is NOT officially supported by FlexRadio Systems.
"""
```

#### Documentation Updates
Update all documentation files:
- Add license section to README.md, README_v2.md
- Include disclaimer in QUICKSTART_v2.md
- Add attribution to MIGRATION_GUIDE_v1_to_v2.md
- Update release notes to include license information

#### Benefits
- **Legal Clarity:** Clear usage rights for all users
- **Attribution:** Recognition for author's work
- **Support Boundaries:** Clear disclaimer about official support
- **Community:** Encourages contributions under known terms
- **Professional:** Industry-standard open-source licensing

---

## Implementation Timeline

### Phase 1: Priority 4 (Immediate) ✅ COMPLETED
- **Estimated Time:** 1-2 hours
- **Actual Time:** 1 hour
- **Completion Date:** 2026-01-26
- ✅ Add MIT License file
- ✅ Update all documentation
- ✅ Add source file headers
- ✅ Create progress tracker

### Phase 2: Priority 2 (Short-term) ✅ COMPLETED
- **Estimated Time:** 1-2 weeks
- **Actual Time:** 1 day
- **Completion Date:** 2026-01-26
- ✅ Implement health check framework
- ✅ Add startup diagnostics
- ✅ Create continuous monitoring
- ✅ Testing across platforms

### Phase 3: Priority 1 (Medium-term) ✅ COMPLETED
- **Estimated Time:** 2-3 weeks
- **Actual Time:** 1 day
- **Completion Date:** 2026-01-27
- ✅ Design socket protocol
- ✅ Implement server streaming
- ✅ Implement client reception
- ✅ Maintain file-based fallback
- ✅ Create comprehensive documentation

### Phase 4: Priority 3 (Long-term)
- **Estimated Time:** 4-6 weeks
- **Status:** Planned
- Design Avalonia UI mockups
- Implement MVVM architecture
- Create all views and view models
- Process management implementation
- Testing and polish

---

## Version Numbering

Following semantic versioning:
- **v2.1.0** - Priority 2 (Health Checks) + Priority 4 (License) ✅ Released
- **v2.2.0** - Priority 1 (Socket Communication) ✅ Released
- **v3.0.0** - Priority 3 (Avalonia UI) - Major version due to new component (Planned)

---

## Compatibility Considerations

- Maintain backward compatibility with v2.0 configuration files
- Support both file-based and socket-based modes simultaneously
- CLI scripts remain functional even with GUI available
- Ensure health checks don't interfere with normal operation
- Document migration paths for each version

---

## Testing Requirements

### Priority 1 Testing
- Socket connection reliability over VPN
- Reconnection logic under various failure scenarios
- Multi-client support
- Performance comparison vs file-based

### Priority 2 Testing
- Health checks across Windows, macOS, Linux
- Various network configurations (VPN, NAT, direct)
- Firewall detection accuracy
- False positive/negative rates

### Priority 3 Testing
- UI responsiveness with high packet rates
- Log tailing with large log files
- Configuration validation
- Cross-platform UI consistency

---

## Community Feedback

These enhancements are based on initial deployment experience. Community feedback is welcome:
- Report issues on GitHub
- Suggest additional features
- Share deployment scenarios
- Contribute code improvements

**Contact:** Chris L White (WX7V)

---

*Document Version: 2.0*  
*Last Updated: 2026-01-27*  
*Status: Priority 1, 2, and 4 Completed - Priority 3 Planned*
