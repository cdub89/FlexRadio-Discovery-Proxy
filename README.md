# Fork of **VA3MW** FlexRadio Broadcast Wedge.  Enhanced by Chris L White, WX7V 2026.
# Updated documentation and logic to help dynamically build the VITA-49 discovery packet for SmartSDR 4.1.5

## WARNING: USE AT YOUR OWN RISK

This script is provided "as is," without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, 
out of, or in connection with the script or the use or other dealings in the script.

By using this script, you acknowledge and agree that you understand this warning, and any use of the script is entirely at your own risk. Any damage caused by the deployment or use of this script is the sole responsibility of the user, and the authors or distributors of this script cannot be held liable for any adverse consequences arising therefrom.

**This script is not supported in any way by FlexRadio Inc.**

---

## Overview

This Python script enables FlexRadio SmartSDR clients to discover and connect to FlexRadio transceivers 
that are not on the same local subnet. It acts as a "wedge" by rebroadcasting VITA-49 discovery packets 
on the local network, allowing clients to see remote radios (e.g., over VPN connections) as if they were local.

The script uses the **VITA-49** packet format, which is the standard used by FlexRadio for discovery broadcasts.

---

## How It Works

1. **Monitors Radio Availability**: Continuously pings the target radio's IP address
2. **Generates VITA-49 Packets**: Creates properly formatted discovery packets with dynamic timestamps
3. **Broadcasts Discovery**: Sends UDP broadcasts to 255.255.255.255:4992 (FlexRadio discovery port)
4. **Client Discovery**: SmartSDR clients on the local network receive these broadcasts and can connect to the remote radio

---

## Dependencies

### Python Version
- **Python 3.x** is required (Python 2.x is NOT supported)
- Download from: https://www.python.org/downloads/

### Standard Libraries (Built-in)
The script uses only Python standard libraries:
- `socket` - Network connections and UDP broadcast
- `subprocess` - Executing ping commands
- `time` - Timing and delays
- `datetime` - Timestamps for logging
- `configparser` - Reading configuration files
- `platform` - OS detection for cross-platform compatibility
- `logging` - Activity logging to broadcast.log
- `struct` - Binary data packing for VITA-49 headers

**No external packages need to be installed.**

---

## System Requirements

### Operating System
- **Primary**: Windows (tested and optimized)
- **Linux/macOS**: Supported with automatic ping command adjustment (`-n` vs `-c`)

### Network Permissions
- Permission to send UDP broadcast packets
- Permission to execute ping commands
- Firewall rules allowing:
  - Outbound UDP to port 4992
  - ICMP ping requests to target radio
  - UDP broadcasts on local network

**Note**: Antivirus and firewall settings may need adjustment.

---

## Configuration

### config.ini Setup

Users **must** configure ALL variables in `config.ini` to match their target radio:

```ini
[DEFAULT]
IP_Address = 192.168.x.x
Callsign = CALL
Nickname = Radio-Nickname
Version = 4.1.5.39794
Serial = XXX-XXXX-XXXX-XXXX
Model = FLEX-6600
Radio_License = 00-1C-2D-XX-XX-XX
```

### Finding Your Radio's Information

To obtain the correct values for your radio:

1. **Capture a discovery packet** using Wireshark or tcpdump:
   - Filter: `udp.port == 4992`
   - Look for packets from your radio's IP
   - Extract values from the text payload

2. **Or use SmartSDR**:
   - Connect to your radio locally
   - Radio information is displayed in the client
   - MAC address is typically the Radio_License value

---

## Usage

1. **Edit config.ini** with your radio's parameters
2. **Run the script**:
   ```bash
   python FRS-Wedge.py
   ```
   Or on Windows, double-click `FRS-Wedge.bat`

3. **Verify operation**: Console should display:
   ```
   User Settings
   
   Radio IP Address: 192.168.X.XXX
   Call Sign: WX7V
   ...
   
   HH:MM:SS - Ping successful and Radio Broadcast message sent.
   ```

4. **Open SmartSDR client**: Your remote radio should now appear in the radio chooser

5. **Connect**: Click the radio to establish connection (VPN/route to radio IP must be working)

### Note on Termination
After connecting, the script can be terminated if desired. However, **there is no risk** in leaving 
it running continuously. If the script is stopped, SmartSDR will lose discovery but existing 
connections will remain active.

---

## VITA-49 Packet Structure

The script generates discovery packets using the VITA-49 standard format:

### Packet Composition

```
[28-byte VITA-49 Header] + [Variable-length Text Payload] + [Padding to 4-byte boundary]
```

### VITA-49 Header Breakdown (28 bytes)

| Bytes | Field | Description | Current Value |
|-------|-------|-------------|---------------|
| 0-1 | Packet Type & Flags | VITA-49 packet identifier | `0x38 0x5C` |
| 2-3 | Packet Size | Total packet size in 32-bit words | **Dynamic** (calculated) |
| 4-7 | Stream ID | Data stream identifier | `0x00 0x00 0x08 0x00` |
| 8-13 | Class ID | Contains FlexRadio OUI (00-1C-2D) | `0x00 0x00 0x1C 0x2D 0x53 0x4C` |
| 14-15 | Class Codes | Information/Packet class codes | `0xFF 0xFF` |
| 16-19 | Integer Timestamp | Unix epoch timestamp (seconds) | **Dynamic** (current time) |
| 20-27 | Fractional Timestamp | Sub-second precision (not used) | `0x00` (8 bytes) |

### Text Payload Format

The payload is a space-separated list of key=value pairs following FlexRadio's discovery protocol:

```
discovery_protocol_version=3.1.0.2 model=FLEX-6600 serial=xxxx-xxxx-xxxx-xxxx 
version=4.1.5.39794 nickname=Lake6600 callsign=WX7V ip=192.168.0.101 port=4992 
status=Available inuse_ip= inuse_host= max_licensed_version=v4 
radio_license_id=00-1C-2D-05-0A-5A fpc_mac= wan_connected=1 licensed_clients=2 
available_clients=2 max_panadapters=4 available_panadapters=4 max_slices=4 
available_slices=4 gui_client_ips= gui_client_hosts= gui_client_programs= 
gui_client_stations= gui_client_handles= min_software_version=2.1.20.0 
external_port_link=1 license_is_unknown=0
```

Terminated with three null bytes: `\x00\x00\x00`

---

## Updating the VITA-49 Header for Future Changes

If FlexRadio updates their discovery protocol, you may need to update the `vita_header` construction. 
Here's how:

### Step 1: Capture Your Radio's Discovery Packet

Use **Wireshark** or **tcpdump** to capture a packet:

**Wireshark Filter:**
```
udp.port == 4992 and ip.src == <your_radio_ip>
```

**tcpdump Command:**
```bash
tcpdump -i any -X udp port 4992
```

### Step 2: Locate the VITA-49 Header

In the packet capture, find the UDP payload (skip Ethernet, IP, and UDP headers).

**Example from packet capture:**
```
UDP Payload starts at offset 0x002A:
002A: 38 5c 00 b4 00 00 08 00 00 00 1c 2d 53 4c ff ff
003A: 69 75 47 db 00 00 00 00 00 00 00 00
```

The first **28 bytes** (0x002A through 0x0045) are the VITA-49 header.

### Step 3: Identify What Changed

Compare with the current header in the script (lines 102-110):

```python
vita_header = (
    b'\x38\x5C' +                              # Bytes 0-1
    struct.pack('>H', packet_size_words) +     # Bytes 2-3 (DYNAMIC - don't change)
    b'\x00\x00\x08\x00' +                      # Bytes 4-7
    b'\x00\x00\x1C\x2D\x53\x4C' +              # Bytes 8-13
    b'\xFF\xFF' +                              # Bytes 14-15
    struct.pack('>I', current_timestamp) +     # Bytes 16-19 (DYNAMIC - don't change)
    b'\x00\x00\x00\x00\x00\x00\x00\x00'        # Bytes 20-27
)
```

### Step 4: Update Static Bytes ONLY

**DO NOT CHANGE:**
- Bytes 2-3: `struct.pack('>H', packet_size_words)` - automatically calculated
- Bytes 16-19: `struct.pack('>I', current_timestamp)` - dynamically generated

**CAN CHANGE:**
- Bytes 0-1: Packet type/flags
- Bytes 4-7: Stream ID
- Bytes 8-13: Class ID (FlexRadio OUI)
- Bytes 14-15: Class codes
- Bytes 20-27: Fractional timestamp (if FlexRadio starts using it)

### Step 5: Update the Text Payload

If new fields are added to the discovery protocol, update line 85:

**Example:** If FlexRadio adds a new field `new_field=value`:

```python
message_text = f'discovery_protocol_version=3.1.0.2 model={model} ... new_field=value ...\x00\x00\x00'
```

**Important Notes:**
1. Keep fields in the same order as your captured packet
2. Maintain proper spacing (single space between fields)
3. Keep the `\x00\x00\x00` terminator at the end
4. Format must exactly match: `key=value key=value ...`

### Step 6: Test

Run the script and verify:
1. No errors in console
2. SmartSDR client can see the radio
3. Connection works properly

### Troubleshooting Header Updates

If SmartSDR still throws exceptions after updating:

1. **Verify byte order**: VITA-49 uses **big-endian** (network byte order)
   - Use `struct.pack('>...', ...)` where `>` means big-endian

2. **Check packet size calculation**: Ensure it includes header + payload + padding

3. **Validate 4-byte alignment**: Total packet must be divisible by 4

4. **Compare hex dumps**: Use a hex editor to compare your script's output with actual radio packets

5. **Check protocol version**: Update line 85 if FlexRadio changes from 3.1.0.2

---

## Logging

The script logs activity to `broadcast.log`:
- INFO: Successful state changes (ping success)
- WARNING: Ping failures
- ERROR: Exceptions during operation

Logs only record **state changes** to avoid file bloat during continuous operation.

---

## Troubleshooting

### Radio Not Appearing in SmartSDR
1. Check firewall allows UDP port 4992 outbound
2. Verify config.ini settings match your radio exactly
3. Ensure VPN/network route to radio IP is working
4. Check broadcast.log for errors

### SmartSDR Exception on Discovery
1. Capture a fresh discovery packet from your radio
2. Update VITA-49 header bytes to match (see "Updating the VITA-49 Header" above)
3. Verify protocol version in message_text

### Ping Successful but No Broadcast
1. Check UDP broadcast permissions
2. Verify 255.255.255.255 broadcasts are allowed on your network
3. Try running as administrator (Windows)

### Script Won't Start
1. Ensure Python 3.x is installed: `python --version`
2. Verify config.ini exists and is properly formatted
3. Check broadcast.log for startup errors

---

## Credits

Written by **VA3MW** with assistance from ChatGPT-4  
Original: May 2024  
Updated: January 2026 (VITA-49 header improvements) by Chris L White **WX7V**  

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

This software is provided "AS IS", WITHOUT WARRANTY OF ANY KIND. See the full license text for complete terms and conditions.
