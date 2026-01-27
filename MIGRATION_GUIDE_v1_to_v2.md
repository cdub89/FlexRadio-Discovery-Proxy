# Migration Guide: v1.x to v2.0

## Overview

This guide helps you transition from the v1.x single-script architecture to the v2.0 client-server architecture.

**Important:** v1.x and v2.0 are **completely independent** systems. You cannot "upgrade" v1.x to v2.0 - you must set up v2.0 from scratch.

---

## Should You Migrate?

### Reasons to Stay on v1.x

Stay with v1.x if:
- ✓ Your current setup works perfectly
- ✓ You have direct VPN with routed subnets
- ✓ You need the absolute simplest setup
- ✓ You only have one radio
- ✓ File latency is unacceptable for your use case

### Reasons to Migrate to v2.0

Migrate to v2.0 if:
- ✓ You want authentic radio status (not ping-based)
- ✓ You need to work across non-routed networks
- ✓ You want to use cloud storage (Dropbox, OneDrive, etc.)
- ✓ You have multiple radios
- ✓ You want automatic packet format updates
- ✓ Your v1.x config requires constant manual updates

---

## Architecture Comparison

### v1.x - Single Script
```
[Local PC]
   │
   ├─ FRS-Discovery-Proxy.py
   │    ├─ Pings radio IP
   │    ├─ Generates synthetic VITA-49 packet
   │    └─ Broadcasts locally
   │
   └─ SmartSDR Client
        └─ Receives broadcast
```

### v2.0 - Client/Server
```
[Remote Location]              [Shared Storage]              [Local PC]
     │                              │                             │
 FlexRadio                          │                             │
     │                              │                             │
     ├─ Broadcasts                  │                             │
     │  VITA-49                     │                             │
     │                              │                             │
     ▼                              │                             │
FRS-Discovery-                      │                             │
Server-v2.py                        │                             │
     │                              │                             │
     └─ Captures ─────────►  discovery.json  ◄─────────┐         │
           packet                   │                   │         │
                                    │             FRS-Discovery-  │
                                    │             Client-v2.py    │
                                    │                   │         │
                                    │                   └─ Broadcasts
                                    │                       locally
                                    │                             │
                                    │                       SmartSDR Client
                                    │                             │
                                                                 Receives
```

---

## Migration Steps

### Phase 1: Preparation (Don't Stop v1.x Yet!)

#### Step 1: Understand Your Current Setup

Document your v1.x configuration:
```ini
# From config.ini
IP_Address = ?
Callsign = ?
Nickname = ?
Version = ?
Serial = ?
Model = ?
Radio_License = ?
```

**Note:** With v2.0, you won't need these anymore! But good to have for comparison.

#### Step 2: Choose Shared Storage Method

Pick one:

**Option A: Network Share (Best for VPN)**
- Pros: Fast, low latency (< 1 second)
- Cons: Requires SMB/NFS setup, VPN must support file sharing
- Setup time: 15-30 minutes

**Option B: Cloud Sync (Best for Internet)**
- Pros: Works anywhere, no VPN needed, automatic backup
- Cons: Higher latency (5-30 seconds), requires cloud account
- Setup time: 10-15 minutes

**Option C: Local Testing**
- Pros: Instant, no network needed
- Cons: Only works on same machine
- Setup time: 2 minutes

#### Step 3: Set Up Shared Storage

**For Network Share (Windows):**
```powershell
# On server side (where radio is)
mkdir C:\FlexRadio
New-SmbShare -Name "FlexRadio" -Path "C:\FlexRadio" -FullAccess "Everyone"

# On client side (where SmartSDR is)
net use Z: \\server-name\FlexRadio
# Test: dir Z:\
```

**For Cloud Sync:**
1. Install Dropbox/OneDrive on both machines
2. Create folder: `FlexRadio`
3. Wait for initial sync
4. Place test file to verify sync works

---

### Phase 2: Set Up v2.0 Server (Remote Location)

#### Step 1: Copy Files to Server

Copy these files to the machine where your FlexRadio is located:
- `FRS-Discovery-Server-v2.py`
- `config-v2.ini`
- `FRS-Discovery-Server-v2.bat` (Windows)

#### Step 2: Edit config-v2.ini (Server Section)

```ini
[SERVER]
Listen_Address = 0.0.0.0
Discovery_Port = 4992
Shared_File_Path = Z:\FlexRadio\discovery.json    # YOUR SHARED PATH HERE
Update_Interval = 2.0
```

**Important:** Use the correct path for your shared storage:
- Network share: `Z:\FlexRadio\discovery.json`
- Dropbox: `C:\Users\YourName\Dropbox\FlexRadio\discovery.json`
- OneDrive: `C:\Users\YourName\OneDrive\FlexRadio\discovery.json`
- Local test: `C:\FlexRadio\discovery.json`

#### Step 3: Test Server

```powershell
# Windows
python FRS-Discovery-Server-v2.py

# Or double-click FRS-Discovery-Server-v2.bat
```

**Expected output:**
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

**Troubleshooting:**

| Issue | Solution |
|-------|----------|
| "No packets received" | Verify radio is on and broadcasting |
| "Permission denied" | Check file path and write permissions |
| "Address already in use" | Stop any other programs using port 4992 |
| "Config not found" | Ensure config-v2.ini is in same folder |

#### Step 4: Verify File Creation

Check that `discovery.json` was created in your shared location:
```powershell
# Windows
dir Z:\FlexRadio\discovery.json
type Z:\FlexRadio\discovery.json

# Should show JSON with radio information
```

---

### Phase 3: Set Up v2.0 Client (Local PC)

#### Step 1: Copy Files to Client

Copy these files to your local PC (where SmartSDR runs):
- `FRS-Discovery-Client-v2.py`
- `config-v2.ini` (same file as server, or copy the CLIENT section)
- `FRS-Discovery-Client-v2.bat` (Windows)

#### Step 2: Edit config-v2.ini (Client Section)

```ini
[CLIENT]
Shared_File_Path = Z:\FlexRadio\discovery.json    # SAME PATH AS SERVER
Broadcast_Address = 255.255.255.255
Discovery_Port = 4992
Check_Interval = 3.0
Max_File_Age = 15.0
```

**Critical:** `Shared_File_Path` must point to the **same file** as the server!

#### Step 3: Verify File Access

Before starting client, verify you can read the file:
```powershell
# Windows
dir Z:\FlexRadio\discovery.json
type Z:\FlexRadio\discovery.json

# Should show recent radio information
```

#### Step 4: Test Client

```powershell
# Windows
python FRS-Discovery-Client-v2.py

# Or double-click FRS-Discovery-Client-v2.bat
```

**Expected output:**
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
```

**Troubleshooting:**

| Issue | Solution |
|-------|----------|
| "File not found" | Check path, verify file sync, check mount |
| "Stale file" | Verify server is still running |
| "Permission denied" | Check firewall allows Python UDP broadcast |
| "No output" | Check config-v2.ini paths are correct |

---

### Phase 4: Test with SmartSDR

#### Step 1: Open SmartSDR

With both server and client running, open SmartSDR.

#### Step 2: Check Radio Chooser

Your radio should appear with:
- Correct model name
- Correct callsign
- Correct status (Available, In Use, etc.)
- Correct IP address

#### Step 3: Attempt Connection

Click the radio to connect. Connection should work just like v1.x.

**Note:** You still need network connectivity to the radio IP! v2.0 only provides discovery, not the actual connection.

---

### Phase 5: Verify & Compare

#### Check v2.0 Radio Info Matches Reality

Compare the information v2.0 displays vs. your v1.x config.ini:

| Field | v1.x (Manual) | v2.0 (Captured) | Match? |
|-------|---------------|-----------------|--------|
| Model | config.ini | Auto-detected | ✓ |
| Serial | config.ini | Auto-detected | ✓ |
| Callsign | config.ini | Auto-detected | ✓ |
| Version | config.ini (may be outdated) | Auto-detected (always current) | ✓ |
| Status | Ping-based guess | Actual radio status | Better! |

#### Verify Status Accuracy

Test scenarios:

1. **Radio Available**
   - v1.x: Shows available if ping succeeds
   - v2.0: Shows "Available" from actual radio status ✓

2. **Radio In Use**
   - v1.x: Shows available even if in use
   - v2.0: Shows "In Use" with client details ✓

3. **Radio Offline**
   - v1.x: Shows failed after ping timeout
   - v2.0: Client shows "stale file" warning ✓

---

### Phase 6: Cutover to v2.0

Once v2.0 is verified working:

#### Step 1: Stop v1.x

```
Ctrl+C in v1.x window
```

#### Step 2: Leave v2.0 Running

Both server and client should remain running.

#### Step 3: Test SmartSDR Again

Verify radio still appears and connects properly.

#### Step 4: Archive v1.x Files (Optional)

```powershell
# Create backup folder
mkdir v1_backup
move FRS-Discovery-Proxy.py v1_backup\
move config.ini v1_backup\
move broadcast.log v1_backup\
move FRS-Discovery-Proxy.bat v1_backup\
```

---

## Configuration Changes Reference

### What Moved from v1 to v2

| v1.x config.ini | v2.0 config-v2.ini | Notes |
|-----------------|---------------------|-------|
| `IP_Address` | (not needed) | Captured from packet |
| `Callsign` | (not needed) | Captured from packet |
| `Nickname` | (not needed) | Captured from packet |
| `Version` | (not needed) | Captured from packet |
| `Serial` | (not needed) | Captured from packet |
| `Model` | (not needed) | Captured from packet |
| `Radio_License` | (not needed) | Captured from packet |
| (none) | `Shared_File_Path` | **NEW** - Required for both |
| (none) | `Update_Interval` | **NEW** - Server only |
| (none) | `Check_Interval` | **NEW** - Client only |
| (none) | `Max_File_Age` | **NEW** - Client only |

### What Stayed the Same

| Setting | v1.x | v2.0 |
|---------|------|------|
| Discovery Port | 4992 (hardcoded) | 4992 (configurable) |
| Broadcast Address | 255.255.255.255 (hardcoded) | 255.255.255.255 (configurable) |
| Logging | broadcast.log | discovery-server.log + discovery-client.log |

---

## Running Both v1 and v2 Simultaneously

You **can** run both v1.x and v2.0 at the same time during testing:

### Why This Works

- v1.x generates synthetic packets with broadcast IP
- v2.0 captures real packets with actual radio IP
- SmartSDR sees both and displays the radio twice
- Both broadcasts use same port (4992) but different content

### Testing Strategy

1. Start v1.x (existing setup)
2. Start v2.0 server
3. Start v2.0 client
4. Open SmartSDR
5. Look for **two** radio entries (might have slightly different info)
6. Connect to either one - both should work
7. Once v2.0 verified, stop v1.x

### Which Radio Entry is Which?

In SmartSDR chooser:
- **v1.x entry**: IP might be synthetic, status always "Available"
- **v2.0 entry**: IP is real, status reflects actual radio state

---

## Troubleshooting Migration Issues

### Both Server and Client Running, No Radio in SmartSDR

**Diagnosis Steps:**

1. Check server log: `discovery-server.log`
   ```
   # Should show: "Packet written - Radio: ..."
   ```

2. Check client log: `discovery-client.log`
   ```
   # Should show: "Broadcasting: ..."
   ```

3. Check file exists and is recent:
   ```powershell
   dir Z:\FlexRadio\discovery.json
   # Modified time should be within last few seconds
   ```

4. Use Wireshark on local PC:
   ```
   Filter: udp.port == 4992
   # Should see broadcasts from client
   ```

5. Check Windows Firewall:
   ```powershell
   # Allow Python through firewall
   netsh advfirewall firewall add rule name="Python" dir=out action=allow program="C:\Python3\python.exe" enable=yes
   ```

### SmartSDR Shows "Exception" When Clicking Radio

**Cause:** Likely network routing issue (not discovery issue)

**Fix:**
1. Verify VPN/network route to radio IP
2. Test: `ping <radio_ip>` from SmartSDR PC
3. v2.0 only provides discovery - connection requires actual network path

### File Age Always "Stale"

**Diagnosis:**
```powershell
# On server: Check file modified time
dir Z:\FlexRadio\discovery.json

# On client: Check same file modified time
dir Z:\FlexRadio\discovery.json

# Times should be within seconds of each other
```

**Possible Causes:**
- Clock skew between machines (sync with NTP)
- File sync delay (increase `Max_File_Age`)
- Server not writing (check server log)
- Network share disconnect (remount share)

### High CPU or Disk Usage

**Cause:** Too frequent file operations

**Fix:**
```ini
# Increase intervals in config-v2.ini
[SERVER]
Update_Interval = 5.0  # Was 2.0

[CLIENT]
Check_Interval = 5.0   # Was 3.0
```

---

## Rollback Plan

If v2.0 doesn't work for you:

### Immediate Rollback

1. Stop v2.0 server and client (Ctrl+C)
2. Start v1.x again
3. Radio reappears in SmartSDR within ~11 seconds

### Complete Rollback

```powershell
# Stop v2.0
# Delete v2.0 files (optional)
del FRS-Discovery-Server-v2.py
del FRS-Discovery-Client-v2.py
del config-v2.ini
del discovery-server.log
del discovery-client.log
del FRS-Discovery-Server-v2.bat
del FRS-Discovery-Client-v2.bat

# Restore v1.x from backup (if archived)
move v1_backup\* .

# Start v1.x
python FRS-Discovery-Proxy.py
```

---

## Post-Migration Checklist

After successfully migrating to v2.0:

- [ ] Server running and capturing packets
- [ ] Client running and broadcasting
- [ ] Radio appears in SmartSDR
- [ ] Connection to radio works
- [ ] Radio status reflects reality (Available/In Use)
- [ ] Both logs show no errors
- [ ] File age stays below Max_File_Age threshold
- [ ] v1.x stopped and archived
- [ ] Documentation updated with your specific paths/setup

---

## Getting Help

### Before Asking for Help

Collect this information:

1. **Version Information**
   ```
   Server v2.0.0
   Client v2.0.0
   Python version: ?
   OS: ?
   ```

2. **Configuration**
   ```ini
   # From config-v2.ini (sanitize paths)
   Shared_File_Path = ?
   Update_Interval = ?
   Check_Interval = ?
   ```

3. **Log Excerpts**
   ```
   # Last 10 lines from each log
   discovery-server.log
   discovery-client.log
   ```

4. **Network Topology**
   ```
   Server location: ?
   Client location: ?
   Shared storage type: ?
   ```

### Where to Get Help

- GitHub Issues: [Repository URL]
- Email: [Contact]
- QRZ: WX7V

**Not supported by FlexRadio Systems, Inc.**

---

## Conclusion

Migration from v1.x to v2.0 is a complete system change, not an upgrade. The effort is worthwhile if you need:

✓ Authentic radio status  
✓ Automatic packet format updates  
✓ Multiple radio support  
✓ Flexible network topology  

Take your time with the migration, test thoroughly, and keep v1.x available for rollback if needed.

---

## License & Attribution

**Copyright © 2026 Chris L White (WX7V)**  
Licensed under the MIT License - see [LICENSE](LICENSE) file

**⚠️ IMPORTANT:** This software is NOT officially supported by FlexRadio Systems, Inc.  
For official support: https://www.flexradio.com

---

**73 de WX7V**
