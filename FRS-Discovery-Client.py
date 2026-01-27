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
from health_checks import HealthChecker

__version__ = "3.0.0"

# Will be reconfigured after loading config
logging.basicConfig(
    filename='discovery-client.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
                        
                        # Only print if packet changed or status changed
                        if packet_data['packet_hex'] != self.last_packet_hex or self.last_status != 'broadcasting':
                            print(f"{current_time} - Radio discovered:")
                            print(f"  {radio_info['model']} ({radio_info['nickname']})")
                            print(f"  Callsign: {radio_info['callsign']} | IP: {radio_info['ip']}")
                            print(f"  Status: {radio_info['status']} | Version: {radio_info['version']}")
                            print(f"  Server: v{packet_data.get('server_version', 'Unknown')}")
                            # logging.info(f"Broadcasting: {radio_info['model']} {radio_info['nickname']}")
                        
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
        logging.error("config.ini not found")
        sys.exit(1)
    
    config.read('config.ini')
    
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
