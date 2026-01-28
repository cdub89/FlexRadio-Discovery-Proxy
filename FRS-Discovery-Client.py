#!/usr/bin/env python3
"""
FlexRadio Discovery Client v3.0.0
Receives FlexRadio discovery packets via TCP socket and rebroadcasts them locally.

This script runs on the local PC where SmartSDR client is running.
It connects to the discovery server and rebroadcasts received packets.

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
import shutil
import glob
from health_checks import HealthChecker

__version__ = "3.0.1"

# Logging will be configured after log rotation
LOG_FILE = 'discovery-client.log'

def rotate_log_file(log_file, max_log_files=2):
    """Rotate log file at startup by renaming with timestamp and clean up old logs
    
    Args:
        log_file: Path to the log file to rotate
        max_log_files: Maximum number of archived log files to keep (0 = keep all)
    """
    if os.path.exists(log_file):
        # Get file modification time for timestamp
        try:
            file_time = os.path.getmtime(log_file)
            timestamp = datetime.datetime.fromtimestamp(file_time).strftime("%Y%m%d_%H%M%S")
            
            # Create archived filename
            base_name = os.path.splitext(log_file)[0]
            ext = os.path.splitext(log_file)[1]
            archived_name = f"{base_name}_{timestamp}{ext}"
            
            # Rename existing log
            shutil.move(log_file, archived_name)
            print(f"Rotated log file: {log_file} → {archived_name}")
            
            # Clean up old log files if max_log_files is set
            if max_log_files > 0:
                cleanup_old_logs(log_file, max_log_files)
            
            return True
        except Exception as e:
            print(f"Warning: Could not rotate log file: {e}")
            return False
    return False

def cleanup_old_logs(log_file, max_log_files):
    """Remove old archived log files beyond the specified limit
    
    Args:
        log_file: Base log file name
        max_log_files: Maximum number of archived logs to keep
    """
    try:
        base_name = os.path.splitext(log_file)[0]
        ext = os.path.splitext(log_file)[1]
        directory = os.path.dirname(log_file) or '.'
        
        # Find all archived log files matching the pattern
        pattern = os.path.join(directory, f"{os.path.basename(base_name)}_*{ext}")
        archived_logs = glob.glob(pattern)
        
        # Sort by modification time (oldest first)
        archived_logs.sort(key=lambda x: os.path.getmtime(x))
        
        # Delete oldest files if we exceed the limit
        files_to_delete = len(archived_logs) - max_log_files
        if files_to_delete > 0:
            for old_log in archived_logs[:files_to_delete]:
                try:
                    os.remove(old_log)
                    print(f"Deleted old log file: {old_log}")
                except Exception as e:
                    print(f"Warning: Could not delete old log file {old_log}: {e}")
    except Exception as e:
        print(f"Warning: Could not cleanup old log files: {e}")

class DiscoveryClient:
    """Main client class handling TCP socket connection"""
    def __init__(self, config):
        self.config = config
        self.running = False
        
        # Client settings
        self.broadcast_address = config['CLIENT']['Broadcast_Address']
        self.discovery_port = int(config['CLIENT']['Discovery_Port'])
        self.server_address = config['CLIENT']['Server_Address']
        self.stream_port = int(config['CLIENT']['Stream_Port'])
        self.reconnect_interval = float(config['CLIENT']['Reconnect_Interval'])
        
        # Sockets
        self.tcp_sock = None
        self.udp_sock = None
        
        # Statistics
        self.broadcast_count = 0
        self.last_status = None
        self.last_packet_hex = None
        
        # Track payload changes
        self.last_payload = None
        self.first_packet_received = False
        
    def start(self):
        """Start the client"""
        print("\n" + "="*70)
        print(f"FlexRadio Discovery Client v{__version__}")
        print("="*70)
        
        print("\nClient Configuration:")
        print(f"  Broadcast Address: {self.broadcast_address}")
        print(f"  Discovery Port: {self.discovery_port}")
        print(f"  Server Address: {self.server_address}")
        print(f"  Stream Port: {self.stream_port}")
        print(f"  Reconnect Interval: {self.reconnect_interval}s")
        
        logging.info(f"Client v{__version__} started")
        
        # Run startup health checks
        health_checker = HealthChecker(self.config, mode='client', version=__version__)
        if health_checker.enabled and health_checker.startup_tests:
            print()  # Blank line before health checks
            health_checker.run_all_checks()
            health_checker.print_results(title="Startup Health Check")
        else:
            print("\n" + "="*70)
        
        # Setup broadcast socket
        self.setup_udp_socket()
        
        print("\nMonitoring for discovery packets...\n")
        
        self.running = True
        
        # Run client
        try:
            self.run()
        except KeyboardInterrupt:
            print("\n\nShutdown requested by user...")
            logging.info(f"Client shutdown - Total broadcasts: {self.broadcast_count}")
        except Exception as e:
            print(f"\nFatal error: {e}")
            logging.error(f"Fatal error: {e}")  # Keep fatal errors in log
        finally:
            self.stop()
    
    def setup_udp_socket(self):
        """Setup UDP socket for broadcasting"""
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    def connect_to_server(self):
        """Connect to the server via TCP"""
        try:
            if self.tcp_sock:
                try:
                    self.tcp_sock.close()
                except:
                    pass
            
            self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_sock.settimeout(10.0)  # 10 second timeout for connect
            
            print(f"Connecting to server {self.server_address}:{self.stream_port}...")
            self.tcp_sock.connect((self.server_address, self.stream_port))
            
            # Set shorter timeout for receiving data (allows periodic status updates)
            self.tcp_sock.settimeout(2.0)
            
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"\n{current_time} - ✓ Connected to server")
            print(f"  Listening for discovery packets...\n")
            # logging.info(f"Connected to server {self.server_address}:{self.stream_port}")
            return True
            
        except socket.timeout:
            print(f"⚠ Connection timeout to {self.server_address}:{self.stream_port}")
            # logging.error(f"Connection timeout")
            return False
        except ConnectionRefusedError:
            print(f"⚠ Connection refused by {self.server_address}:{self.stream_port}")
            # logging.error(f"Connection refused")
            return False
        except Exception as e:
            print(f"⚠ Connection error: {e}")
            # logging.error(f"Connection error: {e}")
            return False
    
    def run(self):
        """Run client with TCP connection to server"""
        health_checker = HealthChecker(self.config, mode='client', version=__version__)
        last_health_check = time.time()
        last_status_update = time.time()
        buffer = ""  # Buffer for incomplete JSON messages
        
        while self.running:
            # Try to connect if not connected
            if not self.tcp_sock:
                if not self.connect_to_server():
                    print(f"Retrying in {self.reconnect_interval} seconds...")
                    time.sleep(self.reconnect_interval)
                    continue
            
            try:
                # Receive data from server (with timeout)
                data = self.tcp_sock.recv(4096)
                
                if not data:
                    # Server closed connection
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"\n{current_time} - Server closed connection")
                    # logging.warning("Server closed connection")
                    self.tcp_sock = None
                    time.sleep(self.reconnect_interval)
                    continue
                
                # Log received data
                # logging.debug(f"Received {len(data)} bytes from server")
                
                # Add received data to buffer
                buffer += data.decode('utf-8')
                # logging.debug(f"Buffer now contains {len(buffer)} characters")
                
                # Process complete JSON messages (delimited by newlines)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    
                    if not line.strip():
                        # logging.debug("Skipping empty line")
                        continue
                    
                    try:
                        # logging.debug(f"Parsing JSON line ({len(line)} chars)")
                        # Parse JSON packet data
                        packet_data = json.loads(line)
                        # logging.debug(f"Successfully parsed JSON packet")
                        
                        # Extract packet hex and convert to bytes
                        packet_bytes = bytes.fromhex(packet_data['packet_hex'])
                        
                        # Display radio information
                        current_time = datetime.datetime.now().strftime("%H:%M:%S")
                        radio_info = packet_data['radio_info']
                        parsed_payload = packet_data.get('parsed_payload', {})
                        
                        # Check if payload changed (compare parsed payload as string to avoid header variations)
                        payload_str = json.dumps(parsed_payload, sort_keys=True)
                        payload_changed = (payload_str != self.last_payload)
                        
                        # Only print if packet changed or status changed
                        if packet_data['packet_hex'] != self.last_packet_hex or self.last_status != 'broadcasting':
                            print(f"{current_time} - Radio discovered:")
                            print(f"  {radio_info['model']} ({radio_info['nickname']})")
                            print(f"  Callsign: {radio_info['callsign']} | IP: {radio_info['ip']}")
                            print(f"  Status: {radio_info['status']} | Version: {radio_info['version']}")
                            print(f"  Server: v{packet_data.get('server_version', 'Unknown')}")
                        
                        # Log initial packet or payload changes
                        if not self.first_packet_received:
                            # Log the first discovery packet with full details
                            logging.info("=" * 80)
                            logging.info(f"INITIAL DISCOVERY PACKET - {current_time}")
                            logging.info("=" * 80)
                            logging.info(f"Radio: {radio_info['model']} ({radio_info['nickname']})")
                            logging.info(f"Callsign: {radio_info['callsign']} | IP: {radio_info['ip']}")
                            logging.info(f"Status: {radio_info['status']} | Version: {radio_info['version']}")
                            logging.info(f"Serial: {radio_info['serial']}")
                            logging.info(f"Server Version: {packet_data.get('server_version', 'Unknown')}")
                            logging.info(f"Broadcasting to local network on port {self.discovery_port}")
                            logging.info(f"Packet Size: {len(packet_bytes)} bytes")
                            logging.info("")
                            
                            # Log full hex dump
                            logging.info("Full Packet Hex Dump:")
                            logging.info("-" * 80)
                            # Format hex dump in 16-byte lines with offset
                            for i in range(0, len(packet_bytes), 16):
                                hex_part = ' '.join(f"{b:02x}" for b in packet_bytes[i:i+16])
                                ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in packet_bytes[i:i+16])
                                logging.info(f"{i:04x}  {hex_part:<48}  {ascii_part}")
                            logging.info("-" * 80)
                            logging.info("")
                            
                            # Log all parsed fields
                            logging.info("Parsed Discovery Fields:")
                            logging.info("-" * 80)
                            for key, value in sorted(parsed_payload.items()):
                                logging.info(f"  {key:30} = {value}")
                            logging.info("=" * 80)
                            logging.info("")
                            
                            # Flush log to disk immediately
                            for handler in logging.getLogger().handlers:
                                handler.flush()
                            
                            print(f"   ℹ Initial discovery packet logged to {LOG_FILE} (full hex dump included)")
                            self.first_packet_received = True
                            self.last_payload = payload_str
                        elif payload_changed:
                            # Log when payload changes with full details
                            logging.info("=" * 80)
                            logging.info(f"DISCOVERY PAYLOAD CHANGED - {current_time}")
                            logging.info("=" * 80)
                            logging.info(f"Radio: {radio_info['model']} ({radio_info['nickname']})")
                            logging.info(f"Callsign: {radio_info['callsign']} | IP: {radio_info['ip']}")
                            logging.info(f"Status: {radio_info['status']} | Version: {radio_info['version']}")
                            logging.info(f"Server Version: {packet_data.get('server_version', 'Unknown')}")
                            logging.info(f"Packet Size: {len(packet_bytes)} bytes")
                            logging.info("")
                            
                            # Log specific changed fields
                            if self.last_payload:
                                try:
                                    old_parsed = json.loads(self.last_payload)
                                    changed_fields = []
                                    for key in parsed_payload.keys():
                                        if key in old_parsed and parsed_payload[key] != old_parsed.get(key):
                                            changed_fields.append((key, old_parsed.get(key), parsed_payload[key]))
                                        elif key not in old_parsed:
                                            changed_fields.append((key, None, parsed_payload[key]))
                                    
                                    # Check for removed fields
                                    for key in old_parsed.keys():
                                        if key not in parsed_payload:
                                            changed_fields.append((key, old_parsed[key], None))
                                    
                                    if changed_fields:
                                        logging.info("Changed Fields:")
                                        logging.info("-" * 80)
                                        for key, old_val, new_val in changed_fields:
                                            if old_val is None:
                                                logging.info(f"  {key:30} = (new) '{new_val}'")
                                            elif new_val is None:
                                                logging.info(f"  {key:30} = (removed) was '{old_val}'")
                                            else:
                                                logging.info(f"  {key:30} = '{old_val}' → '{new_val}'")
                                        logging.info("")
                                except:
                                    pass
                            
                            # Log full hex dump
                            logging.info("Full Packet Hex Dump:")
                            logging.info("-" * 80)
                            # Format hex dump in 16-byte lines with offset
                            for i in range(0, len(packet_bytes), 16):
                                hex_part = ' '.join(f"{b:02x}" for b in packet_bytes[i:i+16])
                                ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in packet_bytes[i:i+16])
                                logging.info(f"{i:04x}  {hex_part:<48}  {ascii_part}")
                            logging.info("-" * 80)
                            logging.info("")
                            
                            # Log all current parsed fields
                            logging.info("All Current Discovery Fields:")
                            logging.info("-" * 80)
                            for key, value in sorted(parsed_payload.items()):
                                logging.info(f"  {key:30} = {value}")
                            logging.info("=" * 80)
                            logging.info("")
                            
                            # Flush log to disk immediately
                            for handler in logging.getLogger().handlers:
                                handler.flush()
                            
                            print(f"   ℹ Payload change logged to {LOG_FILE} (full hex dump included)")
                            self.last_payload = payload_str
                        
                        # Broadcast the packet
                        self.udp_sock.sendto(packet_bytes, (self.broadcast_address, self.discovery_port))
                        self.broadcast_count += 1
                        
                        # Status update
                        if self.last_status != 'broadcasting':
                            print(f"{current_time} - ✓ Started broadcasting discovery packets")
                            self.last_status = 'broadcasting'
                        else:
                            # Periodic update
                            if self.broadcast_count % 10 == 0:  # Every 10 broadcasts
                                print(f"{current_time} - ✓ Broadcasting... (packet #{self.broadcast_count})")
                        
                        self.last_packet_hex = packet_data['packet_hex']
                        
                    except json.JSONDecodeError as e:
                        # logging.error(f"JSON decode error: {e}")
                        continue
                    except Exception as e:
                        print(f"Error processing packet: {e}")
                        # logging.error(f"Packet processing error: {e}")
                        continue
                
                # Periodic health check
                current_time_val = time.time()
                if (health_checker.enabled and 
                    health_checker.periodic_interval > 0 and 
                    current_time_val - last_health_check >= health_checker.periodic_interval):
                    
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"\n{current_time} - Running periodic health check...")
                    health_checker.run_all_checks()
                    health_checker.print_results(title="Periodic Health Check")
                    last_health_check = current_time_val
            
            except socket.timeout:
                # Normal timeout - connection is idle, show periodic status
                current_time_val = time.time()
                
                # Show "waiting" status every 10 seconds if no packets received
                if current_time_val - last_status_update >= 10.0:
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    if self.last_status != 'broadcasting':
                        print(f"{current_time} - Waiting for discovery packets from server...")
                        print(f"  Connected but no packets received yet (broadcast count: {self.broadcast_count})")
                    last_status_update = current_time_val
                
                continue
            
            except ConnectionResetError:
                print("Connection reset by server")
                # logging.warning("Connection reset by server")
                self.tcp_sock = None
                self.last_status = 'disconnected'
                time.sleep(self.reconnect_interval)
            
            except Exception as e:
                print(f"Socket error: {e}")
                # logging.error(f"Socket error: {e}")
                self.tcp_sock = None
                self.last_status = 'error'
                time.sleep(self.reconnect_interval)
    
    def stop(self):
        """Stop the client and cleanup"""
        self.running = False
        
        # Close sockets
        if self.tcp_sock:
            try:
                self.tcp_sock.close()
            except:
                pass
        
        if self.udp_sock:
            self.udp_sock.close()
        
        print(f"\nSocket(s) closed. Client stopped.")
        print(f"Total broadcasts: {self.broadcast_count}")
        logging.info(f"Client stopped - Total broadcasts: {self.broadcast_count}")

def load_config():
    """Load configuration from config.ini"""
    config = configparser.ConfigParser()
    
    if not os.path.exists('config.ini'):
        print("ERROR: config.ini not found!")
        sys.exit(1)
    
    config.read('config.ini')
    
    # Get max log files setting
    max_log_files = config.getint('DIAGNOSTICS', 'Max_Log_Files', fallback=2)
    
    # Rotate log file at startup
    rotate_log_file(LOG_FILE, max_log_files)
    
    # Configure logging after rotation
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        force=True  # Override any existing configuration
    )
    
    # Configure debug logging if enabled
    try:
        debug_logging = config.getboolean('DIAGNOSTICS', 'Debug_Logging', fallback=False)
        if debug_logging:
            logging.getLogger().setLevel(logging.DEBUG)
            print("DEBUG: Debug logging enabled (check discovery-client.log for details)")
    except:
        pass
    
    return config

def main():
    config = load_config()
    client = DiscoveryClient(config)
    client.start()

if __name__ == "__main__":
    main()
