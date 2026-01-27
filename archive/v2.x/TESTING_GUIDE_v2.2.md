# FlexRadio Discovery Proxy v2.2.0 - Testing Guide

**Version:** 2.2.0  
**Date:** January 27, 2026  
**Purpose:** Quick testing guide for socket mode implementation

---

## Quick Test - Socket Mode

### Prerequisites
- FlexRadio on local network at server location
- L3VPN connection between server and client locations
- Python 3.x installed on both machines
- Firewall allows TCP port 5992

---

## Step 1: Configure for Socket Mode

### On Server Machine (Remote Location)

Edit `config-v2.ini`:

```ini
[SERVER]
Listen_Address = 0.0.0.0
Discovery_Port = 4992
Stream_Mode = socket          # ← Set to socket
Stream_Port = 5992            # ← TCP port for clients
Max_Clients = 5
```

### On Client Machine (Local PC)

Edit `config-v2.ini`:

```ini
[CLIENT]
Connection_Mode = socket      # ← Set to socket
Server_Address = <VPN_IP_OF_SERVER>  # ← Your server's VPN IP
Stream_Port = 5992            # ← Must match server
Reconnect_Interval = 5.0
Broadcast_Address = 255.255.255.255
Discovery_Port = 4992
```

---

## Step 2: Start Server

On server machine:

```powershell
cd C:\github\FlexRadio-Discovery-Proxy
python FRS-Discovery-Server-v2.py
```

### Expected Output:
```
======================================================================
FlexRadio Discovery Server v2.2.0
======================================================================

Server Configuration:
  Listen Address: 0.0.0.0
  Discovery Port: 4992
  Stream Mode: SOCKET
  Stream Port: 5992
  Max Clients: 5

=== FlexRadio Discovery Proxy - Health Check ===
...health checks...

Listening for FlexRadio discovery packets...
```

### Verify Server:
✅ Server should bind to UDP port 4992  
✅ Server should bind to TCP port 5992  
✅ Health checks should all pass (or show warnings)  
✅ Should receive discovery packets from FlexRadio

---

## Step 3: Start Client

On client machine:

```powershell
cd C:\github\FlexRadio-Discovery-Proxy
python FRS-Discovery-Client-v2.py
```

### Expected Output:
```
======================================================================
FlexRadio Discovery Client v2.2.0
======================================================================

Client Configuration:
  Connection Mode: SOCKET
  Server Address: 192.168.1.100
  Stream Port: 5992
  Reconnect Interval: 5.0s
  Broadcast Address: 255.255.255.255
  Discovery Port: 4992

=== FlexRadio Discovery Proxy - Health Check ===
...health checks...

Monitoring for discovery packets...

Connecting to server 192.168.1.100:5992...
✓ Connected to server
10:30:45 - Radio discovered:
  FLEX-6600 (Lake6600)
  Callsign: WX7V | IP: 192.168.0.101
  Status: Available | Version: 4.1.5.39794
  Server: v2.2.0
10:30:45 - ✓ Started broadcasting discovery packets
```

### Verify Client:
✅ Client should connect to server  
✅ Client should show "✓ Connected to server"  
✅ Client should receive and display radio info  
✅ Client should broadcast to local network  
✅ Health checks should all pass

---

## Step 4: Verify SmartSDR Discovery

On client machine:

1. Start **SmartSDR**
2. Wait 2-3 seconds
3. Radio should appear in chooser

### Expected Result:
✅ Radio appears in SmartSDR chooser  
✅ Shows correct model, nickname, callsign  
✅ Shows current status (Available/In Use)  
✅ Can connect to radio normally

---

## Step 5: Test Reconnection

### Test Server Restart:

1. On server: Press `Ctrl+C` to stop
2. On client: Should show connection error
3. On server: Restart server
4. On client: Should automatically reconnect

### Expected Client Output:
```
Connection reset by server
Retrying in 5 seconds...
Connecting to server 192.168.1.100:5992...
✓ Connected to server
```

### Verify:
✅ Client detects disconnection immediately  
✅ Client automatically retries connection  
✅ Client successfully reconnects  
✅ Packet streaming resumes  
✅ SmartSDR continues to see radio

---

## Step 6: Test Multi-Client (Optional)

If you have multiple PCs:

1. Start server once (remote location)
2. Start client on PC #1
3. Start client on PC #2
4. Start client on PC #3

### Expected Server Output:
```
Client connected: 192.168.1.10:54321 (Total: 1)
Client connected: 192.168.1.11:54322 (Total: 2)
Client connected: 192.168.1.12:54323 (Total: 3)
...
→ Streamed to 3 client(s)
```

### Verify:
✅ Server accepts multiple clients  
✅ Server shows total client count  
✅ All clients receive packets  
✅ All clients can discover radio

---

## Step 7: Compare with File Mode (Optional)

To verify performance improvement:

### Switch to File Mode:

1. Stop both server and client
2. Edit `config-v2.ini` on both:
   - Server: `Stream_Mode = file`
   - Client: `Connection_Mode = file`
3. Restart both
4. Note the latency differences

### Expected Results:
- **Socket Mode:** Radio appears in < 1 second
- **File Mode:** Radio appears in 5-30 seconds (depends on cloud sync)

---

## Troubleshooting

### Issue: "Connection refused"

**Symptoms:**
```
⚠ Connection refused by 192.168.1.100:5992
Retrying in 5 seconds...
```

**Solutions:**
1. Verify server is running
2. Verify server IP is correct
3. Check firewall allows TCP 5992
4. Verify VPN connection: `ping <server_ip>`

---

### Issue: "Connection timeout"

**Symptoms:**
```
⚠ Connection timeout to 192.168.1.100:5992
Retrying in 5 seconds...
```

**Solutions:**
1. Verify VPN is established
2. Check VPN routing: `ping <server_ip>`
3. Verify server is listening: `netstat -an | findstr 5992`
4. Check firewall rules

---

### Issue: "No clients connected"

**Symptoms:**
```
Server shows:
  → Streamed to 0 client(s)
  ⚠ No clients connected
```

**Solutions:**
1. Start client with correct server address
2. Verify client can reach server
3. Check server isn't at max_clients limit
4. Review client logs for connection errors

---

### Issue: Radio not appearing in SmartSDR

**Symptoms:**
- Server receives packets ✓
- Client receives packets ✓
- SmartSDR shows no radio ✗

**Solutions:**
1. Verify client is broadcasting: Check logs for "Broadcasting..."
2. Check local firewall allows UDP 4992
3. Verify broadcast_address is correct
4. Try manually: `netsh advfirewall firewall add rule name="FlexRadio" protocol=UDP dir=in localport=4992 action=allow`
5. Restart SmartSDR

---

## Performance Verification

### Latency Test:

1. Start server with logging
2. Start client with logging
3. Note timestamps in logs:

**Server log:**
```
2026-01-27 10:30:45.123 - Packet written...
```

**Client log:**
```
2026-01-27 10:30:45.234 - Radio discovered...
```

**Latency:** 234ms - 123ms = **111ms** ✅

### Expected Latencies:
- Local network: < 100ms
- L3VPN: < 200ms
- Internet VPN: < 500ms

If latency > 1 second, check VPN performance.

---

## Health Check Interpretation

### Startup Health Checks:

```
=== FlexRadio Discovery Proxy - Health Check ===
Mode: SERVER
Time: 2026-01-27 10:30:00

[PASS] UDP Port 4992: Successfully bound and listening
[PASS] TCP Port 5992: Successfully bound and listening
[PASS] Network Interface: Bound to 0.0.0.0 (all interfaces)
[INFO] Listening for FlexRadio discovery packets on UDP 4992
[INFO] Listening for client connections on TCP 5992

Status: OPERATIONAL
```

### What Each Status Means:

- **[PASS]** - Check succeeded, no issues
- **[WARN]** - Check passed with warnings, may need attention
- **[FAIL]** - Check failed, will impact operation
- **[INFO]** - Informational message

---

## Log Files

### Server Log: `discovery-server.log`
```
2026-01-27 10:30:45 - INFO - Server v2.2.0 started - Mode: socket
2026-01-27 10:30:46 - INFO - Client connected: 192.168.1.10:54321
2026-01-27 10:30:50 - INFO - Packet streamed to 1 clients - Radio: FLEX-6600 Lake6600
```

### Client Log: `discovery-client.log`
```
2026-01-27 10:30:45 - INFO - Client v2.2.0 started - Mode: socket
2026-01-27 10:30:46 - INFO - Connected to server 192.168.1.100:5992
2026-01-27 10:30:50 - INFO - Broadcasting: FLEX-6600 Lake6600
```

---

## Success Criteria

### ✅ All Tests Pass If:

1. **Server:**
   - Binds to both UDP 4992 and TCP 5992
   - Receives discovery packets from FlexRadio
   - Accepts client connections
   - Streams packets to clients

2. **Client:**
   - Connects to server successfully
   - Receives discovery packets
   - Broadcasts to local network
   - Auto-reconnects after failures

3. **SmartSDR:**
   - Discovers radio within 1-2 seconds
   - Shows correct radio information
   - Can connect to radio normally

4. **Performance:**
   - Latency < 500ms (preferably < 200ms)
   - No connection drops during normal operation
   - Automatic recovery from failures

---

## Reporting Issues

If you encounter issues:

1. **Check logs:** Review both server and client logs
2. **Run health checks:** Note any warnings or failures
3. **Test connectivity:** Verify VPN and firewall
4. **Collect information:**
   - Server OS and IP
   - Client OS and IP
   - VPN type (WireGuard, OpenVPN, etc.)
   - Error messages from logs
   - Health check results

5. **Report on GitHub:** Include all collected information

---

## Quick Reference Commands

### Windows:

```powershell
# Check if port is open
netstat -an | findstr "4992"
netstat -an | findstr "5992"

# Test connectivity
ping <server_ip>
Test-NetConnection <server_ip> -Port 5992

# View logs
Get-Content discovery-server.log -Tail 20
Get-Content discovery-client.log -Tail 20

# Firewall rules
netsh advfirewall firewall add rule name="Flex-Discovery-UDP" protocol=UDP dir=in localport=4992 action=allow
netsh advfirewall firewall add rule name="Flex-Discovery-TCP" protocol=TCP dir=in localport=5992 action=allow
```

### Linux:

```bash
# Check if port is open
netstat -tuln | grep 4992
netstat -tuln | grep 5992

# Test connectivity
ping <server_ip>
nc -zv <server_ip> 5992

# View logs
tail -f discovery-server.log
tail -f discovery-client.log

# Firewall rules (ufw)
sudo ufw allow 4992/udp
sudo ufw allow 5992/tcp
```

---

## Reverting to File Mode

If socket mode doesn't work for your setup:

1. Stop both server and client
2. Edit `config-v2.ini`:
   - Server: `Stream_Mode = file`
   - Client: `Connection_Mode = file`
   - Verify `Shared_File_Path` is correct
3. Restart both components
4. File mode should work as in v2.1.0

---

**For more information, see:**
- `RELEASE_NOTES_v2.2.0.md` - Complete documentation
- `README_v2.md` - Full v2.x guide
- `HEALTH_CHECK_GUIDE.md` - Diagnostics reference

---

*Testing Guide Version: 1.0*  
*Date: January 27, 2026*  
*For: FlexRadio Discovery Proxy v2.2.0*
