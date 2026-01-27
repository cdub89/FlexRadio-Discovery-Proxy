#!/usr/bin/env python3
"""
FlexRadio Discovery Proxy v1.0.1
Single-script architecture for VPN-based FlexRadio discovery.

This script generates synthetic VITA-49 discovery packets based on configuration
and rebroadcasts them on the local network for SmartSDR client discovery.

Copyright (c) 2026 Chris L White (WX7V)
Based on original work by VA3MW (2024)

Licensed under the MIT License - see LICENSE file for details

IMPORTANT: This software is NOT officially supported by FlexRadio Systems, Inc.,
its employees, or its help desk. This is an independent community tool.

For official FlexRadio support: https://www.flexradio.com
"""

import socket
import time
import subprocess
import datetime
import configparser
import platform
import logging
import struct

__version__ = "1.0.1"

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
print("\n" + "="*60)
print("FlexRadio Discovery Proxy v" + __version__)
print("="*60)
print("\nUser Settings\n")
print(f"Radio IP Address: {ip_address}")
print(f"Call Sign: {callsign}")
print(f"Nickname: {nickname}")
print(f"Version: {version}")
print(f"Serial Number: {serial}")
print(f"Model: {model}")
print(f"Radio License: {radio_license}")
print("\n" + "="*60 + "\n")

# Define the broadcast address and the UDP port number
broadcast_address = '255.255.255.255'
port = 4992

# Create and configure the UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# VITA-49 packet sequence counter (4-bit, wraps 0-15)
packet_counter = 0
last_status = None

try:
    while True:
        # Ping the IP address
        try:
            response = subprocess.run(['ping', ping_option, '1', ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            current_status = 'successful' if response.returncode == 0 else 'failed'
            current_time = datetime.datetime.now().strftime("%H:%M:%S")

            if current_status == 'successful':
                # Build the discovery message text with updated protocol version
                message_text = (
                    f'discovery_protocol_version=3.1.0.2 '
                    f'model={model} '
                    f'serial={serial} '
                    f'version={version} '
                    f'nickname={nickname} '
                    f'callsign={callsign} '
                    f'ip={ip_address} '
                    f'port=4992 '
                    f'status=Available '
                    f'inuse_ip= '
                    f'inuse_host= '
                    f'max_licensed_version=v4 '
                    f'radio_license_id={radio_license} '
                    f'fpc_mac= '
                    f'wan_connected=1 '
                    f'licensed_clients=2 '
                    f'available_clients=2 '
                    f'max_panadapters=4 '
                    f'available_panadapters=4 '
                    f'max_slices=4 '
                    f'available_slices=4 '
                    f'gui_client_ips= '
                    f'gui_client_hosts= '
                    f'gui_client_programs= '
                    f'gui_client_stations= '
                    f'gui_client_handles= '
                    f'min_software_version=2.1.20.0 '
                    f'external_port_link=1 '
                    f'license_is_unknown=0'
                )
                
                # Encode payload
                payload_bytes = message_text.encode('utf-8')
                
                # Add padding to align to 4-byte boundary (VITA-49 requirement)
                payload_len = len(payload_bytes)
                if payload_len % 4 != 0:
                    padding_needed = 4 - (payload_len % 4)
                    payload_bytes += b'\x00' * padding_needed
                
                # Calculate total packet size in 32-bit words
                # Header is 28 bytes (7 words) + padded payload
                total_bytes = 28 + len(payload_bytes)
                packet_size_words = total_bytes // 4
                
                # Get current Unix timestamp
                current_timestamp = int(time.time())
                
                # Build VITA-49 header (28 bytes) matching FLEX-6600 format
                # Per VITA-49.0 and FlexRadio implementation:
                # Bytes 0-3: VITA-49 header word
                #   Byte 0: 0x38 = packet type/flags (0011 1000)
                #           Bits 7-4: 0011 = packet type (Extension Data with Stream ID)
                #           Bits 3-0: 1000 = ClassID present, Integer timestamp, TSF=00
                #   Byte 1: upper flags/count field
                #           Bits 7-4: 0101 = TSI field (UTC timestamp)
                #           Bits 3-0: 4-bit packet sequence counter (0-15, wraps around)
                #   Bytes 2-3: Packet size in 32-bit words (big-endian uint16)
                
                # Construct byte 1: TSI field (0x50) + packet counter (0x00-0x0F)
                counter_byte = 0x50 | (packet_counter & 0x0F)
                
                vita_header = (
                    b'\x38' +                                  # Byte 0: Packet type/flags
                    bytes([counter_byte]) +                    # Byte 1: TSI + counter
                    struct.pack('>H', packet_size_words) +     # Bytes 2-3: Packet size in 32-bit words
                    b'\x00\x00\x08\x00' +                      # Bytes 4-7: Stream ID (0x00000800)
                    b'\x00\x00\x1C\x2D' +                      # Bytes 8-11: Class ID High (FlexRadio OUI)
                    b'\x53\x4C\xFF\xFF' +                      # Bytes 12-15: Class ID Low (SL = Signature Line)
                    struct.pack('>I', current_timestamp) +     # Bytes 16-19: Integer timestamp (Unix epoch)
                    b'\x00\x00\x00\x00\x00\x00\x00\x00'        # Bytes 20-27: Fractional timestamp (not used)
                )
                
                # Increment packet counter (wraps at 16)
                packet_counter = (packet_counter + 1) % 16
                
                # Combine header and payload
                message = vita_header + payload_bytes
                
                sock.sendto(message, (broadcast_address, port))
                print(f"{current_time} - Ping successful and Radio Broadcast message sent.")
                if last_status != current_status:
                    logging.info(f"{current_time} - Ping successful and Radio Broadcast message sent.")
                    last_status = current_status
                time.sleep(11)
            else:
                print(f"{current_time} - Ping failed, will retry in 10 seconds...")
                if last_status != current_status:
                    logging.warning(f"{current_time} - Ping status changed to failed.")
                    last_status = current_status
                time.sleep(10)

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
