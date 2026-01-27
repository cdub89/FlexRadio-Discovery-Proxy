#!/usr/bin/env python3
"""
FlexRadio Discovery Client v2.1.0
Reads FlexRadio discovery packets from shared file and rebroadcasts locally.

This script runs on the local PC where SmartSDR client is running.
It reads discovery packets captured by the server and rebroadcasts them.

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
    filename='discovery-client.log',
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

def read_discovery_file(file_path):
    """Read and parse the discovery packet from shared file"""
    try:
        if not os.path.exists(file_path):
            return None, "File not found"
        
        # Check file age
        file_mod_time = os.path.getmtime(file_path)
        file_age = time.time() - file_mod_time
        
        # Read file
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return data, file_age
    
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        return None, str(e)

def main():
    print("\n" + "="*70)
    print(f"FlexRadio Discovery Client v{__version__}")
    print("="*70)
    
    # Load configuration
    config = load_config()
    
    # Client settings
    shared_file_path = config['CLIENT']['Shared_File_Path']
    broadcast_address = config['CLIENT']['Broadcast_Address']
    discovery_port = int(config['CLIENT']['Discovery_Port'])
    check_interval = float(config['CLIENT']['Check_Interval'])
    max_file_age = float(config['CLIENT']['Max_File_Age'])
    
    print("\nClient Configuration:")
    print(f"  Shared File: {shared_file_path}")
    print(f"  Broadcast Address: {broadcast_address}")
    print(f"  Discovery Port: {discovery_port}")
    print(f"  Check Interval: {check_interval}s")
    print(f"  Max File Age: {max_file_age}s")
    
    logging.info(f"Client v{__version__} started")
    
    # Run startup health checks
    health_checker = HealthChecker(config, mode='client')
    if health_checker.enabled and health_checker.startup_tests:
        print()  # Blank line before health checks
        health_checker.run_all_checks()
        overall_status = health_checker.print_results(title="Startup Health Check")
    else:
        print("\n" + "="*70)
    
    print("\nMonitoring for discovery packets...\n")
    
    # Create UDP socket for broadcasting
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    last_status = None
    last_packet_hex = None
    broadcast_count = 0
    last_health_check = time.time()
    
    try:
        while True:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            current_time_val = time.time()
            
            # Periodic health check
            if (health_checker.enabled and 
                health_checker.periodic_interval > 0 and 
                current_time_val - last_health_check >= health_checker.periodic_interval):
                
                print(f"\n{current_time} - Running periodic health check...")
                health_checker.run_all_checks()
                health_checker.print_results(title="Periodic Health Check")
                last_health_check = current_time_val
            
            # Read discovery file
            packet_data, file_age_or_error = read_discovery_file(shared_file_path)
            
            if packet_data is None:
                # File not found or error
                if last_status != 'file_error':
                    print(f"{current_time} - ⚠ Cannot read discovery file: {file_age_or_error}")
                    logging.warning(f"File read error: {file_age_or_error}")
                    last_status = 'file_error'
                time.sleep(check_interval)
                continue
            
            # Check file age
            file_age = file_age_or_error
            
            if file_age > max_file_age:
                # File is too old - radio may be offline
                if last_status != 'stale':
                    print(f"{current_time} - ⚠ Discovery file is stale ({file_age:.1f}s old) - Radio may be offline")
                    logging.warning(f"Stale discovery file: {file_age:.1f}s old")
                    last_status = 'stale'
                time.sleep(check_interval)
                continue
            
            # Convert hex string back to bytes
            try:
                packet_bytes = bytes.fromhex(packet_data['packet_hex'])
                
                # Only broadcast if packet changed or status changed
                if packet_data['packet_hex'] != last_packet_hex or last_status != 'broadcasting':
                    radio_info = packet_data['radio_info']
                    print(f"{current_time} - Radio discovered:")
                    print(f"  {radio_info['model']} ({radio_info['nickname']})")
                    print(f"  Callsign: {radio_info['callsign']} | IP: {radio_info['ip']}")
                    print(f"  Status: {radio_info['status']} | Version: {radio_info['version']}")
                    print(f"  File age: {file_age:.1f}s | Server: v{packet_data.get('server_version', 'Unknown')}")
                    logging.info(f"Broadcasting: {radio_info['model']} {radio_info['nickname']} - File age: {file_age:.1f}s")
                
                # Broadcast the packet
                sock.sendto(packet_bytes, (broadcast_address, discovery_port))
                broadcast_count += 1
                
                # Status update
                if last_status != 'broadcasting':
                    print(f"{current_time} - ✓ Started broadcasting discovery packets")
                    last_status = 'broadcasting'
                else:
                    # Periodic update
                    if broadcast_count % 10 == 0:  # Every 10 broadcasts
                        print(f"{current_time} - ✓ Broadcasting... (packet #{broadcast_count}, file age: {file_age:.1f}s)")
                
                last_packet_hex = packet_data['packet_hex']
                
            except Exception as e:
                print(f"{current_time} - ⚠ Error broadcasting packet: {e}")
                logging.error(f"Broadcast error: {e}")
            
            # Wait before next check
            time.sleep(check_interval)
    
    except KeyboardInterrupt:
        print("\n\nShutdown requested by user...")
        logging.info(f"Client shutdown - Total broadcasts: {broadcast_count}")
    
    except Exception as e:
        print(f"\nFatal error: {e}")
        logging.error(f"Fatal error: {e}")
    
    finally:
        sock.close()
        print(f"Socket closed. Client stopped. (Total broadcasts: {broadcast_count})")
        logging.info("Client stopped")

if __name__ == "__main__":
    main()
