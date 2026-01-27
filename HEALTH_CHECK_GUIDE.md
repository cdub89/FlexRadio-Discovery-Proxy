# FlexRadio Discovery Proxy - Health Check Guide

**Version:** 2.1.0  
**Feature:** Network Health Checks and Diagnostics

---

## Overview

Version 2.1.0 introduces comprehensive health check and diagnostic capabilities to help troubleshoot connectivity issues and ensure proper configuration. The system automatically validates network settings, port availability, connectivity, and permissions at startup and periodically during operation.

---

## Key Features

### 🔍 **Automatic Diagnostics**
- **Startup Health Checks:** Validate configuration before operation begins
- **Periodic Monitoring:** Continuous health monitoring every 60 seconds (configurable)
- **Clear Status Indicators:** Pass/Warn/Fail status for each check
- **Detailed Logging:** All health check results logged for troubleshooting

### 📊 **Server Checks**
- Network interface detection and validation
- UDP port 4992 availability verification
- FlexRadio reachability testing (ping)
- File write permission validation
- Discovery packet reception monitoring

### 📡 **Client Checks**
- Network interface detection
- UDP port 4992 availability verification
- Broadcast capability validation
- VPN/Server connectivity testing (ping)
- File read permission validation
- Stale file detection

---

## Configuration

All health check settings are in the `[DIAGNOSTICS]` section of `config.ini`:

```ini
[DIAGNOSTICS]
# Enable health checks at startup and during operation
Enable_Health_Checks = true

# Run comprehensive diagnostics at startup
Startup_Tests = true

# Interval for periodic health checks during operation (seconds)
# Set to 0 to disable periodic checks
Periodic_Check_Interval = 60.0

# Timeout for ping tests (seconds)
Ping_Timeout = 5.0

# Display detailed network interface information at startup
Display_Interface_Info = true

# For CLIENT: IP address of the server to test connectivity
# Should be the IP of the machine running FRS-Discovery-Server.py
# Leave empty to skip server connectivity tests
Test_Server_IP = 

# For SERVER: IP address of the FlexRadio to monitor
# Leave empty to auto-detect from discovery packets
Test_Radio_IP = 
```

---

## Startup Health Checks

When you start the server or client, health checks run automatically:

### Example Output (Server)

```
======================================================================
FlexRadio Discovery Server v2.1.0
======================================================================

Server Configuration:
  Listen Address: 0.0.0.0
  Discovery Port: 4992
  Shared File: ./discovery.json
  Update Interval: 2.0s

======================================================================
Startup Health Check
======================================================================
[+] [PASS]   Network Interfaces             Found 1 network interface(s)
                                          Hostname: radio-server
                                          Addresses: 192.168.1.100
[+] [PASS]   UDP Port 4992                  Port 4992 is available
[!] [WARN]   FlexRadio Connectivity         No FlexRadio IP configured
[+] [PASS]   File Write Permission          Can write to .

----------------------------------------------------------------------
Status: 3 passed, 1 warning(s) (Total: 4)
Overall: OPERATIONAL (with warnings)
======================================================================

Listening for FlexRadio discovery packets...
```

### Example Output (Client)

```
======================================================================
FlexRadio Discovery Client v2.1.0
======================================================================

Client Configuration:
  Shared File: ./discovery.json
  Broadcast Address: 255.255.255.255
  Discovery Port: 4992
  Check Interval: 3.0s
  Max File Age: 15.0s

======================================================================
Startup Health Check
======================================================================
[+] [PASS]   Network Interfaces             Found 1 network interface(s)
                                          Hostname: my-laptop
                                          Addresses: 10.0.0.5
[+] [PASS]   UDP Port 4992                  Port 4992 is available
[+] [PASS]   Broadcast Capability           Broadcast is enabled
[+] [PASS]   VPN/Server Connectivity        192.168.1.100 is reachable
                                          Latency: 45ms
[!] [WARN]   File Read Permission           Discovery file not yet created
                                          File: ./discovery.json
                                          Waiting for server to create it

----------------------------------------------------------------------
Status: 4 passed, 1 warning(s) (Total: 5)
Overall: OPERATIONAL (with warnings)
======================================================================

Monitoring for discovery packets...
```

---

## Status Indicators

### `[+] [PASS]` - Passed
Everything is working correctly. No action needed.

### `[!] [WARN]` - Warning  
Check passed but with minor issues or optional features not configured. System can still operate but performance may be degraded.

**Common Warnings:**
- FlexRadio/Server IP not configured (optional)
- Discovery file not yet created (normal at startup)
- Port already in use (may be this script running)

### `[X] [FAIL]` - Failed
Critical issue detected. System may not operate correctly.

**Common Failures:**
- Cannot bind to UDP port 4992
- Network interface not available
- File permission denied
- Host unreachable

### `[-] [SKIP]` - Skipped
Check was skipped because prerequisites not met or feature not configured.

---

## Periodic Health Checks

During operation, the system performs health checks every 60 seconds (configurable). Results are displayed and logged:

```
14:30:00 - Running periodic health check...

======================================================================
Periodic Health Check
======================================================================
[+] [PASS]   Network Interfaces             Found 1 network interface(s)
[+] [PASS]   UDP Port 4992                  Port 4992 is available
[+] [PASS]   Broadcast Capability           Broadcast is enabled
[+] [PASS]   VPN/Server Connectivity        192.168.1.100 is reachable
                                          Latency: 47ms
[+] [PASS]   File Read Permission           Can read discovery file

----------------------------------------------------------------------
Status: 5 passed (Total: 5)
Overall: OPERATIONAL
======================================================================
```

To disable periodic checks:
```ini
Periodic_Check_Interval = 0
```

---

## Troubleshooting Guide

### Problem: "UDP Port 4992 - Cannot bind to port 4992"

**Cause:** Another application is using port 4992.

**Solutions:**
1. **Check if script already running:**
   ```
   Windows: netstat -an | findstr :4992
   Linux:   netstat -tulpn | grep 4992
   ```

2. **Stop conflicting applications:**
   - Close other FlexRadio tools
   - Stop other instances of this script
   - Check for SmartSDR running locally

3. **Change port (not recommended):**
   - Modify `Discovery_Port` in config.ini
   - Note: SmartSDR expects port 4992

### Problem: "VPN/Server Connectivity - Host is not reachable"

**Cause:** VPN not connected or server IP incorrect.

**Solutions:**
1. **Verify VPN connection:**
   ```
   ping [server_ip]
   ```

2. **Check VPN routing:**
   - Ensure VPN tunnel is active
   - Verify routing table includes server network
   - Check VPN client logs

3. **Verify server IP:**
   - Confirm `Test_Server_IP` in config.ini
   - Ensure server script is running
   - Check firewall rules

### Problem: "File Write/Read Permission - Permission denied"

**Cause:** Insufficient permissions for shared file location.

**Solutions:**
1. **Check file permissions:**
   ```
   Windows: Right-click → Properties → Security
   Linux:   ls -l [filepath]
   ```

2. **Verify network share access:**
   - Confirm share is mounted
   - Test write/read access manually
   - Check network credentials

3. **Change file location:**
   - Use local path for testing: `./discovery.json`
   - Update `Shared_File_Path` in config.ini

### Problem: "Network Interfaces - No non-loopback interfaces found"

**Cause:** Network adapter disabled or misconfigured.

**Solutions:**
1. **Check network adapters:**
   ```
   Windows: ipconfig
   Linux:   ip addr show
   ```

2. **Enable network adapter:**
   - Windows: Network Connections → Enable adapter
   - Linux: sudo ip link set [interface] up

3. **Verify network configuration:**
   - Ensure adapter has IP address
   - Check DHCP or static IP settings

### Problem: "Broadcast Capability - Cannot enable broadcast"

**Cause:** Network adapter doesn't support broadcast or firewall blocking.

**Solutions:**
1. **Check Windows Firewall:**
   - Allow UDP outbound on all ports
   - Allow Python/script through firewall
   - Create specific rule for port 4992

2. **Verify network settings:**
   - Ensure subnet mask is correct
   - Check if on isolated network
   - Test on different network adapter

---

## Advanced Configuration

### Testing Specific IPs

To test connectivity to specific hosts, configure the test IPs:

**Server Configuration (test FlexRadio):**
```ini
[DIAGNOSTICS]
Test_Radio_IP = 192.168.0.101
```

**Client Configuration (test server over VPN):**
```ini
[DIAGNOSTICS]
Test_Server_IP = 192.168.1.100
```

### Customizing Check Intervals

Adjust how often periodic checks run:

```ini
# Check every 30 seconds (faster)
Periodic_Check_Interval = 30.0

# Check every 5 minutes (less frequent)
Periodic_Check_Interval = 300.0

# Disable periodic checks
Periodic_Check_Interval = 0
```

### Adjusting Ping Timeout

For slow VPN connections, increase ping timeout:

```ini
# Wait up to 10 seconds for ping response
Ping_Timeout = 10.0
```

### Disabling Health Checks

To disable all health checks:

```ini
[DIAGNOSTICS]
Enable_Health_Checks = false
```

**Note:** Not recommended. Health checks help identify problems early.

---

## Logging

All health check results are logged to:
- **Server:** `discovery-server.log`
- **Client:** `discovery-client.log`

Example log entries:
```
2026-01-26 14:25:30 - INFO - Health check: 5 passed (Total: 5) - Overall: OPERATIONAL
2026-01-26 14:26:30 - INFO - Health check: 4 passed, 1 warning(s) (Total: 5) - Overall: OPERATIONAL (with warnings)
2026-01-26 14:27:30 - WARNING - Health check: 3 passed, 2 failed (Total: 5) - Overall: DEGRADED - Some checks failed
```

---

## Best Practices

### 1. Always Run Startup Tests
```ini
Startup_Tests = true
```
Catches configuration issues before operation begins.

### 2. Configure Test IPs
Set `Test_Server_IP` (client) and `Test_Radio_IP` (server) for connectivity validation.

### 3. Monitor Periodic Checks
Watch for status changes during operation. Warnings may indicate:
- VPN connection degradation
- Network congestion
- File sync delays

### 4. Check Logs After Problems
Review log files for detailed error information and trends.

### 5. Use Display Interface Info
```ini
Display_Interface_Info = true
```
Helps identify which network adapter is being used.

---

## Integration with Existing Setup

Health checks are **non-invasive** and **backward compatible**:
- ✅ No changes required to existing config files
- ✅ Works with v2.0 configurations automatically
- ✅ Can be disabled without affecting operation
- ✅ Adds ~1 second to startup time
- ✅ Minimal impact on performance

---

## Examples

### Example 1: Home Lab Setup

**Scenario:** Client and server on same local network.

**Client config.ini:**
```ini
[DIAGNOSTICS]
Enable_Health_Checks = true
Test_Server_IP = 192.168.1.100
```

**Expected startup:**
```
[+] [PASS]   Network Interfaces             Found 1 network interface(s)
[+] [PASS]   UDP Port 4992                  Port 4992 is available
[+] [PASS]   Broadcast Capability           Broadcast is enabled
[+] [PASS]   VPN/Server Connectivity        192.168.1.100 is reachable
                                          Latency: 2ms
[+] [PASS]   File Read Permission           Can read discovery file
```

### Example 2: Remote VPN Access

**Scenario:** Client connects over WireGuard VPN.

**Client config.ini:**
```ini
[DIAGNOSTICS]
Enable_Health_Checks = true
Test_Server_IP = 10.0.0.1
Ping_Timeout = 10.0
```

**Expected startup:**
```
[+] [PASS]   Network Interfaces             Found 2 network interface(s)
[+] [PASS]   UDP Port 4992                  Port 4992 is available
[+] [PASS]   Broadcast Capability           Broadcast is enabled
[+] [PASS]   VPN/Server Connectivity        10.0.0.1 is reachable
                                          Latency: 85ms
[!] [WARN]   File Read Permission           Discovery file not yet created
```

### Example 3: Cloud Storage Setup

**Scenario:** Server and client use OneDrive for file sharing.

**Server config.ini:**
```ini
[DIAGNOSTICS]
Enable_Health_Checks = true
Test_Radio_IP = 192.168.0.101
```

**Expected startup:**
```
[+] [PASS]   Network Interfaces             Found 1 network interface(s)
[+] [PASS]   UDP Port 4992                  Port 4992 is available
[+] [PASS]   FlexRadio Connectivity         192.168.0.101 is reachable
                                          Latency: 3ms
[+] [PASS]   File Write Permission          Can write to C:\Users\...\OneDrive\FlexRadio
```

---

## FAQ

**Q: Do I need to configure Test_Server_IP and Test_Radio_IP?**  
A: No, they're optional. But configuring them enables connectivity testing which helps troubleshoot VPN issues.

**Q: Will health checks interfere with normal operation?**  
A: No. Health checks run in parallel and don't block packet processing.

**Q: Can I disable health checks?**  
A: Yes, set `Enable_Health_Checks = false` in config.ini. But it's recommended to keep them enabled.

**Q: What if I see warnings at startup?**  
A: Warnings are informational. The system can still operate. Review the message to see if action is needed.

**Q: How often should I run periodic checks?**  
A: Default is 60 seconds. Increase for less frequent checks, decrease for more responsive monitoring.

**Q: Do health checks work with v1.x scripts?**  
A: No, health checks are only available in v2.1.0 and later.

---

## Related Documentation

- **[README_v2.md](README_v2.md)** - Complete v2.0 documentation
- **[QUICKSTART_v2.md](QUICKSTART_v2.md)** - Quick setup guide
- **[config.ini](config.ini)** - Configuration file with DIAGNOSTICS section
- **[RELEASE_NOTES_v2.1.0.md](RELEASE_NOTES_v2.1.0.md)** - v2.1.0 release notes

---

**Version:** 2.1.0  
**Last Updated:** 2026-01-26  
**Author:** Chris L White (WX7V)

---

**73 de WX7V**
