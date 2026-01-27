#!/usr/bin/env python3
"""
FlexRadio Discovery Server v2.1.0
Captures FlexRadio VITA-49 discovery packets and writes them to a shared file.

This script runs on the remote location where the FlexRadio is located.
It listens for actual discovery broadcasts and saves them for the client to rebroadcast.

Copyright (c) 2026 Chris L White (WX7V)
Based on original work by VA3MW (2024)

Licensed under the MIT License - see LICENSE file for details

IMPORTANT: This software is NOT officially supported by FlexRadio Systems, Inc.,
its employees, or its help desk. This is an independent community tool.

For official FlexRadio support: https://www.flexradio.com
"""

import socket
import time
import datetime
import configparser
import logging
import json
import os
import sys
from health_checks import HealthChecker

__version__ = "2.1.0"

# Configure logging
logging.basicConfig(
    filename='discovery-server.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_config():
    """Load configuration from config-v2.ini"""
    config = configparser.ConfigParser()
    
    if not os.path.exists('config-v2.ini'):
        print("ERROR: config-v2.ini not found!")
        logging.error("config-v2.ini not found")
        sys.exit(1)
    
    config.read('config-v2.ini')
    return config

def parse_discovery_payload(payload):
    """Parse the space-separated key=value pairs from discovery payload"""
    try:
        # Decode bytes to string, strip null bytes
        payload_str = payload.decode('utf-8', errors='ignore').rstrip('\x00')
        
        # Parse key=value pairs
        parsed = {}
        pairs = payload_str.split(' ')
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                parsed[key] = value
        
        return parsed
    except Exception as e:
        logging.error(f"Error parsing payload: {e}")
        return {}

def main():
    print("\n" + "="*70)
    print(f"FlexRadio Discovery Server v{__version__}")
    print("="*70)
    
    # Load configuration
    config = load_config()
    
    # Server settings
    listen_address = config['SERVER']['Listen_Address']
    discovery_port = int(config['SERVER']['Discovery_Port'])
    shared_file_path = config['SERVER']['Shared_File_Path']
    update_interval = float(config['SERVER']['Update_Interval'])
    
    print("\nServer Configuration:")
    print(f"  Listen Address: {listen_address}")
    print(f"  Discovery Port: {discovery_port}")
    print(f"  Shared File: {shared_file_path}")
    print(f"  Update Interval: {update_interval}s")
    
    logging.info(f"Server v{__version__} started - Listening on {listen_address}:{discovery_port}")
    
    # Run startup health checks
    health_checker = HealthChecker(config, mode='server')
    if health_checker.enabled and health_checker.startup_tests:
        print()  # Blank line before health checks
        health_checker.run_all_checks()
        overall_status = health_checker.print_results(title="Startup Health Check")
    else:
        print("\n" + "="*70)
    
    print("\nListening for FlexRadio discovery packets...\n")
    
    # Create UDP socket for listening
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Bind to the discovery port
        sock.bind((listen_address, discovery_port))
        sock.settimeout(1.0)  # 1 second timeout for periodic checks
        
        last_packet_time = None
        last_write_time = 0
        packet_count = 0
        last_health_check = time.time()
        
        while True:
            try:
                # Receive discovery packet
                data, addr = sock.recvfrom(4096)
                
                current_time = time.time()
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                packet_count += 1
                
                # Only process if it's a valid VITA-49 packet
                if len(data) >= 28 and data[0:1] == b'\x38':
                    # Extract the full packet
                    packet_hex = data.hex()
                    
                    # Try to parse the payload (starts at byte 28)
                    if len(data) > 28:
                        payload = data[28:]
                        parsed_info = parse_discovery_payload(payload)
                        
                        # Extract key information
                        radio_info = {
                            'model': parsed_info.get('model', 'Unknown'),
                            'serial': parsed_info.get('serial', 'Unknown'),
                            'ip': parsed_info.get('ip', addr[0]),
                            'nickname': parsed_info.get('nickname', 'Unknown'),
                            'callsign': parsed_info.get('callsign', 'Unknown'),
                            'version': parsed_info.get('version', 'Unknown'),
                            'status': parsed_info.get('status', 'Unknown')
                        }
                        
                        print(f"{timestamp} - Packet #{packet_count} from {addr[0]}")
                        print(f"  Radio: {radio_info['model']} ({radio_info['nickname']})")
                        print(f"  Callsign: {radio_info['callsign']} | IP: {radio_info['ip']}")
                        print(f"  Status: {radio_info['status']} | Version: {radio_info['version']}")
                        
                        # Write to shared file (rate limited by update_interval)
                        if current_time - last_write_time >= update_interval:
                            packet_data = {
                                'timestamp': timestamp,
                                'timestamp_unix': current_time,
                                'server_version': __version__,
                                'packet_hex': packet_hex,
                                'packet_size': len(data),
                                'source_ip': addr[0],
                                'source_port': addr[1],
                                'radio_info': radio_info,
                                'parsed_payload': parsed_info
                            }
                            
                            try:
                                # Write to shared file
                                with open(shared_file_path, 'w') as f:
                                    json.dump(packet_data, f, indent=2)
                                
                                print(f"  → Packet written to: {shared_file_path}")
                                logging.info(f"Packet written - Radio: {radio_info['model']} {radio_info['nickname']}")
                                last_write_time = current_time
                                
                            except Exception as e:
                                print(f"  ⚠ Error writing to shared file: {e}")
                                logging.error(f"File write error: {e}")
                        
                        last_packet_time = current_time
                
            except socket.timeout:
                # Normal timeout - check if we haven't received packets recently
                current_time_val = time.time()
                if last_packet_time and (current_time_val - last_packet_time > 30):
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"{current_time} - No packets received for 30+ seconds")
                    logging.warning("No discovery packets received for 30+ seconds")
                    last_packet_time = None
                
                # Periodic health check
                if (health_checker.enabled and 
                    health_checker.periodic_interval > 0 and 
                    current_time_val - last_health_check >= health_checker.periodic_interval):
                    
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"\n{current_time} - Running periodic health check...")
                    health_checker.run_all_checks()
                    health_checker.print_results(title="Periodic Health Check")
                    last_health_check = current_time_val
                
                continue
                
            except KeyboardInterrupt:
                raise
                
            except Exception as e:
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                print(f"{current_time} - Error processing packet: {e}")
                logging.error(f"Packet processing error: {e}")
                continue
    
    except KeyboardInterrupt:
        print("\n\nShutdown requested by user...")
        logging.info("Server shutdown by user")
    
    except Exception as e:
        print(f"\nFatal error: {e}")
        logging.error(f"Fatal error: {e}")
    
    finally:
        sock.close()
        print("Socket closed. Server stopped.")
        logging.info("Server stopped")

if __name__ == "__main__":
    main()
