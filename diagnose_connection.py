#!/usr/bin/env python3
"""
Quick diagnostic tool for FlexRadio Discovery Proxy
Tests the connection and shows what's happening in real-time
"""

import socket
import time
import json
import sys

def test_server_connection(server_ip, stream_port):
    """Test connection to server and show what data is received"""
    print("\n" + "="*70)
    print("FlexRadio Discovery Proxy - Connection Diagnostics")
    print("="*70)
    
    print(f"\nTesting connection to {server_ip}:{stream_port}...")
    
    try:
        # Try to connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        
        start = time.time()
        sock.connect((server_ip, stream_port))
        latency = (time.time() - start) * 1000
        
        print(f"✓ Connection successful! (latency: {latency:.0f}ms)")
        
        # Set short timeout for receiving
        sock.settimeout(2.0)
        
        print("\nListening for packets from server...")
        print("(This will wait up to 30 seconds for data)\n")
        
        buffer = ""
        packet_count = 0
        start_time = time.time()
        
        while time.time() - start_time < 30:
            try:
                data = sock.recv(4096)
                
                if not data:
                    print("✗ Server closed connection")
                    break
                
                # Add to buffer
                buffer += data.decode('utf-8')
                
                # Process complete JSON messages
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    
                    if not line.strip():
                        continue
                    
                    try:
                        packet_data = json.loads(line)
                        packet_count += 1
                        
                        current_time = time.strftime("%H:%M:%S")
                        radio_info = packet_data.get('radio_info', {})
                        
                        print(f"{current_time} - Packet #{packet_count} received:")
                        print(f"  Radio: {radio_info.get('model', 'Unknown')} ({radio_info.get('nickname', 'Unknown')})")
                        print(f"  IP: {radio_info.get('ip', 'Unknown')} | Status: {radio_info.get('status', 'Unknown')}")
                        print(f"  Server version: {packet_data.get('server_version', 'Unknown')}")
                        print(f"  Packet size: {packet_data.get('packet_size', 0)} bytes\n")
                        
                    except json.JSONDecodeError as e:
                        print(f"✗ JSON decode error: {e}")
                    except Exception as e:
                        print(f"✗ Error processing packet: {e}")
            
            except socket.timeout:
                # Show periodic status
                elapsed = int(time.time() - start_time)
                if elapsed % 5 == 0:  # Every 5 seconds
                    print(f"[{elapsed}s] Waiting... (received {packet_count} packet(s) so far)")
                continue
            
            except Exception as e:
                print(f"✗ Socket error: {e}")
                break
        
        sock.close()
        
        print("\n" + "="*70)
        print("Diagnostic Results:")
        print("="*70)
        
        if packet_count > 0:
            print(f"✓ SUCCESS: Received {packet_count} packet(s) from server")
            print(f"  The connection is working correctly!")
            print(f"  If your client isn't receiving broadcasts, the issue is likely")
            print(f"  with the client's packet processing, not the connection.")
        else:
            print(f"✗ NO PACKETS: Connection works but server sent no packets")
            print(f"  Possible causes:")
            print(f"  1. Radio is not broadcasting discovery packets")
            print(f"  2. Server is not on same network as radio")
            print(f"  3. Server is not receiving packets from radio")
            print(f"  4. Check server console for 'Packet #X from...' messages")
        
        print("="*70 + "\n")
        
        return packet_count > 0
    
    except socket.timeout:
        print(f"✗ Connection timeout - cannot reach {server_ip}:{stream_port}")
        print(f"  Check firewall, VPN, or server address")
        return False
    
    except ConnectionRefusedError:
        print(f"✗ Connection refused - server not listening on {server_ip}:{stream_port}")
        print(f"  Make sure server script is running")
        return False
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Main diagnostic function"""
    # Default values
    default_ip = "192.168.1.22"
    default_port = 5992
    
    # Get server address
    if len(sys.argv) >= 2:
        server_ip = sys.argv[1]
    else:
        server_ip = input(f"Enter server IP address [{default_ip}]: ").strip() or default_ip
    
    # Get port
    if len(sys.argv) >= 3:
        stream_port = int(sys.argv[2])
    else:
        port_input = input(f"Enter stream port [{default_port}]: ").strip()
        stream_port = int(port_input) if port_input else default_port
    
    # Run test
    success = test_server_connection(server_ip, stream_port)
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user")
        sys.exit(1)
