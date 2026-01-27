#!/usr/bin/env python3
"""
FlexRadio Discovery Proxy - Health Check Module
Provides diagnostic and health check functionality for both server and client.

Copyright (c) 2026 Chris L White (WX7V)

Licensed under the MIT License - see LICENSE file for details
"""

import socket
import subprocess
import platform
import time
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict

class HealthStatus(Enum):
    """Health check status levels"""
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    SKIP = "SKIP"

@dataclass
class HealthCheckResult:
    """Individual health check result"""
    name: str
    status: HealthStatus
    message: str
    details: Optional[str] = None
    latency_ms: Optional[float] = None

class HealthChecker:
    """Main health check coordinator"""
    
    def __init__(self, config, mode='server'):
        """
        Initialize health checker
        
        Args:
            config: ConfigParser object with DIAGNOSTICS section
            mode: 'server' or 'client'
        """
        self.config = config
        self.mode = mode
        self.results: List[HealthCheckResult] = []
        
        # Load diagnostic settings
        try:
            self.enabled = config.getboolean('DIAGNOSTICS', 'Enable_Health_Checks')
            self.startup_tests = config.getboolean('DIAGNOSTICS', 'Startup_Tests')
            self.periodic_interval = config.getfloat('DIAGNOSTICS', 'Periodic_Check_Interval')
            self.ping_timeout = config.getfloat('DIAGNOSTICS', 'Ping_Timeout')
            self.display_interface_info = config.getboolean('DIAGNOSTICS', 'Display_Interface_Info')
            self.test_server_ip = config.get('DIAGNOSTICS', 'Test_Server_IP', fallback='')
            self.test_radio_ip = config.get('DIAGNOSTICS', 'Test_Radio_IP', fallback='')
        except Exception as e:
            logging.warning(f"Error loading diagnostics config: {e}. Using defaults.")
            self.enabled = True
            self.startup_tests = True
            self.periodic_interval = 60.0
            self.ping_timeout = 5.0
            self.display_interface_info = True
            self.test_server_ip = ''
            self.test_radio_ip = ''
    
    def run_all_checks(self) -> List[HealthCheckResult]:
        """Run all applicable health checks based on mode"""
        self.results = []
        
        if not self.enabled:
            return self.results
        
        if self.mode == 'server':
            self._run_server_checks()
        else:
            self._run_client_checks()
        
        return self.results
    
    def _run_server_checks(self):
        """Run server-specific health checks"""
        # Network interface check
        self.results.append(self._check_network_interfaces())
        
        # Port binding check
        discovery_port = int(self.config['SERVER']['Discovery_Port'])
        self.results.append(self._check_udp_port_available(discovery_port))
        
        # Radio reachability (if configured)
        if self.test_radio_ip:
            self.results.append(self._check_ping(self.test_radio_ip, "FlexRadio"))
        
        # File write permission check
        shared_file = self.config['SERVER']['Shared_File_Path']
        self.results.append(self._check_file_write_permission(shared_file))
    
    def _run_client_checks(self):
        """Run client-specific health checks"""
        # Network interface check
        self.results.append(self._check_network_interfaces())
        
        # Port binding check
        discovery_port = int(self.config['CLIENT']['Discovery_Port'])
        self.results.append(self._check_udp_port_available(discovery_port))
        
        # Broadcast capability check
        self.results.append(self._check_broadcast_capability())
        
        # VPN/Server connectivity (if configured)
        if self.test_server_ip:
            self.results.append(self._check_ping(self.test_server_ip, "VPN/Server"))
        
        # File read permission check
        shared_file = self.config['CLIENT']['Shared_File_Path']
        self.results.append(self._check_file_read_permission(shared_file))
    
    def _check_network_interfaces(self) -> HealthCheckResult:
        """Check available network interfaces"""
        try:
            hostname = socket.gethostname()
            interfaces = []
            
            # Get all IP addresses for the host
            try:
                addrs = socket.getaddrinfo(hostname, None)
                for addr in addrs:
                    if addr[0] == socket.AF_INET:  # IPv4 only
                        ip = addr[4][0]
                        if ip not in interfaces and not ip.startswith('127.'):
                            interfaces.append(ip)
            except:
                pass
            
            if interfaces:
                details = f"Hostname: {hostname}\nAddresses: {', '.join(interfaces)}"
                return HealthCheckResult(
                    name="Network Interfaces",
                    status=HealthStatus.PASS,
                    message=f"Found {len(interfaces)} network interface(s)",
                    details=details if self.display_interface_info else None
                )
            else:
                return HealthCheckResult(
                    name="Network Interfaces",
                    status=HealthStatus.WARN,
                    message="No non-loopback interfaces found",
                    details=f"Hostname: {hostname}"
                )
        except Exception as e:
            return HealthCheckResult(
                name="Network Interfaces",
                status=HealthStatus.FAIL,
                message=f"Error detecting interfaces: {e}"
            )
    
    def _check_udp_port_available(self, port: int) -> HealthCheckResult:
        """Check if UDP port can be bound"""
        try:
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            test_sock.bind(('', port))
            test_sock.close()
            
            return HealthCheckResult(
                name=f"UDP Port {port}",
                status=HealthStatus.PASS,
                message=f"Port {port} is available"
            )
        except OSError as e:
            if "Address already in use" in str(e):
                return HealthCheckResult(
                    name=f"UDP Port {port}",
                    status=HealthStatus.WARN,
                    message=f"Port {port} already in use (may be this script)",
                    details=str(e)
                )
            else:
                return HealthCheckResult(
                    name=f"UDP Port {port}",
                    status=HealthStatus.FAIL,
                    message=f"Cannot bind to port {port}",
                    details=str(e)
                )
    
    def _check_broadcast_capability(self) -> HealthCheckResult:
        """Check if broadcast is enabled"""
        try:
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            test_sock.close()
            
            return HealthCheckResult(
                name="Broadcast Capability",
                status=HealthStatus.PASS,
                message="Broadcast is enabled"
            )
        except Exception as e:
            return HealthCheckResult(
                name="Broadcast Capability",
                status=HealthStatus.FAIL,
                message="Cannot enable broadcast",
                details=str(e)
            )
    
    def _check_ping(self, ip_address: str, target_name: str) -> HealthCheckResult:
        """Ping test to check connectivity"""
        if not ip_address:
            return HealthCheckResult(
                name=f"{target_name} Connectivity",
                status=HealthStatus.SKIP,
                message=f"No {target_name} IP configured"
            )
        
        try:
            # Determine ping command based on OS
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
            timeout_value = str(int(self.ping_timeout * 1000)) if platform.system().lower() == 'windows' else str(int(self.ping_timeout))
            
            start_time = time.time()
            result = subprocess.run(
                ['ping', param, '1', timeout_param, timeout_value, ip_address],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.ping_timeout + 1
            )
            latency = (time.time() - start_time) * 1000  # Convert to ms
            
            if result.returncode == 0:
                return HealthCheckResult(
                    name=f"{target_name} Connectivity",
                    status=HealthStatus.PASS,
                    message=f"{ip_address} is reachable",
                    latency_ms=latency
                )
            else:
                return HealthCheckResult(
                    name=f"{target_name} Connectivity",
                    status=HealthStatus.FAIL,
                    message=f"{ip_address} is not reachable",
                    details="Ping failed"
                )
        except subprocess.TimeoutExpired:
            return HealthCheckResult(
                name=f"{target_name} Connectivity",
                status=HealthStatus.FAIL,
                message=f"{ip_address} ping timeout",
                details=f"Timeout after {self.ping_timeout}s"
            )
        except Exception as e:
            return HealthCheckResult(
                name=f"{target_name} Connectivity",
                status=HealthStatus.FAIL,
                message=f"Cannot ping {ip_address}",
                details=str(e)
            )
    
    def _check_file_write_permission(self, file_path: str) -> HealthCheckResult:
        """Check if we can write to shared file location"""
        try:
            # Try to create/write to the file
            import os
            directory = os.path.dirname(file_path) or '.'
            
            if not os.path.exists(directory):
                return HealthCheckResult(
                    name="File Write Permission",
                    status=HealthStatus.FAIL,
                    message=f"Directory does not exist: {directory}"
                )
            
            # Try writing a test file
            test_file = os.path.join(directory, '.health_check_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            
            return HealthCheckResult(
                name="File Write Permission",
                status=HealthStatus.PASS,
                message=f"Can write to {directory}"
            )
        except PermissionError:
            return HealthCheckResult(
                name="File Write Permission",
                status=HealthStatus.FAIL,
                message="Permission denied",
                details=f"Cannot write to {directory}"
            )
        except Exception as e:
            return HealthCheckResult(
                name="File Write Permission",
                status=HealthStatus.WARN,
                message="Cannot verify write permission",
                details=str(e)
            )
    
    def _check_file_read_permission(self, file_path: str) -> HealthCheckResult:
        """Check if we can read from shared file location"""
        try:
            import os
            
            if not os.path.exists(file_path):
                return HealthCheckResult(
                    name="File Read Permission",
                    status=HealthStatus.WARN,
                    message="Discovery file not yet created",
                    details=f"File: {file_path}\nWaiting for server to create it"
                )
            
            # Try reading the file
            with open(file_path, 'r') as f:
                f.read(1)  # Read just one byte
            
            return HealthCheckResult(
                name="File Read Permission",
                status=HealthStatus.PASS,
                message="Can read discovery file"
            )
        except PermissionError:
            return HealthCheckResult(
                name="File Read Permission",
                status=HealthStatus.FAIL,
                message="Permission denied",
                details=f"Cannot read {file_path}"
            )
        except Exception as e:
            return HealthCheckResult(
                name="File Read Permission",
                status=HealthStatus.WARN,
                message="Cannot verify read permission",
                details=str(e)
            )
    
    def print_results(self, title: str = "Health Check Results"):
        """Print formatted health check results"""
        print("\n" + "="*70)
        print(f"{title}")
        print("="*70)
        
        # Count statuses
        pass_count = sum(1 for r in self.results if r.status == HealthStatus.PASS)
        warn_count = sum(1 for r in self.results if r.status == HealthStatus.WARN)
        fail_count = sum(1 for r in self.results if r.status == HealthStatus.FAIL)
        skip_count = sum(1 for r in self.results if r.status == HealthStatus.SKIP)
        
        # Print results
        for result in self.results:
            # Use ASCII-safe symbols for Windows compatibility
            status_symbol = {
                HealthStatus.PASS: "[+]",
                HealthStatus.WARN: "[!]",
                HealthStatus.FAIL: "[X]",
                HealthStatus.SKIP: "[-]"
            }[result.status]
            
            status_text = f"[{result.status.value}]"
            print(f"{status_symbol} {status_text:8} {result.name:30} {result.message}")
            
            if result.latency_ms:
                print(f"           {'':30} Latency: {result.latency_ms:.0f}ms")
            
            if result.details:
                for line in result.details.split('\n'):
                    print(f"           {'':30} {line}")
        
        # Summary
        print("\n" + "-"*70)
        total = len(self.results)
        summary_parts = []
        if pass_count:
            summary_parts.append(f"{pass_count} passed")
        if warn_count:
            summary_parts.append(f"{warn_count} warning(s)")
        if fail_count:
            summary_parts.append(f"{fail_count} failed")
        if skip_count:
            summary_parts.append(f"{skip_count} skipped")
        
        summary = f"Status: {', '.join(summary_parts)} (Total: {total})"
        print(summary)
        
        # Overall status
        if fail_count > 0:
            overall = "DEGRADED - Some checks failed"
        elif warn_count > 0:
            overall = "OPERATIONAL (with warnings)"
        else:
            overall = "OPERATIONAL"
        
        print(f"Overall: {overall}")
        print("="*70 + "\n")
        
        # Log summary
        logging.info(f"Health check: {summary} - Overall: {overall}")
        
        return overall
