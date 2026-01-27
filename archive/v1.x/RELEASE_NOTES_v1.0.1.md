# FlexRadio Discovery Proxy - Release Notes v1.0.1

**Release Date:** January 25, 2026  
**Build:** v1.0.1 Stability Update

---

## Summary

This release addresses critical network stability issues identified in v1.0.0 that caused unreliable connections to SmartSDR clients.

---

## Critical Fixes

### 1. **Fixed Retry Timing for Failed Pings**
**Issue:** When ping failures occurred, v1.0.0 waited 30 seconds before retrying, causing long gaps in discovery broadcasts and apparent "radio offline" status in SmartSDR.

**Fix:** Restored the original 10-second retry interval from the Original-FRS-Wedge.py script.

**Impact:** 
- Dramatically improved recovery time from temporary network interruptions
- Reduced apparent "offline" time from 30s to 10s
- Better alignment with FlexRadio's typical 2-5 second broadcast intervals

```python
# Before (v1.0.0):
time.sleep(30)  # Failed ping - 30 second wait

# After (v1.0.1):
time.sleep(10)  # Failed ping - 10 second wait (matches original)
```

### 2. **Fixed Successful Broadcast Interval**
**Issue:** v1.0.0 used a 10-second interval between successful broadcasts, which was too aggressive compared to the proven original implementation.

**Fix:** Restored the 11-second interval from Original-FRS-Wedge.py.

**Impact:**
- Reduced unnecessary network traffic
- Better stability with FlexRadio clients
- Matches the proven timing from the original working implementation

```python
# Before (v1.0.0):
time.sleep(10)  # Successful ping - 10 second interval

# After (v1.0.1):
time.sleep(11)  # Successful ping - 11 second interval (matches original)
```

### 3. **Improved Payload Formatting**
**Issue:** The payload string in v1.0.0 was constructed as a single long line, making it difficult to audit and maintain.

**Fix:** Reformatted the message_text construction to use multi-line f-strings with clear field separation.

**Impact:**
- Easier to read and verify all fields
- Simpler to add/modify fields in future updates
- No functional change, just improved code maintainability

### 4. **Enhanced User Interface**
**Issue:** Basic startup display didn't clearly identify the running version.

**Fix:** Added formatted header with version information and visual separators.

```
============================================================
FlexRadio Discovery Proxy v1.0.1
============================================================

User Settings

Radio IP Address: 192.168.0.101
Call Sign: WX7V
Nickname: Lake6600
Version: 4.1.5.39794
Serial Number: 3718-0522-6600-0003
Model: FLEX-6600
Radio License: 00-1C-2D-05-0A-5A

============================================================
```

---

## Technical Analysis

### Root Cause of Network Instability

The comparison between Original-FRS-Wedge.py and FRS-Discovery-Proxy.py v1.0.0 revealed:

1. **30-Second Failure Gap:** The primary issue was the tripled retry time (10s → 30s) on failed pings. During network hiccups or temporary connectivity issues, this created a 30-second gap where no discovery packets were sent, causing SmartSDR clients to mark the radio as offline.

2. **Aggressive Broadcast Timing:** The reduced success interval (11s → 10s) may have caused timing conflicts with actual FlexRadio discovery packets on networks where both exist.

3. **Cumulative Effect:** Combined, these timing changes created a less stable connection profile that was particularly problematic during:
   - WiFi interference or signal drops
   - Router/switch temporary congestion
   - VPN tunnel fluctuations
   - DHCP renewals

### What Remained Correct in v1.0.0

The following elements were already correct and remain unchanged:
- VITA-49 header construction (28 bytes)
- Packet sequence counter implementation
- Stream ID, Class ID, and OUI values
- 4-byte padding alignment
- Dynamic timestamp generation
- Protocol version update (3.1.0.2)
- SmartSDR 4.x field compatibility

---

## Testing Recommendations

After deploying v1.0.1, monitor for:

1. **Connection Stability:**
   - Radio should remain visible in SmartSDR during minor network hiccups
   - Recovery from ping failures should occur within 10-15 seconds

2. **Log Monitoring:**
   - Check `broadcast.log` for frequent status transitions
   - Successful broadcasts should occur every ~11 seconds
   - Failed ping retries should be every ~10 seconds

3. **Network Load:**
   - Verify UDP broadcast traffic on port 4992
   - Confirm packet structure matches VITA-49 specification
   - Use Wireshark to validate packet format if issues persist

---

## Upgrade Instructions

### From v1.0.0 to v1.0.1:

1. Stop the running FRS-Discovery-Proxy script (Ctrl+C)
2. Replace `FRS-Discovery-Proxy.py` with the v1.0.1 version
3. No configuration changes needed - `config.ini` remains unchanged
4. Restart using the same method (batch file or direct Python execution)

### Verification:

```bash
# Check version in startup banner
python FRS-Discovery-Proxy.py

# Should display:
# ============================================================
# FlexRadio Discovery Proxy v1.0.1
# ============================================================
```

---

## Known Limitations

These limitations exist in both v1.0.0 and v1.0.1:

1. **Single Radio Support:** Only one radio can be proxied per instance
2. **Broadcast Only:** Does not support multicast discovery (255.255.255.255 only)
3. **Static Configuration:** Changes to `config.ini` require script restart
4. **No Auto-Discovery:** Cannot automatically detect the radio's real IP
5. **Ping-Based Detection:** Relies on ICMP ping, which may be blocked by some firewalls

---

## Future Enhancements (Not in v1.0.1)

Potential improvements for future releases:

- Multi-radio support with separate configurations
- Actual packet listening and rebroadcast (true proxy mode)
- Dynamic IP detection and tracking
- Web-based configuration interface
- System service/daemon installation scripts
- Health monitoring dashboard
- Support for SmartSDR 5.x when released

---

## Credits

**Original Concept:** VA3MW - FlexRadio Broadcast Wedge (2024)  
**Fork & Enhancement:** Chris L White, WX7V (2026)  
**Protocol Documentation:** FlexRadio Systems VITA-49 Implementation

---

## License

MIT License - See LICENSE file for details

---

## Support & Contact

This script is provided as-is and is **not supported by FlexRadio Systems, Inc.**

For issues, enhancements, or questions:
- GitHub Issues: [Your Repository URL]
- Email: [Your Contact]
- QRZ: WX7V

---

**USE AT YOUR OWN RISK**

This software is provided "as is" without warranty of any kind. The authors are not liable for any damages arising from its use.
