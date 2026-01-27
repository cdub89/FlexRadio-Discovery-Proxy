#!/usr/bin/env python3
"""
Test script for health check functionality
"""

import configparser
import sys
from health_checks import HealthChecker, HealthStatus

def create_test_config():
    """Create a test configuration"""
    config = configparser.ConfigParser()
    
    # Server section
    config['SERVER'] = {
        'Listen_Address': '0.0.0.0',
        'Discovery_Port': '4992',
        'Shared_File_Path': './discovery.json',
        'Update_Interval': '2.0'
    }
    
    # Client section
    config['CLIENT'] = {
        'Shared_File_Path': './discovery.json',
        'Broadcast_Address': '255.255.255.255',
        'Discovery_Port': '4992',
        'Check_Interval': '3.0',
        'Max_File_Age': '15.0'
    }
    
    # Diagnostics section
    config['DIAGNOSTICS'] = {
        'Enable_Health_Checks': 'true',
        'Startup_Tests': 'true',
        'Periodic_Check_Interval': '60.0',
        'Ping_Timeout': '5.0',
        'Display_Interface_Info': 'true',
        'Test_Server_IP': '',
        'Test_Radio_IP': ''
    }
    
    return config

def test_server_checks():
    """Test server health checks"""
    print("\n" + "="*70)
    print("TEST: Server Health Checks")
    print("="*70)
    
    config = create_test_config()
    checker = HealthChecker(config, mode='server', version='2.2.0')
    
    results = checker.run_all_checks()
    overall = checker.print_results(title="Server Health Check Test")
    
    # Verify we got results
    assert len(results) > 0, "No health check results returned"
    
    # Verify critical checks exist
    check_names = [r.name for r in results]
    assert "Version & Configuration" in check_names, "Missing version check"
    assert "Network Interfaces" in check_names, "Missing network interface check"
    assert "UDP Port 4992" in check_names, "Missing port check"
    assert "File Write Permission" in check_names, "Missing file write check"
    
    print(f"\n[+] Server checks completed: {len(results)} checks performed")
    return True

def test_client_checks():
    """Test client health checks"""
    print("\n" + "="*70)
    print("TEST: Client Health Checks")
    print("="*70)
    
    config = create_test_config()
    checker = HealthChecker(config, mode='client', version='2.2.0')
    
    results = checker.run_all_checks()
    overall = checker.print_results(title="Client Health Check Test")
    
    # Verify we got results
    assert len(results) > 0, "No health check results returned"
    
    # Verify critical checks exist
    check_names = [r.name for r in results]
    assert "Version & Configuration" in check_names, "Missing version check"
    assert "Network Interfaces" in check_names, "Missing network interface check"
    assert "UDP Port 4992" in check_names, "Missing port check"
    assert "Broadcast Capability" in check_names, "Missing broadcast check"
    assert "File Read Permission" in check_names, "Missing file read check"
    
    print(f"\n[+] Client checks completed: {len(results)} checks performed")
    return True

def test_with_ping():
    """Test with ping to localhost"""
    print("\n" + "="*70)
    print("TEST: Health Checks with Ping Test")
    print("="*70)
    
    config = create_test_config()
    # Add localhost for ping test
    config['DIAGNOSTICS']['Test_Server_IP'] = '127.0.0.1'
    
    checker = HealthChecker(config, mode='client', version='2.2.0')
    results = checker.run_all_checks()
    checker.print_results(title="Client Health Check with Ping")
    
    # Find the ping result
    ping_result = next((r for r in results if 'Connectivity' in r.name), None)
    assert ping_result is not None, "Ping check not found"
    assert ping_result.status == HealthStatus.PASS, f"Ping to localhost should pass: {ping_result.message}"
    assert ping_result.latency_ms is not None, "Ping latency not recorded"
    
    print(f"\n[+] Ping test completed: {ping_result.latency_ms:.0f}ms latency")
    return True

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("FlexRadio Discovery Proxy - Health Check Test Suite")
    print("="*70)
    
    tests = [
        ("Server Health Checks", test_server_checks),
        ("Client Health Checks", test_client_checks),
        ("Ping Test", test_with_ping)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"\n[X] Test FAILED: {test_name}")
            print(f"  Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n[X] Test ERROR: {test_name}")
            print(f"  Exception: {e}")
            failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("="*70)
    
    if failed == 0:
        print("\n[+] ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n[X] {failed} TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
