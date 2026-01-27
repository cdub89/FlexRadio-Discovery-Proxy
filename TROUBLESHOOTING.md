# FlexRadio Discovery Proxy - Troubleshooting Guide

**Version:** 2.2.0+  
**Last Updated:** 2026-01-27

This is the **complete troubleshooting guide** for the FlexRadio Discovery Proxy. All diagnostic procedures, common issues, and solutions are documented here.

---

## Table of Contents

1. [Quick Diagnosis](#quick-diagnosis)
2. [Common Issues](#common-issues)
3. [Debug Mode](#debug-mode)
4. [Diagnostic Tools](#diagnostic-tools)
5. [Socket Mode Issues](#socket-mode-issues)
6. [File Mode Issues](#file-mode-issues)
7. [Network Issues](#network-issues)
8. [Performance Issues](#performance-issues)
9. [Configuration Reference](#configuration-reference)
10. [Getting Help](#getting-help)

---

## Quick Diagnosis

### Step 1: Enable Debug Mode

Edit `config-v2.ini`:
```ini
[DIAGNOSTICS]
Debug_Logging = true
```

Restart both server and client. Check the log files for detailed packet flow information.

### Step 2: Check Health Checks

Both server and client run health checks at startup. Look for:

**✅ All PASS** = Configuration is correct  
**⚠️ WARN** = May cause issues, investigate  
**❌ FAIL** = Must fix before proceeding

### Step 3: Verify Mode Configuration

**Server** (`config-v2.ini`):
```ini
[SERVER]
Stream_Mode = socket    # or 'file'
```

**Client** (`config-v2.ini`):
```ini
[CLIENT]
Connection_Mode = socket    # or 'file'  - Must match server mode!
```

### Step 4: Run Diagnostic Tool

```bash
python diagnose_connection.py
```

This will test the connection and show if packets are flowing.

---

## Common Issues

### Issue 1: Client Not Receiving Broadcasts

**Symptoms:**
- Client connects successfully
- Server reports receiving packets from radio
- Client receives 0 broadcasts

**Debug Steps:**

1. **Enable debug logging** (see above)

2. **Check server log** (`discovery-server.log`):
   ```
   DEBUG - Broadcasting packet to 1 client(s)
   DEBUG - Send to ('192.168.1.200', 54321): success
   ```
   If you see this, server IS sending packets.

3. **Check client log** (`discovery-client.log`):
   ```
   DEBUG - Received 1234 bytes from server
   DEBUG - Buffer now contains 1234 characters
   DEBUG - Parsing JSON line (1230 chars)
   DEBUG - Successfully parsed JSON packet
   ```
   If you DON'T see "Received X bytes", client isn't getting data.

**Common Causes:**

| Cause | Solution |
|-------|----------|
| Server in file mode, client in socket mode | Fix config to match |
| Firewall blocking between server/client | Allow TCP port 5992 |
| Network timeout/packet loss | Check network quality |
| Client disconnected | Check connection status |

---

### Issue 2: Socket Mode - "Connection Refused"

**Error:**
```
[X] [FAIL]   Server TCP Connectivity        Connection refused by 192.168.1.100:5992
```

**Solutions:**

1. **Server not running**
   - Start the server script
   - Check server didn't crash (look at log)

2. **Wrong port**
   - Verify `Stream_Port` matches in both configs
   - Default is 5992

3. **Firewall blocking**
   ```bash
   # Windows (run as Administrator)
   netsh advfirewall firewall add rule name="FlexRadio Discovery" dir=in action=allow protocol=TCP localport=5992
   
   # Linux
   sudo ufw allow 5992/tcp
   ```

4. **Server binding to wrong interface**
   - Set `Listen_Address = 0.0.0.0` in server config

---

### Issue 3: Radio Not Broadcasting

**Symptoms:**
- Server and client both running
- Connection successful
- No packets appear on server

**Verify Radio:**

1. **Ping the radio**
   ```bash
   ping <radio-ip>
   ```

2. **Check radio is powered on** and network cable connected

3. **Restart radio** if needed

4. **Verify server on same network** as radio
   - Discovery packets are Layer 2 broadcasts
   - Won't cross routers unless multicast routing configured

5. **Capture packets** to verify radio is broadcasting:
   ```bash
   # On server machine
   tcpdump -i any udp port 4992
   # or
   tcpdump -i any -X udp port 4992
   ```
   Should see packets every 2-5 seconds from radio IP.

---

### Issue 4: Version Mismatch

**Error:**
```
[X] [FAIL]   Version & Configuration        Socket mode requires v2.2.0+ (running v2.1.0)
```

**Solution:**

**Option A: Upgrade**
1. Download latest code (v2.2.0+)
2. Stop running scripts
3. Replace Python files
4. Restart scripts

**Option B: Switch to File Mode**
Edit `config-v2.ini` on BOTH machines:
```ini
[SERVER]
Stream_Mode = file

[CLIENT]
Connection_Mode = file
```

---

## Debug Mode

### Enabling Debug Logging

**Edit `config-v2.ini`:**
```ini
[DIAGNOSTICS]
Debug_Logging = true
```

**Restart both server and client.**

### What Debug Mode Shows

**Server Log (`discovery-server.log`):**
```
DEBUG - Broadcasting packet to 1 client(s)
DEBUG - Send to ('192.168.1.200', 54321): success
DEBUG - Sent 1234 bytes to ('192.168.1.200', 54321) (packet #1)
```

**Client Log (`discovery-client.log`):**
```
DEBUG - Received 1234 bytes from server
DEBUG - Buffer now contains 1234 characters
DEBUG - Parsing JSON line (1230 chars)
DEBUG - Successfully parsed JSON packet
```

### Interpreting Debug Logs

**Normal Operation:**
```
[Server]
DEBUG - Broadcasting packet to 1 client(s)
DEBUG - Send to X: success
DEBUG - Sent 1234 bytes

[Client]
DEBUG - Received 1234 bytes
DEBUG - Successfully parsed JSON packet
```

**Server sending but client not receiving:**
```
[Server]
DEBUG - Broadcasting packet to 1 client(s)
DEBUG - Send to X: success

[Client]
[No "Received X bytes" message]
```
**→ Network/firewall issue between server and client**

**Client receiving but not parsing:**
```
[Client]
DEBUG - Received 1234 bytes
DEBUG - Parsing JSON line (1230 chars)
ERROR - JSON decode error: ...
```
**→ Data corruption or protocol mismatch**

---

## Diagnostic Tools

### Tool 1: Connection Diagnostic

**Purpose:** Test TCP connection and packet reception

**Usage:**
```bash
python diagnose_connection.py
# or
python diagnose_connection.py <server-ip> <port>
```

**Example:**
```bash
python diagnose_connection.py 192.168.1.22 5992
```

**Output:**
```
Testing connection to 192.168.1.22:5992...
✓ Connection successful! (latency: 15ms)

Listening for packets from server...

10:15:34 - Packet #1 received:
  Radio: FLEX-6600 (Lake6600)
  IP: 192.168.1.101 | Status: Available

======================================================================
✓ SUCCESS: Received 1 packet(s) from server
======================================================================
```

---

### Tool 2: Health Check Test

**Purpose:** Verify diagnostic system is working

**Usage:**
```bash
python test_health_checks.py
```

**Expected:**
```
======================================================================
TEST SUMMARY
======================================================================
Total Tests: 3
Passed: 3
Failed: 0
======================================================================
[+] ALL TESTS PASSED!
```

---

## Socket Mode Issues

### Configuration Requirements

**Server (`config-v2.ini`):**
```ini
[SERVER]
Stream_Mode = socket
Listen_Address = 0.0.0.0
Discovery_Port = 4992
Stream_Port = 5992
Max_Clients = 5
```

**Client (`config-v2.ini`):**
```ini
[CLIENT]
Connection_Mode = socket
Server_Address = 192.168.1.100    # IP of server machine
Stream_Port = 5992                 # Must match server
Reconnect_Interval = 5.0
```

### Health Check Indicators

**Startup Health Check:**
```
[+] [PASS]   Version & Configuration        v2.2.0 - Socket mode supported
[+] [PASS]   Network Interfaces             Found X network interface(s)
[+] [PASS]   UDP Port 4992                  Port 4992 is available
[+] [PASS]   Stream Port 5992               Port 5992 is available
```

**Post-Startup Verification:**
```
[+] [PASS]   TCP Listener Check             Server is listening on port 5992
                                          Connection latency: 2ms

✓ Server is ready to accept client connections
```

### Connection Messages

**Server when client connects:**
```
2026-01-27 10:15:32 - Client connected: ('192.168.1.200', 54321) (Total: 1)
  Waiting for discovery packets to stream...
```

**Server when streaming packets:**
```
10:15:34 - Packet #1 from 192.168.1.101
  Radio: FLEX-6600 (Lake6600)
  → Streamed to 1 client(s)
```

**Client when connected:**
```
10:15:32 - ✓ Connected to server
  Listening for discovery packets...
```

**Client when receiving:**
```
10:15:34 - Radio discovered:
  FLEX-6600 (Lake6600)
  Callsign: WX7V | IP: 192.168.1.101
  Status: Available | Version: 4.1.5.39794

10:15:34 - ✓ Started broadcasting discovery packets
```

### Common Socket Mode Errors

| Error | Meaning | Solution |
|-------|---------|----------|
| Connection refused | Server not listening | Start server, check firewall |
| Connection timeout | Can't reach server | Check network, VPN, routing |
| Server closed connection | Server crashed/stopped | Check server log for errors |
| No packets received | Radio not broadcasting | Verify radio on network |

---

## File Mode Issues

### Configuration Requirements

**Server (`config-v2.ini`):**
```ini
[SERVER]
Stream_Mode = file
Shared_File_Path = .\discovery.json    # or network share path
Update_Interval = 2.0
```

**Client (`config-v2.ini`):**
```ini
[CLIENT]
Connection_Mode = file
Shared_File_Path = .\discovery.json    # Must match server path
Check_Interval = 3.0
Max_File_Age = 15.0
```

### Common File Mode Issues

**Issue:** File not found
```
[!] [WARN]   File Read Permission           Discovery file not yet created
```
**Solution:** Server hasn't received packets yet, wait for radio to broadcast

**Issue:** Permission denied
```
[X] [FAIL]   File Write Permission          Permission denied
```
**Solution:** Check file/directory permissions, run with appropriate privileges

**Issue:** Stale file
```
⚠ Discovery file is stale (25.3s old) - Radio may be offline
```
**Solution:** Radio stopped broadcasting, check radio status

---

## Network Issues

### Firewall Configuration

#### Windows Firewall

**Server (inbound rule):**
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "FlexRadio Discovery Server" `
  -Direction Inbound -Protocol TCP -LocalPort 5992 -Action Allow

New-NetFirewallRule -DisplayName "FlexRadio Discovery UDP" `
  -Direction Inbound -Protocol UDP -LocalPort 4992 -Action Allow
```

**Client (outbound usually allowed by default):**
```powershell
New-NetFirewallRule -DisplayName "FlexRadio Discovery Client" `
  -Direction Outbound -Protocol TCP -RemotePort 5992 -Action Allow
```

#### Linux Firewall (ufw)

```bash
# Server
sudo ufw allow 5992/tcp
sudo ufw allow 4992/udp

# Client (outbound usually allowed)
# No action needed typically
```

#### Linux Firewall (firewalld)

```bash
# Server
sudo firewall-cmd --permanent --add-port=5992/tcp
sudo firewall-cmd --permanent --add-port=4992/udp
sudo firewall-cmd --reload
```

### Network Testing

**Test 1: Ping server**
```bash
ping <server-ip>
```

**Test 2: Check port is open**
```bash
# Windows
Test-NetConnection -ComputerName <server-ip> -Port 5992

# Linux/Mac
nc -zv <server-ip> 5992
# or
telnet <server-ip> 5992
```

**Test 3: Check what's listening**
```bash
# Windows
netstat -an | findstr 5992

# Linux/Mac
netstat -an | grep 5992
# or
ss -tln | grep 5992
```

**Expected:** `0.0.0.0:5992` or `*:5992` in LISTEN state

---

## Performance Issues

### High Latency

**Symptoms:**
- Health checks show >100ms latency
- Packets arrive slowly

**Solutions:**
1. Check network quality (ping times)
2. Verify VPN performance
3. Check CPU usage on both machines
4. Consider file mode if latency consistently high

### Frequent Disconnections

**Symptoms:**
- Client shows "Connection reset"
- Frequent reconnections

**Solutions:**
1. Check network stability
2. Check VPN stability
3. Look for firewall with connection timeout
4. Increase `Reconnect_Interval` in client config
5. Check server isn't hitting `Max_Clients` limit

### Packet Loss

**Symptoms:**
- Client receives some but not all packets
- Gaps in packet sequence

**Solutions:**
1. Enable debug logging
2. Check for "Send to X: FAILED" in server log
3. Check network quality
4. Reduce `Update_Interval` on server
5. Check for MTU issues on network

---

## Configuration Reference

### Modes Comparison

| Feature | Socket Mode | File Mode |
|---------|------------|-----------|
| Latency | <1 second | 5-30 seconds |
| Setup | Complex | Simple |
| Firewall | TCP port required | Not required |
| VPN | Required | Optional (cloud sync) |
| Network failure | Auto-reconnect | Works if sync continues |
| Multiple clients | Supported | Need multiple servers |
| Version required | v2.2.0+ | v2.0.0+ |

### Port Reference

| Port | Protocol | Purpose |
|------|----------|---------|
| 4992 | UDP | FlexRadio discovery broadcasts |
| 5992 | TCP | Discovery packet streaming (socket mode) |

### Configuration Validation

**Check your config matches:**

**Socket Mode:**
```ini
[SERVER]
Stream_Mode = socket
Stream_Port = 5992

[CLIENT]
Connection_Mode = socket
Stream_Port = 5992        # Must match server
Server_Address = X.X.X.X  # Server IP
```

**File Mode:**
```ini
[SERVER]
Stream_Mode = file
Shared_File_Path = <path>

[CLIENT]
Connection_Mode = file
Shared_File_Path = <same path as server>
```

---

## Getting Help

### Information to Gather

When asking for help, provide:

1. **Version information**
   - From console: "Server v2.2.0 started..."
   - Or from script: `grep "__version__" FRS-Discovery-Server-v2.py`

2. **Health check results**
   - Copy full startup health check output
   - Note any FAIL or WARN results

3. **Configuration**
   - `Stream_Mode` / `Connection_Mode`
   - Network topology (same network, VPN, etc.)

4. **Log excerpts**
   - Last 20 lines of both logs
   - Any ERROR or WARNING messages
   - If debug enabled, relevant DEBUG messages

5. **Debug log output**
   - Enable debug mode
   - Run for 30-60 seconds
   - Capture both server and client logs

6. **Network tests**
   - Can ping between machines?
   - Can telnet to port 5992?
   - Results of `diagnose_connection.py`?

### Debug Command Sequence

```bash
# 1. Enable debug mode
# Edit config-v2.ini: Debug_Logging = true

# 2. Start server
python FRS-Discovery-Server-v2.py

# 3. In another terminal, start client
python FRS-Discovery-Client-v2.py

# 4. Wait 30-60 seconds

# 5. Stop both (Ctrl+C)

# 6. Examine logs
# Windows:
type discovery-server.log | findstr DEBUG
type discovery-client.log | findstr DEBUG

# Linux/Mac:
grep DEBUG discovery-server.log
grep DEBUG discovery-client.log
```

### Support Channels

- **GitHub Issues:** https://github.com/cdub89/FlexRadio-Discovery-Proxy/issues
- **Documentation:** Check README_v2.md and this guide

---

## Quick Reference Checklist

Use this when troubleshooting:

**Pre-Flight:**
- [ ] Running v2.2.0 or later (for socket mode)
- [ ] config-v2.ini exists and is valid
- [ ] Stream_Mode/Connection_Mode match
- [ ] Ports match in both configs

**Server:**
- [ ] Server script is running
- [ ] Health checks show PASS
- [ ] Post-startup verification shows "ready"
- [ ] Firewall allows TCP 5992 (socket) or UDP 4992
- [ ] Server on same network as radio
- [ ] Server log shows packet reception

**Client:**
- [ ] Client script is running
- [ ] Health checks show PASS
- [ ] Can connect to server (socket mode)
- [ ] Can read file (file mode)
- [ ] Client log shows connection/file access

**Network:**
- [ ] Can ping between server and client
- [ ] Can telnet to server:5992 (socket mode)
- [ ] VPN is connected (if remote)
- [ ] No firewall blocking between machines
- [ ] Latency is acceptable (<100ms)

**Radio:**
- [ ] Radio is powered on
- [ ] Radio on network
- [ ] Can ping radio from server
- [ ] Radio broadcasting discovery (tcpdump shows packets)

---

## Summary

**Most Common Issues:**

1. **Config mismatch** - Server and client in different modes
2. **Firewall blocking** - TCP port 5992 not allowed
3. **Wrong server IP** - Client connecting to wrong address
4. **Radio not broadcasting** - Radio offline or wrong network
5. **Version mismatch** - Old version with socket config

**First Steps:**
1. Enable debug logging
2. Check health checks
3. Run diagnostic tool
4. Verify radio is broadcasting

**Remember:** The enhanced diagnostics will tell you exactly what's wrong. If all health checks pass but client receives nothing, the radio isn't broadcasting or the server isn't receiving packets.

---

**Document Version:** 3.0 (Consolidated)  
**Date:** 2026-01-27  
**Replaces:** All previous troubleshooting documents
