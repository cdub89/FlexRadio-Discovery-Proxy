# Configuration Setup Guide

## First-Time Setup

When setting up the FlexRadio Discovery Proxy for the first time, you'll need to create your personal configuration files from the provided templates.

### Step 1: Create Your Configuration File

Copy the template file to create your personal configuration:

```bash
# On Windows (PowerShell)
Copy-Item config.ini.template config.ini

# On Linux/Mac
cp config.ini.template config.ini
```

### Step 2: Edit Your Configuration

Open `config.ini` in your text editor and customize the following settings:

#### For Server Configuration:
- **Listen_Address**: Usually keep as `0.0.0.0` (all interfaces)
- **Discovery_Port**: Keep as `4992` (FlexRadio standard)
- **Stream_Port**: Keep as `5992` or customize if needed
- **Max_Clients**: Adjust based on how many clients you expect

#### For Client Configuration:
- **Server_Address**: Set to your server's IP address (e.g., `10.8.0.1` for VPN or `192.168.1.25` for local network)
- **Stream_Port**: Must match the server's `Stream_Port`
- **Reconnect_Interval**: Adjust if you want faster/slower reconnection attempts
- **Use_Cached_Packet**: Set to `true` to enable offline operation
- **Max_Cache_Age**: Maximum age of cached packet in seconds

#### For Diagnostics:
- **Enable_Health_Checks**: `true` or `false` to enable/disable health monitoring
- **Debug_Logging**: Set to `true` only when troubleshooting (creates verbose logs)
- **Test_Server_IP**: (Client only) Set to server IP to test connectivity
- **Test_Radio_IP**: (Server only) Set to radio IP to monitor connectivity

### Step 3: Verify Your Configuration

Run the appropriate script to test your configuration:

```bash
# Server test
python FRS-Discovery-Server.py

# Client test
python FRS-Discovery-Client.py
```

## Important Notes

### File Exclusions

The following files are **excluded from version control** and contain your personal network information:

- `config.ini` - Your personal configuration
- `last_discovery_packet.json` - Runtime cache file
- `*.log` - All log files

### Template Files (Version Controlled)

These files **are** included in version control as examples:

- `config.ini.template` - Configuration template with example values
- `last_discovery_packet.json.template` - Example cached packet structure

### Never Commit Personal Information

⚠️ **Warning**: Never commit your actual `config.ini` file to version control, as it may contain:
- Internal IP addresses
- Network topology information
- Radio serial numbers
- Amateur radio callsigns
- Other personally identifiable information

## Updating Configuration

When updating your configuration:

1. Make changes to your `config.ini` file (not the template)
2. Test the changes
3. If you want to share a new configuration option, update `config.ini.template` with example values

## Troubleshooting

If you're having configuration issues:

1. Compare your `config.ini` with `config.ini.template` to ensure you have all required fields
2. Check the log files (`discovery-server.log` or `discovery-client.log`)
3. Enable `Debug_Logging = true` in the `[DIAGNOSTICS]` section for detailed output
4. Verify network connectivity using the health check features

## Example Configurations

### Example 1: VPN Remote Access

**Server** (at radio site):
```ini
[SERVER]
Listen_Address = 0.0.0.0
Stream_Port = 5992
```

**Client** (remote location via VPN):
```ini
[CLIENT]
Server_Address = 10.8.0.1  # VPN server IP
Stream_Port = 5992
Use_Cached_Packet = true
```

### Example 2: Local Network

**Server**:
```ini
[SERVER]
Listen_Address = 192.168.1.25
Stream_Port = 5992
```

**Client** (same network):
```ini
[CLIENT]
Server_Address = 192.168.1.25
Stream_Port = 5992
Use_Cached_Packet = false
```

## See Also

- `README.md` - Main documentation
- `TROUBLESHOOTING.md` - Common issues and solutions
- `HEALTH_CHECK_GUIDE.md` - Health check features
