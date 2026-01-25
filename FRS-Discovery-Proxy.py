import socket
import time
import subprocess
import datetime
import configparser
import platform
import logging
import struct

__version__ = "1.0.0"

# Configure logging
logging.basicConfig(filename='broadcast.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')
ip_address = config['DEFAULT']['IP_Address']
callsign = config['DEFAULT']['Callsign']
nickname = config['DEFAULT']['Nickname']
version = config['DEFAULT']['Version']
serial = config['DEFAULT']['Serial']
model = config['DEFAULT']['Model']
radio_license = config['DEFAULT']['Radio_License']

# Determine the ping command based on the OS
ping_option = '-n' if platform.system() == 'Windows' else '-c'

# Print user settings
print("\nUser Settings\n")
print(f"Radio IP Address: {ip_address}")
print(f"Call Sign: {callsign}")
print(f"Nickname: {nickname}")
print(f"Version: {version}")
print(f"Serial Number: {serial}")
print(f"Model: {model}")
print(f"Radio License: {radio_license}")
print("\n")

# Define the broadcast address and the UDP port number
broadcast_address = '255.255.255.255'
port = 4992

# Create and configure the UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

last_status = None

try:
    while True:
        # Ping the IP address
        try:
            response = subprocess.run(['ping', ping_option, '1', ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            current_status = 'successful' if response.returncode == 0 else 'failed'
            current_time = datetime.datetime.now().strftime("%H:%M:%S")

            if current_status == 'successful':
                # Build the discovery message text
                message_text = f'discovery_protocol_version=3.1.0.2 model={model} serial={serial} version={version} nickname={nickname} callsign={callsign} ip={ip_address} port=4992 status=Available inuse_ip= inuse_host= max_licensed_version=v4 radio_license_id={radio_license} fpc_mac= wan_connected=1 licensed_clients=2 available_clients=2 max_panadapters=4 available_panadapters=4 max_slices=4 available_slices=4 gui_client_ips= gui_client_hosts= gui_client_programs= gui_client_stations= gui_client_handles= min_software_version=2.1.20.0 external_port_link=1 license_is_unknown=0\x00\x00\x00'
                
                # Calculate packet size in 32-bit words
                # VITA-49 header is 28 bytes (7 words), payload needs to be counted
                payload_bytes = message_text.encode('utf-8')
                total_bytes = 28 + len(payload_bytes)
                # Round up to nearest 4-byte boundary and add padding if needed
                if total_bytes % 4 != 0:
                    padding_needed = 4 - (total_bytes % 4)
                    payload_bytes += b'\x00' * padding_needed
                    total_bytes += padding_needed
                packet_size_words = total_bytes // 4
                
                # Get current Unix timestamp
                current_timestamp = int(time.time())
                
                # Build VITA-49 header (28 bytes) matching FLEX-6600 format
                vita_header = (
                    b'\x38\x5C' +                              # Bytes 0-1: Packet type and flags
                    struct.pack('>H', packet_size_words) +     # Bytes 2-3: Packet size in 32-bit words
                    b'\x00\x00\x08\x00' +                      # Bytes 4-7: Stream ID
                    b'\x00\x00\x1C\x2D\x53\x4C' +              # Bytes 8-13: Class ID (FlexRadio OUI: 00-1C-2D)
                    b'\xFF\xFF' +                              # Bytes 14-15: Information/Packet class codes
                    struct.pack('>I', current_timestamp) +     # Bytes 16-19: Integer timestamp (Unix epoch)
                    b'\x00\x00\x00\x00\x00\x00\x00\x00'        # Bytes 20-27: Fractional timestamp (not used)
                )
                
                # Combine header and payload
                message = vita_header + payload_bytes
                
                sock.sendto(message, (broadcast_address, port))
                print(f"{current_time} - Ping successful and Radio Broadcast message sent.")
                if last_status != current_status:
                    logging.info(f"{current_time} - Ping successful and Radio Broadcast message sent.")
                    last_status = current_status
                time.sleep(10)
            else:
                print(f"{current_time} - Ping failed, will retry in 30 seconds...")
                if last_status != current_status:
                    logging.warning(f"{current_time} - Ping status changed to failed.")
                    last_status = current_status
                time.sleep(30)

        except Exception as e:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"{current_time} - Error: {e}")
            if last_status != 'exception':
                logging.error(f"{current_time} - Error during ping or UDP broadcast: {e}")
                last_status = 'exception'
finally:
    sock.close()
    logging.info("Socket closed and program terminated.")
    print("Socket closed and program terminated.")
