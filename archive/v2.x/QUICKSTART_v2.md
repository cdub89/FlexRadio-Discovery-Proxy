# FlexRadio Discovery Proxy v2.0 - Quick Start Guide

**Goal:** Get your remote FlexRadio discoverable in SmartSDR in 15 minutes.

---

## ⚠️ Important Notice

**This software is NOT officially supported by FlexRadio Systems, Inc.**

This is an independent, community-developed tool. For official FlexRadio support, visit https://www.flexradio.com or https://helpdesk.flexradio.com

**License:** MIT License - Copyright © 2026 Chris L White (WX7V)

---

## Prerequisites

- [ ] Python 3.6+ installed on both machines
- [ ] FlexRadio broadcasting on remote network
- [ ] Shared storage accessible from both locations (network share or cloud)

---

## 5-Minute Setup (Cloud Storage Method)

### Step 1: Install Dropbox/OneDrive (Both Machines)

**Remote machine (where FlexRadio is):**
```powershell
# Install Dropbox/OneDrive/Google Drive
# Create folder: FlexRadio
# Note the path: C:\Users\YourName\Dropbox\FlexRadio
```

**Local machine (where SmartSDR is):**
```powershell
# Install same cloud service
# Wait for FlexRadio folder to sync
```

### Step 2: Configure Server (Remote Machine)

Edit `config-v2.ini`:
```ini
[SERVER]
Listen_Address = 0.0.0.0
Discovery_Port = 4992
Shared_File_Path = C:\Users\YourName\Dropbox\FlexRadio\discovery.json
Update_Interval = 2.0
```

### Step 3: Start Server (Remote Machine)

```powershell
python FRS-Discovery-Server-v2.py
```

**Look for:**
```
Packet #1 from 192.168.0.101
  Radio: FLEX-6600 (Lake6600)
  → Packet written to: ...discovery.json
```

### Step 4: Configure Client (Local Machine)

Edit `config-v2.ini`:
```ini
[CLIENT]
Shared_File_Path = C:\Users\YourName\Dropbox\FlexRadio\discovery.json
Broadcast_Address = 255.255.255.255
Discovery_Port = 4992
Check_Interval = 3.0
Max_File_Age = 15.0
```

**Important:** Use the **same path** as server!

### Step 5: Start Client (Local Machine)

```powershell
python FRS-Discovery-Client-v2.py
```

**Look for:**
```
Radio discovered:
  FLEX-6600 (Lake6600)
✓ Started broadcasting discovery packets
```

### Step 6: Open SmartSDR

Your radio should appear in the chooser. Click to connect!

---

## 10-Minute Setup (Network Share Method)

### Step 1: Create Share (Remote Machine)

**Windows:**
```powershell
mkdir C:\FlexRadio
New-SmbShare -Name "FlexRadio" -Path "C:\FlexRadio" -FullAccess "Everyone"
```

**Linux:**
```bash
mkdir /srv/flexradio
# Add to /etc/samba/smb.conf:
# [FlexRadio]
#   path = /srv/flexradio
#   read only = no
```

### Step 2: Mount Share (Local Machine)

**Windows:**
```powershell
net use Z: \\server-name\FlexRadio
```

**Linux:**
```bash
mount -t cifs //server-name/FlexRadio /mnt/flexradio
```

### Step 3: Configure Both Machines

**Server config-v2.ini:**
```ini
[SERVER]
Shared_File_Path = C:\FlexRadio\discovery.json
```

**Client config-v2.ini:**
```ini
[CLIENT]
Shared_File_Path = Z:\discovery.json
```

### Step 4: Start Both Scripts

**Remote:**
```powershell
python FRS-Discovery-Server-v2.py
```

**Local:**
```powershell
python FRS-Discovery-Client-v2.py
```

### Step 5: Open SmartSDR

Done!

---

## Troubleshooting (2 Minutes)

### "No packets received"
- Is radio powered on?
- Is radio on same subnet as server?

### "File not found"
- Did server write file first?
- Is path correct on both sides?
- Has cloud service synced?

### "Stale file"
- Is server still running?
- Check `discovery-server.log`

### "Radio not in SmartSDR"
- Is client broadcasting? Check console output
- Windows Firewall blocking Python?
- Run client as Administrator

---

## Testing

### Verify Server Works
```powershell
# Should see in server console:
Packet #1 from 192.168.0.101
  → Packet written to: ...

# Should see file created:
dir <path>\discovery.json
```

### Verify Client Works
```powershell
# Should see in client console:
Radio discovered:
  FLEX-6600 (Lake6600)
✓ Started broadcasting

# Should see broadcasts in Wireshark:
Filter: udp.port == 4992
```

### Verify SmartSDR
```
1. Open SmartSDR
2. Look for your radio in chooser
3. Click to connect
4. Should connect normally
```

---

## Daily Operation

### Starting System

**Remote location (once):**
```powershell
# Leave running 24/7
python FRS-Discovery-Server-v2.py
```

**Local PC (when using SmartSDR):**
```powershell
# Start before opening SmartSDR
python FRS-Discovery-Client-v2.py

# Or double-click:
FRS-Discovery-Client-v2.bat
```

### Stopping System

Just press `Ctrl+C` in each window. That's it!

---

## Next Steps

- Read [README_v2.md](README_v2.md) for full documentation
- See [MIGRATION_GUIDE_v1_to_v2.md](MIGRATION_GUIDE_v1_to_v2.md) if coming from v1.x
- Review [RELEASE_NOTES_v2.0.0.md](RELEASE_NOTES_v2.0.0.md) for technical details

---

## Support

Issues? Check logs:
- Server: `discovery-server.log`
- Client: `discovery-client.log`

Questions? Contact WX7V via GitHub or QRZ.

**Not supported by FlexRadio Systems, Inc.**

---

**That's it! Enjoy your remote FlexRadio access!**

**73 de WX7V**
