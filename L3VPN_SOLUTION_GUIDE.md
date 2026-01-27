# FlexRadio Discovery over L3 VPN - Solution Guide

## The Problem: Broadcast Packets Don't Cross L3 VPNs

### Why FlexRadio Discovery Fails with WireGuard/L3 VPNs

**FlexRadio Discovery Protocol:**
- Uses UDP broadcast to `255.255.255.255:4992`
- Packets are sent at Layer 2 (Ethernet broadcast)
- Works perfectly on local subnet

**L3 VPN Limitation (WireGuard, OpenVPN, etc.):**
- Routes **unicast** IP packets between networks (Layer 3)
- **Does NOT forward broadcast packets**
- Broadcast packets are subnet-local only
- No way to route `255.255.255.255` across VPN

**Result:**
```
[Remote Radio] → Broadcasts 255.255.255.255 → [Stops at router]
                                              [Never crosses VPN]
[Local SmartSDR] ← Can't see broadcasts ← [VPN endpoint]
```

### Traditional "Solution": L2 VPN (Complex!)

**L2 VPN (Ethernet Bridge):**
- Bridges entire Ethernet segments
- Forwards ALL Layer 2 traffic (including broadcasts)
- Complex setup (TAP mode, bridging, DHCP coordination)
- Performance overhead
- Security concerns (entire networks exposed)

**Why it's complicated:**
```
Configure TAP interfaces → Set up Ethernet bridge → 
Coordinate DHCP → Manage broadcast storms → 
Handle MAC addressing → Performance tuning
```

---

## The v2.0 Solution: Capture & Rebroadcast Real Packets

### How v2.0 Works Over L3 VPN

```
┌─────────────────────────────────────────────────────────────────────┐
│  Remote Location (Same Subnet as FlexRadio)                        │
│                                                                      │
│  ┌─────────────────┐                                                │
│  │   FlexRadio     │                                                │
│  │   192.168.1.50  │                                                │
│  └────────┬────────┘                                                │
│           │                                                          │
│           │ UDP Broadcast 255.255.255.255:4992                      │
│           │ (REAL VITA-49 Discovery Packet)                         │
│           ▼                                                          │
│  ┌──────────────────────────────────────────────┐                   │
│  │  FRS-Discovery-Server-v2.py                  │                   │
│  │  - Listens on 0.0.0.0:4992                  │                   │
│  │  - Receives ACTUAL broadcast packet          │                   │
│  │  - Captures complete packet: data.hex()      │                   │
│  │  - Parses payload for display                │                   │
│  │  - Stores in discovery.json                  │                   │
│  └────────────────────┬─────────────────────────┘                   │
│                       │                                              │
└───────────────────────┼──────────────────────────────────────────────┘
                        │
                        │ File Transfer via:
                        │ - SMB/CIFS over L3 VPN (WireGuard)
                        │ - OR Cloud Sync (Dropbox/OneDrive)
                        │ - OR NFS over L3 VPN
                        │
                        ▼ discovery.json contains:
                        │ { "packet_hex": "385200b4...",
                        │   "radio_info": { "model": "FLEX-6600", ... },
                        │   ... }
                        │
┌───────────────────────┼──────────────────────────────────────────────┐
│  Local PC (Different Subnet, Connected via L3 VPN)                  │
│                       │                                              │
│  ┌────────────────────▼────────────────────────┐                    │
│  │  FRS-Discovery-Client-v2.py                 │                    │
│  │  - Reads discovery.json                     │                    │
│  │  - Reconstructs packet: bytes.fromhex()     │                    │
│  │  - Validates freshness (Max_File_Age)       │                    │
│  └────────────────────┬────────────────────────┘                    │
│                       │                                              │
│                       │ UDP Broadcast 255.255.255.255:4992          │
│                       │ (SAME packet as original!)                  │
│                       ▼                                              │
│  ┌─────────────────────────────────────────────┐                    │
│  │  SmartSDR Client                            │                    │
│  │  - Receives "local" broadcast               │                    │
│  │  - Sees radio with REAL status              │                    │
│  │  - Connects to radio via L3 VPN             │                    │
│  └─────────────────────────────────────────────┘                    │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Key Implementation Details

#### Server Captures REAL Packets (Not Synthetic!)

**Line 102-113 in FRS-Discovery-Server-v2.py:**
```python
# Receive discovery packet (THIS IS THE REAL PACKET FROM RADIO!)
data, addr = sock.recvfrom(4096)

# Only process if it's a valid VITA-49 packet
if len(data) >= 28 and data[0:1] == b'\x38':
    # Extract the COMPLETE packet as hex string
    packet_hex = data.hex()  # <-- ENTIRE packet preserved!
```

**This is NOT generating a packet - it's capturing the actual broadcast!**

#### Server Stores Complete Packet

**Line 138-148 in FRS-Discovery-Server-v2.py:**
```python
packet_data = {
    'timestamp': timestamp,
    'timestamp_unix': current_time,
    'server_version': __version__,
    'packet_hex': packet_hex,        # <-- Complete packet!
    'packet_size': len(data),
    'source_ip': addr[0],
    'source_port': addr[1],
    'radio_info': radio_info,         # <-- For display/logging
    'parsed_payload': parsed_info     # <-- For debugging
}

# Write to shared file
with open(shared_file_path, 'w') as f:
    json.dump(packet_data, f, indent=2)
```

**The `packet_hex` field contains the COMPLETE, UNMODIFIED packet!**

#### Client Reconstructs EXACT Packet

**Line 129 in FRS-Discovery-Client-v2.py:**
```python
# Convert hex string back to bytes
packet_bytes = bytes.fromhex(packet_data['packet_hex'])
```

**This recreates the EXACT packet that FlexRadio sent!**

#### Client Rebroadcasts Authentic Packet

**Line 142 in FRS-Discovery-Client-v2.py:**
```python
# Broadcast the packet (SAME packet as radio sent!)
sock.sendto(packet_bytes, (broadcast_address, discovery_port))
```

**SmartSDR receives the SAME VITA-49 packet as if the radio was local!**

---

## Setup for WireGuard L3 VPN

### Scenario: Remote Radio Access via WireGuard

**Network Topology:**
```
Remote Site:                      Local Site:
  FlexRadio: 192.168.1.50          Your PC: 10.0.0.100
  Server: 192.168.1.10             Client: 10.0.0.100
  WireGuard: 10.255.0.1            WireGuard: 10.255.0.2
        │                               │
        └───────────────┬───────────────┘
                    WireGuard VPN
                   (10.255.0.0/24)
```

### Step 1: Configure WireGuard (Already Done)

Your existing WireGuard setup provides:
- ✅ IP routing between 192.168.1.0/24 ↔ 10.0.0.0/24
- ✅ Can ping radio: `ping 192.168.1.50` works
- ✅ Can access files via SMB/NFS over VPN
- ❌ No broadcast forwarding (by design!)

**This is perfect for v2.0! No changes needed to WireGuard.**

### Step 2: Set Up File Sharing Over WireGuard

#### Option A: SMB Share (Recommended for Windows)

**On Remote Site (192.168.1.10):**
```powershell
# Create shared folder
mkdir C:\FlexRadio
New-SmbShare -Name "FlexRadio" -Path "C:\FlexRadio" -FullAccess "Everyone"

# Ensure SMB is allowed through firewall
New-NetFirewallRule -DisplayName "SMB In" -Direction Inbound -Protocol TCP -LocalPort 445 -Action Allow
```

**On Local PC (10.0.0.100):**
```powershell
# Map network drive via WireGuard IP
net use Z: \\10.255.0.1\FlexRadio

# Test access
dir Z:\
```

#### Option B: NFS Share (Recommended for Linux)

**On Remote Site:**
```bash
# Install NFS server
sudo apt install nfs-kernel-server

# Create shared folder
sudo mkdir /srv/flexradio
sudo chmod 777 /srv/flexradio

# Add to /etc/exports
echo "/srv/flexradio 10.255.0.0/24(rw,sync,no_subtree_check)" | sudo tee -a /etc/exports

# Export shares
sudo exportfs -ra
```

**On Local PC:**
```bash
# Mount NFS share via WireGuard IP
sudo mount -t nfs 10.255.0.1:/srv/flexradio /mnt/flexradio

# Test access
ls /mnt/flexradio
```

### Step 3: Configure Server (Remote Site)

Edit `config-v2.ini` on remote site:
```ini
[SERVER]
Listen_Address = 0.0.0.0
Discovery_Port = 4992
Shared_File_Path = C:\FlexRadio\discovery.json    # Windows SMB
# OR
Shared_File_Path = /srv/flexradio/discovery.json  # Linux NFS
Update_Interval = 2.0
```

**Start server:**
```bash
python FRS-Discovery-Server-v2.py
```

**Expected output:**
```
======================================================================
FlexRadio Discovery Server v2.0.0
======================================================================

Server Configuration:
  Listen Address: 0.0.0.0
  Discovery Port: 4992
  Shared File: C:\FlexRadio\discovery.json
  Update Interval: 2.0s

======================================================================

Listening for FlexRadio discovery packets...

14:23:45 - Packet #1 from 192.168.1.50
  Radio: FLEX-6600 (Lake6600)
  Callsign: WX7V | IP: 192.168.1.50
  Status: Available | Version: 4.1.5.39794
  → Packet written to: C:\FlexRadio\discovery.json
```

### Step 4: Configure Client (Local PC)

Edit `config-v2.ini` on local PC:
```ini
[CLIENT]
Shared_File_Path = Z:\discovery.json             # Windows mapped drive
# OR
Shared_File_Path = /mnt/flexradio/discovery.json # Linux NFS mount
Broadcast_Address = 255.255.255.255
Discovery_Port = 4992
Check_Interval = 3.0
Max_File_Age = 15.0
```

**Start client:**
```bash
python FRS-Discovery-Client-v2.py
```

**Expected output:**
```
======================================================================
FlexRadio Discovery Client v2.0.0
======================================================================

Client Configuration:
  Shared File: Z:\discovery.json
  Broadcast Address: 255.255.255.255
  Discovery Port: 4992
  Check Interval: 3.0s
  Max File Age: 15.0s

======================================================================

Monitoring for discovery packets...

14:23:50 - Radio discovered:
  FLEX-6600 (Lake6600)
  Callsign: WX7V | IP: 192.168.1.50
  Status: Available | Version: 4.1.5.39794
  File age: 2.3s | Server: v2.0.0
14:23:50 - ✓ Started broadcasting discovery packets
```

### Step 5: Open SmartSDR

Your radio now appears in SmartSDR as if it were local!

**Why it works:**
1. Server captures real broadcast on remote subnet
2. Packet stored in file
3. File transferred over L3 VPN (unicast, works fine!)
4. Client rebroadcasts on local subnet
5. SmartSDR sees "local" broadcast
6. Connection uses L3 VPN unicast (works!)

---

## Verification: Real Packets vs Synthetic

### How to Verify Packets are Authentic

#### Method 1: Compare with Wireshark Capture

**On remote site (same subnet as radio):**
```bash
# Capture real broadcast from radio
sudo tcpdump -i eth0 -X udp port 4992 and host 192.168.1.50 > real_packet.txt
```

**Check discovery.json:**
```bash
cat /srv/flexradio/discovery.json | jq -r '.packet_hex' | head -c 100
```

**The hex should match the Wireshark capture exactly!**

#### Method 2: Check Radio Status Field

**Real packet shows actual status:**
- `"status": "Available"` - Radio is free
- `"status": "In Use"` - Radio is being used
- Includes actual client IPs, handles, etc.

**Synthetic packet (v1.x) always shows:**
- `"status": "Available"` - Even when in use!
- Empty client fields

**Check the file:**
```bash
cat discovery.json | jq '.parsed_payload.status'
# Output: "Available" or "In Use" (REAL STATUS!)
```

#### Method 3: Firmware Version Auto-Updates

**Real packet:**
- Version is always current
- Updates automatically when radio firmware updated
- Example: `"version": "4.1.5.39794"`

**Synthetic packet (v1.x):**
- Version is manually configured
- Becomes outdated unless manually updated
- Example: Still shows `"4.1.5.39794"` even after radio updated to 4.2.x

#### Method 4: Inspect discovery.json Structure

The file explicitly shows it's a captured packet:
```json
{
  "timestamp": "2026-01-26 14:23:45",
  "server_version": "2.0.0",
  "packet_hex": "385200b400000800...",     ← Complete raw packet!
  "packet_size": 748,
  "source_ip": "192.168.1.50",             ← Radio's actual IP
  "source_port": 4992,                     ← Received from port 4992
  "radio_info": {
    "model": "FLEX-6600",
    "serial": "3718-0522-6600-0003",
    "status": "Available",                 ← Real-time status!
    ...
  }
}
```

---

## Advantages Over L2 VPN

| Aspect | L2 VPN (Bridge) | v2.0 (L3 + File Transfer) |
|--------|-----------------|---------------------------|
| **Setup Complexity** | High (TAP, bridge, DHCP) | Low (file sharing only) |
| **VPN Mode** | TAP (Ethernet bridge) | TUN (IP routing) ✓ |
| **WireGuard Compatible** | Requires special config | Native WireGuard ✓ |
| **Performance** | High overhead (all L2 traffic) | Minimal (only discovery) ✓ |
| **Security** | Entire networks exposed | Only file share exposed ✓ |
| **Broadcast Traffic** | All broadcasts forwarded | Only discovery needed ✓ |
| **Maintenance** | Complex (bridge/DHCP issues) | Simple (file sharing) ✓ |
| **Latency** | ~5-50ms | ~1-5s (acceptable for discovery) |
| **Packet Authenticity** | Real | Real ✓ |

---

## Troubleshooting

### Server Not Receiving Packets

**Symptoms:**
```
Listening for FlexRadio discovery packets...
(no packets shown)
```

**Diagnosis:**
```bash
# On server, check if packets are arriving
sudo tcpdump -i any udp port 4992

# Should see broadcasts from radio IP
```

**Solutions:**
1. Ensure server is on same subnet as radio
2. Check firewall allows UDP 4992 inbound
3. Verify radio is powered on and broadcasting

### File Not Syncing Over VPN

**Symptoms:**
```
Client: ⚠ Cannot read discovery file: File not found
```

**Diagnosis:**
```bash
# On local PC, test file share access
# Windows:
dir Z:\
# Linux:
ls /mnt/flexradio
```

**Solutions:**
1. Verify WireGuard tunnel is up: `wg show`
2. Test connectivity: `ping 10.255.0.1`
3. Check SMB/NFS share permissions
4. Ensure firewall allows SMB (445) or NFS (2049)

### SmartSDR Sees Radio but Can't Connect

**This is NOT a discovery issue - it's network routing!**

**Diagnosis:**
```bash
# On local PC, test radio connectivity
ping 192.168.1.50

# Should work via WireGuard!
```

**Solutions:**
1. Verify WireGuard routes include radio subnet
2. Add route if missing:
   ```bash
   # Linux:
   sudo ip route add 192.168.1.0/24 via 10.255.0.1 dev wg0
   
   # Windows:
   route add 192.168.1.0 mask 255.255.255.0 10.255.0.1
   ```
3. Check WireGuard AllowedIPs includes radio subnet

---

## Summary

### What v2.0 Does:
1. ✅ **Captures** real VITA-49 packets from FlexRadio
2. ✅ **Stores** complete packet as hex (unmodified!)
3. ✅ **Transfers** via file share over L3 VPN
4. ✅ **Rebroadcasts** authentic packet locally
5. ✅ **SmartSDR** receives real discovery packet

### What It Does NOT Do:
- ❌ Generate synthetic packets (v1.x did this)
- ❌ Modify packet contents
- ❌ Require L2 VPN or bridging
- ❌ Forward all broadcast traffic

### Why It Works With WireGuard:
- Uses standard L3 IP routing (WireGuard's strength!)
- File transfer is unicast (works over any VPN)
- Only rebroadcasts on local subnet (client side)
- Radio connection uses unicast TCP/UDP (works via VPN)

---

## Quick Start for WireGuard Users

```bash
# Remote site (192.168.1.10):
1. Set up SMB/NFS share (one-time)
2. Edit config-v2.ini → Shared_File_Path
3. python FRS-Discovery-Server-v2.py
4. Verify packets being captured

# Local PC (10.0.0.100):
1. Mount share via WireGuard IP (one-time)
2. Edit config-v2.ini → same Shared_File_Path
3. python FRS-Discovery-Client-v2.py
4. Open SmartSDR → Radio appears!
```

**That's it! No L2 VPN, no bridging, no TAP mode!**

---

**Author:** Chris L White, WX7V  
**License:** MIT  
**Not supported by FlexRadio Systems, Inc.**

**73 de WX7V**
