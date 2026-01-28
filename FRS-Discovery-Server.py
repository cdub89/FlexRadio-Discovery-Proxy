#!/usr/bin/env python3
"""
FlexRadio Discovery Server v3.0.0
Captures FlexRadio VITA-49 discovery packets and streams them to clients via TCP socket.

This script runs on the remote location where the FlexRadio is located.
It listens for actual discovery broadcasts and distributes them to connected clients.

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
import threading
import select
import shutil
import glob
from health_checks import HealthChecker, HealthStatus

__version__ = "3.0.1"

# Logging will be configured after log rotation
LOG_FILE = 'discovery-server.log'

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

class ClientConnection:
    """Represents a connected client"""
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.connected_at = time.time()
        self.packets_sent = 0
    
    def send_packet(self, data):
        """Send packet data to client"""
        try:
            # Send packet as JSON with newline delimiter
            json_data = json.dumps(data) + '\n'
            bytes_data = json_data.encode('utf-8')
            self.sock.sendall(bytes_data)
            self.packets_sent += 1
            # logging.debug(f"Sent {len(bytes_data)} bytes to {self.addr} (packet #{self.packets_sent})")
            return True
        except Exception as e:
            # logging.error(f"Error sending to client {self.addr}: {e}")
            return False

class DiscoveryServer:
    """Main server class handling TCP socket streaming"""
    def __init__(self, config):
        self.config = config
        self.running = False
        self.clients = []
        self.clients_lock = threading.Lock()
        
        # Server settings
        self.listen_address = config['SERVER']['Listen_Address']
        self.discovery_port = int(config['SERVER']['Discovery_Port'])
        self.stream_port = int(config['SERVER']['Stream_Port'])
        self.max_clients = int(config['SERVER']['Max_Clients'])
        
        # Sockets
        self.udp_sock = None
        self.tcp_sock = None
        
        # Statistics
        self.packet_count = 0
        self.last_packet_time = None
        
        # Track payload changes
        self.last_payload = None
        self.first_packet_received = False
        
    def start(self):
        """Start the server"""
        print("\n" + "="*70)
        print(f"FlexRadio Discovery Server v{__version__}")
        print("="*70)
        
        print("\nServer Configuration:")
        print(f"  Listen Address: {self.listen_address}")
        print(f"  Discovery Port: {self.discovery_port}")
        print(f"  Stream Port: {self.stream_port}")
        print(f"  Max Clients: {self.max_clients}")
        
        logging.info(f"Server v{__version__} started")
        
        # Run startup health checks (before sockets are setup)
        health_checker = HealthChecker(self.config, mode='server', version=__version__)
        if health_checker.enabled and health_checker.startup_tests:
            print()  # Blank line before health checks
            health_checker.run_all_checks(is_startup=True)
            health_checker.print_results(title="Startup Health Check")
        else:
            print("\n" + "="*70)
        
        # Setup sockets
        self.setup_udp_socket()
        self.setup_tcp_socket()
        
        # Set running flag before starting accept thread
        self.running = True
        
        # Start client acceptor thread
        accept_thread = threading.Thread(target=self.accept_clients, daemon=True)
        accept_thread.start()
        
        # Post-startup verification
        if health_checker.enabled:
            print("\n" + "="*70)
            print("Post-Startup Verification")
            print("="*70)
            time.sleep(0.5)  # Give server time to start listening
            health_checker_verify = HealthChecker(self.config, mode='server', version=__version__)
            health_checker_verify.run_all_checks(is_startup=False)
            
            # Only print TCP Listener result
            tcp_result = next((r for r in health_checker_verify.results if 'TCP Listener' in r.name), None)
            if tcp_result:
                status_symbol = {
                    HealthStatus.PASS: "[+]",
                    HealthStatus.WARN: "[!]",
                    HealthStatus.FAIL: "[X]",
                    HealthStatus.SKIP: "[-]"
                }.get(tcp_result.status, "[?]")
                
                print(f"{status_symbol} [{tcp_result.status.value}]   {tcp_result.name:30} {tcp_result.message}")
                if tcp_result.latency_ms:
                    print(f"           {'':30} Connection latency: {tcp_result.latency_ms:.0f}ms")
                
                if tcp_result.status == HealthStatus.PASS:
                    print("\n✓ Server is ready to accept client connections")
                else:
                    print("\n⚠ WARNING: Server may not be accepting connections properly")
                    if tcp_result.details:
                        print(f"  Details: {tcp_result.details}")
            print("="*70)
        
        print("\nListening for FlexRadio discovery packets...")
        print("(Waiting for radio broadcasts on UDP port 4992)\n")
        
        self.running = True
        
        # Main packet reception loop
        try:
            self.run()
        except KeyboardInterrupt:
            print("\n\nShutdown requested by user...")
            logging.info("Server shutdown by user")
        except Exception as e:
            print(f"\nFatal error: {e}")
            logging.error(f"Fatal error: {e}")  # Keep fatal errors in log
        finally:
            self.stop()
    
    def setup_udp_socket(self):
        """Setup UDP socket for receiving discovery packets"""
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_sock.bind((self.listen_address, self.discovery_port))
        self.udp_sock.settimeout(1.0)  # 1 second timeout for periodic checks
    
    def setup_tcp_socket(self):
        """Setup TCP socket for client connections"""
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_sock.bind((self.listen_address, self.stream_port))
        self.tcp_sock.listen(self.max_clients)
        self.tcp_sock.settimeout(1.0)  # Non-blocking with timeout
        logging.info(f"TCP server listening on {self.listen_address}:{self.stream_port}")
    
    def accept_clients(self):
        """Accept incoming client connections"""
        try:
            # logging.info("Accept thread started")
            
            while self.running:
                try:
                    client_sock, client_addr = self.tcp_sock.accept()
                    # logging.debug(f"Accepted connection from {client_addr}")
                    
                    with self.clients_lock:
                        if len(self.clients) >= self.max_clients:
                            # logging.warning(f"Max clients reached, rejecting {client_addr}")
                            client_sock.close()
                            continue
                        
                        client = ClientConnection(client_sock, client_addr)
                        self.clients.append(client)
                        print(f"→ Client connected: {client_addr} (Total: {len(self.clients)})")
                        # logging.info(f"Client connected: {client_addr}")
                
                except socket.timeout:
                    # This is normal - just means no connection attempt in last second
                    continue
                except Exception as e:
                    if self.running:
                        pass  # logging.error(f"Error accepting client: {e}")
        except Exception as e:
            print(f"⚠ FATAL: Accept thread crashed: {e}")
            # logging.error(f"Accept thread crashed: {e}")
    
    def remove_disconnected_clients(self):
        """Remove clients that have disconnected"""
        with self.clients_lock:
            disconnected = []
            for client in self.clients:
                try:
                    # Simple check: try to get peer name
                    client.sock.getpeername()
                except:
                    # Connection is dead
                    disconnected.append(client)
            
            for client in disconnected:
                self.clients.remove(client)
                duration = time.time() - client.connected_at
                print(f"← Client disconnected: {client.addr} ({client.packets_sent} packets sent, {duration:.0f}s)")
                # logging.info(f"Client disconnected: {client.addr} - Sent {client.packets_sent} packets in {duration:.1f}s")
                try:
                    client.sock.close()
                except:
                    pass
    
    def broadcast_to_clients(self, packet_data):
        """Send packet data to all connected clients"""
        with self.clients_lock:
            if not self.clients:
                # logging.debug("No clients to broadcast to")
                return
            
            # logging.debug(f"Broadcasting packet to {len(self.clients)} client(s)")
            
            failed_clients = []
            for client in self.clients:
                success = client.send_packet(packet_data)
                # logging.debug(f"Send to {client.addr}: {'success' if success else 'FAILED'}")
                if not success:
                    failed_clients.append(client)
            
            # Remove failed clients
            for client in failed_clients:
                if client in self.clients:
                    self.clients.remove(client)
                    print(f"← Client send failed: {client.addr}")
                    # logging.warning(f"Client removed: {client.addr}")
                    try:
                        client.sock.close()
                    except:
                        pass
    
    def parse_discovery_payload(self, payload):
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
            # logging.error(f"Error parsing payload: {e}")
            return {}
    
    def run(self):
        """Main packet processing loop"""
        last_health_check = time.time()
        health_checker = HealthChecker(self.config, mode='server', version=__version__)
        
        while self.running:
            try:
                # Receive discovery packet
                data, addr = self.udp_sock.recvfrom(4096)
                
                current_time = time.time()
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                self.packet_count += 1
                
                # Only process if it's a valid VITA-49 packet
                if len(data) >= 28 and data[0:1] == b'\x38':
                    # Extract the full packet
                    packet_hex = data.hex()
                    
                    # Try to parse the payload (starts at byte 28)
                    if len(data) > 28:
                        payload = data[28:]
                        parsed_info = self.parse_discovery_payload(payload)
                        
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
                        
                        print(f"[{timestamp}] {radio_info['model']} ({radio_info['nickname']}) - {radio_info['callsign']} @ {radio_info['ip']} - {radio_info['status']}")
                        
                        # Log initial packet or payload changes
                        payload_changed = (payload != self.last_payload)
                        
                        if not self.first_packet_received:
                            # Log the first discovery packet with full details
                            logging.info("=" * 80)
                            logging.info(f"INITIAL DISCOVERY PACKET - {timestamp}")
                            logging.info("=" * 80)
                            logging.info(f"Radio: {radio_info['model']} ({radio_info['nickname']})")
                            logging.info(f"Callsign: {radio_info['callsign']} | IP: {radio_info['ip']}")
                            logging.info(f"Status: {radio_info['status']} | Version: {radio_info['version']}")
                            logging.info(f"Serial: {radio_info['serial']}")
                            logging.info(f"Source: {addr[0]}:{addr[1]} | Packet Size: {len(data)} bytes")
                            logging.info("")
                            
                            # Log full hex dump
                            logging.info("Full Packet Hex Dump:")
                            logging.info("-" * 80)
                            # Format hex dump in 16-byte lines with offset
                            for i in range(0, len(data), 16):
                                hex_part = ' '.join(f"{b:02x}" for b in data[i:i+16])
                                ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
                                logging.info(f"{i:04x}  {hex_part:<48}  {ascii_part}")
                            logging.info("-" * 80)
                            logging.info("")
                            
                            # Log all parsed fields
                            logging.info("Parsed Discovery Fields:")
                            logging.info("-" * 80)
                            for key, value in sorted(parsed_info.items()):
                                logging.info(f"  {key:30} = {value}")
                            logging.info("=" * 80)
                            logging.info("")
                            
                            # Flush log to disk immediately
                            for handler in logging.getLogger().handlers:
                                handler.flush()
                            
                            print(f"   ℹ Initial discovery packet logged to {LOG_FILE} (full hex dump included)")
                            self.first_packet_received = True
                            self.last_payload = payload
                        elif payload_changed:
                            # Log when payload changes with full details
                            logging.info("=" * 80)
                            logging.info(f"DISCOVERY PAYLOAD CHANGED - {timestamp}")
                            logging.info("=" * 80)
                            logging.info(f"Radio: {radio_info['model']} ({radio_info['nickname']})")
                            logging.info(f"Callsign: {radio_info['callsign']} | IP: {radio_info['ip']}")
                            logging.info(f"Status: {radio_info['status']} | Version: {radio_info['version']}")
                            logging.info(f"Source: {addr[0]}:{addr[1]} | Packet Size: {len(data)} bytes")
                            logging.info("")
                            
                            # Log specific changed fields
                            if self.last_payload:
                                old_parsed = self.parse_discovery_payload(self.last_payload)
                                changed_fields = []
                                for key in parsed_info.keys():
                                    if key in old_parsed and parsed_info[key] != old_parsed.get(key):
                                        changed_fields.append((key, old_parsed.get(key), parsed_info[key]))
                                    elif key not in old_parsed:
                                        changed_fields.append((key, None, parsed_info[key]))
                                
                                # Check for removed fields
                                for key in old_parsed.keys():
                                    if key not in parsed_info:
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
                            
                            # Log full hex dump
                            logging.info("Full Packet Hex Dump:")
                            logging.info("-" * 80)
                            # Format hex dump in 16-byte lines with offset
                            for i in range(0, len(data), 16):
                                hex_part = ' '.join(f"{b:02x}" for b in data[i:i+16])
                                ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
                                logging.info(f"{i:04x}  {hex_part:<48}  {ascii_part}")
                            logging.info("-" * 80)
                            logging.info("")
                            
                            # Log all current parsed fields
                            logging.info("All Current Discovery Fields:")
                            logging.info("-" * 80)
                            for key, value in sorted(parsed_info.items()):
                                logging.info(f"  {key:30} = {value}")
                            logging.info("=" * 80)
                            logging.info("")
                            
                            # Flush log to disk immediately
                            for handler in logging.getLogger().handlers:
                                handler.flush()
                            
                            print(f"   ℹ Payload change logged to {LOG_FILE} (full hex dump included)")
                            self.last_payload = payload
                        
                        # Prepare complete packet data for distribution
                        # This includes: header, stream_id, timestamps, payload - everything
                        packet_data = {
                            'timestamp': timestamp,
                            'timestamp_unix': current_time,
                            'server_version': __version__,
                            'packet_hex': packet_hex,  # Complete VITA-49 packet as hex string
                            'packet_size': len(data),
                            'source_ip': addr[0],
                            'source_port': addr[1],
                            'radio_info': radio_info,
                            'parsed_payload': parsed_info
                        }
                        
                        # Send packet to all connected clients
                        with self.clients_lock:
                            client_count = len(self.clients)
                        
                        if client_count > 0:
                            self.broadcast_to_clients(packet_data)
                            print(f"   → Sent to {client_count} client(s)")
                        else:
                            # Only show warning occasionally
                            if self.packet_count % 10 == 1:
                                print(f"   ⚠ No clients connected")
                        
                        self.last_packet_time = current_time
            
            except socket.timeout:
                # Normal timeout - check for stale connection
                current_time_val = time.time()
                if self.last_packet_time and (current_time_val - self.last_packet_time > 30):
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    print(f"{current_time} - No packets received for 30+ seconds")
                    # logging.warning("No discovery packets received for 30+ seconds")
                    self.last_packet_time = None
                
                # Remove disconnected clients
                self.remove_disconnected_clients()
                
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
                # logging.error(f"Packet processing error: {e}")
                continue
    
    def stop(self):
        """Stop the server and cleanup"""
        self.running = False
        
        # Close all client connections
        with self.clients_lock:
            for client in self.clients:
                try:
                    client.sock.close()
                except:
                    pass
            self.clients.clear()
        
        # Close sockets
        if self.udp_sock:
            self.udp_sock.close()
        if self.tcp_sock:
            self.tcp_sock.close()
        
        print(f"\nSocket(s) closed. Server stopped.")
        print(f"Total packets received: {self.packet_count}")
        logging.info(f"Server stopped - Total packets: {self.packet_count}")

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
            print("DEBUG: Debug logging enabled (check discovery-server.log for details)")
    except:
        pass
    
    return config

def main():
    config = load_config()
    server = DiscoveryServer(config)
    server.start()

if __name__ == "__main__":
    main()
