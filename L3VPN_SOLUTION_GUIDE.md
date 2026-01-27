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

## The v3.0 Solution: TCP Socket Streaming

### How v3.0 Works Over L3 VPN

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
│  │  FRS-Discovery-Server.py                     │                   │
│  │  - Listens on 0.0.0.0:4992 (UDP)            │                   │
│  │  - Receives ACTUAL broadcast packet          │                   │
│  │  - Parses payload for display                │                   │
│  │  - Listens on 0.0.0.0:5992 (TCP)            │                   │
│  └────────────────────┬─────────────────────────┘                   │
│                       │                                              │
└───────────────────────┼──────────────────────────────────────────────┘
                        │
                        │ TCP Connection over L3 VPN
                        │ (WireGuard, OpenVPN, etc.)
                        │ - Real-time packet streaming
                        │ - Sub-second latency
                        │ - Unicast (works over L3!)
                        │
┌───────────────────────┼──────────────────────────────────────────────┐
│  Local PC (Different Subnet, Connected via L3 VPN)                  │
│                       │                                              │
│  ┌────────────────────▼────────────────────────┐                    │
│  │  FRS-Discovery-Client.py                    │                    │
│  │  - Connects to server via TCP               │                    │
│  │  - Receives packets in real-time            │                    │
│  │  - Reconstructs packet: bytes.fromhex()     │                    │
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

**Server receives the actual broadcast:**
```python
# Receive discovery packet (THIS IS THE REAL PACKET FROM RADIO!)
data, addr = sock.recvfrom(4096)

# Only process if it's a valid VITA-49 packet
if len(data) >= 28 and data[0:1] == b'\x38':
    # Extract the COMPLETE packet as hex string
    packet_hex = data.hex()  # <-- ENTIRE packet preserved!
```

**This is NOT generating a packet - it's capturing the actual broadcast!**

#### Server Streams Complete Packet via TCP

**Server sends packet to all connected clients:**
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

# Send to all connected clients via TCP
json_data = json.dumps(packet_data) + '\n'
client.sock.sendall(json_data.encode('utf-8'))
```

**The `packet_hex` field contains the COMPLETE, UNMODIFIED packet!**

#### Client Reconstructs EXACT Packet

**Client receives via TCP:**
```python
# Receive data from server
data = self.tcp_sock.recv(4096)

# Parse JSON packet data
packet_data = json.loads(line)

# Convert hex string back to bytes
packet_bytes = bytes.fromhex(packet_data['packet_hex'])
```

**This recreates the EXACT packet that FlexRadio sent!**

#### Client Rebroadcasts Authentic Packet

**Client broadcasts locally:**
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
- ✅ TCP connections work across VPN
- ❌ No broadcast forwarding (by design!)

**This is perfect for v3.0! No changes needed to WireGuard.**

### Step 2: Ensure Firewall Rules

**On Remote Site (Server):**
```bash
# Allow UDP 4992 (FlexRadio discovery)
sudo ufw allow 4992/udp

# Allow TCP 5992 (Discovery proxy)
sudo ufw allow 5992/tcp

# Or Windows:
New-NetFirewallRule -DisplayName "FlexRadio Discovery UDP" -Direction Inbound -Protocol UDP -LocalPort 4992 -Action Allow
New-NetFirewallRule -DisplayName "Discovery Proxy TCP" -Direction Inbound -Protocol TCP -LocalPort 5992 -Action Allow
```

### Step 3: Configure Server (Remote Site)

Edit `config.ini` on remote site:
```ini
[SERVER]
Listen_Address = 0.0.0.0
Discovery_Port = 4992
Stream_Port = 5992
Max_Clients = 5
```

**Start server:**
```bash
python FRS-Discovery-Server.py
```

**Expected output:**
```
======================================================================
FlexRadio Discovery Server v3.0.0
======================================================================

Server Configuration:
  Listen Address: 0.0.0.0
  Discovery Port: 4992
  Stream Port: 5992
  Max Clients: 5

======================================================================

Listening for FlexRadio discovery packets...

[2026-01-27 14:23:45] FLEX-6600 (Lake6600) - WX7V @ 192.168.1.50 - Available
   → Sent to 0 client(s)
   ⚠ No clients connected
```

### Step 4: Configure Client (Local PC)

Edit `config.ini` on local PC:
```ini
[CLIENT]
Server_Address = 10.255.0.1        # WireGuard IP of remote server
Stream_Port = 5992                  # Must match server
Reconnect_Interval = 5.0
Broadcast_Address = 255.255.255.255
Discovery_Port = 4992
```

**Start client:**
```bash
python FRS-Discovery-Client.py
```

**Expected output:**
```
======================================================================
FlexRadio Discovery Client v3.0.0
======================================================================

Client Configuration:
  Broadcast Address: 255.255.255.255
  Discovery Port: 4992
  Server Address: 10.255.0.1
  Stream Port: 5992
  Reconnect Interval: 5.0s

======================================================================

Monitoring for discovery packets...

Connecting to server 10.255.0.1:5992...

14:23:50 - ✓ Connected to server
  Listening for discovery packets...

14:23:52 - Radio discovered:
  FLEX-6600 (Lake6600)
  Callsign: WX7V | IP: 192.168.1.50
  Status: Available | Version: 4.1.5.39794
  Server: v3.0.0
14:23:52 - ✓ Started broadcasting discovery packets
```

### Step 5: Open SmartSDR

Your radio now appears in SmartSDR as if it were local!

**Why it works:**
1. Server captures real broadcast on remote subnet
2. Packet streamed via TCP over L3 VPN (unicast, works!)
3. Client receives packet in real-time (<1 second)
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

**Check server output - packet_hex matches Wireshark capture exactly!**

#### Method 2: Check Radio Status Field

**Real packet shows actual status:**
- `"status": "Available"` - Radio is free
- `"status": "In Use"` - Radio is being used
- Includes actual client IPs, handles, etc.

**Synthetic packet (v1.x) always shows:**
- `"status": "Available"` - Even when in use!
- Empty client fields

#### Method 3: Firmware Version Auto-Updates

**Real packet:**
- Version is always current
- Updates automatically when radio firmware updated
- Example: `"version": "4.1.5.39794"`

**Synthetic packet (v1.x):**
- Version is manually configured
- Becomes outdated unless manually updated

---

## Advantages Over Other Solutions

| Aspect | L2 VPN (Bridge) | File Mode (v2.x) | Socket Mode (v3.0) |
|--------|-----------------|------------------|--------------------|
| **Setup Complexity** | High (TAP, bridge, DHCP) | Medium (file shares) | Low (TCP only) ✓ |
| **VPN Mode** | TAP (Ethernet bridge) | TUN (IP routing) | TUN (IP routing) ✓ |
| **WireGuard Compatible** | Requires special config | Yes | Native ✓ |
| **Performance** | High overhead (all L2 traffic) | Medium (file I/O) | Minimal (TCP stream) ✓ |
| **Latency** | ~5-50ms | 5-30s | <1s ✓ |
| **Setup Required** | Bridging, DHCP | File shares, cloud sync | Firewall rule only ✓ |
| **Maintenance** | Complex | Medium | Simple ✓ |
| **Reliability** | Medium | Medium (sync issues) | High ✓ |
| **Packet Authenticity** | Real ✓ | Real ✓ | Real ✓ |

### Why File Mode Was Abandoned (v2.x)

Version 2.x supported file-based streaming, but it proved unsatisfactory:
- **Network share overhead:** Required SMB/NFS configuration, permissions, firewall rules
- **Cloud storage latency:** OneDrive, Google Drive, and Dropbox introduced 5-30 second delays
- **High write frequency:** Constant file updates caused performance issues with cloud sync
- **Complexity:** More moving parts to troubleshoot
- **Reliability:** File locks, sync conflicts, stale file detection issues

Socket mode (v3.0) solved all these problems with direct TCP streaming.

---

## Troubleshooting

### Server Not Receiving Packets

**Symptoms:**
```
Listening for FlexRadio discovery packets...
   ⚠ No packets received for 30+ seconds
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

### Client Cannot Connect to Server

**Symptoms:**
```
⚠ Connection timeout to 10.255.0.1:5992
```

**Diagnosis:**
```bash
# Test VPN connectivity
ping 10.255.0.1

# Test TCP port
telnet 10.255.0.1 5992
# or
nc -zv 10.255.0.1 5992
```

**Solutions:**
1. Verify WireGuard tunnel is up: `wg show`
2. Check server firewall allows TCP 5992
3. Verify server is running and listening
4. Check client has correct server IP in config

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

### What v3.0 Does:
1. ✅ **Captures** real VITA-49 packets from FlexRadio
2. ✅ **Streams** complete packet via TCP to clients
3. ✅ **Works** over any L3 VPN (WireGuard, OpenVPN, etc.)
4. ✅ **Rebroadcasts** authentic packet locally
5. ✅ **SmartSDR** receives real discovery packet

### What It Does NOT Do:
- ❌ Generate synthetic packets (v1.x did this)
- ❌ Modify packet contents
- ❌ Require L2 VPN or bridging
- ❌ Require file shares or cloud storage
- ❌ Forward all broadcast traffic

### Why It Works With WireGuard:
- Uses standard L3 IP routing (WireGuard's strength!)
- TCP streaming is unicast (works over any VPN)
- Sub-second latency for discovery
- Only rebroadcasts on local subnet (client side)
- Radio connection uses unicast TCP/UDP (works via VPN)

---

## Quick Start for WireGuard Users

```bash
# Remote site (192.168.1.10):
1. Edit config.ini → verify Server_Address = 0.0.0.0
2. Ensure firewall allows TCP 5992
3. python FRS-Discovery-Server.py
4. Verify packets being captured

# Local PC (10.0.0.100):
1. Edit config.ini → Server_Address = 10.255.0.1 (WireGuard IP)
2. python FRS-Discovery-Client.py
3. Verify connection to server
4. Open SmartSDR → Radio appears!
```

**That's it! No L2 VPN, no bridging, no TAP mode, no file shares!**

---

**Author:** Chris L White, WX7V  
**License:** MIT  
**Not supported by FlexRadio Systems, Inc.**

**73 de WX7V**
